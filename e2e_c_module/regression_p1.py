# -*- coding: utf-8 -*-
"""P1 专项回归测试（BUG-01 / BUG-02 / BUG-03）。

用法：
    python regression_p1.py --label before
    python regression_p1.py --label after

每次运行自行创建 E2E_P1_ 前缀的隔离数据、执行断言、按主键精确清理，
结果写入 regression_p1_<label>.json。密码与 token 仅存内存。
"""
import concurrent.futures
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
LABEL = "after"
if "--label" in sys.argv:
    LABEL = sys.argv[sys.argv.index("--label") + 1]
OUT = HERE / ("regression_p1_%s.json" % LABEL)

D0 = dt.date.today()
D1 = (D0 + dt.timedelta(days=3)).isoformat()   # 评价主流程
D2 = (D0 + dt.timedelta(days=4)).isoformat()   # 冲突 / 取消 / 拒绝
D3 = (D0 + dt.timedelta(days=5)).isoformat()   # slots 一致性
D4 = (D0 + dt.timedelta(days=6)).isoformat()   # 并发

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


def call(method, path, token=None, body=None, params=None, timeout=90):
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


def rec(cid, bug, name, expected, ok, resp=None, db=None, note=""):
    CASES.append({
        "id": cid, "bug": bug, "name": name, "expected": expected,
        "status": "PASS" if ok else "FAIL", "ok": bool(ok),
        "http": resp["status"] if resp else None,
        "response": resp["body"] if resp else None,
        "db": db, "note": note,
    })
    print("[%s] %-7s %-6s %s (HTTP %s)" % (
        "PASS" if ok else "FAIL", cid, bug, name, resp["status"] if resp else "-"))


def one(sql, args=None):
    rows = common.query(sql, args)
    return common.row_dict(rows[0]) if rows else None


def cnt(sql, args=None):
    return common.query(sql, args)[0]["c"]


def setup():
    CTX["baseline"] = {t: cnt("SELECT COUNT(*) AS c FROM `%s`" % t) for t in common.C_TABLES}
    pw = secrets.token_urlsafe(14)
    hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    tag = "E2E_P1_" + LABEL + "_" + time.strftime("%H%M%S")

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
        "VALUES (%s,%s,'female','E2E_P1_职称','anxiety,sleep','video,voice,offline',5,"
        "'E2E_P1_学历','E2E_P1_资质',100,80,150,5.0,0,0,'E2E_P1_简介','active',1,0,'approved')",
        (users["CNS1"][0], tag + "_咨询师"))
    CTX["counselor_ids"].append(cid_)
    CTX["counselor_id"] = cid_

    for key, (_, email) in users.items():
        r = call("POST", "/api/auth/login", body={"email": email, "password": pw})
        tok = (r["raw"].get("data") or {}).get("token")
        if tok:
            CTX["tokens"][key] = tok
    if len(CTX["tokens"]) != 3:
        raise RuntimeError("隔离账号登录失败，无法执行回归测试")


def create(date_str, hour, minute=0, token="STU_A", counselor=None, ctype="video"):
    body = {
        "counselor_id": counselor if counselor is not None else CTX["counselor_id"],
        "consultation_type": ctype,
        "appointment_date": "%s %02d:%02d:00" % (date_str, hour, minute),
        "user_name": "E2E_P1_预约人",
        "problem_description": "E2E_P1 回归测试",
    }
    r = call("POST", "/api/appointment/create", token=CTX["tokens"][token], body=body)
    d = data_of(r)
    if r["status"] == 200 and isinstance(d, dict) and d.get("id"):
        CTX["appointment_ids"].append(d["id"])
    return r, (d.get("id") if isinstance(d, dict) else None)


def finish(aid):
    """pending -> confirmed -> in_progress -> completed"""
    call("POST", "/api/consultation/order/%s/handle" % aid,
         token=CTX["tokens"]["CNS1"], body={"action": "agree"})
    call("POST", "/api/consultation/%s/message" % aid, token=CTX["tokens"]["STU_A"],
         body={"content": "E2E_P1 消息", "message_type": "text"})
    call("POST", "/api/consultation/%s/end" % aid, token=CTX["tokens"]["STU_A"])


def review(aid, rating, token="STU_A"):
    return call("POST", "/api/appointment/%s/review" % aid, token=CTX["tokens"][token],
                body={"rating": rating, "content": "E2E_P1 评价 %s" % rating,
                      "tags": ["E2E_P1"], "is_anonymous": True})


def coun_stats():
    return one("SELECT rating, review_count FROM counselors WHERE id=%s", (CTX["counselor_id"],))


def agg_stats():
    return one("SELECT COUNT(*) AS c, AVG(rating) AS a FROM consultation_reviews WHERE counselor_id=%s",
               (CTX["counselor_id"],))


def slots(date_str):
    r = call("GET", "/api/counselor/%s/slots" % CTX["counselor_id"], params={"date": date_str})
    return r, {x.get("time"): x.get("available") for x in items_of(r) if isinstance(x, dict)}


def run_cases():
    C1 = CTX["counselor_id"]

    # ---------- BUG-01 ----------
    r1, a1 = create(D1, 9)
    r2, a2 = create(D1, 10)
    finish(a1)
    finish(a2)
    r = call("GET", "/api/appointment/counselor/list", token=CTX["tokens"]["CNS1"],
             params={"page": 1, "page_size": 50})
    items = items_of(r)
    with_info = [x for x in items if isinstance(x.get("user_info"), dict)]
    db_user = one("SELECT id, nickname FROM users WHERE id=%s",
                  (CTX["user_ids"][0],)) if CTX["user_ids"] else None
    ok = r["status"] == 200 and len(items) >= 2 and len(with_info) >= 2 and \
         all(set(("id", "nickname", "email", "phone")).issubset(x["user_info"].keys()) for x in with_info)
    rec("P1-01", "BUG-01", "咨询师查看自己收到的预约列表",
        "200，返回名下订单且 user_info 结构完整（id/nickname/email/phone）", ok, r,
        db={"appointments_in_db": cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s", (C1,)),
            "items_returned": len(items), "items_with_user_info": len(with_info),
            "sample_user": db_user},
        note="修复前访问未定义的 Appointment.user 关系导致 500。")

    # ---------- BUG-02 ----------
    rv = review(a1, 4.5)
    s, a = coun_stats(), agg_stats()
    ok = rv["status"] == 200 and abs(float(s["rating"]) - float(a["a"])) < 0.001 and \
         int(s["review_count"]) == int(a["c"]) == 1
    rec("P1-02", "BUG-02", "首次评价后评分/评价数更新",
        "counselors.rating=4.5、review_count=1，与 consultation_reviews 聚合一致", ok, rv,
        db={"counselors": s, "aggregate": a},
        note="autoflush=False 下 db.add(review) 后未 flush，聚合查不到新评价。")

    rv = review(a2, 3.5)
    s, a = coun_stats(), agg_stats()
    ok = rv["status"] == 200 and abs(float(s["rating"]) - 4.0) < 0.001 and \
         int(s["review_count"]) == int(a["c"]) == 2
    rec("P1-03", "BUG-02", "第二条评价后统计累计更新",
        "counselors.rating=4.0、review_count=2", ok, rv,
        db={"counselors": s, "aggregate": a})

    # ---------- BUG-03：等值 / 重叠 / 反向重叠 / 相邻 ----------
    r, dup_base = create(D2, 12)
    before = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s "
                 "AND status IN ('pending','confirmed','in_progress')", (C1, D2 + " 12:00:00"))
    r, _ = create(D2, 12)
    after = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s AND appointment_date=%s "
                "AND status IN ('pending','confirmed','in_progress')", (C1, D2 + " 12:00:00"))
    rec("P1-04", "BUG-03", "同一时刻重复预约仍被拒绝（原有行为不回归）",
        "400「该时段已被预约」，DB 有效预约仍为 1 条",
        r["status"] == 400 and before == 1 and after == 1, r,
        db={"before": before, "after": after})

    r, half_id = create(D2, 12, 30)
    overlap = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s "
                  "AND appointment_date IN (%s,%s) AND status IN ('pending','confirmed','in_progress')",
                  (C1, D2 + " 12:00:00", D2 + " 12:30:00"))
    rec("P1-05", "BUG-03", "半小时重叠时段被拒绝（12:00 与 12:30）",
        "400，DB 不存在两条重叠的有效预约", r["status"] == 400 and overlap == 1, r,
        db={"overlapping_active_rows": overlap, "duration_minutes": 60},
        note="修复前仅做 appointment_date 完全相等判断，12:30 会被放行。")

    r, adj_id = create(D2, 13)
    rec("P1-06", "BUG-03", "首尾相接的相邻时段不应误判冲突（12:00 与 13:00）",
        "200，13:00 可正常预约", r["status"] == 200, r,
        db={"slot_a": D2 + " 12:00:00", "slot_b": D2 + " 13:00:00"},
        note="半开区间 [start, end) 判定，首尾相接不算重叠。")

    r, back_base = create(D2, 14, 30)
    r, back_try = create(D2, 14, 0)
    rec("P1-07", "BUG-03", "反向重叠被拒绝（已有 14:30，再约 14:00）",
        "400，新区间 [14:00,15:00) 与 [14:30,15:30) 重叠", r["status"] == 400, r,
        db={"existing": D2 + " 14:30:00", "attempted": D2 + " 14:00:00"})

    # ---------- BUG-03：取消 / 拒绝释放时段 ----------
    r, cancel_id = create(D2, 16)
    rc = call("POST", "/api/appointment/%s/cancel" % cancel_id,
              token=CTX["tokens"]["STU_A"], params={"reason": "E2E_P1"})
    r, rebook_id = create(D2, 16)
    row = one("SELECT status FROM appointments WHERE id=%s", (cancel_id,))
    rec("P1-08", "BUG-03", "取消状态释放时段，可重新预约",
        "cancel=200、重新预约=200，原单 status=cancelled",
        rc["status"] == 200 and r["status"] == 200 and row["status"] == "cancelled", r,
        db={"cancelled_status": row["status"]})

    r, reject_id = create(D2, 17)
    rr = call("POST", "/api/consultation/order/%s/handle" % reject_id,
              token=CTX["tokens"]["CNS1"], body={"action": "reject", "reason": "E2E_P1"})
    r, rebook2_id = create(D2, 17)
    row = one("SELECT status, cancel_reason FROM appointments WHERE id=%s", (reject_id,))
    rec("P1-09", "BUG-03", "咨询师拒绝（cancelled）释放时段，可重新预约",
        "reject=200、重新预约=200，原单 status=cancelled",
        rr["status"] == 200 and r["status"] == 200 and row["status"] == "cancelled", r,
        db={"rejected_status": row["status"]})

    # ---------- BUG-03：slots 与 create 使用同一冲突逻辑 ----------
    r, odd_id = create(D3, 17, 30)
    rs, smap = slots(D3)
    ok = r["status"] == 200 and rs["status"] == 200 and \
         smap.get("17:00-18:00") is False and smap.get("18:00-19:00") is False and \
         smap.get("09:00-10:00") is True
    rec("P1-10", "BUG-03", "非整点预约（17:30）同时占用 17:00 与 18:00 时段",
        "slots 中 17:00-18:00 / 18:00-19:00 均不可用，09:00-10:00 仍可用", ok, rs,
        db={"created_at": D3 + " 17:30:00", "duration_minutes": 60,
            "slot_map": {k: smap.get(k) for k in ("09:00-10:00", "17:00-18:00", "18:00-19:00")}},
        note="验证 /counselor/{id}/slots 与 /appointment/create 共用区间冲突判定。")

    # ---------- BUG-03：并发重叠预约 ----------
    def concurrent_create(hour, minute):
        body = {
            "counselor_id": C1,
            "consultation_type": "video",
            "appointment_date": "%s %02d:%02d:00" % (D4, hour, minute),
            "user_name": "E2E_P1_并发",
        }
        rr = call("POST", "/api/appointment/create", token=CTX["tokens"]["STU_A"], body=body)
        d = data_of(rr)
        if rr["status"] == 200 and isinstance(d, dict) and d.get("id"):
            CTX["appointment_ids"].append(d["id"])
        return rr["status"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(concurrent_create, 11, 0)
        f2 = pool.submit(concurrent_create, 11, 30)
        statuses = sorted([f1.result(), f2.result()])
    active = cnt("SELECT COUNT(*) AS c FROM appointments WHERE counselor_id=%s "
                 "AND appointment_date IN (%s,%s) AND status IN ('pending','confirmed','in_progress')",
                 (C1, D4 + " 11:00:00", D4 + " 11:30:00"))
    rec("P1-11", "BUG-03", "并发创建重叠时段（11:00 与 11:30）",
        "恰好 1 个 200、1 个 400，DB 仅 1 条有效预约",
        statuses == [200, 400] and active == 1, None,
        db={"http_statuses": statuses, "active_rows": active},
        note="两个线程同时提交请求；修复后由咨询师行锁串行化校验 + 区间冲突判定拦截。")


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
        rec("P1-ERR", "-", "回归套件执行", "所有用例正常执行", False,
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
            "dates": {"D1": D1, "D2": D2, "D3": D3, "D4": D4},
            "stats": stats, "cases": CASES, "cleanup": clean,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nLABEL=%s STATS=%s CLEANUP=%s" % (
            LABEL, stats, clean.get("baseline_restored", clean.get("cleanup_error"))))
        print("RESULTS ->", OUT)


if __name__ == "__main__":
    main()
