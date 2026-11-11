"""云托管适配中间件（纯 ASGI 实现）。

云托管平台的反向代理会占用 Authorization 头（注入平台自身的 JWT），
导致应用自己签发的 token 无法到达后端。这里做两件事：

1. 若请求带 X-App-Token，用它替换 Authorization；
2. 若无 X-App-Token 且 Authorization 是平台注入的（iss=cloudstudio），剔除之。

采用纯 ASGI 中间件而非 BaseHTTPMiddleware：后者会先行解析并缓存 headers，
之后再改 scope 往往不生效。
"""

APP_TOKEN_HEADER = b"x-app-token"
AUTH_HEADER = b"authorization"


def _payload_of(token: str):
    """解析 JWT payload（不验签，仅用于识别平台 token）。"""
    import base64
    import json

    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:  # noqa: BLE001
        return None


def _is_platform_token(auth_value: str) -> bool:
    """平台注入的 token payload 里 iss 含 cloudstudio。"""
    if not auth_value or not auth_value.lower().startswith("bearer "):
        return False
    data = _payload_of(auth_value.split(" ", 1)[1])
    return bool(data) and "cloudstudio" in str(data.get("iss", ""))


class AppTokenMiddleware:
    """把 X-App-Token 提升为标准 Authorization: Bearer <token>。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw = list(scope.get("headers") or [])

        app_token = None
        for key, value in raw:
            if key.lower() == APP_TOKEN_HEADER:
                app_token = value.decode("latin-1").strip()
                break

        if app_token:
            raw = [(k, v) for k, v in raw if k.lower() != AUTH_HEADER]
            raw.append((AUTH_HEADER, f"Bearer {app_token}".encode("latin-1")))
        else:
            raw = [
                (k, v)
                for k, v in raw
                if not (k.lower() == AUTH_HEADER and _is_platform_token(v.decode("latin-1")))
            ]

        scope["headers"] = raw
        await self.app(scope, receive, send)
