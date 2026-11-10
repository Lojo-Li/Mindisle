"""
A 线（用户与权限）公共鉴权基座。

设计目标：在不修改 B/C/D/E 任何业务模块文件的前提下，为全站提供
  1. 单一可信的 JWT 解码入口（G1）
  2. 登出后令牌立即失效的黑名单（G5）
  3. 可供各业务线后续接入的统一角色依赖 require_roles（G1）

所有现存模块都通过 app.core.security.decode_access_token 解析令牌，
因此本模块收敛解码逻辑后，B/C/D/E 无需改动即可获得一致的安全语义。
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

_bearer_optional = HTTPBearer(auto_error=False)

# 业务角色：与 User.role 的 Enum('user', 'admin', 'counselor') 保持一致
ROLE_USER = "user"
ROLE_COUNSELOR = "counselor"
ROLE_ADMIN = "admin"


def token_fingerprint(token: str) -> str:
    """用摘要作为黑名单键，避免明文令牌落盘/落库。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class _TokenBlacklist:
    """已登出令牌黑名单。

    进程内字典保证单进程即时生效；若 Redis 可用则同时写入（带 TTL），
    以便多 worker / 重启后仍然有效。Redis 不可用时静默降级，绝不阻断业务。
    """

    _KEY_PREFIX = "auth:revoked:"

    def __init__(self) -> None:
        self._local: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._redis = None
        self._redis_disabled = False

    def _client(self):
        if self._redis is not None or self._redis_disabled:
            return self._redis
        if not getattr(settings, "REDIS_ENABLED", False):
            self._redis_disabled = True
            return None
        try:
            import redis

            client = redis.Redis(
                host=getattr(settings, "REDIS_HOST", "localhost"),
                port=getattr(settings, "REDIS_PORT", 6379),
                db=getattr(settings, "REDIS_DB", 0),
                password=getattr(settings, "REDIS_PASSWORD", None) or None,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
                decode_responses=True,
            )
            client.ping()
            self._redis = client
        except Exception as exc:  # Redis 未启动 / 网络异常均降级
            logger.warning("[AuthGuard] Redis 不可用，令牌黑名单降级为进程内存: %s", exc)
            self._redis_disabled = True
        return self._redis

    def _purge(self, now: float) -> None:
        expired = [key for key, deadline in self._local.items() if deadline <= now]
        for key in expired:
            self._local.pop(key, None)

    def revoke(self, token: str, exp: Optional[Any] = None) -> None:
        """将令牌加入黑名单，直到其自然过期为止。"""
        fp = token_fingerprint(token)
        now = time.time()
        try:
            deadline = float(exp) if exp is not None else now
        except (TypeError, ValueError):
            deadline = now
        if deadline <= now:
            deadline = now + 60  # 已过期令牌也保留 1 分钟，防止边界重放
        ttl = max(1, int(deadline - now))

        client = self._client()
        if client is not None:
            try:
                client.setex(self._KEY_PREFIX + fp, ttl, "1")
            except Exception as exc:
                logger.warning("[AuthGuard] Redis 写入黑名单失败，降级内存: %s", exc)
                self._redis = None
                self._redis_disabled = True

        with self._lock:
            self._local[fp] = deadline
            if len(self._local) > 5000:
                self._purge(now)

    def is_revoked(self, token: str) -> bool:
        fp = token_fingerprint(token)
        now = time.time()
        with self._lock:
            deadline = self._local.get(fp)
            if deadline is not None:
                if deadline > now:
                    return True
                self._local.pop(fp, None)
        client = self._client()
        if client is not None:
            try:
                return bool(client.exists(self._KEY_PREFIX + fp))
            except Exception as exc:
                logger.warning("[AuthGuard] Redis 查询黑名单失败，降级内存: %s", exc)
                self._redis = None
                self._redis_disabled = True
        return False


blacklist = _TokenBlacklist()


def _decode_unchecked(token: str) -> Optional[Dict[str, Any]]:
    """只做签名与有效期校验，不查黑名单（供登出时使用）。"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def decode_payload(token: str) -> Optional[Dict[str, Any]]:
    """全站唯一的 JWT 解码入口：签名校验 + 登出黑名单校验。

    返回 None 表示令牌无效，由各模块沿用其原有的 401 分支处理。
    """
    if not token:
        return None
    payload = _decode_unchecked(token)
    if payload is None or not payload.get("sub"):
        return None
    if blacklist.is_revoked(token):
        return None
    return payload


def revoke_token(token: str) -> bool:
    """登出时调用：让该令牌在下一次请求即失效。"""
    if not token:
        return False
    payload = _decode_unchecked(token)
    blacklist.revoke(token, payload.get("exp") if payload else None)
    return True


@dataclass(frozen=True)
class Identity:
    """统一身份对象：身份只从已签名 JWT 解析，不信任 body/query/header 透传。"""

    user_id: int
    role: str
    email: Optional[str]
    token: str
    payload: Dict[str, Any]


def resolve_identity(token: str) -> Optional[Identity]:
    payload = decode_payload(token)
    if payload is None:
        return None
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError, KeyError):
        return None
    role = payload.get("role")
    if not role:
        role = ROLE_ADMIN if payload.get("type") == "admin" else ROLE_USER
    return Identity(
        user_id=user_id,
        role=str(role),
        email=payload.get("email"),
        token=token,
        payload=payload,
    )


async def get_current_identity(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_optional),
) -> Identity:
    """A 线统一鉴权依赖（推荐 B/C/D/E 后续接入，接入前不改动其代码）。"""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    identity = resolve_identity(credentials.credentials)
    if identity is None:
        raise HTTPException(status_code=401, detail="无效的认证令牌或登录已失效")
    return identity


def require_roles(*roles: str):
    """角色守卫工厂：已登录但角色不符统一返回 403（与 401 语义分离）。

    用法： ``@router.get(..., dependencies=[Depends(require_roles("admin"))])``
    """

    async def _dependency(identity: Identity = Depends(get_current_identity)) -> Identity:
        if roles and identity.role not in roles:
            raise HTTPException(status_code=403, detail="当前角色无权访问该资源")
        return identity

    return _dependency
