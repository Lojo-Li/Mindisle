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
    # 距离阈值（L2 平方距离）。归一化向量下 d = 2 - 2cos，
    # 取 1.2 约等于 cos >= 0.4，低于此相关度的案例不再注入 prompt。
    # 旧值 3.0 相当于 cos >= -0.5，等于不过滤。
    RAG_DISTANCE_THRESHOLD: float = 1.2

    # ── AI 心理支持（E 线）──
    AI_ASSISTANT_NAME: str = "小屿"

    # 是否校验 AI 服务端 TLS 证书。
    # 旧代码硬编码 verify=False，等于把用户的心理自述明文暴露给中间人。
    # 只有在本地证书链确实有问题时才临时置 False，且不得用于线上。
    AI_VERIFY_SSL: bool = True

    # 风险热线（JSON 数组字符串，可在 .env 覆盖）
    # 上线前请核对号码有效性，各地号码不同
    CRISIS_HOTLINES_JSON: str = (
        '[{"name":"全国心理援助热线","number":"12356",'
        '"description":"国家卫健委统一热线，24 小时"},'
        '{"name":"北京心理危机研究与干预中心","number":"010-82951332",'
        '"description":"24 小时免费危机干预"},'
        '{"name":"希望24热线","number":"400-161-9995",'
        '"description":"24 小时心理危机干预"}]'
    )

    # 风险事件是否通知后台（写入 risk_events 后由前端轮询/后台查看）
    RISK_PERSIST_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
