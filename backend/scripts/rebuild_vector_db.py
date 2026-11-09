"""
重建心理知识库向量索引（本地开发用，可重复执行）

为什么需要这个脚本：
1. 仓库自带的 chroma_db 是在别的机器上生成的，换环境后跨进程打开会报
   "Cannot open header file"。
2. **Windows 上路径含中文时，hnswlib 无法打开索引文件**。项目目录名是
   「腾讯实训营」，因此向量库必须放在纯英文路径下，否则只能在写入它的
   同一个进程里查询，服务重启后就失效。
3. 默认的 l2 距离在未归一化向量上数值很大，和 rag_service 里的阈值不匹配，
   统一改成 cosine，距离直接等于 1-相似度，阈值含义清晰。

用法：
    cd backend
    .venv/Scripts/python.exe scripts/rebuild_vector_db.py --out C:/mindisle_chroma
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "database", "Psychology-10K-ZH.json"
)
DEFAULT_MODEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"
)


def check_ascii(path: str) -> None:
    """hnswlib 在 Windows 上打不开非 ASCII 路径，提前拦下来给出可读提示。"""
    if os.name != "nt":
        return
    try:
        path.encode("ascii")
    except UnicodeEncodeError:
        raise SystemExit(
            "向量库路径包含非 ASCII 字符（例如中文），Windows 上 hnswlib 会无法打开索引。\n"
            f"  当前路径: {path}\n"
            "  请换到纯英文路径，例如 --out C:/mindisle_chroma"
        )


def main():
    ap = argparse.ArgumentParser(description="重建心理知识库向量索引")
    ap.add_argument("--data", default=DEFAULT_DATA, help="语料 JSON 路径")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="本地嵌入模型目录")
    ap.add_argument("--out", default="C:/mindisle_chroma", help="向量库输出目录（建议纯英文路径）")
    ap.add_argument("--collection", default="psychology_kb")
    ap.add_argument("--batch", type=int, default=300)
    ap.add_argument("--limit", type=int, default=None, help="只入库前 N 条（调试用）")
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    check_ascii(out)

    if not os.path.isdir(args.model):
        raise SystemExit(f"找不到本地嵌入模型目录: {args.model}\n请先下载模型后重试。")

    print(f"[1/4] 读取语料: {args.data}")
    with open(args.data, "r", encoding="utf-8") as f:
        raw = json.load(f)
    items = [
        {"input": e["input"].strip(), "output": e["output"].strip()}
        for e in raw
        if e.get("input", "").strip() and e.get("output", "").strip()
    ]
    if args.limit:
        items = items[: args.limit]
    print(f"       有效条目: {len(items)}")

    print(f"[2/4] 加载嵌入模型: {args.model}")
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    ef = SentenceTransformerEmbeddingFunction(model_name=os.path.abspath(args.model))

    print(f"[3/4] 重建集合（cosine 度量）: {out}")
    client = chromadb.PersistentClient(path=out)
    try:
        client.delete_collection(args.collection)
        print("       已删除旧集合")
    except Exception:
        pass

    col = client.get_or_create_collection(
        name=args.collection,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    print(f"[4/4] 写入（批大小 {args.batch}）")
    started = time.time()
    for i in range(0, len(items), args.batch):
        batch = items[i: i + args.batch]
        col.add(
            documents=[x["input"] for x in batch],
            metadatas=[{"output": x["output"]} for x in batch],
            ids=[f"psych_{i + j}" for j in range(len(batch))],
        )
        done = min(i + args.batch, len(items))
        print(f"       {done}/{len(items)}")

    print(f"\n完成，共 {col.count()} 条，耗时 {time.time() - started:.0f}s")

    probe = col.query(query_texts=["我很焦虑，睡不着"], n_results=3)
    print("\n自检查询「我很焦虑，睡不着」：")
    for doc, dist in zip(probe["documents"][0], probe["distances"][0]):
        print(f"  相似度 {1 - dist:.3f}  {doc[:28]}")
    print("\n提示：cosine 距离 = 1 - 相似度，rag_service 的阈值按相似度下限配置。")


if __name__ == "__main__":
    main()
