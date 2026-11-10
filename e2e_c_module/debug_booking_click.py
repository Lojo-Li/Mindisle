"""真实浏览器测试：打开 /workspace/booking，登录后点击「选择时段」，观察弹窗是否出现。"""
import sys
import json
from pathlib import Path

PW = Path(__file__).resolve().parent / "_pwlib"
sys.path.insert(0, str(PW))

from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
OUT = Path(__file__).resolve().parent


def main():
    logs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        page.on("console", lambda m: logs.append("[%s] %s" % (m.type, m.text[:200])))
        page.on("pageerror", lambda e: logs.append("[PAGEERROR] " + str(e)[:300]))

        # 1. 登录
        page.goto(BASE + "/login", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        print("登录页 URL:", page.url)

        # 尝试填写登录表单
        try:
            page.fill('input[type="email"], input[placeholder*="邮箱"], input[placeholder*="mail"]', "user@test.com")
            page.fill('input[type="password"]', "123456")
            page.click('button:has-text("登录"), button[type="submit"]')
            page.wait_for_timeout(3000)
        except Exception as e:
            print("登录表单填写失败:", e)

        print("登录后 URL:", page.url)

        # 2. 直接进 booking
        page.goto(BASE + "/workspace/booking", wait_until="networkidle")
        page.wait_for_timeout(2500)
        print("booking URL:", page.url)

        # 3. 统计卡片与按钮
        cards = page.locator(".docs .doc")
        print("卡片数量:", cards.count())

        btns = page.locator(".docs .doc button", has_text="选择时段")
        print("「选择时段」按钮数量:", btns.count())

        if btns.count() == 0:
            print("\n>>> 没有找到任何「选择时段」按钮，页面内容：")
            print(page.locator(".docs").inner_html()[:800])
        else:
            # 打印第一张卡片的文字
            print("第一张卡片文字:", cards.first.inner_text()[:150].replace("\n", " | "))

            # 4. 点击前记录 overlay 状态
            ov = page.locator("#bookOverlay")
            print("点击前 overlay class:", ov.get_attribute("class"))

            # 5. 点击
            btns.first.click()
            page.wait_for_timeout(1500)

            print("点击后 overlay class:", ov.get_attribute("class"))
            print("点击后 overlay display:", ov.evaluate("el => getComputedStyle(el).display"))
            print("弹窗标题:", page.locator("#bookTitle").inner_text() if page.locator("#bookTitle").count() else "(无)")

            # 日期和时段是否有内容
            days_html = page.locator("#days").inner_html() if page.locator("#days").count() else ""
            slots_html = page.locator("#slots").inner_html() if page.locator("#slots").count() else ""
            print("日期按钮数:", days_html.count("data-day"))
            print("时段按钮数:", slots_html.count("data-slot"))

            page.screenshot(path=str(OUT / "debug_booking_after_click.png"), full_page=False)
            print("截图已保存: debug_booking_after_click.png")

        # 6. 控制台日志
        print("\n=== 控制台日志 ===")
        for l in logs[-20:]:
            print(" ", l)

        browser.close()


if __name__ == "__main__":
    main()
