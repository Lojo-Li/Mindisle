# -*- coding: utf-8 -*-
"""C 模块浏览器端到端测试（Playwright + 系统 Chrome，隔离账号/数据）。

只新增 E2E_UI_ 前缀数据，结束按主键精确清理；密码与 token 仅存内存。
"""
import datetime as dt
import json
import secrets
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_pwlib"))
sys.path.insert(0, str(HERE))

import bcrypt  # noqa: E402
import requests  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

import common  # noqa: E402

FRONT = "http://127.0.0.1:5173"
API = common.BASE_URL
TAG = "E2E_UI_" + time.strftime("%Y%m%d%H%M%S")
TEST_DATE = (dt.date.today() + dt.timedelta(days=3)).isoformat()
OUT = HERE / "browser_results.json"

CTX = {"user_ids": [], "counselor_ids": [], "appointment_ids": []}
CASES = []


def rec(cid, name, expected, ok, actual="", note=""):
    CASES.append({"id": cid, "name": name, "expected": expected,
                  "status": "PASS" if ok else "FAIL", "actual": str(actual)[:500], "note": note})
    print("[%s] %s %s | %s" % ("PASS" if ok else "FAIL", cid, name, str(actual)[:160]))


def setup():
    pw = secrets.token_urlsafe(14)
    h = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

    def user(role, tag):
        email = "%s_%s@example.com" % (TAG, tag)
        _, uid = common.execute(
            "INSERT INTO users (email,password_hash,nickname,status,is_verified,is_deleted,role) "
            "VALUES (%s,%s,%s,'active',1,0,%s)", (email, h, TAG + "_" + tag, role))
        CTX["user_ids"].append(uid)
        return uid, email

    suid, semail = user("user", "STU")
    cuid, _ = user("counselor", "CNS")
    cname = TAG + "_咨询师"
    _, cid_ = common.execute(
        "INSERT INTO counselors (user_id,name,gender,title,specialties,consultation_types,"
        "experience_years,education,qualifications,price_video,price_voice,price_offline,"
        "rating,review_count,consultation_count,bio,status,is_verified,is_deleted,application_status) "
        "VALUES (%s,%s,'female','E2E_UI_职称','anxiety,sleep','video,voice,offline',5,"
        "'E2E_UI_学历','E2E_UI_资质',100,80,150,5.0,0,0,'E2E_UI_简介','active',1,0,'approved')",
        (cuid, cname))
    CTX["counselor_ids"].append(cid_)
    CTX["counselor_id"] = cid_
    CTX["counselor_name"] = cname
    CTX["student_email"] = semail
    CTX["password"] = pw
    CTX["student_user_id"] = suid


def cleanup():
    log = []
    aids = CTX["appointment_ids"]
    uids = CTX["user_ids"]
    cids = CTX["counselor_ids"]
    if aids:
        ph = ",".join(["%s"] * len(aids))
        for t in ["consultation_messages", "consultation_reviews"]:
            n, _ = common.execute("DELETE FROM `%s` WHERE appointment_id IN (%s)" % (t, ph), tuple(aids))
            log.append("%s:-%s" % (t, n))
        n, _ = common.execute("DELETE FROM appointments WHERE id IN (%s)" % ph, tuple(aids))
        log.append("appointments:-%s" % n)
    if uids:
        uph = ",".join(["%s"] * len(uids))
        for t, c in [("notifications", "user_id"), ("inquiry_messages", "sender_id"),
                     ("counselor_inquiries", "user_id")]:
            try:
                n, _ = common.execute("DELETE FROM `%s` WHERE `%s` IN (%s)" % (t, c, uph), tuple(uids))
                log.append("%s:-%s" % (t, n))
            except Exception:
                pass
    if cids:
        n, _ = common.execute("DELETE FROM counselors WHERE id IN (%s)" % ",".join(["%s"] * len(cids)), tuple(cids))
        log.append("counselors:-%s" % n)
    if uids:
        n, _ = common.execute("DELETE FROM users WHERE id IN (%s)" % ",".join(["%s"] * len(uids)), tuple(uids))
        log.append("users:-%s" % n)
    CTX["cleanup_log"] = log


def main():
    browser = None
    try:
        setup()
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)[:200]))

            # UI-01 公开咨询师列表由真实接口渲染
            page.goto(FRONT + "/counselor", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1200)
            html = page.content()
            ok = CTX["counselor_name"] in html
            rec("UI-01", "浏览器打开 /counselor，验证咨询师卡片由后端数据渲染",
                "页面 DOM 出现隔离测试咨询师名称（证明前端真实调用 /api/counselor/list）", ok,
                "counselor_name_found=%s, page_errors=%s" % (ok, errors[:3]))

            # UI-02 通过登录页真实登录
            page.goto(FRONT + "/login", wait_until="networkidle", timeout=30000)
            page.fill("#account", CTX["student_email"])
            page.fill("#pwd", CTX["password"])
            page.click("#submitBtn")
            page.wait_for_timeout(2500)
            token = page.evaluate("() => sessionStorage.getItem('token')")
            logged_in = bool(token) and "/login" not in page.url
            rec("UI-02", "在登录页输入隔离账号并点击登录",
                "sessionStorage 写入 token，且页面离开 /login", logged_in,
                "url=%s, token_present=%s, page_errors=%s" % (page.url, bool(token), errors[:3]))

            token = token or ""
            headers = {"Authorization": "Bearer " + token}

            # UI-03 用浏览器会话令牌创建预约，再在订单页验证渲染
            appointment_no = None
            aid = None
            if logged_in:
                resp = requests.post(API + "/api/appointment/create", headers=headers, timeout=60, json={
                    "counselor_id": CTX["counselor_id"],
                    "consultation_type": "video",
                    "appointment_date": TEST_DATE + " 09:00:00",
                    "user_name": TAG + "_预约人",
                    "problem_description": "E2E_UI 浏览器链路测试",
                })
                if resp.status_code == 200:
                    d = resp.json().get("data", {})
                    aid = d.get("id")
                    appointment_no = d.get("appointment_no")
                    if aid:
                        CTX["appointment_ids"].append(aid)
                rec("UI-03a", "使用浏览器会话令牌调用创建预约接口",
                    "200 且返回 appointment_no", resp.status_code == 200 and bool(appointment_no),
                    "http=%s appointment_no_present=%s" % (resp.status_code, bool(appointment_no)))

                page.goto(FRONT + "/counselor/orders", wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)
                html = page.content()
                ok = bool(appointment_no) and appointment_no in html and "待确认" in html
                rec("UI-03b", "浏览器打开 /counselor/orders 查看预约状态",
                    "DOM 显示该预约编号与「待确认」状态标签", ok,
                    "appointment_no_in_dom=%s, pending_label_in_dom=%s, page_errors=%s" %
                    (bool(appointment_no) and appointment_no in html, "待确认" in html, errors[:3]))

                # UI-04 点击取消预约并确认弹框
                if aid:
                    btn = page.get_by_role("button", name="取消预约")
                    clicked = False
                    try:
                        if btn.count() > 0:
                            btn.first.click()
                            clicked = True
                            page.wait_for_timeout(600)
                            confirm = page.get_by_role("button", name="确定")
                            if confirm.count() > 0:
                                confirm.first.click()
                            page.wait_for_timeout(1800)
                    except Exception as e:
                        click_error = repr(e)[:200]
                    html = page.content()
                    row = common.query("SELECT status, cancel_reason FROM appointments WHERE id=%s", (aid,))
                    db_status = row[0]["status"] if row else None
                    ok = clicked and db_status == "cancelled" and "已取消" in html
                    rec("UI-04", "点击「取消预约」并在确认框确认",
                        "DB status=cancelled 且页面出现「已取消」标签", ok,
                        "clicked=%s db_status=%s cancelled_label_in_dom=%s page_errors=%s" %
                        (clicked, db_status, "已取消" in html, errors[:3]),
                        note="前端按钮点击后调用 POST /api/appointment/{id}/cancel。")
                else:
                    rec("UI-04", "点击「取消预约」并在确认框确认", "DB status=cancelled", False,
                        "未创建预约，用例阻塞", )
            else:
                rec("UI-03a", "使用浏览器会话令牌调用创建预约接口", "200", False, "登录失败导致阻塞")
                rec("UI-03b", "浏览器打开 /counselor/orders 查看预约状态", "DOM 显示预约", False, "登录失败导致阻塞")
                rec("UI-04", "点击「取消预约」并在确认框确认", "DB status=cancelled", False, "登录失败导致阻塞")

            # UI-05 全新浏览器上下文（无登录态）访问受保护路由
            ctx2 = browser.new_context(viewport={"width": 1440, "height": 900})
            page2 = ctx2.new_page()
            page2.goto(FRONT + "/counselor/orders", wait_until="networkidle", timeout=30000)
            page2.wait_for_timeout(900)
            ok = "/login" in page2.url
            rec("UI-05", "未登录访问 /counselor/orders 路由守卫",
                "重定向到 /login", ok, "final_url=%s" % page2.url)
            ctx2.close()
            ctx.close()
    except Exception:
        traceback.print_exc()
        rec("UI-ERR", "浏览器测试执行", "全部用例正常执行", False, traceback.format_exc()[-800:])
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        try:
            cleanup()
        except Exception:
            traceback.print_exc()
        after = {t: common.query("SELECT COUNT(*) AS c FROM `%s`" % t)[0]["c"] for t in common.C_TABLES}
        OUT.write_text(json.dumps({
            "run_tag": TAG, "test_date": TEST_DATE, "cases": CASES,
            "cleanup": CTX.get("cleanup_log", []),
            "db_after": after,
            "stats": {"PASS": sum(1 for c in CASES if c["status"] == "PASS"),
                      "FAIL": sum(1 for c in CASES if c["status"] == "FAIL")},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print("BROWSER_RESULTS ->", OUT)


if __name__ == "__main__":
    main()
