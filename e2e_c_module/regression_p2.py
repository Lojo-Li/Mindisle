# -*- coding: utf-8 -*-
"""第二阶段 P2 回归测试（BUG-04 ~ BUG-08）。

用法： python regression_p2.py --label before|after

前置：后端须由 run_backend_mail_mock.py 启动（邮件服务已 Mock，绝不发真实邮件）。
每次运行自行创建 E2E_P2_ 前缀隔离数据、断言、按主键精确清理。
密码与 token 仅存内存；结果写入 regression_p2_<label>.json。
"""
import datetime as dt
import json
import secrets
import sys
import time
import traceback
from pathlib import Path

import bcrypt
import requests

import common

HERE = Path(__file__).resolve().parent
BASE = common.BASE_URL
LABEL = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "after"
OUT = HERE / ("regression_p2_%s.json" % LABEL)
EVENT_LOG = HERE / "mail_mock_events.jsonl"
ERR_LOG = HERE / "backend.p2.err.log"
D = (dt.date.today() + dt.timedelta(days=3)).isoformat()

CTX = {"user_ids": [], "counselor_ids": [], "appointment_ids": [], "tokens": {}}
CASES = []


def redact(obj):
    keys = {"token", "access_token", "password", "password_hash", "authorization",
            "secret", "email", "phone", "user_contact"}
    if isinstance(obj, dict):
        return {k: ("<redacted>" if k.lower() in keys else redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


def call(method, path, token=None, body=None, params=None, timeout=60):
    headers = {"Authorization": "Bearer " + token} if token else {}
    try:
        r = requests.request(method, BASE + path, json=body, params=params,
                             headers=headers, timeout=timeout)
        try:
            payload = r.json()
        except ValueError:
            payload = r.text[:500]
        return {"status": r.status_code, "body": redact(payload), "raw": payload}
    except Exception as e:
        return {"status": -1, "body": {"error": repr(e)}, "raw": {}}


def data_of(r):
    b = r.get("raw")
    return b.get("data") if isinstance(b, dict) else None


def items_of(r):
    d = data_of(r)
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and isinstance(d.get("items"), list):
        return d["items"]
    return []


def detail_of(r):
    b = r.get("raw")
    return str(b.get("detail", "")) if isinstance(b, dict) else ""


def rec(cid, bug, name, expected, ok, resp=None, db=None, note=""):
    CASES.append({"id": cid, "bug": bug, "name": name, "expected": expected,
                  "status": "PASS" if ok else "FAIL", "ok": bool(ok),
                  "http": resp["status"] if resp else None,
                  "response": resp["body"] if resp else None, "db": db, "note": note})
    print("[%s] %-7s %-7s %s (HTTP %s)" % (
        "PASS" if ok else "FAIL", cid, bug, name, resp["status"] if resp else "-"))


def one(sql, args=None):
    rows = common.query(sql, args)
    return common.row_dict(rows[0]) if rows else None


def cnt(sql, args=None):
    return common.query(sql, args)[0]["c"]


def log_pos(path):
    return path.stat().st_size if path.exists() else 0


def log_tail(path, pos):
    if not path.exists():
        return ""
    with path.open("rb") as fh:
        fh.seek(pos)
        return fh.read().decode("utf-8", errors="replace")


def event_tail(pos):
    text = log_tail(EVENT_LOG, pos)
    return [json.loads(x) for x in text.splitlines() if x.strip()]


def setup():
    CTX["baseline"] = {t: cnt("SELECT COUNT(*) AS c FROM `%s`" % t) for t in common.C_TABLES}
    pw = secrets.token_urlsafe(14)
    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    tag = "E2E_P2_%s_%s" % (LABEL, time.strftime("%H%M%S"))

    def add_user(role, suffix):
        email = "%s_%s@example.com" % (tag, suffix)
        _, uid = common.execute(
            "INSERT INTO users (email,password_hash,nickname,status,is_verified,is_deleted,role) "
            "VALUES (%s,%s,%s,'active',1,0,%s)", (email, hashed, tag + "_" + suffix, role))
        CTX["user_ids"].append(uid)
        return uid, email

    users = {}
    for role, key in [("user", "STU_A"), ("user", "STU_B"), ("counselor", "CNS1")]:
        users[key] = add_user(role, key)
    _, cid_ = common.execute(
        "INSERT INTO counselors (user_id,name,gender,title,specialties,consultation_types,"
        "experience_years,education,qualifications,price_video,price_voice,price_offline,"
        "rating,review_count,consultation_count,bio,status,is_verified,is_deleted,application_status) "
        "VALUES (%s,%s,'female','E2E_P2_职称','anxiety,sleep','video,voice,offline',5,"
        "'E2E_P2_学历','E2E_P2_资质',100,80,150,5.0,0,0,'E2E_P2_简介','active',1,0,'approved')",
        (users["CNS1"][0], tag + "_咨询师"))
    CTX["counselor_ids"].append(cid_)
    CTX["counselor_id"] = cid_

    for key, (_, email) in users.items():
        r = call("POST", "/api/auth/login", body={"email": email, "password": pw})
        tok = (r["raw"].get("data") or {}).get("token")
        if tok:
            CTX["tokens"][key] = tok
    if len(CTX["tokens"]) != 3:
        raise RuntimeError("隔离账号登录失败")


def create(hour, date_value=None, token="STU_A", ctype="video"):
    body = {
        "counselor_id": CTX["counselor_id"],
        "consultation_type": ctype,
        "appointment_date": date_value or ("%s %02d:00:00" % (D, hour)),
        "user_name": "E2E_P2_预约人",
        "problem_description": "E2E_P2 回归测试",
    }
    r = call("POST", "/api/appointment/create", token=CTX["tokens"][token], body=body)
    d = data_of(r)
    if r["status"] == 200 and isinstance(d, dict) and d.get("id"):
        CTX["appointment_ids"].append(d["id"])
    return r, (d.get("id") if isinstance(d, dict) else None)


def finish(aid):
    call("POST", "/api/consultation/order/%s/handle" % aid,
         token=CTX["tokens"]["CNS1"], body={"action": "agree"})
    call("POST", "/api/consultation/%s/message" % aid, token=CTX["tokens"]["STU_A"],
         body={"content": "E2E_P2 消息", "message_type": "text"})
    call("POST", "/api/consultation/%s/end" % aid, token=CTX["tokens"]["STU_A"])


def run_cases():
    T, C1 = CTX["tokens"], CTX["counselor_id"]

    # ---------- BUG-05 ----------
    for cid_, bug_input in [("P2-01", "%sT13:00:00Z" % D),
                            ("P2-02", "%sT13:00:00+08:00" % D)]:
        r, _ = create(13, date_value=bug_input)
        rows = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date LIKE %s",
                   (C1, D + "%13%"))
        rec(cid_, "BUG-05", "带时区输入返回明确 400（%s）" % bug_input.split("T")[-1],
            "400 且提示日期时间格式错误，DB 无新增", r["status"] == 400 and
            "日期时间格式错误" in detail_of(r) and rows == 0, r,
            db={"rows_at_13": rows})

    r, a_main = create(9, date_value="%sT09:00:00" % D)
    rec("P2-03", "BUG-05", "前端既有格式 YYYY-MM-DDTHH:MM:SS 仍可创建（无回归）",
        "200 且真实落库", r["status"] == 200 and bool(a_main), r,
        db={"appointment_id": a_main})

    r1, _ = create(13, date_value="2020-01-01 09:00:00")
    r2, _ = create(13, date_value="not-a-datetime")
    rec("P2-04", "BUG-05", "过去时间 / 格式错误仍返回 400（无回归）",
        "两个请求均 400", r1["status"] == 400 and r2["status"] == 400, r2,
        db={"past_http": r1["status"], "bad_format_http": r2["status"]})

    # ---------- BUG-04 / BUG-06 / BUG-07 ----------
    perm_cases = [
        ("P2-05", "BUG-04", "学生B 读取学生A 预约详情",
         lambda: call("GET", "/api/appointment/%s" % a_main, token=T["STU_B"]), 403),
        ("P2-06", "BUG-04", "学生访问咨询师订单列表",
         lambda: call("GET", "/api/consultation/counselor/orders", token=T["STU_A"],
                      params={"page": 1, "page_size": 50}), 403),
        ("P2-07", "BUG-04", "学生接受/拒绝订单",
         lambda: call("POST", "/api/consultation/order/%s/handle" % a_main, token=T["STU_A"],
                      body={"action": "agree"}), 403),
        ("P2-08", "BUG-06", "学生访问 /appointment/counselor/list",
         lambda: call("GET", "/api/appointment/counselor/list", token=T["STU_A"],
                      params={"page": 1, "page_size": 50}), 403),
        ("P2-09", "BUG-07", "学生B 取消学生A 预约",
         lambda: call("POST", "/api/appointment/%s/cancel" % a_main, token=T["STU_B"],
                      params={"reason": "E2E_P2"}), 403),
        ("P2-10", "BUG-07", "学生B 替学生A 提交评价",
         lambda: call("POST", "/api/appointment/%s/review" % a_main, token=T["STU_B"],
                      body={"rating": 5, "content": "E2E_P2"}), 403),
    ]
    before_status = one("SELECT status FROM appointments WHERE id=%s", (a_main,))
    for cid_, bug, name, fn, expect in perm_cases:
        r = fn()
        after_status = one("SELECT status FROM appointments WHERE id=%s", (a_main,))
        ok = r["status"] == expect and before_status["status"] == after_status["status"]
        rec(cid_, bug, name, "HTTP %s 且 DB 状态不变" % expect, ok, r,
            db={"status_before": before_status["status"], "status_after": after_status["status"]},
            note="修复前：500（HTTPException 被吞）/ 400（归属与不存在未区分）")

    r = call("POST", "/api/appointment/99999999/cancel", token=T["STU_A"], params={"reason": "E2E_P2"})
    rec("P2-11", "BUG-07", "不存在的预约仍返回 400「预约不存在」（区分性不回归）",
        "400 且文案为预约不存在", r["status"] == 400 and "预约不存在" in detail_of(r), r)

    # ---------- 无回归：C 与 B 既有能力 ----------
    r = call("GET", "/api/appointment/counselor/list", token=T["CNS1"],
             params={"page": 1, "page_size": 50})
    rec("P2-12", "NO-REG", "咨询师查看自己收到的预约列表（P1 BUG-01 成果保持）",
        "200 且含 user_info", r["status"] == 200 and
        any(isinstance(x.get("user_info"), dict) for x in items_of(r)), r,
        db={"items": len(items_of(r))})

    rb1 = call("GET", "/api/counselor/list", params={"keyword": "E2E_P2_", "page": 1, "page_size": 20})
    rb2 = call("GET", "/api/counselor/%s/slots" % C1, params={"date": D})
    slots = items_of(rb2)
    rec("P2-13", "NO-REG", "B 模块咨询师列表与可预约时段接口保持不变",
        "两个接口均 200，slots 仍为 10 个整点且字段完整",
        rb1["status"] == 200 and rb2["status"] == 200 and len(slots) == 10 and
        all(set(("time", "available", "price")).issubset(x.keys()) for x in slots), rb2,
        db={"slots_count": len(slots), "counselor_list_http": rb1["status"]})

    _, a_cancel = create(10)
    rc = call("POST", "/api/appointment/%s/cancel" % a_cancel, token=T["STU_A"],
              params={"reason": "E2E_P2"})
    _, a_review = create(11)
    finish(a_review)
    rv = call("POST", "/api/appointment/%s/review" % a_review, token=T["STU_A"],
              body={"rating": 4.5, "content": "E2E_P2 评价", "is_anonymous": True})
    stats = one("SELECT rating, review_count FROM counselors WHERE id=%s", (C1,))
    agg = one("SELECT COUNT(*) AS c, AVG(rating) AS a FROM consultation_reviews WHERE counselor_id=%s", (C1,))
    rec("P2-14", "NO-REG", "本人取消、完成、评价及评分统计（P1 成果保持）",
        "取消/评价均 200，counselors 统计与评价聚合一致",
        rc["status"] == 200 and rv["status"] == 200 and
        int(stats["review_count"]) == int(agg["c"]) == 1 and
        abs(float(stats["rating"]) - float(agg["a"])) < 0.001, rv,
        db={"cancel_http": rc["status"], "review_http": rv["status"],
            "counselors": stats, "aggregate": agg})

    # ---------- BUG-08（邮件 Mock 事件 + 后端日志，无真实邮件） ----------
    ev_pos, err_pos = log_pos(EVENT_LOG), log_pos(ERR_LOG)
    _, a_mail = create(12)
    r_cancel_mail = call("POST", "/api/appointment/%s/cancel" % a_mail,
                         token=T["STU_A"], params={"reason": "E2E_P2"})
    events = event_tail(ev_pos)
    err_new = log_tail(ERR_LOG, err_pos)
    counselor_conf = [e for e in events if e["event"] == "confirmation_counselor"]
    cancelled_events = [e for e in events if e["event"] == "cancelled"]
    no_attr_error = "'Counselor' object has no attribute 'email'" not in err_new
    ok = (r_cancel_mail["status"] == 200 and len(counselor_conf) >= 1 and
          all(e["has_email"] for e in counselor_conf) and len(cancelled_events) >= 2 and
          no_attr_error)
    rec("P2-15", "BUG-08", "咨询师预约/取消邮件经 users.email 关联发出（Mock，无真实邮件）",
        "创建/取消均 200；Mock 事件含 confirmation_counselor 且带收件地址；"
        "cancelled 事件>=2；后端日志不再出现 AttributeError", ok, r_cancel_mail,
        db={"mock_events": events, "counselor_confirmation_count": len(counselor_conf),
            "cancelled_event_count": len(cancelled_events),
            "attribute_error_in_new_log": not no_attr_error},
        note="邮件服务由 run_backend_mail_mock.py 用 unittest.mock 隔离，未调用真实 SMTP。")


def cleanup():
    log = []
    aids, uids, cids = CTX["appointment_ids"], CTX["user_ids"], CTX["counselor_ids"]
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
    after = {t: cnt("SELECT COUNT(*) AS c FROM `%s`" % t) for t in common.C_TABLES}
    return {"cleanup": log, "baseline_restored": all(after[k] == v for k, v in CTX["baseline"].items()),
            "db_after": after}


def main():
    clean = {}
    try:
        setup()
        run_cases()
    except Exception:
        traceback.print_exc()
        rec("P2-ERR", "-", "回归套件执行", "所有用例正常执行", False,
            note=traceback.format_exc()[-1000:])
    finally:
        try:
            clean = cleanup()
        except Exception:
            traceback.print_exc()
            clean = {"cleanup_error": traceback.format_exc()[-500:]}
        stats = {"PASS": sum(1 for c in CASES if c["status"] == "PASS"),
                 "FAIL": sum(1 for c in CASES if c["status"] == "FAIL")}
        OUT.write_text(json.dumps({
            "label": LABEL, "run_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": D, "stats": stats, "cases": CASES, "cleanup": clean,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nLABEL=%s STATS=%s CLEANUP=%s" % (
            LABEL, stats, clean.get("baseline_restored", clean.get("cleanup_error"))))
        print("RESULTS ->", OUT)


if __name__ == "__main__":
    main()
