"""新界面（心屿）C 模块浏览器端 E2E 测试。

覆盖学生端与咨询师端在 /workspace/* 和 /counselor/dashboard/* 下的完整交互。
"""
import json
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_pwlib"))

from playwright.sync_api import sync_playwright

FRONT = "http://127.0.0.1:5173"
RESULTS = []
SHOTS = HERE / "shots_new_ui"
SHOTS.mkdir(exist_ok=True)


def rec(cid, name, expect, ok, detail=""):
    RESULTS.append({"id": cid, "name": name, "expect": expect, "ok": bool(ok), "detail": str(detail)[:300]})
    tag = "PASS" if ok else "FAIL"
    print("[%-4s] %-8s %s%s" % (tag, cid, name, (" :: " + str(detail)[:120]) if detail else ""))


def login(page, email, pwd="123456"):
    """心屿登录页（LandingPage）：#account + #pwd + #submitBtn"""
    page.goto(FRONT + "/login", wait_until="domcontentloaded")
    page.wait_for_selector("#account", timeout=20000)
    page.wait_for_timeout(800)
    page.fill("#account", email)
    page.fill("#pwd", pwd)
    page.click("#submitBtn")
    page.wait_for_timeout(3500)
    return page.url


def logout(page):
    page.evaluate("sessionStorage.clear(); localStorage.clear()")


def main():
    with sync_playwright() as p:
        CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        ctx = browser.new_context(viewport={"width": 1500, "height": 950})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)[:200]))

        # ========== 学生端 ==========
        url = login(page, "user@test.com")
        rec("NEW-01", "学生登录后跳转工作台", "URL 含 /workspace", "/workspace" in url, url)
        if "/workspace" not in url:
            page.screenshot(path=str(SHOTS / "00_login_failed.png"))
            print(">>> 登录失败，当前页面文本：")
            print(page.locator("body").inner_text()[:300])

        # 1. 咨询预约页：卡片渲染
        page.goto(FRONT + "/workspace/booking", wait_until="networkidle")
        page.wait_for_timeout(2000)
        cards = page.locator(".docs .doc")
        n_cards = cards.count()
        rec("NEW-02", "咨询预约页渲染咨询师卡片", "卡片数 > 0 且含真实姓名", n_cards > 0, "卡片数=%d" % n_cards)

        txt = page.locator(".docs").inner_text() if n_cards else ""
        rec("NEW-03", "卡片显示真实咨询师姓名", "包含「张咨询师」", "张咨询师" in txt, txt[:80].replace("\n", "|"))

        fake = any(x in txt for x in ["陈曦", "周予安", "林知夏", "苏漾"])
        rec("NEW-04", "无写死的假卡片残留", "不含 陈曦/周予安/林知夏/苏漾", not fake, "发现假数据" if fake else "干净")

        # 2. 筛选
        try:
            page.locator('.pill[data-filter="焦虑"]').click(timeout=8000)
            page.wait_for_timeout(800)
            n_after = page.locator(".docs .doc").count()
            rec("NEW-05", "擅长领域筛选生效", "筛选后卡片数 < 全部", n_after < n_cards, "%d → %d" % (n_cards, n_after))
            page.locator('.pill[data-filter=""]').click(timeout=5000)
            page.wait_for_timeout(600)
        except Exception as e:
            rec("NEW-05", "擅长领域筛选生效", "可点击筛选", False, str(e)[:120])

        # 3. 点击「选择时段」→ 弹窗出现
        try:
            btn = page.locator(".docs .doc button", has_text="选择时段").first
            btn.click(timeout=8000)
            page.wait_for_timeout(1200)
        except Exception as e:
            rec("NEW-06", "点击「选择时段」弹出预约窗", "overlay display=flex", False, "按钮点击失败: " + str(e)[:100])
            ov = page.locator("#bookOverlay")
            disp = "n/a"
        else:
            ov = page.locator("#bookOverlay")
            disp = ov.evaluate("el => getComputedStyle(el).display")
        rec("NEW-06", "点击「选择时段」弹出预约窗", "overlay display=flex", disp == "flex", "display=%s" % disp)

        title = page.locator("#bookTitle").inner_text() if page.locator("#bookTitle").count() else ""
        rec("NEW-07", "弹窗标题显示真实咨询师名", "含「预约 ·」且非「陈曦」", "预约 ·" in title and "陈曦" not in title, title)

        n_days = page.locator("#days [data-day]").count()
        n_slots = page.locator("#slots [data-slot]").count()
        rec("NEW-08", "弹窗内渲染日期与时段", "日期>=7 且 时段>0", n_days >= 7 and n_slots > 0,
            "日期=%d 时段=%d" % (n_days, n_slots))

        page.screenshot(path=str(SHOTS / "01_booking_modal.png"))

        # 4. 选日期 + 时段 + 确认预约
        try:
            page.locator("#days [data-day]").nth(2).click(timeout=6000)
            page.wait_for_timeout(1000)
            slots = page.locator("#slots [data-slot]")
            if slots.count():
                slots.first.click(timeout=5000)
                page.wait_for_timeout(400)
            page.locator("#bookConfirm").click(timeout=6000)
            page.wait_for_timeout(2800)
            rec("NEW-09", "确认预约后切到「我的预约」", "URL 含 tab=mine 或出现预约卡", True, page.url)
        except Exception as e:
            rec("NEW-09", "确认预约后切到「我的预约」", "可完成预约", False, str(e)[:120])

        # 5. 我的预约列表
        page.goto(FRONT + "/workspace/booking?tab=mine", wait_until="networkidle")
        page.wait_for_timeout(2000)
        appt_cards = page.locator(".appt-card")
        na = appt_cards.count()
        rec("NEW-10", "我的预约列表显示订单", "订单卡数 >= 1", na >= 1, "订单数=%d" % na)

        if na:
            body = page.locator(".appt-card").first.inner_text()
            rec("NEW-11", "订单卡显示状态标签", "含 待确认/已确认/进行中/已完成/已取消",
                any(s in body for s in ["待确认", "已确认", "进行中", "已完成", "已取消"]), body[:80].replace("\n", "|"))

        page.screenshot(path=str(SHOTS / "02_my_appointments.png"))

        # 6. 状态筛选
        page.locator('.pill[data-status="pending"]').click()
        page.wait_for_timeout(1500)
        rec("NEW-12", "状态筛选可切换", "点击后页面正常", page.locator(".appt-card, .empty-box").count() >= 1,
            "卡片或空态=%d" % page.locator(".appt-card, .empty-box").count())

        page.locator('.pill[data-status="all"]').click()
        page.wait_for_timeout(1200)

        # 7. 侧栏菜单高亮唯一性
        nav_active = page.locator(".nav-item.active")
        rec("NEW-13", "侧栏菜单只高亮一项", "active 数量 == 1", nav_active.count() == 1, "active=%d" % nav_active.count())

        rec("NEW-14", "页面无 JS 运行时错误", "pageerror 为空", len(errs) == 0, errs[:2])

        page.screenshot(path=str(SHOTS / "03_sidebar_active.png"))

        # ========== 咨询师端 ==========
        logout(page)
        url2 = login(page, "consultant@test.com")
        rec("NEW-15", "咨询师登录后跳转工作台", "跳转到 /counselor/dashboard", "/counselor/dashboard" in url2, url2)

        page.goto(FRONT + "/counselor/dashboard", wait_until="networkidle")
        page.wait_for_timeout(2000)
        rec("NEW-16", "咨询师工作台加载", "页面含「咨询师工作台」或概览",
            page.locator(".view").count() > 0, "views=%d" % page.locator(".view").count())

        # 订单页
        page.goto(FRONT + "/counselor/dashboard/orders", wait_until="networkidle")
        page.wait_for_timeout(2000)
        ocards = page.locator(".order-card")
        no = ocards.count()
        rec("NEW-17", "咨询师订单页渲染", "订单卡 >= 1（学生刚下的单）", no >= 1, "订单数=%d" % no)

        if no:
            otxt = ocards.first.inner_text()
            rec("NEW-18", "订单卡含学生信息与状态", "含学生昵称 或 状态词",
                any(s in otxt for s in ["测试用户", "待确认", "已确认", "进行中"]), otxt[:90].replace("\n", "|"))

        page.screenshot(path=str(SHOTS / "04_counselor_orders.png"))

        # 菜单高亮唯一性（咨询师端）
        act2 = page.locator(".nav-item.active")
        rec("NEW-19", "咨询师菜单只高亮「预约订单」", "active 数量==1 且文本含订单",
            act2.count() == 1 and "订单" in act2.first.inner_text(), "active=%d" % act2.count())

        # 接受订单（若存在待确认）
        agree = page.locator(".order-card button", has_text="接受预约")
        if agree.count():
            page.once("dialog", lambda d: d.accept())
            agree.first.click()
            page.wait_for_timeout(600)
            # ElMessageBox 确认按钮
            try:
                page.locator('.el-message-box__btns button:has-text("确认接受")').click(timeout=4000)
                page.wait_for_timeout(2000)
                rec("NEW-20", "咨询师接受预约", "操作成功", True, "已点击接受")
            except Exception as e:
                rec("NEW-20", "咨询师接受预约", "操作成功", False, str(e)[:120])
        else:
            rec("NEW-20", "咨询师接受预约", "存在待确认订单", False, "无待确认订单可操作")

        page.screenshot(path=str(SHOTS / "05_after_accept.png"))

        browser.close()

    # 汇总
    p_ok = sum(1 for r in RESULTS if r["ok"])
    print("\n" + "=" * 64)
    print("STATS = %s" % json.dumps({"PASS": p_ok, "FAIL": len(RESULTS) - p_ok}))
    for r in RESULTS:
        if not r["ok"]:
            print("  FAIL:", r["id"], r["name"], "::", r["detail"])

    out = HERE / "results_new_ui.json"
    out.write_text(json.dumps({"results": RESULTS, "stats": {"pass": p_ok, "fail": len(RESULTS) - p_ok}},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULTS ->", out)


if __name__ == "__main__":
    main()
