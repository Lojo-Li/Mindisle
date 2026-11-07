"""
验证码存储服务
"""
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VerificationCodeService:
    """验证码服务（内存存储）"""

    # 存储验证码: {email: {"code": "123456", "expire_at": timestamp}}
    _codes: Dict[str, dict] = {}

    @staticmethod
    def _clean_expired_codes():
        """清理过期的验证码"""
        current_time = time.time()
        expired_emails = [
            email for email, data in VerificationCodeService._codes.items()
            if data.get("expire_at", 0) < current_time
        ]
        for email in expired_emails:
            del VerificationCodeService._codes[email]
            logger.info(f"清理过期验证码: {email}")

    @staticmethod
    def save_code(email: str, code: str) -> bool:
        """
        保存验证码

        Args:
            email: 邮箱
            code: 验证码

        Returns:
            bool: 是否保存成功
        """
        try:
            # 清理过期验证码
            VerificationCodeService._clean_expired_codes()

            # 计算过期时间
            expire_at = time.time() + settings.VERIFICATION_CODE_EXPIRE_SECONDS

            # 保存验证码
            VerificationCodeService._codes[email] = {
                "code": code,
                "expire_at": expire_at,
                "created_at": time.time()
            }

            logger.info(f"验证码已保存: {email}, 过期时间: {datetime.fromtimestamp(expire_at)}")
            return True

        except Exception as e:
            logger.error(f"保存验证码失败: {e}")
            return False

    @staticmethod
    def verify_code(email: str, code: str, delete: bool = True) -> bool:
        """
        验证验证码

        Args:
            email: 邮箱
            code: 验证码
            delete: 验证成功后是否删除验证码，默认True

        Returns:
            bool: 是否验证成功
        """
        try:
            # 清理过期验证码
            VerificationCodeService._clean_expired_codes()

            # 获取存储的验证码
            stored_data = VerificationCodeService._codes.get(email)

            if not stored_data:
                logger.warning(f"验证码不存在或已过期: {email}")
                return False

            # 检查是否过期
            if stored_data["expire_at"] < time.time():
                logger.warning(f"验证码已过期: {email}")
                del VerificationCodeService._codes[email]
                return False

            # 验证码匹配
            if stored_data["code"] != code:
                logger.warning(f"验证码不匹配: {email}")
                return False

            # 验证成功，根据参数决定是否删除验证码
            if delete:
                del VerificationCodeService._codes[email]
            logger.info(f"验证码验证成功: {email}, delete={delete}")
            return True

        except Exception as e:
            logger.error(f"验证验证码失败: {e}")
            return False

    @staticmethod
    def mark_verified(email: str):
        """
        标记邮箱已验证（用于重置密码流程）

        Args:
            email: 邮箱
        """
        if email in VerificationCodeService._codes:
            VerificationCodeService._codes[email]["verified"] = True

    @staticmethod
    def is_verified(email: str) -> bool:
        """
        检查邮箱是否已验证（用于重置密码流程）

        Args:
            email: 邮箱

        Returns:
            bool: 是否已验证
        """
        stored_data = VerificationCodeService._codes.get(email)
        return stored_data and stored_data.get("verified", False)

    @staticmethod
    def get_remaining_time(email: str) -> Optional[int]:
        """
        获取验证码剩余有效时间（秒）

        Args:
            email: 邮箱

        Returns:
            int: 剩余秒数，如果验证码不存在返回None
        """
        stored_data = VerificationCodeService._codes.get(email)
        if not stored_data:
            return None

        remaining = stored_data["expire_at"] - time.time()
        return max(0, int(remaining))

    @staticmethod
    def can_send_code(email: str, cooldown: int = 60) -> tuple[bool, int]:
        """
        检查是否可以发送验证码（防止频繁发送）

        Args:
            email: 邮箱
            cooldown: 冷却时间（秒），默认60秒

        Returns:
            tuple: (是否可以发送, 剩余冷却秒数)
        """
        stored_data = VerificationCodeService._codes.get(email)

        if not stored_data:
            return True, 0

        # 检查是否在冷却期内
        elapsed = time.time() - stored_data["created_at"]
        if elapsed < cooldown:
            remaining = cooldown - elapsed
            return False, int(remaining)

        return True, 0
