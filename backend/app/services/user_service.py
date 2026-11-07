"""
用户服务层 - 个人中心功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from pathlib import Path
import uuid
import os

from app.models.user import User
from app.models.chat import ChatDialogue, ChatMessage, ChatTag, ChatDialogueTag
from app.models.test import TestResult
from app.models.counselor import Appointment
from app.models.knowledge import KnowledgeFavorite
from app.schemas.user import (
    UserProfileResponse, UserProfileUpdate, PrivacySettings,
    UserStatistics, ActivityTrendItem, TestDistributionItem, ChatDistributionItem
)


class UserService:
    """用户服务 - 个人中心功能"""

    # ==================== 用户资料管理 ====================

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> UserProfileResponse:
        """获取用户资料"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            gender=user.gender,
            birth_date=user.birth_date,
            phone=user.phone,
            bio=user.bio,
            role=user.role,  # 使用用户的实际角色，而不是硬编码为"user"
            status=user.status,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )

    @staticmethod
    def update_user_profile(db: Session, user_id: int, update_data: UserProfileUpdate) -> UserProfileResponse:
        """更新用户资料"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        # 更新字段
        if update_data.nickname is not None:
            user.nickname = update_data.nickname
        if update_data.phone is not None:
            user.phone = update_data.phone
        if update_data.birth_date is not None:
            user.birth_date = update_data.birth_date
        if update_data.gender is not None:
            user.gender = update_data.gender
        if update_data.bio is not None:
            user.bio = update_data.bio

        db.commit()
        db.refresh(user)

        return UserService.get_user_profile(db, user_id)

    # ==================== 头像上传 ====================

    @staticmethod
    def upload_avatar(file_data: bytes, filename: str, content_type: str) -> str:
        """上传头像文件"""
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if content_type not in allowed_types:
            raise ValueError("不支持的文件类型，仅支持 JPG、PNG、GIF 格式")

        # 验证文件大小（2MB）
        max_size = 2 * 1024 * 1024
        if len(file_data) > max_size:
            raise ValueError("文件大小不能超过 2MB")

        # 创建上传目录
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名
        file_ext = Path(filename).suffix or '.jpg'
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = upload_dir / unique_filename

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_data)

        # 返回访问URL
        return f"/uploads/avatars/{unique_filename}"

    @staticmethod
    def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> UserProfileResponse:
        """更新用户头像"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        user.avatar = avatar_url
        # 注意：不在这里commit，由调用方统一管理事务
        db.flush()
        db.refresh(user)

        return UserService.get_user_profile(db, user_id)

    # ==================== 隐私设置 ====================

    @staticmethod
    def get_privacy_settings(db: Session, user_id: int) -> PrivacySettings:
        """获取隐私设置"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        return PrivacySettings(
            save_chat_history=user.save_chat_history,
            chat_visible=not user.chat_only_visible,
            save_test_records=user.save_test_records,
            allow_trend_analysis=user.allow_trend_analysis
        )

    @staticmethod
    def update_privacy_settings(db: Session, user_id: int, settings: PrivacySettings) -> PrivacySettings:
        """更新隐私设置"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        # 更新隐私设置
        user.save_chat_history = settings.save_chat_history
        user.chat_only_visible = not settings.chat_visible
        user.save_test_records = settings.save_test_records
        user.allow_trend_analysis = settings.allow_trend_analysis

        db.commit()
        db.refresh(user)

        return UserService.get_privacy_settings(db, user_id)

    # ==================== 数据清除 ====================

    @staticmethod
    def clear_chat_history(db: Session, user_id: int) -> int:
        """清除对话记录"""
        # 获取用户的所有对话ID
        dialogue_ids = db.query(ChatDialogue.id).filter(
            ChatDialogue.user_id == user_id
        ).all()

        dialogue_ids = [d[0] for d in dialogue_ids]

        if not dialogue_ids:
            return 0

        # 删除对话消息
        deleted_messages = db.query(ChatMessage).filter(
            ChatMessage.dialogue_id.in_(dialogue_ids)
        ).delete(synchronize_session=False)

        # 删除对话
        deleted_dialogues = db.query(ChatDialogue).filter(
            ChatDialogue.id.in_(dialogue_ids)
        ).delete(synchronize_session=False)

        db.commit()

        return deleted_dialogues

    @staticmethod
    def clear_test_records(db: Session, user_id: int) -> int:
        """清除测试记录"""
        # 先删除进度记录
        db.query(TestResult).filter(
            and_(
                TestResult.user_id == user_id,
                TestResult.is_deleted == False
            )
        ).delete(synchronize_session=False)

        deleted_count = db.query(TestResult).filter(
            TestResult.user_id == user_id
        ).delete(synchronize_session=False)

        db.commit()

        return deleted_count

    # ==================== 数据统计 ====================

    @staticmethod
    def get_user_statistics(db: Session, user_id: int, time_range: str = "30days") -> UserStatistics:
        """获取用户数据统计"""
        # 计算时间范围
        days_map = {
            "7days": 7,
            "30days": 30,
            "90days": 90
        }
        days = days_map.get(time_range, 30)
        start_date = datetime.now() - timedelta(days=days)

        # 统计测试次数
        test_count = db.query(func.count(TestResult.id)).filter(
            and_(
                TestResult.user_id == user_id,
                TestResult.created_at >= start_date,
                TestResult.is_deleted == False
            )
        ).scalar() or 0

        # 统计对话次数
        chat_count = db.query(func.count(ChatDialogue.id)).filter(
            and_(
                ChatDialogue.user_id == user_id,
                ChatDialogue.created_at >= start_date,
                ChatDialogue.is_deleted == False
            )
        ).scalar() or 0

        # 统计预约次数
        appointment_count = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.user_id == user_id,
                Appointment.created_at >= start_date,
                Appointment.status.in_(['pending', 'confirmed', 'in_progress', 'completed'])
            )
        ).scalar() or 0

        # 统计收藏文章次数
        favorite_count = db.query(func.count(KnowledgeFavorite.id)).filter(
            and_(
                KnowledgeFavorite.user_id == user_id,
                KnowledgeFavorite.created_at >= start_date
            )
        ).scalar() or 0

        return UserStatistics(
            test_count=test_count,
            chat_count=chat_count,
            appointment_count=appointment_count,
            favorite_count=favorite_count
        )

    @staticmethod
    def get_activity_trend(db: Session, user_id: int, time_range: str = "30days") -> List[ActivityTrendItem]:
        """获取活动趋势数据"""
        # 计算时间范围
        days_map = {
            "7days": 7,
            "30days": 30,
            "90days": 90
        }
        days = days_map.get(time_range, 30)
        start_date = datetime.now() - timedelta(days=days)

        # 查询每日活动数据（对话 + 测试）
        trend_data = []

        for i in range(days):
            current_date = (datetime.now() - timedelta(days=days - i - 1)).date()
            next_date = current_date + timedelta(days=1)

            # 统计该日期的对话数
            chat_count = db.query(func.count(ChatDialogue.id)).filter(
                and_(
                    ChatDialogue.user_id == user_id,
                    ChatDialogue.created_at >= datetime.combine(current_date, datetime.min.time()),
                    ChatDialogue.created_at < datetime.combine(next_date, datetime.min.time()),
                    ChatDialogue.is_deleted == False
                )
            ).scalar() or 0

            # 统计该日期的测试数
            test_count = db.query(func.count(TestResult.id)).filter(
                and_(
                    TestResult.user_id == user_id,
                    TestResult.created_at >= datetime.combine(current_date, datetime.min.time()),
                    TestResult.created_at < datetime.combine(next_date, datetime.min.time()),
                    TestResult.is_deleted == False
                )
            ).scalar() or 0

            trend_data.append(ActivityTrendItem(
                date=current_date.strftime("%Y-%m-%d"),
                count=chat_count + test_count
            ))

        return trend_data

    @staticmethod
    def get_test_distribution(db: Session, user_id: int) -> List[TestDistributionItem]:
        """获取测试分类分布"""
        # 优先使用test_id，如果为空则使用questionnaire_id
        results = db.query(
            func.coalesce(TestResult.test_id, TestResult.questionnaire_id).label('test_id'),
            func.count(TestResult.id).label('count')
        ).filter(
            and_(
                TestResult.user_id == user_id,
                TestResult.is_deleted == False
            )
        ).group_by(
            func.coalesce(TestResult.test_id, TestResult.questionnaire_id)
        ).all()

        distribution = []
        # TODO: 需要关联 PsychologicalTest 表获取测试名称
        # 目前使用测试ID作为名称
        for test_id, count in results:
            distribution.append(TestDistributionItem(
                name=f"测试{test_id}",
                value=count
            ))

        return distribution

    @staticmethod
    def get_chat_distribution(db: Session, user_id: int) -> List[ChatDistributionItem]:
        """获取对话主题分布"""
        # 通过 ChatDialogueTag 中间表统计标签分布
        results = db.query(
            ChatTag.name,
            func.count(ChatDialogue.id).label('count')
        ).join(
            ChatDialogueTag, ChatDialogueTag.tag_id == ChatTag.id
        ).join(
            ChatDialogue, ChatDialogue.id == ChatDialogueTag.dialogue_id
        ).filter(
            and_(
                ChatDialogue.user_id == user_id,
                ChatDialogue.is_deleted == False,
                ChatTag.is_deleted == False
            )
        ).group_by(ChatTag.id, ChatTag.name).all()

        distribution = []
        for tag_name, count in results:
            distribution.append(ChatDistributionItem(
                name=tag_name,
                count=count
            ))

        return distribution

    # ==================== 账户管理 ====================

    @staticmethod
    def delete_account(db: Session, user_id: int) -> bool:
        """注销账户"""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("用户不存在")

        # 标记为已删除
        user.is_deleted = True
        user.deleted_at = datetime.now()
        user.email = f"deleted_{user.id}_{user.email}"  # 邮箱可复用

        # 清除关联数据
        UserService.clear_chat_history(db, user_id)
        UserService.clear_test_records(db, user_id)

        db.commit()

        return True
