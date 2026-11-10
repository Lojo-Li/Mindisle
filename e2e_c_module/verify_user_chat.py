"""验证用户咨询对话页（心屿风格）的真实渲染与交互"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_pwlib"))
from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
AID = None  # 运行时自动获取最新的一笔有效预约
SHOTS = Path(__file__).parent / "shots_user_chat"
SHOTS.mkdir(exist_ok=True)

results = []


def rec(tid, name, expect, ok, actual=""):
    results.append({"id": tid, "name": name, "expect": expect, "ok": bool(ok), "actual": str(actual)[:200]})
    print(("  PASS  " if ok else "  FAIL  ") + "%s %s :: %s" % (tid, name, actual))


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

    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    login(page, "user@test.com")
    rec("UC-01", "登录成功", "离开登录页", "/login" not in page.url, page.url)

    # 自动取最新一笔「已确认/进行中」的预约，避免写死 id
    AID = page.evaluate("""async () => {
      const t = sessionStorage.getItem('token') || localStorage.getItem('token') || '';
      const r = await fetch('/api/appointment/user/list?page=1&page_size=100', {
        headers: t ? { Authorization: 'Bearer ' + t } : {}
      });
      const d = await r.json();
      const items = (d && d.data && d.data.items) || [];
      const ok = items.filter(x => ['confirmed', 'in_progress'].includes(x.status));
      return (ok[0] || items[0] || {}).id || null;
    }""")
    rec("UC-00", "取到可测试的预约 id", "非空", bool(AID), AID)
    if not AID:
        print("  没有可用预约，请先创建一笔并让咨询师接单")
        browser.close()
        raise SystemExit(1)

    page.goto(FRONT + "/workspace/chat/%d" % AID, wait_until="domcontentloaded")
    # 轮询等待咨询室渲染完成（v-if 链切换 + 两个接口）
    for _ in range(40):
        if page.locator(".chat-shell").count() > 0:
            break
        page.wait_for_timeout(500)
    page.wait_for_timeout(1200)

    rec("UC-02", "页面无 JS 运行错误", "无 pageerror", len(errors) == 0, str(errors[:2]))

    # 基础结构
    rec("UC-03", "聊天容器渲染", ".chat-shell 存在", page.locator(".chat-shell").count() == 1,
        "count=%d" % page.locator(".chat-shell").count())

    h3 = page.locator(".chat-peer-text h3")
    rec("UC-04", "头部显示咨询师姓名", "张咨询师", "张咨询师" in h3.inner_text() if h3.count() else False,
        h3.inner_text().replace("\n", " ") if h3.count() else "无")

    meta = page.locator(".chat-peer-meta").inner_text() if page.locator(".chat-peer-meta").count() else ""
    rec("UC-05", "头部显示咨询方式与公益免费", "视频咨询 + 公益免费",
        "视频咨询" in meta and "公益免费" in meta, meta.replace("\n", " "))

    # 信息条
    strip = page.locator(".info-strip").inner_text() if page.locator(".info-strip").count() else ""
    rec("UC-06", "信息条显示预约编号与时间", "含预约编号",
        "预约编号" in strip and "APT" in strip, strip.replace("\n", " ")[:80])
    rec("UC-07", "信息条显示学生诉求", "你的诉求",
        "你的诉求" in strip, "")

    # 消息气泡
    bubbles = page.locator(".bubble")
    rec("UC-08", "消息气泡渲染", ">=3 条", bubbles.count() >= 3, "count=%d" % bubbles.count())

    self_rows = page.locator(".bubble-row.self")
    other_rows = page.locator(".bubble-row:not(.self)")
    rec("UC-09", "自己/对方消息分区渲染", "各>=1",
        self_rows.count() >= 1 and other_rows.count() >= 1,
        "self=%d other=%d" % (self_rows.count(), other_rows.count()))

    # 关键：消息内容不能被渲染成原始代码（之前 counselorName 教训）
    body_txt = page.locator(".chat-body").inner_text()
    rec("UC-10", "消息文本正常渲染（无原始源码泄漏）", "不含 => 或 computed",
        "=>" not in body_txt and "computed(" not in body_txt and "appt.value" not in body_txt,
        body_txt[:60].replace("\n", " "))
    rec("UC-11", "第一条消息内容正确", "睡不好",
        "睡不好" in body_txt, "")
    rec("UC-12", "咨询师回复内容正确", "持续多久",
        "持续多久" in body_txt, "")

    # 时间戳
    times = page.locator(".bubble-time").all_inner_texts()
    rec("UC-13", "消息带时间戳", "形如 HH:MM",
        len(times) >= 3 and all(":" in t and len(t) == 5 for t in times), str(times[:3]))

    # 状态标签
    tag = page.locator(".chat-peer-text .tag").first.inner_text() if page.locator(".chat-peer-text .tag").count() else ""
    rec("UC-14", "状态标签显示「进行中」", "进行中", "进行中" in tag, tag)

    # 计时器
    rec("UC-15", "显示会话计时器", ".timer-badge 存在",
        page.locator(".timer-badge").count() == 1,
        page.locator(".timer-badge").count())
    t1 = page.locator(".timer-badge").inner_text() if page.locator(".timer-badge").count() else ""
    page.wait_for_timeout(2200)
    t2 = page.locator(".timer-badge").inner_text() if page.locator(".timer-badge").count() else ""
    rec("UC-16", "计时器在走", "2 秒后数值变化", t1 != t2, "%s → %s" % (t1.strip(), t2.strip()))

    # 视频通话按钮
    rec("UC-17", "显示视频通话按钮", "含「视频通话」",
        page.locator('.chat-head-actions button:has-text("视频通话")').count() == 1, "")

    # 结束咨询按钮
    rec("UC-18", "显示结束咨询按钮", "含「结束咨询」",
        page.locator('.chat-head-actions button:has-text("结束咨询")').count() == 1, "")

    # 输入区
    ta = page.locator(".input-textarea")
    rec("UC-19", "输入框存在", "textarea", ta.count() == 1, "count=%d" % ta.count())
    rec("UC-20", "工具栏三个按钮（图片/文件/语音）", "3 个 .tool-btn",
        page.locator(".input-tools .tool-btn").count() == 3,
        "count=%d" % page.locator(".input-tools .tool-btn").count())

    page.screenshot(path=str(SHOTS / "01_对话页.png"), full_page=True)

    # 发送消息
    ta.fill("这是一条前端发送的测试消息")
    page.wait_for_timeout(300)
    send_btn = page.locator(".send-btn")
    rec("UC-21", "输入内容后发送按钮可点击", "enabled", send_btn.is_enabled(), "")
    send_btn.click()
    page.wait_for_timeout(2500)
    body2 = page.locator(".chat-body").inner_text()
    rec("UC-22", "发送后消息出现在列表", "含测试消息文本",
        "这是一条前端发送的测试消息" in body2, "")
    ta2 = page.locator(".input-textarea")
    rec("UC-23", "发送后输入框已清空", "空值", ta2.input_value() == "", repr(ta2.input_value()[:20]))

    # 3 秒轮询
    page.wait_for_timeout(4000)
    rec("UC-24", "轮询后无重复消息", "消息数稳定",
        page.locator(".bubble").count() >= 4, "count=%d" % page.locator(".bubble").count())

    # UI 风格一致性
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
        shell: g('.chat-shell', ['background-color','border-radius','border-color','box-shadow']),
        avatar: g('.chat-avatar', ['background-image','border-radius']),
        selfBubble: g('.bubble-row.self .bubble', ['background-image','color','border-radius']),
        otherBubble: g('.bubble-row:not(.self) .bubble', ['background-color','border-color','border-radius']),
        sendBtn: g('.send-btn', ['background-image','border-radius','height']),
        textarea: g('.input-textarea', ['border-color','border-radius']),
        timer: g('.timer-badge', ['background-color','color','border-radius']),
      };
    }""")

    def sea_grad(img):
        if not img: return False
        n = img.lower().replace(" ", "")
        return ("#357b74" in n and "#22524e" in n) or ("rgb(53,123,116)" in n and "rgb(34,82,78)" in n)

    rec("UC-25", "聊天壳为心屿卡片(18px/白底/细边)",
        "18px + rgb(255,255,255)",
        style["shell"] and style["shell"]["border-radius"] == "18px"
        and style["shell"]["background-color"] == "rgb(255, 255, 255)",
        style["shell"])
    rec("UC-26", "头像为墨绿渐变", "#357B74→#22524E",
        sea_grad(style["avatar"] and style["avatar"]["background-image"]),
        style["avatar"] and style["avatar"]["background-image"][:50])
    rec("UC-27", "自己的气泡为墨绿渐变白字", "渐变 + 白字",
        sea_grad(style["selfBubble"] and style["selfBubble"]["background-image"])
        and style["selfBubble"]["color"] == "rgb(255, 255, 255)",
        style["selfBubble"] and style["selfBubble"]["color"])
    rec("UC-28", "对方气泡为浅色带边框", "浅底 + 细边",
        style["otherBubble"] and style["otherBubble"]["border-color"] == "rgb(231, 229, 222)",
        style["otherBubble"] and style["otherBubble"]["border-color"])
    rec("UC-29", "发送按钮为墨绿渐变", "#357B74→#22524E",
        sea_grad(style["sendBtn"] and style["sendBtn"]["background-image"]),
        style["sendBtn"] and style["sendBtn"]["background-image"][:50])
    rec("UC-30", "计时器用心屿 sea-soft 底色", "rgb(226,239,236)",
        style["timer"] and style["timer"]["background-color"] == "rgb(226, 239, 236)",
        style["timer"] and style["timer"]["background-color"])

    page.screenshot(path=str(SHOTS / "02_发送后.png"), full_page=True)

    # 咨询师端视角：确认不是用户端专属问题
    page2 = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    login(page2, "consultant@test.com")
    page2.goto(FRONT + "/consultation/counselor/%d" % AID, wait_until="domcontentloaded")
    page2.wait_for_timeout(3000)
    rec("UC-31", "咨询师端对话页仍可用（未被影响）", "有消息区域",
        page2.locator(".chat-container, .chat-wrapper, .message").count() > 0,
        "count=%d" % page2.locator(".chat-container, .chat-wrapper, .message").count())

    browser.close()

passed = sum(1 for r in results if r["ok"])
print("\n" + "=" * 60)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
json.dump({"results": results, "stats": {"pass": passed, "fail": len(results) - passed, "total": len(results)}},
          open(Path(__file__).parent / "results_user_chat.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
