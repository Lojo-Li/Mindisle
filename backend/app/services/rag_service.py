"""
RAG 服务 - 基于 ChromaDB 的向量检索增强生成
"""
import logging
import os
import threading
from typing import List, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        """懒加载 Sentence-Transformers 嵌入函数（先从本地加载）"""
        if self._ef is None:
            import os
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            # 优先从本地目录加载，避免连 huggingface.co
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_path = os.path.join(base_dir, self._LOCAL_MODEL_PATH)
            if os.path.isdir(local_path):
                logger.info(f"[RAG] 从本地加载嵌入模型: {local_path}")
                self._ef = SentenceTransformerEmbeddingFunction(model_name=local_path)
            else:
                logger.info("[RAG] 未找到本地模型，从 HuggingFace 在线加载")
                self._ef = SentenceTransformerEmbeddingFunction(
                    model_name="paraphrase-multilingual-MiniLM-L12-v2"
                )
        return self._ef

    def _get_client(self):
        """懒加载 ChromaDB 客户端"""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            import os
            # 统一解析为 backend/ 目录下的 chroma_db，不受启动目录影响
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, settings.CHROMA_DB_PATH.lstrip("./\\"))
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

    def search_similar(self, query: str, n_results: int = None) -> List[Dict]:
        """
        检索与用户输入语义相似的心理咨询案例

        Args:
            query: 用户当前消息
            n_results: 返回结果数量，默认使用配置值

        Returns:
            List[Dict]: 相似案例列表，每项包含 input、output、distance
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

            similar_cases = []
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i]
                if distance > settings.RAG_DISTANCE_THRESHOLD:
                    continue
                metadata = results["metadatas"][0][i]
                similar_cases.append({
                    "input": doc,
                    "output": metadata.get("output", ""),
                    "distance": round(distance, 4)
                })

            if similar_cases:
                print(f"[RAG] 查询: 「{query[:30]}」 → 命中 {len(similar_cases)} 条")
                for idx, c in enumerate(similar_cases, 1):
                    print(f"  [{idx}] 距离={c['distance']}  {c['input'][:40]}...")
            else:
                print(f"[RAG] 查询: 「{query[:30]}」 → 无命中（距离均超过阈值 {settings.RAG_DISTANCE_THRESHOLD}）")

            return similar_cases

        except Exception as e:
            logger.warning(f"RAG 检索失败，跳过增强: {e}")
            return []

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
