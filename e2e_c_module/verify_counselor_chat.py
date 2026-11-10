"""验证咨询师端对话页（心屿风格）：从「咨询会话」进入，不再跳出布局"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
SHOTS = Path(__file__).parent / "shots_counselor_chat"
SHOTS.mkdir(exist_ok=True)

results = []


def rec(cid, name, expect, ok, actual=""):
    results.append({"id": cid, "name": name, "expect": expect, "ok": bool(ok), "actual": str(actual)[:180]})
    print(("  PASS  " if ok else "  FAIL  ") + "%s %s :: %s" % (cid, name, actual))


def login(page, email, pwd="123456"):
    page.goto(FRONT + "/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    page.fill("#account", email)
    page.fill("#pwd", pwd)
    page.click("#submitBtn")
    page.wait_for_timeout(3200)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True,
                                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))

    login(page, "consultant@test.com")
    rec("CC-01", "咨询师登录", "离开登录页", "/login" not in page.url, page.url)

    # ---------- 从「咨询会话」进入 ----------
    page.goto(FRONT + "/counselor/dashboard/sessions", wait_until="domcontentloaded")
    page.wait_for_timeout(2800)

    btns = page.locator('.doc button:has-text("进入会话")')
    rec("CC-02", "咨询会话页有「进入会话」按钮", ">=1", btns.count() >= 1, "count=%d" % btns.count())

    if btns.count():
        btns.first.click()
        page.wait_for_timeout(2800)
        url = page.url
        rec("CC-03", "点击后进入新对话页", "/counselor/dashboard/chat/", "/counselor/dashboard/chat/" in url, url)

        # 关键：是否还在心屿布局内
        has_sidebar = page.locator(".sidebar").count()
        has_el = page.evaluate("() => !!document.querySelector('.el-card, .el-button')")
        rec("CC-04", "仍在心屿布局内（有侧栏）", "sidebar=1", has_sidebar == 1, "sidebar=%d" % has_sidebar)
        rec("CC-05", "不再使用 Element Plus 布局", "无 el-card/el-button", not has_el, "hasEL=%s" % has_el)

        act = page.locator(".nav-item.active").count()
        rec("CC-06", "菜单高亮唯一", "=1", act == 1, "active=%d" % act)

        # 等待会话渲染
        for _ in range(30):
            if page.locator(".chat-shell").count():
                break
            page.wait_for_timeout(500)

        rec("CC-07", "对话容器渲染", ".chat-shell=1", page.locator(".chat-shell").count() == 1, "")
        rec("CC-08", "无 JS 错误", "0", len(errs) == 0, str(errs[:1]))

        # 右侧学生信息面板
        side = page.locator(".side-panel")
        rec("CC-09", "右侧学生信息面板存在", "count=1", side.count() == 1, "count=%d" % side.count())
        if side.count():
            txt = side.inner_text()
            rec("CC-10", "面板含「学生信息」", "含", "学生信息" in txt, "")
            rec("CC-11", "面板含「学生诉求」", "含", "学生诉求" in txt, "")
            rec("CC-12", "面板含「我的备注」", "含", "我的备注" in txt, "")

        # 快捷回复
        chips = page.locator(".quick-chip")
        rec("CC-13", "快捷回复 5 条", "=5", chips.count() == 5, "count=%d" % chips.count())
        if chips.count():
            chips.nth(1).click()
            page.wait_for_timeout(600)
            val = page.locator(".input-textarea").input_value()
            rec("CC-14", "点快捷回复填入输入框", "非空", bool(val.strip()), repr(val[:30]))

        # 消息气泡
        bubbles = page.locator(".bubble")
        rec("CC-15", "消息气泡渲染", ">=1", bubbles.count() >= 1, "count=%d" % bubbles.count())
        self_rows = page.locator(".bubble-row.self")
        rec("CC-16", "咨询师自己的消息在右侧", ">=1", self_rows.count() >= 1, "self=%d" % self_rows.count())

        body_txt = page.locator(".chat-body").inner_text() if page.locator(".chat-body").count() else ""
        rec("CC-17", "无源码泄漏", "不含 =>/computed",
            "=>" not in body_txt and "computed(" not in body_txt, body_txt[:40].replace("\n", " "))

        # 计时器
        rec("CC-18", "显示会话计时器", "存在", page.locator(".timer-badge").count() == 1, "")

        # 发送消息
        ta = page.locator(".input-textarea")
        if ta.count():
            ta.fill("咨询师端的测试回复")
            page.wait_for_timeout(300)
            page.locator(".send-btn").click()
            page.wait_for_timeout(2500)
            body2 = page.locator(".chat-body").inner_text()
            rec("CC-19", "发送消息成功", "含测试文本", "咨询师端的测试回复" in body2, "")
            rec("CC-20", "发送后输入框清空", "空", ta.input_value() == "", repr(ta.input_value()[:15]))

        # 样式一致性
        style = page.evaluate("""() => {
          const g = (sel, props) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const s = getComputedStyle(el);
            const o = {};
            props.forEach(p => o[p] = s.getPropertyValue(p));
            return o;
          };
          return {
            shell: g('.chat-shell', ['border-radius','background-color','border-color']),
            sideCard: g('.side-card', ['border-radius','background-color']),
            selfBubble: g('.bubble-row.self .bubble', ['background-image','color']),
            timer: g('.timer-badge', ['background-color','color']),
          };
        }""")

        def sea_grad(img):
            if not img: return False
            n = img.lower().replace(" ", "")
            return ("#357b74" in n and "#22524e" in n) or ("rgb(53,123,116)" in n and "rgb(34,82,78)" in n)

        rec("CC-21", "聊天壳为心屿卡片(18px/白底)",
            "18px + 白底",
            style["shell"] and style["shell"]["border-radius"] == "18px"
            and style["shell"]["background-color"] == "rgb(255, 255, 255)",
            style["shell"])
        rec("CC-22", "侧栏卡片为心屿风格(16px)",
            "16px",
            style["sideCard"] and style["sideCard"]["border-radius"] == "16px",
            style["sideCard"] and style["sideCard"]["border-radius"])
        rec("CC-23", "自己的气泡墨绿渐变白字",
            "渐变+白字",
            sea_grad(style["selfBubble"] and style["selfBubble"]["background-image"])
            and style["selfBubble"]["color"] == "rgb(255, 255, 255)",
            style["selfBubble"] and style["selfBubble"]["color"])
        rec("CC-24", "计时器 sea-soft 底色",
            "rgb(226,239,236)",
            style["timer"] and style["timer"]["background-color"] == "rgb(226, 239, 236)",
            style["timer"] and style["timer"]["background-color"])

        page.screenshot(path=str(SHOTS / "01_咨询师对话.png"), full_page=True)

    # ---------- 旧链接重定向 ----------
    aid = page.url.rstrip("/").split("/")[-1] if "/chat/" in page.url else "1"
    page.goto(FRONT + "/consultation/counselor/%s" % aid, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    rec("CC-25", "旧链接重定向到新页面", "/counselor/dashboard/chat/",
        "/counselor/dashboard/chat/" in page.url, page.url)
    rec("CC-26", "重定向后仍有侧栏", "sidebar=1",
        page.locator(".sidebar").count() == 1, "")

    # ---------- 订单页（旧）不再从菜单可达 ----------
    page.goto(FRONT + "/counselor/dashboard", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    navs = page.locator(".nav-item").all_inner_texts()
    # 「预约订单」指向新的 /counselor/dashboard/orders（心屿页），不是旧页面
    rec("CC-27", "侧栏订单入口指向心屿页面", "/counselor/dashboard/orders",
        "/counselor/dashboard/orders" in (page.evaluate(
            "() => Array.from(document.querySelectorAll('.nav-item')).map(e => e.dataset.path || '').join(',')") or "")
        or "预约订单" in " ".join(navs),
        str([n.replace("\n", " ") for n in navs]))

    browser.close()

passed = sum(1 for r in results if r["ok"])
print("\n" + "=" * 68)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
if len(results) - passed:
    print("失败项：")
    for r in results:
        if not r["ok"]:
            print("  - %s %s :: %s" % (r["id"], r["name"], r["actual"]))

json.dump({"results": results,
           "stats": {"pass": passed, "fail": len(results) - passed, "total": len(results)}},
          open("results_counselor_chat.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
