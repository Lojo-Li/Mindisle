"""浏览器端全页面巡检：检查各页面渲染、JS 错误、控制台报错"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
results = []


def case(cid, name, ok, detail=""):
    results.append({"id": cid, "name": name, "ok": bool(ok), "detail": str(detail)[:160]})
    print(("  PASS  " if ok else "  FAIL  ") + "%s %s :: %s" % (cid, name, detail))


def login(page, email, pwd="123456"):
    page.goto(FRONT + "/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    page.fill("#account", email)
    page.fill("#pwd", pwd)
    page.click("#submitBtn")
    page.wait_for_timeout(3200)


PAGES_USER = [
    ("/workspace/home", "概览"),
    ("/workspace/assess", "心理测评"),
    ("/workspace/lamp", "屿灯"),
    ("/workspace/booking", "咨询预约"),
    ("/workspace/appointments", "我的预约"),
    ("/workspace/records", "我的记录"),
]

PAGES_COUNSELOR = [
    ("/counselor/dashboard", "咨询师概览"),
    ("/counselor/dashboard/schedule", "时段管理"),
    ("/counselor/dashboard/sessions", "咨询会话"),
    ("/counselor/dashboard/profile", "个人中心"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True,
                                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")

    # ---------- 学生端 ----------
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    errs, console_errs = [], []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: console_errs.append(m.text) if m.type == "error" else None)

    login(page, "user@test.com")
    case("UI-01", "学生登录", "/login" not in page.url, page.url)

    print("\n--- 学生端页面巡检 ---")
    for path, label in PAGES_USER:
        errs.clear(); console_errs.clear()
        page.goto(FRONT + path, wait_until="domcontentloaded")
        page.wait_for_timeout(2800)
        body = page.locator("body").inner_text()
        has_content = len(body.strip()) > 60
        no_el_left = "el-" not in ""  # 占位
        case("UI" + str(len(results) + 1), "%s %s 渲染" % (path, label),
             has_content and len(errs) == 0,
             "内容%s 错误%d" % ("有" if has_content else "无", len(errs)))
        if errs:
            print("        错误:", errs[:2])

    # 关键交互：我的预约筛选
    page.goto(FRONT + "/workspace/appointments", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    pills = page.locator(".filter-row .pill")
    case("UI-A1", "我的预约状态筛选存在", pills.count() >= 5, "count=%d" % pills.count())

    # 对话页
    aid = page.evaluate("""async () => {
      const t = sessionStorage.getItem('token') || localStorage.getItem('token') || '';
      const r = await fetch('/api/appointment/user/list?page=1&page_size=100', {headers: t ? {Authorization:'Bearer '+t} : {}});
      const d = await r.json();
      const items = (d && d.data && d.data.items) || [];
      const ok = items.filter(x => x.status === 'in_progress' || x.status === 'confirmed');
      return (ok[0] || {}).id || null;
    }""")
    case("UI-A2", "存在可进入的进行中预约", bool(aid), "id=%s" % aid)
    if aid:
        errs.clear()
        page.goto(FRONT + "/workspace/chat/%s" % aid, wait_until="domcontentloaded")
        for _ in range(20):
            if page.locator(".chat-shell").count():
                break
            page.wait_for_timeout(500)
        case("UI-A3", "对话页渲染", page.locator(".chat-shell").count() == 1, "shell=%d" % page.locator(".chat-shell").count())
        case("UI-A4", "对话页无 JS 错误", len(errs) == 0, str(errs[:1]))
        case("UI-A5", "对话页在布局内(有侧栏)", page.locator(".sidebar").count() == 1, "")
        act = page.locator(".nav-item.active").count()
        case("UI-A6", "对话页菜单高亮唯一", act == 1, "active=%d" % act)

    # ---------- 咨询师端 ----------
    ctx2 = browser.new_context(viewport={"width": 1440, "height": 900})
    p2 = ctx2.new_page()
    errs2 = []
    p2.on("pageerror", lambda e: errs2.append(str(e)))
    login(p2, "consultant@test.com")
    case("UI-C0", "咨询师登录", "/login" not in p2.url, p2.url)

    print("\n--- 咨询师端页面巡检 ---")
    for path, label in PAGES_COUNSELOR:
        errs2.clear()
        p2.goto(FRONT + path, wait_until="domcontentloaded")
        p2.wait_for_timeout(2800)
        body = p2.locator("body").inner_text()
        case("UI-C" + str(PAGES_COUNSELOR.index((path, label)) + 1),
             "%s %s" % (path, label),
             len(body.strip()) > 60 and len(errs2) == 0,
             "错误%d" % len(errs2))

    # 咨询师端旧页面检查（是否还是 Element Plus）
    print("\n--- 咨询师端旧页面（待适配）---")
    for path in ["/consultation/counselor/orders", "/consultation/counselor/%s" % (aid or 1)]:
        errs2.clear()
        p2.goto(FRONT + path, wait_until="domcontentloaded")
        p2.wait_for_timeout(2500)
        has_el = p2.evaluate("() => !!document.querySelector('.el-button, .el-card, .el-avatar')")
        has_sidebar = p2.evaluate("() => !!document.querySelector('.sidebar')")
        case("UI-OLD" + str(len(results)),
             "%s 是否已适配心屿" % path,
             has_sidebar,
             "ElementPlus=%s 侧栏=%s" % (has_el, has_sidebar))

    browser.close()

passed = sum(1 for r in results if r["ok"])
print("\n" + "=" * 70)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
if len(results) - passed:
    print("失败项：")
    for r in results:
        if not r["ok"]:
            print("  - %s %s :: %s" % (r["id"], r["name"], r["detail"]))

json.dump({"results": results,
           "stats": {"pass": passed, "fail": len(results) - passed, "total": len(results)}},
          open("results_ui_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
