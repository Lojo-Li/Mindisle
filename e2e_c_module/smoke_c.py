"""C 模块冒烟验证（走 HTTP 接口，不直连数据库）。

用法：python smoke_c.py [BASE_URL]
默认 http://127.0.0.1:8000
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
results = []


def call(method, path, token=None, body=None, expect=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            payload = r.read().decode()
            code = r.status
    except urllib.error.HTTPError as e:
        payload = e.read().decode()
        code = e.code
    except Exception as e:
        return None, str(e), 0
    try:
        parsed = json.loads(payload) if payload else None
    except Exception:
        parsed = payload[:200]
    return parsed, payload, code


def case(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + ((" :: " + str(detail)[:180]) if detail else ""))


def login(email, password="123456"):
    p, _, c = call("POST", "/api/auth/login", body={"email": email, "password": password})
    if isinstance(p, dict):
        d = p.get("data") or {}
        return d.get("token")
    return None


print("BASE =", BASE)
print("\n[1] 登录")
user_tok = login("user@test.com")
case("用户登录 user@test.com", bool(user_tok), "token 前缀 " + (user_tok[:18] if user_tok else "无"))

cd_tok = login("consultant@test.com")
case("咨询师登录 consultant@test.com", bool(cd_tok))

# 找 counselor1 对应的 counselors.id
print("\n[2] 咨询师列表与时段")
p, raw, c = call("GET", "/api/counselor/list?page=1&page_size=50")
items = ((p or {}).get("data") or {}).get("items") or []
case("GET /api/counselor/list", c == 200 and len(items) > 0, "共 %d 个" % len(items))

target = None
for it in items:
    if it.get("user_id") == 1:
        target = it
        break
if not target and items:
    target = items[0]
cid = target["id"] if target else None
print("   目标咨询师 id=%s name=%s" % (cid, (target or {}).get("name")))

tomorrow = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
p, raw, c = call("GET", "/api/counselor/%s/slots?date=%s" % (cid, tomorrow))
slots = []
if isinstance(p, dict):
    d = p.get("data")
    slots = d if isinstance(d, list) else (d or {}).get("slots") or []
case("GET /api/counselor/%s/slots?date=%s" % (cid, tomorrow), c == 200, "时段数 %d" % len(slots))

print("\n[3] 创建预约")
appt_id = None
slot_time = slots[0] if slots else None
if isinstance(slot_time, dict):
    slot_time = slot_time.get("time") or slot_time.get("start_time") or slot_time.get("value")
# slots 返回形如 "09:00-10:00"，取起始时间
if isinstance(slot_time, str) and "-" in slot_time:
    slot_time = slot_time.split("-")[0]
body = {
    "counselor_id": cid,
    "appointment_date": "%sT%s:00" % (tomorrow, slot_time) if slot_time else "%sT10:00:00" % tomorrow,
    "consultation_type": "video",
    "notes": "C 模块冒烟测试",
}
p, raw, c = call("POST", "/api/appointment/create", token=user_tok, body=body)
case("POST /api/appointment/create", c in (200, 201), "HTTP %s %s" % (c, str(p)[:150]))
if isinstance(p, dict):
    d = p.get("data") or {}
    appt_id = d.get("id") or d.get("appointment_id")
print("   预约 id =", appt_id)

print("\n[4] 用户预约列表 / 详情")
p, raw, c = call("GET", "/api/appointment/user/list", token=user_tok)
case("GET /api/appointment/user/list", c == 200, "HTTP %s" % c)
if appt_id:
    p, raw, c = call("GET", "/api/appointment/%s" % appt_id, token=user_tok)
    case("GET /api/appointment/%s" % appt_id, c == 200, "HTTP %s" % c)

print("\n[5] 重复预约同一时段（应 400 冲突）")
if slot_time:
    p, raw, c = call("POST", "/api/appointment/create", token=user_tok, body=body)
    case("同时间段重复预约被拒", c == 400, "HTTP %s %s" % (c, str(p)[:120]))

print("\n[6] 咨询师订单列表与处理")
p, raw, c = call("GET", "/api/consultation/counselor/orders", token=cd_tok)
case("GET /api/consultation/counselor/orders", c == 200, "HTTP %s" % c)
if appt_id:
    p, raw, c = call("POST", "/api/consultation/order/%s/handle" % appt_id, token=cd_tok, body={"action": "agree"})
    case("POST /api/consultation/order/%s/handle (agree)" % appt_id, c == 200, "HTTP %s %s" % (c, str(p)[:120]))

print("\n[7] 越权校验")
p, raw, c = call("GET", "/api/consultation/counselor/orders", token=user_tok)
case("普通用户访问咨询师订单 → 403", c == 403, "HTTP %s" % c)
if appt_id:
    other_tok = login("student1@test.com")
    p, raw, c = call("GET", "/api/appointment/%s" % appt_id, token=other_tok)
    case("其他用户访问他人预约详情 → 403", c == 403, "HTTP %s" % c)
    p, raw, c = call("GET", "/api/appointment/%s" % appt_id, token=cd_tok)
    case("本单咨询师访问预约详情 → 200", c == 200, "HTTP %s" % c)
    p, raw, c = call("POST", "/api/appointment/%s/cancel" % appt_id, token=other_tok)
    case("其他用户取消他人预约 → 403", c == 403, "HTTP %s" % c)

print("\n[8] 取消预约")
if appt_id:
    p, raw, c = call("POST", "/api/appointment/%s/cancel?reason=%s" % (appt_id, urllib.parse.quote("冒烟测试取消")), token=user_tok)
    case("POST /api/appointment/%s/cancel" % appt_id, c == 200, "HTTP %s %s" % (c, str(p)[:120]))

print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
for n, ok, d in results:
    if not ok:
        print("  FAIL:", n, "::", str(d)[:200])
