"""
SoulStation - 心理咨询服务平台
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def _warmup_rag_sync():
    """在线程池中执行 RAG 冷启动，不阻塞主线程。"""
    try:
        from app.services.rag_service import rag_service
        collection = rag_service._get_collection()
        count = collection.count()
        logger.info(f"[RAG预热] 完成，知识库共 {count} 条记录")
    except Exception as e:
        logger.warning(f"[RAG预热] 失败（不影响服务启动）: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时在后台预热 RAG，避免首次请求冷启动。"""
    asyncio.get_event_loop().run_in_executor(None, _warmup_rag_sync)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="心理咨询服务平台 API",
    lifespan=lifespan
)

# A 线公共接口约定：统一错误响应 {code, message, data, detail}（保留 detail 兼容）
from app.core.api_contract import install_api_contract
install_api_contract(app)


# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
@app.get("/")
async def root():
    # 生产部署时根路径返回前端页面；本地开发无 static 目录则返回 API 信息
    spa_index = Path("static") / "index.html"
    if spa_index.is_file():
        from fastapi.responses import FileResponse
        return FileResponse(spa_index)
    return {
        "message": "Welcome to SoulStation API",
        "version": settings.APP_VERSION
    }

@app.get("/test/redis")
async def test_redis():
    """测试 Redis 连接状态"""
    from app.services.verification_redis_service import RedisVerificationCodeService
    import redis

    result = {
        "redis_enabled": settings.REDIS_ENABLED,
        "redis_host": settings.REDIS_HOST,
        "redis_port": settings.REDIS_PORT,
        "redis_db": settings.REDIS_DB,
        "redis_password_set": bool(settings.REDIS_PASSWORD)
    }

    if settings.REDIS_ENABLED:
        try:
            client = RedisVerificationCodeService._get_redis_client()

            if isinstance(client, redis.Redis):
                # 测试连接
                client.ping()

                # 测试读写
                test_key = "test:api_connection"
                client.set(test_key, "ok", ex=10)
                test_value = client.get(test_key)
                client.delete(test_key)

                result["status"] = "connected"
                result["read_write_test"] = "success" if test_value == "ok" else "failed"
                result["message"] = "Redis 连接正常"
            else:
                result["status"] = "fallback"
                result["message"] = "Redis 连接失败，使用内存存储"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Redis 错误: {str(e)}"
    else:
        result["status"] = "disabled"
        result["message"] = "Redis 未启用"

    return result

# 认证路由
from app.api.auth import router as auth_router
app.include_router(auth_router, prefix="/api")

# 心理测试路由
from app.api.test import router as test_router
app.include_router(test_router, prefix="/api")

# 用户路由
from app.api.user import router as user_router
app.include_router(user_router, prefix="/api")

# 智能问答路由
from app.api.chat.router import router as chat_router
app.include_router(chat_router, prefix="/api")

# 咨询师预约路由
from app.api.counselor import router as counselor_router, router_appointment as appointment_router, router_inquiry as inquiry_router, router_schedule as counselor_schedule_router
app.include_router(counselor_router, prefix="/api")
app.include_router(appointment_router, prefix="/api")
app.include_router(inquiry_router, prefix="/api")
app.include_router(counselor_schedule_router, prefix="/api")

# 咨询对话路由
from app.api.consultation import router as consultation_router
app.include_router(consultation_router, prefix="/api")

# 心理知识路由
from app.api.knowledge import router as knowledge_router
app.include_router(knowledge_router, prefix="/api")

# 通知路由
from app.api.notification import router as notification_router
app.include_router(notification_router, prefix="/api")

# 后台管理路由
from app.api.admin import router as admin_router
app.include_router(admin_router, prefix="/api")

# AI 心理支持路由（E 线：引用溯源 / 答案反馈 / 风险工单）
from app.api.ai_support import router as ai_support_router
app.include_router(ai_support_router, prefix="/api")

# 静态文件服务 - 用于访问上传的头像等文件
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 生产部署：托管前端构建产物（存在 static 目录时才生效，本地开发不受影响）
# 前后端同源，无需跨域配置；未匹配的路径回落到 index.html 交给 vue-router 处理
_static_dir = Path("static")
if _static_dir.is_dir() and (_static_dir / "index.html").exists():
    import mimetypes
    from fastapi.responses import FileResponse
    from fastapi import Request

    # Windows 上 Python 的 mimetypes 常把 .js 识别成 text/plain，
    # 浏览器会拒绝执行 ES module（"Failed to load module script"），必须显式注册
    for _ext, _mime in {
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".map": "application/json",
    }.items():
        mimetypes.add_type(_mime, _ext)

    app.mount("/assets", StaticFiles(directory=str(_static_dir / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str, request: Request):
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "uploads/")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = _static_dir / full_path
        if full_path and candidate.is_file():
            media_type, _ = mimetypes.guess_type(str(candidate))
            return FileResponse(candidate, media_type=media_type)
        return FileResponse(_static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
