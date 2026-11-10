"""验证心屿布局中「个人中心」与「消息通知」入口已禁用

覆盖：
1. 左下角用户区块不再是可点击按钮（无 jump 到 /profile）
2. 顶栏通知图标已移除
3. 点击用户区块后 URL 保持不变
4. 用户端与咨询师端都验证
"""
import json
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
API = "http://127.0.0.1:8000/api"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)

passed = failed = 0
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

ACCOUNTS = [
    {"name": "普通用户", "email": "user@test.com", "password": "123456", "path": "/workspace/home"},
    {"name": "咨询师", "email": "consultant@test.com", "password": "123456", "path": "/counselor/dashboard"},
]


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")


def login(email, password):
    body = json.dumps({"email": email, "password": password}).encode()
    for p in ("/auth/login", "/users/login"):
        try:
            req = urllib.request.Request(
                API + p, data=body, headers={"Content-Type": "application/json"})
            data = json.loads(_opener.open(req, timeout=10).read())
            payload = data.get("data") or data
            tok = payload.get("token") or payload.get("access_token")
            info = payload.get("userInfo") or payload.get("user") or {}
            if tok:
                return tok, info
        except Exception:
            continue
    return None, {}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True)

        for acc in ACCOUNTS:
            print(f"\n{'=' * 44}\n=== {acc['name']} ===")
            tok, info = login(acc["email"], acc["password"])
            if not tok:
                check(f"{acc['name']} 登录成功", False, "拿不到 token")
                continue
            check(f"{acc['name']} 登录成功", True)

            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script(
                f"sessionStorage.setItem('token', {json.dumps(tok)});"
                f"sessionStorage.setItem('userRole', {json.dumps(info.get('role') or 'user')});"
                f"sessionStorage.setItem('userInfo', {json.dumps(json.dumps(info, ensure_ascii=False))});")
            page = ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))

            page.goto(BASE + acc["path"], wait_until="networkidle")
            page.wait_for_timeout(1800)

            # 1. 用户区块应为 div 而非 button
            tag = page.evaluate(
                "() => { const e = document.querySelector('.sidebar-foot .user-card');"
                "return e ? e.tagName.toLowerCase() : null; }")
            print(f"  用户区块标签: {tag}")
            check("左下角用户区块不是按钮", tag == "div", f"实际 {tag}")

            # 2. 用户区块无点击跳转
            has_onclick = page.evaluate(
                "() => { const e = document.querySelector('.sidebar-foot .user-card');"
                "return e ? (!!e.getAttribute('onclick') || e.hasAttribute('data-go')) : true; }")
            check("用户区块无点击事件", has_onclick is False)

            # 3. 鼠标样式不是手型
            cur = page.evaluate(
                "() => { const e = document.querySelector('.sidebar-foot .user-card');"
                "return e ? getComputedStyle(e).cursor : 'none'; }")
            print(f"  用户区块 cursor: {cur}")
            check("用户区块鼠标非手型", cur == "default", f"实际 {cur}")

            # 4. 通知图标已移除
            notice = page.evaluate(
                "() => document.querySelectorAll('.top-actions .icon-btn').length")
            titles = page.evaluate(
                "() => Array.from(document.querySelectorAll('.top-actions .icon-btn'))"
                ".map(b => b.getAttribute('title'))")
            print(f"  顶栏按钮: {titles}")
            check("顶栏已无「通知」按钮", "通知" not in titles, str(titles))
            check("通知红点已移除",
                  page.evaluate("() => !document.querySelector('.top-actions .pip')"))

            # 5. 点击用户区块 URL 不变
            before = page.url
            page.evaluate(
                "() => { const e = document.querySelector('.sidebar-foot .user-card');"
                "if (e) e.click(); }")
            page.wait_for_timeout(900)
            after = page.url
            print(f"  点击前: {before}\n  点击后: {after}")
            check("点击用户区块不跳转", before == after, f"{before} -> {after}")
            check("未跳到 /profile", "/profile" not in after)

            # 6. 无 JS 报错
            check("页面无 JS 报错", not errs, str(errs[:2]))

            tag_name = "用户端" if "workspace" in acc["path"] else "咨询师端"
            page.screenshot(path=str(OUT / f"入口禁用_{tag_name}.png"))
            ctx.close()

        browser.close()

    print(f"\n{'=' * 44}")
    print(f"通过 {passed} / 失败 {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
