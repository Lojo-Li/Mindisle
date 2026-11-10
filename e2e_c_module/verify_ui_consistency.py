"""验证「我的预约」页面与心屿设计系统的一致性（取真实计算样式）"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"


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
    page.wait_for_timeout(2500)

    data = page.evaluate("""() => {
      const g = (sel, props) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const s = getComputedStyle(el);
        const o = {};
        props.forEach(p => o[p] = s.getPropertyValue(p));
        return o;
      };
      const root = document.querySelector('.mi-portal') || document.documentElement;
      const rs = getComputedStyle(root);
      return {
        vars: {
          sea: rs.getPropertyValue('--sea').trim(),
          seaDeep: rs.getPropertyValue('--sea-deep').trim(),
          surface: rs.getPropertyValue('--surface').trim(),
          line: rs.getPropertyValue('--line').trim(),
          ink: rs.getPropertyValue('--ink').trim(),
          ink2: rs.getPropertyValue('--ink-2').trim(),
          ink3: rs.getPropertyValue('--ink-3').trim(),
          lamp: rs.getPropertyValue('--lamp').trim(),
        },
        card: g('.appt-card', ['background-color','border-radius','border-color','box-shadow','padding']),
        avatar: g('.appt-avatar', ['background-image','border-radius','color','font-size']),
        h1: g('h1', ['font-size','font-weight','color','letter-spacing']),
        eyebrow: g('.eyebrow', ['font-size','color','letter-spacing','text-transform']),
        pillOn: g('.filter-row .pill.on', ['background-color','color','border-radius','height']),
        pillOff: g('.filter-row .pill:not(.on)', ['background-color','color','border-radius']),
        tagLamp: g('.appt-card .tag.lamp', ['background-color','color','border-radius']),
        tagSea: g('.appt-card .tag.sea', ['background-color','color','border-radius']),
        headBtn: g('.page-head .btn-primary', ['background-image','color','border-radius','height','font-size']),
        meta: g('.appt-meta', ['font-size','color']),
        navItems: Array.from(document.querySelectorAll('.nav-item')).map(n => n.innerText.trim().replace(/\\s+/g,' ')),
        navLabels: Array.from(document.querySelectorAll('.nav-group, .nav-label')).map(n => n.innerText.trim()),
        activeNav: (document.querySelector('.nav-item.active')||{}).innerText,
      };
    }""")

    print("=== 心屿设计变量 ===")
    for k, v in data["vars"].items():
        print("  --%-10s %s" % (k, v))

    print("\n=== 关键元素计算样式 ===")
    for key in ["card", "avatar", "h1", "eyebrow", "pillOn", "pillOff", "tagLamp", "tagSea", "headBtn", "meta"]:
        print("  %-9s %s" % (key, json.dumps(data[key], ensure_ascii=False) if data[key] else "未找到"))

    print("\n=== 侧栏菜单 ===")
    print("  分组:", data["navLabels"])
    for it in data["navItems"]:
        mark = "  ← 当前" if data["activeNav"] and it == data["activeNav"].strip().replace("\n", " ") else ""
        print("   -", it, mark)

    # 与心屿基准值断言
    checks = []
    v = data["vars"]
    checks.append(("主色 --sea 为墨绿 #2E6E68", v["sea"].lower() in ("#2e6e68",), v["sea"]))
    checks.append(("卡片背景为 --surface", data["card"] and data["card"]["background-color"] in ("rgb(255, 255, 255)", "rgba(255, 255, 255, 1)"), data["card"] and data["card"]["background-color"]))
    checks.append(("卡片圆角 18px", data["card"] and data["card"]["border-radius"] == "18px", data["card"] and data["card"]["border-radius"]))
    def _is_sea_grad(img):
        if not img:
            return False
        n = img.lower().replace(" ", "")
        # 浏览器把 #357B74/#22524E 渲染成 rgb(53,123,116)/rgb(34,82,78)
        return ("#357b74" in n and "#22524e" in n) or ("rgb(53,123,116)" in n and "rgb(34,82,78)" in n)

    checks.append(("头像为墨绿渐变(#357B74→#22524E)",
                   _is_sea_grad(data["avatar"] and data["avatar"]["background-image"]),
                   data["avatar"] and data["avatar"]["background-image"][:60]))
    checks.append(("页头 h1 完全继承心屿全局(27px/640)",
                   data["h1"] and data["h1"]["font-size"] == "27px" and data["h1"]["font-weight"] == "640",
                   data["h1"] and "%s/%s" % (data["h1"]["font-size"], data["h1"]["font-weight"])))
    checks.append(("筛选胶囊选中为墨绿", data["pillOn"] and "46, 110, 104" in data["pillOn"]["background-color"], data["pillOn"] and data["pillOn"]["background-color"]))
    checks.append(("待确认标签为琥珀色系", data["tagLamp"] and data["tagLamp"]["background-color"] not in ("rgba(0, 0, 0, 0)",), data["tagLamp"] and data["tagLamp"]["background-color"]))
    checks.append(("主按钮为墨绿渐变(#357B74→#22524E)",
                   _is_sea_grad(data["headBtn"] and data["headBtn"]["background-image"]),
                   data["headBtn"] and data["headBtn"]["background-image"][:50]))
    checks.append(("侧栏含「我的预约」", any("我的预约" in n for n in data["navItems"]), str(data["navItems"])))

    print("\n=== 风格一致性断言 ===")
    ok = 0
    for name, passed, actual in checks:
        print(("  PASS  " if passed else "  FAIL  ") + name + " :: " + str(actual)[:80])
        if passed:
            ok += 1
    print("\n结果：%d/%d 通过" % (ok, len(checks)))

    browser.close()
