"""测量「我的预约」空态与卡片态的尺寸/样式一致性"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
SHOTS = Path(__file__).parent / "shots_my_appt"
SHOTS.mkdir(exist_ok=True)

JS = """() => {
  const r = el => el ? el.getBoundingClientRect() : null;
  const cs = el => el ? getComputedStyle(el) : null;
  const card = document.querySelector('.appt-card') || document.querySelector('.card');
  const empty = document.querySelector('.empty');
  const ph = document.querySelector('.page-head');
  const fr = document.querySelector('.filter-row');
  return {
    mode: document.querySelector('.appt-list') ? 'list' : 'empty',
    cardBox: r(card) ? [Math.round(r(card).width), Math.round(r(card).height)] : null,
    cardStyle: cs(card) ? {
      border: cs(card).border, radius: cs(card).borderRadius,
      bg: cs(card).backgroundColor, shadow: cs(card).boxShadow,
      padding: cs(card).padding, marginTop: cs(card).marginTop
    } : null,
    emptyBox: r(empty) ? [Math.round(r(empty).width), Math.round(r(empty).height)] : null,
    emptyStyle: cs(empty) ? {
      padding: cs(empty).padding, color: cs(empty).color,
      fontSize: cs(empty).fontSize, textAlign: cs(empty).textAlign
    } : null,
    pageHeadW: r(ph) ? Math.round(r(ph).width) : null,
    filterW: r(fr) ? Math.round(r(fr).width) : null,
    emptyText: empty ? empty.innerText.split('\\n').filter(Boolean).join(' | ') : null
  };
}"""


def login(page, email, pwd="123456"):
    page.goto(FRONT + "/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    page.fill("#account", email)
    page.fill("#pwd", pwd)
    page.click("#submitBtn")
    page.wait_for_timeout(3000)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True,
                                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    login(page, "user@test.com")
    page.goto(FRONT + "/workspace/appointments", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    info = page.evaluate(JS)
    print("=== 当前模式:", info["mode"], "===")
    print(json.dumps(info, ensure_ascii=False, indent=2))

    if info["mode"] == "empty":
        w = info["cardBox"][0] if info["cardBox"] else None
        same_w = (w == info["pageHeadW"] == info["filterW"])
        print("\n=== 空态与页面内容区对齐校验 ===")
        print("  卡片宽度:", w)
        print("  page-head 宽度:", info["pageHeadW"])
        print("  filter-row 宽度:", info["filterW"])
        print(("  PASS  " if same_w else "  FAIL  ") + "空态卡片与页头/筛选栏等宽")
        print(("  PASS  " if info["cardStyle"] and info["cardStyle"]["radius"] == "18px" else "  FAIL  ")
              + "空态使用标准卡片外壳(18px 圆角)")
        print(("  PASS  " if info["emptyStyle"] and info["emptyStyle"]["textAlign"] == "center" else "  FAIL  ")
              + "空态文字居中（继承 .mi-portal .empty）")
    page.screenshot(path=str(SHOTS / "07_空态修复后.png"), full_page=True)
    browser.close()
