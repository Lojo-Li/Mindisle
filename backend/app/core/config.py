"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "心屿 Mindisle"
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
    MAIL_FROM_NAME: str = "心屿 Mindisle"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.163.com"
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True

    # 验证码配置
    VERIFICATION_CODE_EXPIRE_SECONDS: int = 300  # 验证码过期时间（秒）

    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # ── 大模型（OpenAI 兼容接口，供应商可换）──────────────────────────
    # 只要服务商兼容 /chat/completions，改这三个值就能切换，代码不用动。
    # LLM_* 优先；为空时回落到下面的 DOUBAO_* 旧配置，保证老环境仍可启动。
    LLM_BASE_URL: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""

    # 豆包 API 配置（历史配置，保留兼容）
    DOUBAO_API_KEY: str = ""
    DOUBAO_APP_ID: str = ""  # 旧版控制台 App ID
    DOUBAO_ACCESS_TOKEN: str = ""  # 旧版控制台 Access Token
    DOUBAO_SECRET_KEY: str = ""  # 旧版控制台 Secret Key
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    DOUBAO_MODEL: str = "doubao-1-5-pro-32k-250115"

    @property
    def LLM_ACTIVE_BASE_URL(self) -> str:
        return self.LLM_BASE_URL or self.DOUBAO_BASE_URL

    @property
    def LLM_ACTIVE_API_KEY(self) -> str:
        return self.LLM_API_KEY or self.DOUBAO_API_KEY

    @property
    def LLM_ACTIVE_MODEL(self) -> str:
        return self.LLM_MODEL or self.DOUBAO_MODEL

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
    # 距离度量。cosine 时 distance = 1 - 相似度，阈值语义最直观；
    # l2 时 distance 为平方欧氏距离，需按归一化假设换算。
    RAG_METRIC: str = "cosine"
    # 相似度下限（0~1）。低于此值的案例不再注入 prompt。
    RAG_MIN_SIMILARITY: float = 0.45
    # 兼容旧配置：当 RAG_METRIC=l2 时作为距离阈值使用
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
        # 后面的文件覆盖前面的：.env.local 用于放真实密钥，不进版本库。
        # 仓库里的 .env 已被提交过，不要再往里写任何新密钥。
        env_file = (".env", ".env.local")
        case_sensitive = True
        # .env 里出现未声明的变量时忽略而不是崩溃：
        # 否则队友多写一行（例如 HF_HUB_OFFLINE）就会导致整个服务起不来
        extra = "ignore"


settings = Settings()
