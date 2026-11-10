"""运行时大模型配置（支持热重载，换 key 不用重启）。

为什么要这个模块
----------------
原来 api_key 在 ``AIService.__init__`` 里一次性绑进 OpenAI 客户端，而
``ai_service`` 是模块级单例，进程不重启就永远是旧 key。可 uvicorn 重启要
重新加载 chroma 向量库和嵌入模型，十几秒内 AI 完全不可用——演示现场换 key
很难受。key 有有效期的话，这个代价会被反复支付。

策略
----
1. 若 ``LLM_CONFIG_FILE``（默认 ``./llm.json``）存在且格式正确，以它为准；
2. 否则退回环境变量 ``LLM_*`` / ``DOUBAO_*``，保持原有部署方式完全不变。

每次调用前 ``stat`` 一次文件（微秒级），mtime 或内容变了就返回新配置，
调用方据此重建客户端——于是"改文件即生效"。

文件格式（务必 .gitignore，不要提交）::

    {"base_url": "https://...", "api_key": "sk-...", "model": "deepseek-flash"}
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings

DEFAULT_FILE = "llm.json"

# backend/ 目录（本文件位于 backend/app/services/llm_config.py）
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass(frozen=True)
class LLMConfig:
    """一份已解析的大模型配置。"""

    base_url: str
    api_key: str
    model: str
    source: str  # "file" | "env"
    path: str  # source=env 时为空串
    signature: tuple  # 变化即代表需要重建客户端

    @property
    def masked_key(self) -> str:
        """脱敏后的 key，用于日志和状态接口，绝不返回明文。"""
        key = self.api_key or ""
        if len(key) <= 10:
            return "*" * len(key)
        return f"{key[:6]}{'*' * 6}{key[-4:]}"

    def describe(self) -> dict:
        return {
            "source": self.source,
            "path": self.path,
            "base_url": self.base_url,
            "model": self.model,
            "api_key": self.masked_key,
        }


def config_file_path() -> str:
    """定位配置文件。

    LLM_CONFIG_FILE 显式指定优先；否则先找 ``backend/llm.json``（不依赖启动时
    的工作目录），再退到当前目录下的 ``llm.json``。
    """
    explicit = os.getenv("LLM_CONFIG_FILE")
    if explicit:
        return os.path.abspath(explicit)

    primary = os.path.join(BACKEND_DIR, DEFAULT_FILE)
    if os.path.exists(primary):
        return primary

    cwd_candidate = os.path.abspath(DEFAULT_FILE)
    if os.path.exists(cwd_candidate):
        return cwd_candidate
    return primary


def _from_env() -> LLMConfig:
    return LLMConfig(
        base_url=settings.LLM_ACTIVE_BASE_URL,
        api_key=settings.LLM_ACTIVE_API_KEY,
        model=settings.LLM_ACTIVE_MODEL,
        source="env",
        path="",
        signature=(
            "env",
            settings.LLM_ACTIVE_BASE_URL,
            settings.LLM_ACTIVE_API_KEY,
            settings.LLM_ACTIVE_MODEL,
        ),
    )


def _from_file(path: str, mtime: float, size: int) -> Optional[LLMConfig]:
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, ValueError):
        # 文件正在被编辑时可能读到半个 JSON，此时沿用上一次的配置即可
        return None

    if not isinstance(data, dict):
        return None

    base_url = str(data.get("base_url") or "").strip()
    api_key = str(data.get("api_key") or "").strip()
    model = str(data.get("model") or "").strip()
    if not (base_url and api_key and model):
        return None

    return LLMConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        source="file",
        path=path,
        signature=(path, mtime, size, base_url, api_key, model),
    )


def load() -> LLMConfig:
    """返回当前生效的配置。每次调用都会检查一次文件是否变化。"""
    path = config_file_path()
    try:
        stat = os.stat(path)
    except OSError:
        return _from_env()

    cfg = _from_file(path, stat.st_mtime, stat.st_size)
    return cfg if cfg is not None else _from_env()
