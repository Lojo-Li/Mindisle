"""验证「我的预约」页面依赖的接口链路：创建 → 列表 → 取消。"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000"


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode() or "null"), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode() or "null"), e.code


def login(email, pwd="123456"):
    d, _ = call("POST", "/api/auth/login", body={"email": email, "password": pwd})
    return (d or {}).get("data", {}).get("token")


tok = login("user@test.com")
print("1. 登录:", "OK" if tok else "FAIL")

# 取咨询师与时段
d, _ = call("GET", "/api/counselor/list?page=1&page_size=5", tok)
items = (d or {}).get("data", {}).get("items", [])
cid = items[0]["id"] if items else 1
cname = items[0]["name"] if items else "?"

tomorrow = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
d, _ = call("GET", "/api/counselor/%s/slots?date=%s" % (cid, tomorrow), tok)
slots = (d or {}).get("data") or []
free = [s["time"].split("-")[0] for s in slots if s.get("available")]
print("2. 咨询师 %s(%s) 明日空闲时段: %d 个" % (cname, cid, len(free)))

if not free:
    print("   无空闲时段，跳过创建")
    raise SystemExit

# 创建
d, c = call("POST", "/api/appointment/create", tok, {
    "counselor_id": cid,
    "consultation_type": "video",
    "appointment_date": "%sT%s:00" % (tomorrow, free[0]),
})
appt = (d or {}).get("data", {}) if isinstance(d, dict) else {}
aid = appt.get("id")
print("3. 创建预约: HTTP %s, id=%s, 咨询师=%s" % (c, aid, cname))

# 列表（页面加载的数据）
d, c = call("GET", "/api/appointment/user/list?page=1&page_size=100", tok)
data = (d or {}).get("data", {})
rows = data.get("items", [])
print("4. 我的预约列表: HTTP %s, total=%s" % (c, data.get("total")))
for r in rows[:3]:
    cn = (r.get("counselor") or {}).get("name", "?")
    print("     - id=%s %s %s status=%s" % (r.get("id"), cn, r.get("appointment_date"), r.get("status")))

# 状态筛选计数（页面标签角标）
for st in ["pending", "confirmed", "completed"]:
    d, c = call("GET", "/api/appointment/user/list?status_filter=%s&page=1&page_size=1" % st, tok)
    print("     %-10s total=%s" % (st, (d or {}).get("data", {}).get("total")))

# 取消
if aid:
    d, c = call("POST", "/api/appointment/%s/cancel" % aid, tok)
    print("5. 取消预约: HTTP %s %s" % (c, (d or {}).get("message", "")))
    # 时段应释放
    d, _ = call("GET", "/api/counselor/%s/slots?date=%s" % (cid, tomorrow), tok)
    slots2 = (d or {}).get("data") or []
    still_busy = [s for s in slots2 if s.get("time", "").startswith(free[0]) and not s.get("available")]
    print("6. 时段释放: %s" % ("是 ✅" if not still_busy else "否 ❌"))
