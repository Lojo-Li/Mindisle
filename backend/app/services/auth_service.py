"""
认证服务层
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.email_service import EmailService
from app.services.verification_redis_service import VerificationCodeService
import random
import string
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_verification_code(db: Session, email: str, purpose: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        发送验证码

        Args:
            db: 数据库会话
            email: 邮箱地址
            purpose: 验证码用途，"register" 注册 / "reset" 找回密码

        Returns:
            tuple: (是否成功, 消息, 剩余冷却时间)
        """
        try:
            # 根据用途检查用户状态
            if purpose == "reset":
                # 找回密码：用户必须存在且账号正常
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    return False, "该邮箱未注册账号", 0
                if user.is_deleted:
                    return False, "账号已注销，无法找回密码", 0
                if not user.is_active:
                    return False, "账号已停用，无法找回密码", 0
            elif purpose == "register":
                # 注册：邮箱不能已被注册
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return False, "该邮箱已被注册", 0
            # 检查是否可以发送（防止频繁发送）
            can_send, remaining = VerificationCodeService.can_send_code(email, cooldown=60)
            if not can_send:
                return False, f"请等待 {remaining} 秒后再试", remaining

            # 生成验证码
            code = AuthService.generate_verification_code()

            # 保存验证码
            if not VerificationCodeService.save_code(email, code):
                return False, "验证码保存失败", 0

            # 发送邮件
            try:
                EmailService.send_verification_code(email, code)
                logger.info(f"验证码已发送到: {email}")

                # 开发环境下，在日志中打印验证码
                import os
                if os.getenv("DEBUG", "True") == "True":
                    logger.warning(f"[开发环境] 验证码: {code}")

                return True, "验证码已发送", 0

            except Exception as e:
                logger.error(f"发送邮件失败: {e}")
                # 邮件发送失败，删除已保存的验证码
                try:
                    # 尝试删除 Redis 中的验证码
                    if hasattr(VerificationCodeService, '_make_key'):
                        client = VerificationCodeService._get_redis_client()
                        if isinstance(client, __import__('redis').Redis):
                            key = VerificationCodeService._make_key(email)
                            client.delete(key)
                    else:
                        # 回退到内存存储
                        VerificationCodeService._codes.pop(email, None)
                except:
                    pass
                return False, "邮件发送失败，请稍后重试", 0

        except Exception as e:
            logger.error(f"发送验证码失败: {e}")
            return False, "发送失败，请稍后重试", 0

    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        """
        验证验证码

        Args:
            email: 邮箱
            code: 验证码

        Returns:
            bool: 是否验证成功
        """
        return VerificationCodeService.verify_code(email, code)

    @staticmethod
    def verify_code_for_reset(email: str, code: str) -> bool:
        """
        验证验证码（用于重置密码，不删除验证码）

        Args:
            email: 邮箱
            code: 验证码

        Returns:
            bool: 是否验证成功
        """
        if not VerificationCodeService.verify_code(email, code, delete=False):
            return False

        # 标记为已验证
        VerificationCodeService.mark_verified(email)
        return True

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str) -> bool:
        """
        重置密码

        Args:
            db: 数据库会话
            email: 邮箱
            new_password: 新密码

        Returns:
            bool: 是否重置成功
        """
        # 检查是否已验证
        if not VerificationCodeService.is_verified(email):
            return False

        # 获取用户
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return False

        # 更新密码
        user.password_hash = get_password_hash(new_password)
        db.commit()

        # 删除验证码（清理 Redis 或内存中的数据）
        try:
            # 尝试删除 Redis 中的验证码
            if hasattr(VerificationCodeService, '_make_key'):
                import redis
                client = VerificationCodeService._get_redis_client()
                if isinstance(client, redis.Redis):
                    key = VerificationCodeService._make_key(email)
                    client.delete(key)
                    # 同时删除已验证标记
                    verified_key = f"verified_email:{email}"
                    client.delete(verified_key)
            else:
                # 回退到内存存储
                VerificationCodeService._codes.pop(email, None)
        except:
            pass

        return True

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """创建新用户"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            nickname=user.email.split('@')[0]  # 默认昵称为邮箱前缀
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # 发送欢迎邮件（异步）
        try:
            EmailService.send_welcome_email(user.email, db_user.nickname)
        except Exception as e:
            logger.error(f"发送欢迎邮件失败: {e}")

        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """验证用户"""
        user = AuthService.get_user_by_email(db, email)
        if not user:
            logger.warning(f"用户不存在: {email}")
            return None

        logger.info(f"找到用户: {user.email}, status: {user.status}, is_verified: {user.is_verified}")

        if not verify_password(password, user.password):
            logger.warning(f"密码验证失败: {email}")
            return None

        if not user.is_active:
            logger.warning(f"用户未激活: {email}")
            return None

        if user.is_banned:
            logger.warning(f"用户已被封禁: {email}")
            return None

        logger.info(f"用户验证成功: {email}")
        return user

    @staticmethod
    def update_last_login(db: Session, user: User) -> User:
        """更新最后登录时间"""
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, login_data: UserLogin) -> Optional[dict]:
        """用户登录（支持普通用户和管理员）"""
        # 先尝试作为普通用户登录
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)

        # 如果普通用户登录失败，尝试管理员登录
        if not user:
            from app.models.admin import Admin
            admin = db.query(Admin).filter(
                (Admin.email == login_data.email) | (Admin.username == login_data.email)
            ).first()

            if admin:
                # 验证管理员密码
                if verify_password(login_data.password, admin.password_hash):
                    if not admin.is_active:
                        logger.warning(f"管理员未激活: {login_data.email}")
                        return None

                    # 更新最后登录时间
                    admin.last_login_at = datetime.utcnow()
                    db.commit()
                    db.refresh(admin)

                    # 创建访问令牌
                    access_token = create_access_token(
                        data={
                            "sub": str(admin.id),
                            "email": admin.email or admin.username,
                            "role": "admin",
                            "type": "admin"  # 标识这是管理员token
                        }
                    )

                    # 返回管理员信息和令牌
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": {
                            "id": admin.id,
                            "email": admin.email or f"{admin.username}@admin.local",
                            "nickname": admin.real_name or admin.username,
                            "role": "admin",
                            "avatar": None,
                            "is_active": admin.is_active
                        },
                        "redirect": "/admin/dashboard"
                    }

            return None

        # 普通用户登录成功
        # 更新最后登录时间
        AuthService.update_last_login(db, user)

        # 创建访问令牌
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        if user.role == "admin":
            token_data["type"] = "admin"
            # 优先使用 admins 表中的 ID 作为 sub，确保 get_current_admin 能通过 ID 直接匹配到记录
            from app.models.admin import Admin as AdminModel
            admin_record = db.query(AdminModel).filter(
                AdminModel.email == user.email,
                AdminModel.deleted_at.is_(None)
            ).first()
            if admin_record:
                token_data["sub"] = str(admin_record.id)
        access_token = create_access_token(data=token_data)

        # 根据角色确定跳转路径
        redirect_path = "/"
        if user.role == "admin":
            redirect_path = "/admin"
        elif user.role == "counselor":
            redirect_path = "/counselor/dashboard"  # 咨询师工作台
        else:
            redirect_path = "/"

        # 返回用户信息和令牌
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
            "redirect": redirect_path
        }

    @staticmethod
    def register(db: Session, user_data: UserCreate, code: str) -> Optional[User]:
        """用户注册"""
        # 验证验证码
        if not AuthService.verify_code(user_data.email, code):
            return None

        # 检查邮箱是否已存在
        existing_user = AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
            return None

        # 创建用户
        return AuthService.create_user(db, user_data)
