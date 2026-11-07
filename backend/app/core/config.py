"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "SoulStation"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/soulstation"

    # JWT 配置
    SECRET_KEY: str = "soulstation-secret-key-2024-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30天

    # 邮件配置
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "SoulStation"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.163.com"
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True

    # 验证码配置
    VERIFICATION_CODE_EXPIRE_SECONDS: int = 300  # 验证码过期时间（秒）

    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # 豆包 API 配置
    DOUBAO_API_KEY: str = ""
    DOUBAO_APP_ID: str = ""  # 旧版控制台 App ID
    DOUBAO_ACCESS_TOKEN: str = ""  # 旧版控制台 Access Token
    DOUBAO_SECRET_KEY: str = ""  # 旧版控制台 Secret Key
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    DOUBAO_MODEL: str = "doubao-1-5-pro-32k-250115"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "redis123456"
    REDIS_ENABLED: bool = True

    # 文件上传配置
    UPLOAD_DIR: str = "./app/static/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 前端 URL
    FRONTEND_URL: str = "http://localhost:5173"

    # 公网访问URL（用于语音识别等需要公网访问的场景）
    PUBLIC_URL: str = "http://localhost:8000"

    # ChromaDB 配置
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "psychology_kb"
    RAG_TOP_K: int = 3  # 检索返回的相似案例数量
    RAG_DISTANCE_THRESHOLD: float = 3.0  # 距离阈值，超过此值视为相关性不足

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
