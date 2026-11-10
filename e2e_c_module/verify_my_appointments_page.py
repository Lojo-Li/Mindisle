"""验证「我的预约」页面的真实渲染效果（截图 + DOM 断言）"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
SHOTS = Path(__file__).parent / "shots_my_appt"
SHOTS.mkdir(exist_ok=True)

results = []


def rec(tid, name, expect, ok, actual=""):
    results.append({"id": tid, "name": name, "expect": expect, "ok": ok, "actual": str(actual)[:200]})
    print(("  PASS  " if ok else "  FAIL  ") + "%s %s :: %s" % (tid, name, actual))


def login(page, email, pwd="123456"):
    page.goto(FRONT + "/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    page.fill("#account", email)
    page.fill("#pwd", pwd)
    page.click("#submitBtn")
    page.wait_for_timeout(3000)


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # ---------- 学生端 ----------
    login(page, "user@test.com")
    rec("MA-01", "学生登录成功", "离开登录页", "/login" not in page.url, page.url)

    page.goto(FRONT + "/workspace/appointments", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    # 侧栏「我的」分组里有「我的预约」
    nav = page.locator(".nav-item", has_text="我的预约")
    rec("MA-02", "侧栏「我的」分组含我的预约菜单", "菜单存在", nav.count() > 0, "count=%d" % nav.count())
    rec("MA-03", "当前菜单高亮", "active 且唯一",
        page.locator(".nav-item.active").count() == 1,
        "active=%d" % page.locator(".nav-item.active").count())

    # 页头
    h1 = page.locator("h1").first.inner_text()
    rec("MA-04", "页头标题为「我的预约」", "我的预约", h1.strip() == "我的预约", h1.strip())

    # 筛选胶囊
    pills = page.locator(".filter-row .pill")
    rec("MA-05", "状态筛选 6 个胶囊", "6", pills.count() == 6, "count=%d" % pills.count())

    # 预约卡片
    cards = page.locator(".appt-card")
    rec("MA-06", "预约卡片渲染", ">=3", cards.count() >= 3, "count=%d" % cards.count())

    # 检查卡片内容
    if cards.count():
        first = cards.first
        txt = first.inner_text()
        rec("MA-07", "卡片显示咨询师姓名", "张咨询师", "张咨询师" in txt, txt[:60].replace("\n", " | "))
        rec("MA-08", "卡片显示公益免费", "公益免费", "公益免费" in txt, "")
        rec("MA-09", "卡片显示订单号", "APT", "APT" in txt, "")

    # 状态标签
    tags_txt = page.locator(".appt-card .tag").all_inner_texts()
    has_pending = any("待确认" in t for t in tags_txt)
    has_confirmed = any("已确认" in t for t in tags_txt)
    has_cancelled = any("已取消" in t for t in tags_txt)
    rec("MA-10", "状态标签覆盖多状态", "待确认/已确认/已取消 都有",
        has_pending and has_confirmed and has_cancelled,
        "pending=%s confirmed=%s cancelled=%s" % (has_pending, has_confirmed, has_cancelled))

    # 取消原因显示
    body_txt = page.locator("section").first.inner_text()
    rec("MA-11", "已取消卡片显示取消原因", "取消原因", "取消原因" in body_txt, "")

    # 操作按钮
    btns = page.locator(".appt-actions button").all_inner_texts()
    rec("MA-12", "操作按钮（取消预约/进入咨询）", "含取消预约或进入咨询",
        any("取消预约" in b for b in btns) or any("进入咨询" in b for b in btns),
        str(btns))

    page.screenshot(path=str(SHOTS / "01_全部.png"), full_page=True)
    n_all = page.locator(".appt-card").count()

    # 状态筛选：已取消应只显示 cancelled 的卡片，且少于全部
    page.locator(".filter-row .pill", has_text="已取消").click()
    page.wait_for_timeout(900)
    n_cancel = page.locator(".appt-card").count()
    # 卡片上应全部是「已取消」标签
    cancel_tags = page.locator(".appt-card .tag").all_inner_texts()
    only_cancelled = all("已取消" in t or "公益免费" in t or "视频咨询" in t or "语音咨询" in t or "线下咨询" in t
                         for t in cancel_tags)
    rec("MA-13", "筛选「已取消」只显示已取消卡片", "卡片数 < 全部 且 全是已取消",
        n_cancel < n_all and only_cancelled and n_cancel >= 1,
        "全部 %d → 已取消 %d" % (n_all, n_cancel))
    page.screenshot(path=str(SHOTS / "02_已取消.png"), full_page=True)

    page.locator(".filter-row .pill", has_text="全部").click()
    page.wait_for_timeout(700)

    # 取消操作：找到待确认的卡片
    page.locator(".filter-row .pill", has_text="待确认").click()
    page.wait_for_timeout(800)
    cancel_btns = page.locator('.appt-actions button:has-text("取消预约")')
    if cancel_btns.count():
        cancel_btns.first.click()
        page.wait_for_timeout(900)
        dlg = page.locator(".el-message-box")
        rec("MA-14", "点击取消弹出确认框", "弹窗出现", dlg.count() > 0, "count=%d" % dlg.count())
        page.screenshot(path=str(SHOTS / "03_取消确认框.png"), full_page=True)
        # 点「再想想」关闭
        if dlg.count():
            page.locator('.el-message-box button:has-text("再想想")').first.click()
            page.wait_for_timeout(600)
        rec("MA-15", "取消确认框可关闭", "弹窗消失", page.locator(".el-message-box").count() == 0, "")
    else:
        rec("MA-14", "点击取消弹出确认框", "有待确认卡片", False, "无可取消卡片")
        rec("MA-15", "取消确认框可关闭", "-", False, "跳过")

    # 跳转 booking
    page.locator('.page-head button:has-text("预约咨询")').first.click()
    page.wait_for_timeout(1800)
    rec("MA-16", "「预约咨询」跳转到 booking", "/workspace/booking", "/workspace/booking" in page.url, page.url)

    # booking 页不再有重复的「查看我的预约」按钮，改由侧栏导航进入
    dup = page.locator('.page-head button:has-text("查看我的预约")')
    rec("MA-17a", "booking 页头已无重复的「查看我的预约」按钮", "数量为 0", dup.count() == 0, "count=%d" % dup.count())
    page.locator('.nav-item', has_text="我的预约").first.click()
    page.wait_for_timeout(1500)
    rec("MA-17", "侧栏可进入我的预约", "/workspace/appointments", "/workspace/appointments" in page.url, page.url)

    # ---------- 咨询师端不受影响 ----------
    page2 = ctx.new_page()
    login(page2, "consultant@test.com")
    page2.goto(FRONT + "/counselor/dashboard", wait_until="domcontentloaded")
    page2.wait_for_timeout(2000)
    rec("MA-18", "咨询师端工作台正常", "页面含概览内容",
        page2.locator(".nav-item.active").count() == 1,
        "active=%d" % page2.locator(".nav-item.active").count())
    page2.screenshot(path=str(SHOTS / "04_咨询师端.png"), full_page=True)

    browser.close()

passed = sum(1 for r in results if r["ok"])
print("\n" + "=" * 60)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
json.dump({"results": results, "stats": {"pass": passed, "fail": len(results) - passed, "total": len(results)}},
          open(Path(__file__).parent / "results_my_appt.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
