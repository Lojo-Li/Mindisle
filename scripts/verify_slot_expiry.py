"""验证预约时段过期置灰：真实浏览器点击 + 截图

覆盖：
1. 今天（已过营业时间）所有时段不可点、带删除线
2. 明天所有时段可选且可点
3. 点击过期时段不产生选中态
"""
import json
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
API = "http://127.0.0.1:8000/api"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)

passed = failed = 0

# 本机请求绕过系统代理，避免 7890 代理拦截 127.0.0.1
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def api_get(path):
    return json.loads(_opener.open(API + path, timeout=10).read())


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")


def login_token():
    """用普通用户账号登录，返回 (token, userInfo)

    后端登录响应结构：{"code":200,"data":{"token":..., "userInfo":{...}, "redirect":...}}
    """
    body = json.dumps({"email": "user@test.com", "password": "123456"}).encode()
    for path in ("/auth/login", "/users/login", "/login"):
        try:
            req = urllib.request.Request(
                API + path, data=body,
                headers={"Content-Type": "application/json"})
            data = json.loads(_opener.open(req, timeout=10).read())
            payload = data.get("data") or data
            tok = (payload.get("token") or payload.get("access_token")
                   or data.get("token"))
            info = payload.get("userInfo") or payload.get("user") or {}
            if tok:
                return tok, info
        except Exception as e:
            last_err.append(f"{path}: {e}")
            continue
    return None, {}


last_err = []


def main():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"今天={today}  明天={tomorrow}\n")

    print("=== 1. 后端接口字段 ===")
    slots_today = api_get(f"/counselor/1/slots?date={today}")["data"]
    slots_tmr = api_get(f"/counselor/1/slots?date={tomorrow}")["data"]

    check("今天时段全部 available=false",
          all(not s["available"] for s in slots_today),
          str([s["available"] for s in slots_today]))
    check("今天时段全部标记 expired=true",
          all(s.get("expired") for s in slots_today))
    check("今天时段 reason=past",
          all(s.get("reason") == "past" for s in slots_today))
    check("明天时段全部 available=true",
          all(s["available"] for s in slots_tmr))
    check("明天时段 expired 全为 false",
          all(not s.get("expired") for s in slots_tmr))
    check("price 返回 0.0 而非 null（公益免费）",
          all(s.get("price") == 0.0 for s in slots_tmr),
          str([s.get("price") for s in slots_tmr][:3]))

    token, user = login_token()
    print(f"\n登录 token: {'已获取' if token else '未获取（将直接打开页面）'}")
    if not token and last_err:
        print(f"  登录尝试: {last_err}")
    if user:
        print(f"用户: {user.get('username') or user.get('nickname') or user.get('email')}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        if token:
            role = (user or {}).get("role") or "user"
            ctx.add_init_script(
                f"sessionStorage.setItem('token', {json.dumps(token)});"
                f"sessionStorage.setItem('userRole', {json.dumps(role)});"
                f"sessionStorage.setItem('userInfo', {json.dumps(json.dumps(user, ensure_ascii=False))});")
        page = ctx.new_page()

        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))

        print("\n=== 2. 打开预约页 ===")
        page.goto(f"{BASE}/workspace/booking", wait_until="networkidle")
        page.wait_for_timeout(1200)
        check("页面无 JS 报错", not errs, str(errs[:2]))

        # 打开第一个咨询师的预约弹层
        # 列表卡片：已过营业时间时全部应为「不可预约」+ 按钮禁用
        book_btns = page.query_selector_all("[data-book]")
        check("存在「选择时段」按钮", len(book_btns) > 0, f"找到 {len(book_btns)} 个")
        if not book_btns:
            browser.close()
            return
        # 列表层与弹层是两套口径：
        # - 列表看"未来 7 天能不能约到"（可约明天 → 显示可预约，按钮可点）
        # - 弹层看"这个具体时段能不能约"（今天已过的要置灰）
        all_enabled = not any(b.is_disabled() for b in book_btns)
        list_txt = page.inner_text('[data-list="docs"]')
        check("列表层：当前可约「可预约」且按钮可点",
              all_enabled and "可预约" in list_txt.replace("不可预约", ""),
              f"all_enabled={all_enabled}")

        # 直接点第一个「选择时段」按钮打开弹层
        page.evaluate("() => { const b = document.querySelector('[data-book]'); if (b) b.click(); }")
        page.wait_for_selector("#bookOverlay.open", timeout=8000)
        page.wait_for_timeout(1500)
        days_txt = page.inner_text("#days").replace("\n", " ")

        # --- 今天 ---
        slots = page.query_selector_all("#slots .slot")
        print(f"\n  今天时段数: {len(slots)}")
        check("今天时段已渲染", len(slots) == 10, f"实际 {len(slots)}")

        disabled_cnt = sum(1 for s in slots if s.is_disabled())
        check("今天时段全部 disabled", disabled_cnt == len(slots),
              f"disabled={disabled_cnt}/{len(slots)}")

        strike = page.evaluate("""() => {
            const s = document.querySelector('#slots .slot');
            if (!s) return null;
            const cs = getComputedStyle(s);
            return { decoration: cs.textDecorationLine, opacity: cs.opacity, cursor: cs.cursor };
        }""")
        print(f"  首时段样式: {strike}")
        check("过期时段有删除线",
              strike and "line-through" in (strike.get("decoration") or ""))
        check("过期时段透明度降低",
              strike and float(strike.get("opacity") or 1) < 0.6)
        check("过期时段鼠标为 not-allowed",
              strike and strike.get("cursor") == "not-allowed")

        # 点击过期时段不应选中
        page.evaluate("() => document.querySelector('#slots .slot').click()")
        page.wait_for_timeout(400)
        on_cnt = len(page.query_selector_all("#slots .slot.on"))
        check("点击过期时段不会被选中", on_cnt == 0, f"on={on_cnt}")

        # 有"已无可约时段"提示
        slots_text = page.inner_text("#slots")
        check("提示该日已无可约时段", "已没有可约时段" in slots_text, slots_text[:60])

        page.screenshot(path=str(OUT / "预约_今天全部过期.png"), full_page=False)

        # --- 明天 ---
        print("\n=== 3. 切到明天 ===")
        page.evaluate("() => document.querySelector('[data-day=\"1\"]').click()")
        page.wait_for_timeout(1500)
        slots2 = page.query_selector_all("#slots .slot")
        dis2 = sum(1 for s in slots2 if s.is_disabled())
        check("明天时段全部可选", dis2 == 0 and len(slots2) == 10,
              f"disabled={dis2}/{len(slots2)}")

        # 点一个明天时段应能选中
        page.evaluate("() => document.querySelector('#slots .slot').click()")
        page.wait_for_timeout(400)
        on2 = len(page.query_selector_all("#slots .slot.on"))
        check("明天时段可正常选中", on2 == 1, f"on={on2}")

        page.screenshot(path=str(OUT / "预约_明天可选.png"), full_page=False)

        print(f"\n页面错误: {errs if errs else '无'}")
        browser.close()

    print(f"\n{'=' * 46}")
    print(f"通过 {passed} / 失败 {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
