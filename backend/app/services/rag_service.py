"""
RAG 服务 - 基于 ChromaDB 的向量检索增强生成
"""
import logging
import os
import threading
from typing import List, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)

# HuggingFace 的离线开关必须在导入 sentence-transformers 之前写进进程环境，
# 放进 .env 是无效的（那个库直接读 os.environ）。
# 本地已有模型时强制离线：否则离线/断网环境下每次检索都会去联网重试，
# 表现为"发消息后迟迟不出字"，很难从日志看出原因。
_MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")
)
if os.path.isdir(_MODELS_DIR) and os.listdir(_MODELS_DIR):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
else:
    # 没有本地模型又需要下载时，国内直连 huggingface.co 经常超时，默认走镜像
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


class RAGService:
    """RAG 向量检索服务，延迟初始化避免启动时加载大模型"""

    # 模型本地路径（相对于 backend/ 目录）
    _LOCAL_MODEL_PATH = "models/"

    def __init__(self):
        self._client = None
        self._collection = None
        self._ef = None
        self._lock = threading.Lock()  # 防止并发初始化时的竞争条件

    def _get_embedding_function(self):
        """懒加载 Sentence-Transformers 嵌入函数（优先本地模型目录）"""
        if self._ef is None:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            # 优先从本地目录加载，避免连 huggingface.co
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            # 归一化为绝对路径：带尾分隔符的相对路径会被当成模型名去联网拉取
            local_path = os.path.abspath(os.path.join(base_dir, self._LOCAL_MODEL_PATH))
            if os.path.isdir(local_path):
                logger.info(f"[RAG] 从本地加载嵌入模型: {local_path}")
                self._ef = SentenceTransformerEmbeddingFunction(model_name=local_path)
            else:
                logger.info("[RAG] 未找到本地模型，从 HuggingFace 在线加载")
                self._ef = SentenceTransformerEmbeddingFunction(
                    model_name="paraphrase-multilingual-MiniLM-L12-v2"
                )
        return self._ef

    def _resolve_db_path(self) -> str:
        """解析向量库路径；路径含非 ASCII 字符时自动迁移到纯英文目录。

        为什么必须这么做：底层的 hnswlib 按字节打开文件，遇到中文路径会
        直接报 "Cannot open header file"。这个错误的迷惑性很强——数据本身
        完好，但检索永远返回 0 条，前端表现为"回答没有依据、内容变空泛"，
        不像报错，更像模型能力下降。

        中文目录在国内开发机上极常见（例如 E:\\...\\腾讯实训营\\...），
        所以这里不靠"记得改配置"，而是自动把索引复制到用户目录下的
        ASCII 路径再使用。
        """
        raw = (settings.CHROMA_DB_PATH or "./chroma_db").strip()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = raw if os.path.isabs(raw) else os.path.join(base_dir, raw.lstrip("./\\"))
        path = os.path.abspath(path)

        if all(ord(ch) < 128 for ch in path):
            return path

        safe_root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        safe_path = os.path.join(safe_root, "mindisle_chroma")

        # 目标不存在、或源库比缓存新（重建过向量库）时才复制。
        # 少了这个判断，升级向量库后仍会读到旧缓存，表现为"明明重建了还是查不到"。
        src_db = os.path.join(path, "chroma.sqlite3")
        dst_db = os.path.join(safe_path, "chroma.sqlite3")
        need_copy = not os.path.exists(dst_db)
        if not need_copy:
            try:
                need_copy = os.path.getmtime(src_db) > os.path.getmtime(dst_db) + 1
            except OSError:
                need_copy = True

        if need_copy:
            try:
                import shutil
                if os.path.exists(safe_path):
                    shutil.rmtree(safe_path, ignore_errors=True)
                shutil.copytree(path, safe_path, dirs_exist_ok=True)
                logger.warning(
                    "[RAG] 向量库路径含非 ASCII 字符（hnswlib 无法打开），"
                    "已复制到纯英文路径：%s", safe_path
                )
            except Exception as exc:
                logger.error("[RAG] 迁移向量库失败，退回原路径（检索可能失效）：%s", exc)
                return path
        return safe_path

    def _get_client(self):
        """懒加载 ChromaDB 客户端"""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            db_path = self._resolve_db_path()
            os.makedirs(db_path, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client

    def _get_collection(self):
        """获取或创建集合（双重检查锁，线程安全）"""
        if self._collection is None:
            with self._lock:
                if self._collection is None:
                    client = self._get_client()
                    self._collection = client.get_or_create_collection(
                        name=settings.CHROMA_COLLECTION_NAME,
                        embedding_function=self._get_embedding_function()
                    )
        return self._collection

    def search_with_sources(self, query: str, n_results: int = None) -> List[Dict]:
        """
        检索相似案例，并返回可用于"引用出处"的结构化信息。

        与 search_similar 的区别：额外返回 vector_id、score（换算到 0~1 的
        相似度）、title 与 snippet，供前端展示"参考来源"并落库溯源。

        Returns:
            List[Dict]: 每项包含 vector_id / input / output / distance / score
                        / title / snippet
        """
        if n_results is None:
            n_results = settings.RAG_TOP_K

        try:
            collection = self._get_collection()
            count = collection.count()
            if count == 0:
                return []

            actual_n = min(n_results, count)
            results = collection.query(
                query_texts=[query],
                n_results=actual_n
            )

            sources = []
            ids = results.get("ids", [[]])[0]
            metric = getattr(settings, "RAG_METRIC", "cosine")
            min_sim = getattr(settings, "RAG_MIN_SIMILARITY", 0.45)
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i]
                # cosine: distance = 1 - 相似度；l2: 归一化向量下 d = 2 - 2cos
                if metric == "cosine":
                    score = max(0.0, min(1.0, 1 - distance))
                else:
                    score = max(0.0, min(1.0, 1 - distance / 2))
                if score < min_sim:
                    continue
                metadata = results["metadatas"][0][i] or {}
                sources.append({
                    "vector_id": ids[i] if i < len(ids) else None,
                    "input": doc,
                    "output": metadata.get("output", ""),
                    "distance": round(distance, 4),
                    "score": round(score, 4),
                    "title": (doc or "").strip()[:24] or "心理知识片段",
                    "snippet": (metadata.get("output") or doc or "").strip()[:120],
                })

            if sources:
                print(f"[RAG] 查询「{query[:30]}」→ 命中 {len(sources)} 条")
            else:
                print(f"[RAG] 查询「{query[:30]}」→ 无命中（相似度下限 {min_sim}）")

            return sources

        except Exception as e:
            logger.warning(f"RAG 检索失败，跳过增强: {e}")
            return []

    def search_similar(self, query: str, n_results: int = None) -> List[Dict]:
        """
        检索与用户输入语义相似的心理咨询案例（兼容旧调用）

        Args:
            query: 用户当前消息
            n_results: 返回结果数量，默认使用配置值

        Returns:
            List[Dict]: 相似案例列表，每项包含 input、output、distance
        """
        sources = self.search_with_sources(query, n_results)
        return [
            {
                "input": s["input"],
                "output": s["output"],
                "distance": s["distance"],
            }
            for s in sources
        ]

    def get_collection_count(self) -> int:
        """获取知识库中的记录数量"""
        try:
            return self._get_collection().count()
        except Exception:
            return 0

    def is_ready(self) -> bool:
        """检查知识库是否已有数据"""
        return self.get_collection_count() > 0


# 全局单例
rag_service = RAGService()
