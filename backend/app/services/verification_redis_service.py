"""
验证码存储服务（Redis版本）

使用Redis存储验证码，支持分布式部署和持久化
"""
import json
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
import redis
from redis import Redis
from redis.connection import ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisVerificationCodeService:
    """验证码服务（Redis存储）"""

    _redis_pool: Optional[ConnectionPool] = None
    _redis_client: Optional[Redis] = None

    @classmethod
    def _get_redis_client(cls) -> Redis:
        """
        获取Redis客户端连接

        Returns:
            Redis: Redis客户端实例
        """
        if cls._redis_client is None:
            try:
                # 创建连接池
                cls._redis_pool = ConnectionPool(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )

                # 创建Redis客户端
                cls._redis_client = Redis(
                    connection_pool=cls._redis_pool
                )

                # 测试连接
                cls._redis_client.ping()
                logger.info(f"Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")

            except Exception as e:
                logger.error(f"Redis连接失败: {e}")
                # 如果Redis连接失败，回退到内存存储
                logger.warning("回退到内存存储模式")
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService

        return cls._redis_client

    @classmethod
    def _make_key(cls, email: str) -> str:
        """
        生成Redis key

        Args:
            email: 邮箱

        Returns:
            str: Redis key
        """
        return f"verification_code:{email}"

    @classmethod
    def _make_cooldown_key(cls, email: str) -> str:
        """
        生成冷却时间key

        Args:
            email: 邮箱

        Returns:
            str: Redis key
        """
        return f"verification_cooldown:{email}"

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
            client = RedisVerificationCodeService._get_redis_client()

            # 如果回退到内存存储
            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.save_code(email, code)

            key = RedisVerificationCodeService._make_key(email)

            # 准备存储的数据
            data = {
                "code": code,
                "email": email,
                "created_at": datetime.now().isoformat()
            }

            # 保存到Redis，设置过期时间
            expire_seconds = settings.VERIFICATION_CODE_EXPIRE_SECONDS
            client.setex(
                key,
                expire_seconds,
                json.dumps(data)
            )

            # 设置冷却时间（防止频繁发送）
            cooldown_key = RedisVerificationCodeService._make_cooldown_key(email)
            client.setex(cooldown_key, 60, "1")  # 60秒冷却

            logger.info(f"验证码已保存到Redis: {email}, 过期时间: {expire_seconds}秒")
            return True

        except Exception as e:
            logger.error(f"保存验证码到Redis失败: {e}")
            # 回退到内存存储
            try:
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.save_code(email, code)
            except:
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
            client = RedisVerificationCodeService._get_redis_client()

            # 如果回退到内存存储
            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.verify_code(email, code, delete)

            key = RedisVerificationCodeService._make_key(email)

            # 从Redis获取验证码
            data_str = client.get(key)

            if not data_str:
                logger.warning(f"验证码不存在或已过期: {email}")
                return False

            data = json.loads(data_str)

            # 验证码匹配
            if data["code"] != code:
                logger.warning(f"验证码不匹配: {email}")
                return False

            # 验证成功，根据参数决定是否删除验证码
            if delete:
                client.delete(key)
                logger.info(f"验证码验证成功并已删除: {email}")
            else:
                logger.info(f"验证码验证成功: {email}, delete={delete}")

            return True

        except Exception as e:
            logger.error(f"验证验证码失败: {e}")
            # 回退到内存存储
            try:
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.verify_code(email, code, delete)
            except:
                return False

    @staticmethod
    def mark_verified(email: str):
        """
        标记邮箱已验证（用于重置密码流程）

        Args:
            email: 邮箱
        """
        try:
            client = RedisVerificationCodeService._get_redis_client()

            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.mark_verified(email)

            key = f"verified_email:{email}"
            client.setex(key, 600, "1")  # 10分钟有效
            logger.info(f"标记邮箱已验证: {email}")

        except Exception as e:
            logger.error(f"标记邮箱验证失败: {e}")

    @staticmethod
    def is_verified(email: str) -> bool:
        """
        检查邮箱是否已验证（用于重置密码流程）

        Args:
            email: 邮箱

        Returns:
            bool: 是否已验证
        """
        try:
            client = RedisVerificationCodeService._get_redis_client()

            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.is_verified(email)

            key = f"verified_email:{email}"
            return client.exists(key) > 0

        except Exception as e:
            logger.error(f"检查邮箱验证状态失败: {e}")
            return False

    @staticmethod
    def get_remaining_time(email: str) -> Optional[int]:
        """
        获取验证码剩余有效时间（秒）

        Args:
            email: 邮箱

        Returns:
            int: 剩余秒数，如果验证码不存在返回None
        """
        try:
            client = RedisVerificationCodeService._get_redis_client()

            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.get_remaining_time(email)

            key = RedisVerificationCodeService._make_key(email)
            ttl = client.ttl(key)

            if ttl < 0:
                return None

            return int(ttl)

        except Exception as e:
            logger.error(f"获取验证码剩余时间失败: {e}")
            return None

    @staticmethod
    def can_send_code(email: str, cooldown: int = 60) -> Tuple[bool, int]:
        """
        检查是否可以发送验证码（防止频繁发送）

        Args:
            email: 邮箱
            cooldown: 冷却时间（秒），默认60秒

        Returns:
            tuple: (是否可以发送, 剩余冷却秒数)
        """
        try:
            client = RedisVerificationCodeService._get_redis_client()

            if not isinstance(client, Redis):
                from app.services.verification_service import VerificationCodeService
                return VerificationCodeService.can_send_code(email, cooldown)

            cooldown_key = RedisVerificationCodeService._make_cooldown_key(email)
            ttl = client.ttl(cooldown_key)

            if ttl > 0:
                return False, int(ttl)

            return True, 0

        except Exception as e:
            logger.error(f"检查发送限制失败: {e}")
            return True, 0

    @classmethod
    def close_connection(cls):
        """关闭Redis连接"""
        if cls._redis_pool:
            cls._redis_pool.disconnect()
            cls._redis_pool = None
            cls._redis_client = None
            logger.info("Redis连接已关闭")


# 导出兼容的接口
def get_verification_service():
    """
    获取验证码服务实例

    根据配置自动选择使用Redis或内存存储

    Returns:
        验证码服务类
    """
    # 检查是否启用了Redis
    redis_enabled = getattr(settings, 'REDIS_ENABLED', True)

    if redis_enabled:
        try:
            # 尝试连接Redis
            client = RedisVerificationCodeService._get_redis_client()
            if isinstance(client, Redis):
                logger.info("使用Redis存储验证码")
                return RedisVerificationCodeService
        except Exception as e:
            logger.warning(f"Redis不可用，使用内存存储: {e}")

    # 回退到内存存储
    logger.info("使用内存存储验证码")
    from app.services.verification_service import VerificationCodeService
    return VerificationCodeService


# 默认导出Redis版本
VerificationCodeService = get_verification_service()
