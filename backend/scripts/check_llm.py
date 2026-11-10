"""
大模型连通性自检（几乎不消耗额度）

用法：
    .venv/Scripts/python.exe scripts/check_llm.py            # 发一次最小请求（输出上限 16 token）
    .venv/Scripts/python.exe scripts/check_llm.py --list     # 只列模型，零 token

设计原则：
1. 只发一次请求，max_tokens=16，不复述长 prompt
2. 密钥只打印长度与首尾，不打印全文
3. 失败时给出可执行的判断（是密钥问题、模型问题还是余额问题）
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx  # noqa: E402
from openai import OpenAI  # noqa: E402

from app.core.config import settings  # noqa: E402


def mask(key: str) -> str:
    if not key:
        return "（未配置）"
    if len(key) <= 12:
        return "*" * len(key)
    return f"{key[:6]}…{key[-4:]}（长度 {len(key)}）"


def explain(err: Exception) -> str:
    text = str(err)
    low = text.lower()
    status = getattr(err, "status_code", None)

    if status == 401 or "authentication" in low or "invalid api key" in low or "invalid_api_key" in low:
        return "密钥无效或已失效（401）——检查 LLM_API_KEY 是否复制完整、是否带了多余空格"
    if status == 402 or "insufficient" in low or "balance" in low:
        return "账户余额不足（402）——去服务商控制台充值"
    if status == 404 or "model" in low and ("not found" in low or "not exist" in low or "not open" in low):
        return "模型不存在或未开通（404）——检查 LLM_MODEL 是否拼写正确、该模型是否已开通"
    if status == 429:
        return "触发限流或额度上限（429）——稍后再试"
    if status == 400:
        return "请求参数被拒绝（400）——多半是模型名不被该地址支持"
    if "timeout" in low or "timed out" in low:
        return "请求超时——网络到服务商不通，或需要代理"
    if "connect" in low or "getaddrinfo" in low or "nodename" in low:
        return "域名解析或连接失败——检查 LLM_BASE_URL 是否写错、网络是否可达"
    return f"未归类错误：{text[:200]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="只列模型，不消耗 token")
    args = parser.parse_args()

    base = settings.LLM_ACTIVE_BASE_URL
    model = settings.LLM_ACTIVE_MODEL
    key = settings.LLM_ACTIVE_API_KEY

    print("=" * 56)
    print("  当前模型配置")
    print("=" * 56)
    print(f"  BASE_URL : {base}")
    print(f"  MODEL    : {model}")
    print(f"  API_KEY  : {mask(key)}")
    print()

    if not key:
        print("✗ 没有配置密钥。请在 backend/.env 里加一行：")
        print("  LLM_API_KEY=你的密钥")
        return 2

    # 必须显式传 http_client：当前 openai 与 httpx 版本组合下，
    # 不传会走默认构造并因 proxies 参数报 TypeError（后端服务同理）
    http_client = httpx.Client(
        timeout=30.0,
        verify=settings.AI_VERIFY_SSL,
    )
    client = OpenAI(
        base_url=base,
        api_key=key,
        http_client=http_client,
        max_retries=0,
    )

    if args.list:
        try:
            models = client.models.list()
            names = sorted(m.id for m in models.data)
            print(f"✓ 密钥可用，可见 {len(names)} 个模型：")
            for n in names:
                mark = "  ← 当前配置" if n == model else ""
                print(f"    {n}{mark}")
            if model not in names:
                print(f"\n! 当前配置的 {model} 不在列表里，可能不可用")
            return 0
        except Exception as e:  # noqa: BLE001
            print(f"✗ 列模型失败：{explain(e)}")
            print(f"  原始信息：{str(e)[:300]}")
            return 1

    print("发送一次最小请求（max_tokens=16，用于验证链路）…")
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "回复两个字：收到"}],
            max_tokens=16,
            temperature=0,
        )
    except Exception as e:  # noqa: BLE001
        print(f"\n✗ 调用失败：{explain(e)}")
        print(f"  原始信息：{str(e)[:300]}")
        return 1

    cost = time.time() - t0
    content = (resp.choices[0].message.content or "").strip()
    usage = resp.usage
    print(f"\n✓ 调用成功  耗时 {cost:.2f}s")
    print(f"  回复内容：{content[:60]}")
    print(f"  实际模型：{resp.model}")
    if usage:
        print(f"  本次消耗：输入 {usage.prompt_tokens} / 输出 {usage.completion_tokens} token")
    return 0


if __name__ == "__main__":
    sys.exit(main())
