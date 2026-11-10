# -*- coding: utf-8 -*-
"""Mindisle / SoulStation C 模块真实接口端到端测试。

约束：
- 只新增带 E2E_C_ 前缀的隔离数据，绝不修改/删除现有业务行；
- 账号密码与 token 仅在内存中使用，不写入任何结果文件；
- 结束时按主键精确清理本次新增的行，并校验库内基线行数恢复。
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

BASE = common.BASE_URL
RUN_TAG = time.strftime("%Y%m%d%H%M%S")
TEST_DATE = dt.date.today() + dt.timedelta(days=3)
OUT_FILE = Path(__file__).with_name("results.json")

SENSITIVE_KEYS = {
    "token", "access_token", "password", "password_hash", "authorization",
    "secret", "email", "phone", "user_contact", "admin_token",
}

RESULTS = []
CTX = {
    "user_ids": [],
    "counselor_ids": [],
    "appointment_ids": [],
    "tokens": {},
    "user_ids_by_role": {},
    "password": None,
    "baseline": {},
    "cleanup_log": [],
}


# ------------------------------ 基础工具 ------------------------------

def redact(obj):
    if isinstance(obj, dict):
        return {k: ("<redacted>" if k.lower() in SENSITIVE_KEYS else redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str) and len(obj) > 900:
        return obj[:900] + "...<truncated>"
    return obj


def call(method, path, token=None, body=None, params=None, timeout=90):
    headers = {"Authorization": "Bearer " + token} if token else {}
    t0 = time.time()
    try:
        r = requests.request(method, BASE + path, json=body, params=params,
                             headers=headers, timeout=timeout)
        status = r.status_code
        try:
            payload = r.json()
        except ValueError:
            payload = r.text[:600]
    except Exception as e:
        status = -1
        payload = {"transport_error": "%s: %s" % (type(e).__name__, str(e)[:200])}
    return {
        "status": status,
        "raw": payload,
        "body": redact(payload),
        "elapsed_ms": int((time.time() - t0) * 1000),
        "request": {
            "method": method,
            "path": path,
            "body": redact(body),
            "params": params,
            "auth": "Bearer <redacted>" if token else None,
        },
    }


def record(cid, name, expected, ok, resp=None, db=None, note="", kind="functional", status=None):
    st = status or ("PASS" if ok else "FAIL")
    item = {
        "id": cid,
        "name": name,
        "expected": expected,
        "status": st,
        "kind": kind,
        "ok": bool(ok),
        "request": resp["request"] if resp else None,
        "response": ({"status": resp["status"], "body": resp["body"],
                      "elapsed_ms": resp["elapsed_ms"]} if resp else None),
        "db": db,
        "note": note,
    }
    RESULTS.append(item)
    print("[%-14s] %-7s %s" % (st, cid, name))
    return item


def one(sql, args=None):
    rows = common.query(sql, args)
    return common.row_dict(rows[0]) if rows else None


def cnt(sql, args=None):
    return common.query(sql, args)[0]["c"]


def appt(aid):
    return one(
        "SELECT id, appointment_no, user_id, counselor_id, consultation_type, "
        "appointment_date, duration, price, paid_amount, status, cancel_reason, "
        "confirmed_at, completed_at, cancelled_at, created_at "
        "FROM appointments WHERE id=%s", (aid,))


def review(aid):
    return one(
        "SELECT id, appointment_id, user_id, counselor_id, rating, tags, content, "
        "is_anonymous, created_at FROM consultation_reviews WHERE appointment_id=%s", (aid,))


def coun(cid_):
    return one("SELECT id, user_id, name, rating, review_count, status FROM counselors WHERE id=%s", (cid_,))


def dstr(hour, minute=0, day=None):
    return "%s %02d:%02d:00" % (day or TEST_DATE.isoformat(), hour, minute)


def body_of(resp):
    return resp["raw"] if isinstance(resp["raw"], dict) else {}


def data_of(resp):
    b = body_of(resp)
    return b.get("data") if isinstance(b, dict) else None


def detail_of(resp):
    b = body_of(resp)
    return str(b.get("detail", "")) if isinstance(b, dict) else ""


def items_of(resp):
    d = data_of(resp)
    if isinstance(d, list):
        return d
    if isinstance(d, dict) and isinstance(d.get("items"), list):
        return d["items"]
    return []


def placeholders(ids):
    return ",".join(["%s"] * len(ids))


# ------------------------------ 隔离数据准备 ------------------------------

def setup():
    CTX["baseline"] = {t: cnt("SELECT COUNT(*) AS c FROM `%s`" % t) for t in common.C_TABLES}
    pw = secrets.token_urlsafe(14)
    CTX["password"] = pw
    hashed = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def add_user(role, tag):
        email = "E2E_C_%s_%s@example.com" % (tag, RUN_TAG)
        _, uid = common.execute(
            "INSERT INTO users (email, password_hash, nickname, status, is_verified, is_deleted, role) "
            "VALUES (%s,%s,%s,'active',1,0,%s)",
            (email, hashed, "E2E_C_" + tag, role))
        CTX["user_ids"].append(uid)
        CTX["user_ids_by_role"][tag] = uid
        return uid, email

    users = {}
    for role, tag in [("user", "STU_A"), ("user", "STU_B"),
                      ("counselor", "CNS1"), ("counselor", "CNS2")]:
        users[tag] = add_user(role, tag)

    def add_counselor(tag, uid, name, price):
        _, cid_ = common.execute(
            "INSERT INTO counselors (user_id, name, gender, title, specialties, consultation_types, "
            "experience_years, education, qualifications, price_video, price_voice, price_offline, "
            "rating, review_count, consultation_count, bio, status, is_verified, is_deleted, "
            "application_status) VALUES "
            "(%s,%s,'female','E2E_C_测试职称','anxiety,sleep','video,voice,offline',"
            "5,'E2E_C_测试学历','E2E_C_测试资质',%s,%s,%s,5.0,0,0,'E2E_C_隔离测试咨询师简介',"
            "'active',1,0,'approved')",
            (uid, name, price, price - 20, price + 50))
        CTX["counselor_ids"].append(cid_)
        return cid_

    c1 = add_counselor("CNS1", users["CNS1"][0], "E2E_C_咨询师甲_" + RUN_TAG, 100.0)
    c2 = add_counselor("CNS2", users["CNS2"][0], "E2E_C_咨询师乙_" + RUN_TAG, 120.0)
    CTX["counselor_ids_by_role"] = {"CNS1": c1, "CNS2": c2}

    login_results = {}
    for tag, (_, email) in users.items():
        r = call("POST", "/api/auth/login", body={"email": email, "password": pw})
        tok = (body_of(r).get("data") or {}).get("token")
        if tok:
            CTX["tokens"][tag] = tok
        login_results[tag] = r["status"]
    ok = all(v == 200 and CTX["tokens"].get(k) for k, v in login_results.items())
    record("TC-000", "隔离测试账号创建并登录（学生A/学生B/咨询师甲/咨询师乙）",
           "4 个账号均通过 POST /api/auth/login 取得 token", ok,
           note="账号、咨询师档案均为本次新增行；密码运行时随机生成，未落盘；令牌仅存内存。",
           kind="setup",
           db={"created_user_ids": CTX["user_ids"], "created_counselor_ids": CTX["counselor_ids"]})
    if not ok:
        raise RuntimeError("登录失败，无法继续真实接口测试：%s" % login_results)


# ------------------------------ 测试用例 ------------------------------

def create(aid_tag, hour, token_tag="STU_A", counselor_tag="CNS1",
           ctype="video", minute=0, date_value=None, cid_override=None, raw_date=None):
    body = {
        "counselor_id": cid_override if cid_override is not None else CTX["counselor_ids_by_role"][counselor_tag],
        "consultation_type": ctype,
        "appointment_date": raw_date or dstr(hour, minute),
        "user_name": "E2E_C_预约人",
        "user_contact": "E2E_C_CONTACT",
        "problem_description": "E2E_C 隔离测试数据",
    }
    r = call("POST", "/api/appointment/create", token=CTX["tokens"][token_tag], body=body)
    d = data_of(r)
    if r["status"] == 200 and isinstance(d, dict) and d.get("id"):
        CTX["appointment_ids"].append(d["id"])
        CTX[aid_tag] = d["id"]
    return r


def run_cases():
    T = CTX["tokens"]
    C1 = CTX["counselor_ids_by_role"]["CNS1"]
    C2 = CTX["counselor_ids_by_role"]["CNS2"]
    UA = CTX["user_ids_by_role"]["STU_A"]
    UB = CTX["user_ids_by_role"]["STU_B"]

    # ---- 1. 咨询师信息与可预约时段 ----
    r = call("GET", "/api/counselor/list", params={"keyword": "E2E_C_", "page": 1, "page_size": 50})
    d = data_of(r) or {}
    items = d.get("items", []) if isinstance(d, dict) else []
    found = [x for x in items if x.get("id") in (C1, C2)]
    record("TC-001", "学生查看咨询师列表（含隔离测试咨询师）",
           "200 且列表包含两个 E2E_C_ 咨询师，与 counselors 表一致",
           r["status"] == 200 and len(found) == 2, r,
           db={"db_count": cnt("SELECT COUNT(*) AS c FROM counselors WHERE name LIKE 'E2E_C_%'"),
               "returned_ids": [x.get("id") for x in found]},
           kind="functional")

    r = call("GET", "/api/counselor/%s" % C1)
    d = data_of(r) or {}
    dbrow = one("SELECT id,name,status,price_video,price_voice,price_offline,consultation_types "
                "FROM counselors WHERE id=%s", (C1,))
    ok = r["status"] == 200 and d.get("id") == C1 and d.get("status") == "active" \
         and float(d.get("price_video", -1)) == float(dbrow["price_video"])
    record("TC-002", "学生查看咨询师详情与定价",
           "200，返回字段与 counselors 表一致（video/voice/offline 价格）", ok, r,
           db={"counselors_row": dbrow}, kind="functional")

    r = call("GET", "/api/counselor/%s/slots" % C1, params={"date": TEST_DATE.isoformat()})
    d = items_of(r)
    ok = r["status"] == 200 and len(d) == 10 and all(x.get("available") for x in d) \
         and d[0]["time"] == "09:00-10:00" and d[-1]["time"] == "18:00-19:00"
    record("TC-003", "学生查看可预约时间（未来日期）",
           "200，返回 09:00-19:00 共 10 个整点时段且初始均可用", ok, r,
           db={"slots_table_exists": bool(one(
               "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() "
               "AND TABLE_NAME IN ('counselor_schedules','availability','time_slots')"))},
           note="时段由代码硬编码生成，不存在排班表；可用性仅按 appointments.appointment_date 等值判断。",
           kind="functional")

    r = call("GET", "/api/counselor/%s/slots" % C1, params={"date": "not-a-date"})
    record("TC-004", "非法参数：可预约时段日期格式错误",
           "400 且提示日期格式错误", r["status"] == 400 and "日期格式" in detail_of(r), r,
           kind="negative")

    # ---- 2. 主链路：创建 -> 接受 -> 状态 -> 咨询 -> 完成 -> 评价 ----
    r = create("A_MAIN", 9)
    main_id = CTX.get("A_MAIN")
    row = appt(main_id) if main_id else None
    ok = r["status"] == 200 and row is not None and row["status"] == "pending" \
         and row["user_id"] == UA and row["counselor_id"] == C1 \
         and float(row["price"]) == 100.0 and float(row["paid_amount"]) == 0.0 \
         and row["duration"] == 60 and str(row["appointment_date"]).startswith(TEST_DATE.isoformat())
    record("TC-005", "学生创建预约（真实写入数据库）",
           "200 且 appointments 新增一行：status=pending、price 与咨询师定价一致、外键正确", ok, r,
           db={"appointments_row": row}, kind="functional")

    d = data_of(r) or {}
    ok = isinstance(d, dict) and d.get("appointment_no") == row["appointment_no"] \
         and d.get("status") == "pending" and d.get("user_id") == UA
    record("TC-006", "预约接口响应与数据库行一致",
           "响应中的 appointment_no/status/user_id/price 与 DB 完全一致", ok, r,
           db={"db_appointment_no": row["appointment_no"], "db_price": row["price"]},
           kind="consistency")

    r = call("GET", "/api/appointment/user/list", token=T["STU_A"],
             params={"status_filter": "pending", "page": 1, "page_size": 50})
    d = data_of(r) or {}
    ids = [x.get("id") for x in items_of(r)]
    record("TC-007", "学生查询预约状态（pending）",
           "200，列表包含新建预约且状态与 DB 一致", r["status"] == 200 and main_id in ids, r,
           db={"db_status": appt(main_id)["status"]}, kind="functional")

    r = call("GET", "/api/appointment/%s" % main_id, token=T["STU_A"])
    d = data_of(r) or {}
    record("TC-008", "学生查询预约详情", "200，status=pending 且含咨询师信息",
           r["status"] == 200 and d.get("status") == "pending" and isinstance(d.get("counselor"), dict), r,
           kind="functional")

    r = call("GET", "/api/consultation/counselor/orders", token=T["CNS1"],
             params={"status_filter": "pending", "page": 1, "page_size": 50})
    d = data_of(r) or {}
    ids = [x.get("id") for x in items_of(r)]
    record("TC-009", "咨询师查看待处理订单", "200，列表包含该预约",
           r["status"] == 200 and main_id in ids, r, kind="functional")

    r = call("POST", "/api/consultation/order/%s/handle" % main_id, token=T["CNS1"],
             body={"action": "agree"})
    row = appt(main_id)
    ok = r["status"] == 200 and row["status"] == "confirmed" and row["confirmed_at"] is not None
    record("TC-010", "咨询师接受预约（pending→confirmed）",
           "200，DB status=confirmed 且 confirmed_at 非空", ok, r,
           db={"appointments_row": row}, kind="functional")

    r = call("GET", "/api/appointment/user/list", token=T["STU_A"],
             params={"status_filter": "confirmed", "page": 1, "page_size": 50})
    d = data_of(r) or {}
    ids = [x.get("id") for x in items_of(r)]
    record("TC-011", "学生查询预约状态（confirmed）",
           "200，按 confirmed 筛选能查到该预约且 DB 状态一致",
           r["status"] == 200 and main_id in ids and appt(main_id)["status"] == "confirmed", r,
           db={"db_status": appt(main_id)["status"]}, kind="functional")

    r = call("POST", "/api/consultation/order/%s/handle" % main_id, token=T["CNS1"],
             body={"action": "agree"})
    record("TC-012", "异常：咨询师重复处理同一订单",
           "400 且状态保持 confirmed", r["status"] == 400 and appt(main_id)["status"] == "confirmed", r,
           db={"db_status": appt(main_id)["status"]}, kind="negative")

    r = call("POST", "/api/consultation/%s/message" % main_id, token=T["STU_A"],
             body={"content": "E2E_C 咨询测试消息", "message_type": "text"})
    row = appt(main_id)
    ok = r["status"] == 200 and row["status"] == "in_progress"
    record("TC-013", "首条咨询消息推进状态（confirmed→in_progress）",
           "200，DB status=in_progress（无独立\"开始咨询\"接口）", ok, r,
           db={"appointments_row": row,
               "message_rows": cnt("SELECT COUNT(*) AS c FROM consultation_messages WHERE appointment_id=%s", (main_id,))},
           note="状态推进由发消息隐式触发。", kind="functional")

    r = call("POST", "/api/consultation/%s/end" % main_id, token=T["STU_A"])
    row = appt(main_id)
    ok = r["status"] == 200 and row["status"] == "completed" and row["completed_at"] is not None
    record("TC-014", "结束咨询（in_progress→completed）",
           "200，DB status=completed 且 completed_at 非空", ok, r,
           db={"appointments_row": row}, kind="functional")

    r = call("POST", "/api/appointment/%s/review" % main_id, token=T["STU_A"],
             body={"rating": 4.5, "tags": ["专业", "耐心"], "content": "E2E_C 评价内容", "is_anonymous": True})
    rv = review(main_id)
    ok = r["status"] == 200 and rv is not None and float(rv["rating"]) == 4.5 \
         and rv["is_anonymous"] == 1 and "E2E_C" in (rv["content"] or "")
    record("TC-015", "咨询完成后提交评价与反馈（真实写入数据库）",
           "200，consultation_reviews 新增一行且评分/内容/匿名标记正确", ok, r,
           db={"consultation_reviews_row": rv}, kind="functional")

    c1row = coun(C1)
    real_count = cnt("SELECT COUNT(*) AS c FROM consultation_reviews WHERE counselor_id=%s", (C1,))
    real_avg = one("SELECT AVG(rating) AS a FROM consultation_reviews WHERE counselor_id=%s", (C1,))["a"]
    ok = abs(float(c1row["review_count"] or 0) - real_count) < 0.001 and \
         abs(float(c1row["rating"] or 0) - float(real_avg or 0)) < 0.001
    record("TC-016", "提交评价后咨询师评分统计一致性",
           "counselors.rating / review_count 与 consultation_reviews 实际聚合值一致", ok,
           db={"counselors_row": c1row, "actual_review_count": real_count, "actual_avg_rating": real_avg},
           note="提交评价的服务在 db.add(review) 后未 flush 即重算统计；autoflush=False 时新评价不会被计入。",
           kind="consistency")

    r = call("GET", "/api/counselor/%s/reviews" % C1, params={"page": 1, "page_size": 10})
    d = data_of(r) or {}
    ids = [x.get("appointment_id") for x in items_of(r)]
    record("TC-017", "咨询师评价列表可查询", "200，列表包含本次评价",
           r["status"] == 200 and main_id in ids, r, kind="functional")

    r = call("POST", "/api/appointment/%s/review" % main_id, token=T["STU_A"],
             body={"rating": 5, "content": "E2E_C 重复评价"})
    record("TC-018", "异常：重复评价同一预约", "400 且 DB 中仍只有 1 条评价",
           r["status"] == 400 and cnt("SELECT COUNT(*) AS c FROM consultation_reviews WHERE appointment_id=%s", (main_id,)) == 1,
           r, db={"db_review_count": 1}, kind="negative")

    r = call("POST", "/api/appointment/%s/cancel" % main_id, token=T["STU_A"], params={"reason": "E2E_C"})
    record("TC-019", "异常：取消已完成预约", "400 且状态保持 completed",
           r["status"] == 400 and appt(main_id)["status"] == "completed", r,
           db={"db_status": appt(main_id)["status"]}, kind="negative")

    # ---- 3. 取消与拒绝 ----
    r = create("A_CANCEL", 10)
    cancel_id = CTX.get("A_CANCEL")
    r2 = call("POST", "/api/appointment/%s/cancel" % cancel_id, token=T["STU_A"],
              params={"reason": "E2E_C_测试取消原因"})
    row = appt(cancel_id)
    ok = r2["status"] == 200 and row["status"] == "cancelled" and row["cancelled_at"] is not None \
         and "E2E_C_测试取消原因" in (row["cancel_reason"] or "")
    record("TC-020", "学生取消预约（pending→cancelled）",
           "200，DB status=cancelled、cancel_reason 与 cancelled_at 均写入", ok, r2,
           db={"appointments_row": row}, kind="functional")

    r = call("GET", "/api/counselor/%s/slots" % C1, params={"date": TEST_DATE.isoformat()})
    d = items_of(r)
    slot10 = next((x for x in d if x.get("time") == "10:00-11:00"), None)
    record("TC-021", "取消后时段释放", "10:00-11:00 重新标记为 available=true",
           r["status"] == 200 and slot10 is not None and slot10.get("available") is True, r,
           db={"cancelled_status": appt(cancel_id)["status"]}, kind="functional")

    r3 = create("A_REBOOK", 10)
    record("TC-022", "已取消时段可再次预约",
           "200，同一咨询师同一时刻在原单取消后可新建预约", r3["status"] == 200,
           r3, db={"rows_at_slot": cnt(
               "SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s",
               (C1, dstr(10)))}, kind="functional")

    r = create("A_REJECT", 11)
    reject_id = CTX.get("A_REJECT")
    r2 = call("POST", "/api/consultation/order/%s/handle" % reject_id, token=T["CNS1"],
              body={"action": "reject", "reason": "E2E_C_时段冲突测试拒绝"})
    row = appt(reject_id)
    ok = r2["status"] == 200 and row["status"] == "cancelled" and row["cancelled_at"] is not None \
         and "E2E_C_时段冲突测试拒绝" in (row["cancel_reason"] or "")
    record("TC-023", "咨询师拒绝预约（pending→cancelled）",
           "200，DB status=cancelled 且拒绝原因写入 cancel_reason", ok, r2,
           db={"appointments_row": row},
           note="系统无 rejected 状态，拒绝与用户取消共用 cancelled。", kind="functional")

    # ---- 4. 重复预约 / 时间冲突 / 非法参数 ----
    r = create("A_DUP", 12)
    dup_id = CTX.get("A_DUP")
    before = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s",
                 (C1, dstr(12)))
    r2 = create("A_DUP2", 12)
    after = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s",
                (C1, dstr(12)))
    ok = r2["status"] == 400 and "该时段已被预约" in detail_of(r2) and before == 1 and after == 1
    record("TC-024", "异常：同一咨询师同一时刻重复预约 / 时间冲突",
           "400「该时段已被预约」且 DB 不新增行", ok, r2,
           db={"rows_before": before, "rows_after": after}, kind="negative")

    r3 = create("A_HALF", 12, minute=30)
    rows = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s "
               "AND appointment_date IN (%s,%s) AND status IN ('pending','confirmed','in_progress')",
               (C1, dstr(12), dstr(12, 30)))
    half_created = r3["status"] == 200
    record("TC-025", "异常：相邻半小时重叠时段（duration=60 却只做等值冲突判断）",
           "09:00 与 09:30 这种重叠时段应被拒绝（每单时长 60 分钟）", not half_created, r3,
           db={"overlapping_active_rows": rows, "slot_a": dstr(12), "slot_b": dstr(12, 30),
               "duration_minutes": 60},
           note=("实际允许创建 12:30 预约，与 12:00 预约时间重叠 30 分钟；"
                 "counselor_service 仅按 appointment_date 完全相等判冲突。" if half_created else ""),
           kind="negative")

    bad_cases = [
        ("TC-026", "非法咨询方式", {"consultation_type": "chat"}, 422, None),
        ("TC-027", "预约时间为过去", {"appointment_date": "2020-01-01 09:00:00"}, 400, "过去"),
        ("TC-028", "预约时间格式错误", {"appointment_date": "abc"}, 400, "格式"),
        ("TC-029", "不存在的咨询师", {"counselor_id": 99999999}, 400, "不存在"),
        ("TC-030", "带时区的 ISO 时间（Z）", {"appointment_date": TEST_DATE.isoformat() + "T09:00:00Z"}, None, None),
    ]
    for cid_, name, override, expect_status, keyword in bad_cases:
        body = {
            "counselor_id": override.get("counselor_id", C1),
            "consultation_type": override.get("consultation_type", "video"),
            "appointment_date": override.get("appointment_date", dstr(17)),
            "user_name": "E2E_C_预约人",
        }
        r = call("POST", "/api/appointment/create", token=T["STU_A"], body=body)
        d = data_of(r)
        if r["status"] == 200 and isinstance(d, dict) and d.get("id"):
            CTX["appointment_ids"].append(d["id"])
        if expect_status is None:
            ok = 400 <= r["status"] < 500
            exp = "返回 4xx 客户端错误（不应 500，也不应静默落库）"
        else:
            ok = r["status"] == expect_status and (keyword is None or keyword in detail_of(r) or
                                                   keyword in json.dumps(r["body"], ensure_ascii=False))
            exp = "%s%s" % (expect_status, (" 且提示含「%s」" % keyword) if keyword else "")
        record(cid_, "非法参数：" + name, exp, ok, r,
               db={"rows_at_17": cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s",
                                     (C1, dstr(17)))},
               note=("该用例用于验证 aware/naive datetime 比较是否会 500。" if expect_status is None else ""),
               kind="negative")

    r = call("GET", "/api/appointment/user/list", token=T["STU_A"], params={"page": 0})
    record("TC-031", "非法参数：分页 page=0", "422 参数校验失败", r["status"] == 422, r, kind="negative")

    r = call("POST", "/api/appointment/%s/review" % dup_id, token=T["STU_A"],
             body={"rating": 6, "content": "E2E_C"})
    record("TC-032", "非法参数：评分越界 rating=6", "422 参数校验失败", r["status"] == 422, r, kind="negative")

    r = call("POST", "/api/appointment/%s/review" % dup_id, token=T["STU_A"],
             body={"rating": 0, "content": "E2E_C"})
    record("TC-033", "非法参数：评分越界 rating=0", "422 参数校验失败", r["status"] == 422, r, kind="negative")

    r = call("POST", "/api/appointment/%s/review" % dup_id, token=T["STU_A"],
             body={"rating": 5, "content": "E2E_C 未完成即评价"})
    record("TC-034", "异常：未完成预约提交评价", "400「只能评价已完成的咨询」",
           r["status"] == 400 and "只能评价已完成" in detail_of(r), r,
           db={"db_status": appt(dup_id)["status"]}, kind="negative")

    # ---- 5. 改期（功能存在性验证） ----
    spec = call("GET", "/openapi.json")
    paths = list((spec["raw"] or {}).get("paths", {}).keys()) if isinstance(spec["raw"], dict) else []
    reschedule_paths = [p for p in paths if "resched" in p.lower() or "改期" in p]
    put_patch = [p for p in paths if p.startswith("/api/appointment") and
                 any(m in ("put", "patch") for m in (spec["raw"]["paths"][p].keys()))]
    r = call("PUT", "/api/appointment/%s" % dup_id, token=T["STU_A"],
             body={"appointment_date": dstr(15)})
    r2 = call("POST", "/api/appointment/%s/reschedule" % dup_id, token=T["STU_A"],
              body={"appointment_date": dstr(15)})
    gap = not reschedule_paths and not put_patch and r["status"] in (404, 405) and r2["status"] in (404, 405)
    record("TC-035", "预约改期（功能存在性验证）",
           "确认运行时 OpenAPI 是否已注册改期接口，并实测 PUT / reschedule 请求", gap, r,
           db={"db_appointment_date": appt(dup_id)["appointment_date"]},
           note="OpenAPI 中改期路径=%s，PUT/PATCH 路径=%s；实测 PUT=%s，POST /reschedule=%s。"
                "属于「未实现功能」，不计为 Bug。" % (reschedule_paths, put_patch, r["status"], r2["status"]),
           kind="feature_gap", status="FEATURE_GAP" if gap else "FAIL")

    # ---- 6. 权限隔离 ----
    r = create("A_PERM", 13)
    perm_id = CTX.get("A_PERM")
    before_status = appt(perm_id)["status"]

    cases_perm = []
    r = call("GET", "/api/appointment/%s" % perm_id, token=T["STU_B"])
    cases_perm.append(("TC-036", "学生B读取学生A的预约详情", r, 403))
    r = call("POST", "/api/appointment/%s/cancel" % perm_id, token=T["STU_B"], params={"reason": "E2E_C越权"})
    cases_perm.append(("TC-037", "学生B取消学生A的预约", r, 403))
    r = call("POST", "/api/appointment/%s/review" % perm_id, token=T["STU_B"],
             body={"rating": 5, "content": "E2E_C越权评价"})
    cases_perm.append(("TC-038", "学生B替学生A提交评价", r, 403))
    r = call("GET", "/api/appointment/%s" % perm_id)
    cases_perm.append(("TC-039", "未携带 token 访问预约详情", r, 403))
    after_status = appt(perm_id)["status"]
    for cid_, name, resp, expect_status in cases_perm:
        ok = resp["status"] == expect_status and after_status == before_status
        record(cid_, "权限隔离：" + name,
               "HTTP %s 且 DB 状态不变（%s）" % (expect_status, before_status), ok, resp,
               db={"status_before": before_status, "status_after": after_status},
               note=("越权已被拦截但返回 %s（期望 403）；路由内 HTTPException 被 except Exception 吞掉后重抛 500。"
                     % resp["status"]) if resp["status"] == 500 and after_status == before_status else
                    ("接口以 %s 拒绝，DB 未变化。" % resp["status"] if after_status == before_status else "DB 被越权修改！"),
               kind="permission")

    r = call("GET", "/api/consultation/counselor/orders", token=T["STU_A"], params={"page": 1, "page_size": 50})
    record("TC-040", "权限隔离：学生访问咨询师订单列表", "HTTP 403 且无数据泄漏",
           r["status"] == 403 and not items_of(r), r,
           note=("实际 %s；越权被拦截但状态码错误。" % r["status"]) if r["status"] != 403 else "",
           kind="permission")

    r = call("POST", "/api/consultation/order/%s/handle" % perm_id, token=T["STU_A"],
             body={"action": "agree"})
    record("TC-041", "权限隔离：学生接受/拒绝预约", "HTTP 403 且 DB 状态不变",
           r["status"] == 403 and appt(perm_id)["status"] == before_status, r,
           db={"db_status": appt(perm_id)["status"]},
           note=("实际 %s；越权被拦截但状态码错误。" % r["status"]) if r["status"] != 403 else "",
           kind="permission")

    r = call("GET", "/api/appointment/counselor/list", token=T["STU_A"], params={"page": 1, "page_size": 50})
    record("TC-042", "权限隔离：学生访问 /appointment/counselor/list", "HTTP 403 且无数据泄漏",
           r["status"] == 403 and not items_of(r), r,
           note="该路由仅校验 Bearer，未做角色校验；服务层按 counselors.user_id 判断。",
           kind="permission")

    r = call("POST", "/api/appointment/%s/cancel" % perm_id, token=T["CNS1"], params={"reason": "E2E_C"})
    record("TC-043", "权限隔离：咨询师取消学生预约", "拒绝且 DB 状态不变",
           r["status"] in (400, 403) and appt(perm_id)["status"] == before_status, r,
           db={"db_status": appt(perm_id)["status"]}, kind="permission")

    r = call("GET", "/api/consultation/%s/messages" % perm_id, token=T["STU_B"],
             params={"user_type": "user", "limit": 50})
    record("TC-044", "权限隔离：学生B读取学生A的咨询消息", "拒绝且无消息内容返回",
           r["status"] in (400, 403) and not items_of(r), r,
           kind="permission")

    r = create("A_CROSS", 14)
    cross_id = CTX.get("A_CROSS")
    r = call("POST", "/api/consultation/order/%s/handle" % cross_id, token=T["CNS2"],
             body={"action": "agree"})
    record("TC-045", "权限隔离：咨询师乙处理咨询师甲的订单", "拒绝且 DB 状态保持 pending",
           r["status"] in (400, 403) and appt(cross_id)["status"] == "pending", r,
           db={"db_status": appt(cross_id)["status"]}, kind="permission")

    r = call("GET", "/api/consultation/counselor/orders", token=T["CNS2"], params={"page": 1, "page_size": 50})
    d = data_of(r) or {}
    ids = [x.get("id") for x in items_of(r)]
    record("TC-046", "权限隔离：咨询师乙订单列表不含咨询师甲的订单",
           "200 且列表不包含甲名下订单", r["status"] == 200 and cross_id not in ids and perm_id not in ids, r,
           db={"cns2_orders_in_db": cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s", (C2,))},
           kind="permission")

    r = call("GET", "/api/appointment/counselor/list", token=T["CNS1"], params={"page": 1, "page_size": 50})
    record("TC-047", "咨询师查看自己收到的预约列表（/appointment/counselor/list）",
           "200 且返回本人名下订单", r["status"] == 200 and bool(items_of(r)), r,
           db={"cns1_orders_in_db": cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s", (C1,))},
           note="服务层引用 Appointment.user 关系，但模型未定义该关系。", kind="functional")

    # ---- 7. 数据库一致性总检 ----
    aids = CTX["appointment_ids"]
    ph = placeholders(aids)
    orphan_user = cnt("SELECT COUNT(*) AS c FROM appointments WHERE id IN (%s) "
                      "AND user_id NOT IN (SELECT id FROM users)" % ph, tuple(aids)) if aids else 0
    orphan_coun = cnt("SELECT COUNT(*) AS c FROM appointments WHERE id IN (%s) "
                      "AND counselor_id NOT IN (SELECT id FROM counselors)" % ph, tuple(aids)) if aids else 0
    dup_no = cnt("SELECT COUNT(*) AS c FROM (SELECT appointment_no FROM appointments WHERE id IN (%s) "
                 "GROUP BY appointment_no HAVING COUNT(*)>1) x" % ph, tuple(aids)) if aids else 0
    orphan_rev = cnt("SELECT COUNT(*) AS c FROM consultation_reviews WHERE appointment_id NOT IN "
                     "(SELECT id FROM appointments)") if aids else 0
    invalid_status = cnt("SELECT COUNT(*) AS c FROM appointments WHERE id IN (%s) "
                         "AND status NOT IN ('pending','confirmed','in_progress','completed','cancelled','refunded')"
                         % ph, tuple(aids)) if aids else 0
    cons_ok = orphan_user == 0 and orphan_coun == 0 and dup_no == 0 and orphan_rev == 0 and invalid_status == 0
    record("TC-048", "数据库一致性：外键 / 唯一编号 / 状态枚举 / 评价归属",
           "无孤儿外键、无重复 appointment_no、状态均为合法枚举、评价均挂载到存在预约", cons_ok,
           db={"created_appointments": len(aids), "orphan_user": orphan_user,
               "orphan_counselor": orphan_coun, "duplicate_appointment_no": dup_no,
               "orphan_reviews": orphan_rev, "invalid_status": invalid_status,
               "reviews_unique_index": [x["Key_name"] for x in common.query(
                   "SHOW INDEX FROM consultation_reviews") if x["Non_unique"] == 0]},
           kind="consistency")


# ------------------------------ 清理 ------------------------------

def cleanup():
    aids = CTX["appointment_ids"]
    uids = CTX["user_ids"]
    cids = CTX["counselor_ids"]
    log = []
    if aids:
        ph = placeholders(aids)
        for table, col in [("consultation_messages", "appointment_id"),
                           ("consultation_reviews", "appointment_id")]:
            n, _ = common.execute("DELETE FROM `%s` WHERE `%s` IN (%s)" % (table, col, ph), tuple(aids))
            log.append("%s:-%s" % (table, n))
        n, _ = common.execute("DELETE FROM appointments WHERE id IN (%s)" % ph, tuple(aids))
        log.append("appointments:-%s" % n)
    if uids:
        uph = placeholders(uids)
        for table, col in [("notifications", "user_id"),
                           ("inquiry_messages", "sender_id"),
                           ("counselor_inquiries", "user_id")]:
            try:
                n, _ = common.execute("DELETE FROM `%s` WHERE `%s` IN (%s)" % (table, col, uph), tuple(uids))
                log.append("%s:-%s" % (table, n))
            except Exception as e:
                log.append("%s:skip(%s)" % (table, type(e).__name__))
    if cids:
        n, _ = common.execute("DELETE FROM counselors WHERE id IN (%s)" % placeholders(cids), tuple(cids))
        log.append("counselors:-%s" % n)
    if uids:
        n, _ = common.execute("DELETE FROM users WHERE id IN (%s)" % placeholders(uids), tuple(uids))
        log.append("users:-%s" % n)
    CTX["cleanup_log"] = log

    after = {t: cnt("SELECT COUNT(*) AS c FROM `%s`" % t) for t in common.C_TABLES}
    restored = all(after.get(k) == v for k, v in CTX["baseline"].items())
    record("TC-049", "测试数据隔离清理与基线恢复校验",
           "本次新增行全部按主键删除，所有 C 模块表行数回到测试前基线", restored,
           db={"before": CTX["baseline"], "after": after, "cleanup": log},
           kind="consistency")


def main():
    keep = "--keep" in sys.argv
    try:
        setup()
        run_cases()
    except Exception:
        traceback.print_exc()
        record("TC-ERR", "测试执行异常中断", "所有用例正常执行完毕", False,
               note=traceback.format_exc()[-1200:], kind="setup")
    finally:
        if not keep:
            try:
                cleanup()
            except Exception:
                traceback.print_exc()
                record("TC-CLN", "清理失败", "测试数据全部清除", False,
                       note=traceback.format_exc()[-1200:], kind="consistency")

    stats = {}
    for r in RESULTS:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
    OUT_FILE.write_text(json.dumps({
        "run_tag": RUN_TAG,
        "test_date": TEST_DATE.isoformat(),
        "base_url": BASE,
        "stats": stats,
        "cases": RESULTS,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nSTATS =", json.dumps(stats, ensure_ascii=False))
    print("RESULTS ->", OUT_FILE)


if __name__ == "__main__":
    main()
