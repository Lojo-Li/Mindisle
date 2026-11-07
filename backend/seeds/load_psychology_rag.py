"""
心理知识库数据入库脚本
将 Psychology-10K-ZH.json 数据处理后存入 ChromaDB 向量数据库

用法：
    cd backend
    python seeds/load_psychology_rag.py

可选参数：
    --reset     重建集合（删除旧数据后重新入库）
    --limit N   只入库前 N 条（用于测试）
"""
import json
import os
import sys
import argparse

# 将 backend/ 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "database", "Psychology-10K-ZH.json"
)
CHROMA_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chroma_db"
)
COLLECTION_NAME = "psychology_kb"
BATCH_SIZE = 500


def load_json_data(limit: int = None):
    """加载并清洗 JSON 数据，只保留 input 和 output"""
    print(f"[1/4] 加载数据文件: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"数据文件不存在: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items = []
    for entry in raw:
        inp = entry.get("input", "").strip()
        out = entry.get("output", "").strip()
        if inp and out:
            items.append({"input": inp, "output": out})

    if limit:
        items = items[:limit]

    print(f"       有效数据: {len(items)} 条 (原始: {len(raw)} 条)")
    return items


def main():
    parser = argparse.ArgumentParser(description="心理知识库数据入库")
    parser.add_argument("--reset", action="store_true", help="删除旧集合后重新入库")
    parser.add_argument("--limit", type=int, default=None, help="只入库前 N 条（测试用）")
    args = parser.parse_args()

    items = load_json_data(limit=args.limit)

    print("[2/4] 初始化 Sentence-Transformers 嵌入模型（使用本地模型）...")
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    ef = SentenceTransformerEmbeddingFunction(
        model_name=model_path
    )

    print(f"[3/4] 连接 ChromaDB: {CHROMA_DB_PATH}")
    import chromadb
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    if args.reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print("       已删除旧集合")
        except Exception:
            pass

    # 检查是否已有数据
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        existing_count = collection.count()
        if existing_count > 0 and not args.reset:
            print(f"       集合已存在，共 {existing_count} 条记录。")
            print("       如需重新入库请加 --reset 参数。")
            return
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )

    print(f"[4/4] 开始入库（批大小 {BATCH_SIZE}）...")
    total = len(items)
    for i in range(0, total, BATCH_SIZE):
        batch = items[i: i + BATCH_SIZE]

        # 以 input（患者提问）作为文档，output（咨询师回答）存入 metadata
        documents = [item["input"] for item in batch]
        metadatas = [{"output": item["output"]} for item in batch]
        ids = [f"psych_{i + j}" for j in range(len(batch))]

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        done = min(i + BATCH_SIZE, total)
        print(f"       进度: {done}/{total} ({done * 100 // total}%)")

    final_count = collection.count()
    print(f"\n✅ 入库完成！知识库共有 {final_count} 条记录。")
    print(f"   ChromaDB 路径: {CHROMA_DB_PATH}")


if __name__ == "__main__":
    main()
