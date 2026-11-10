"""验证咨询师端新页面（订单管理 + 会话）依赖的业务链路。"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000"
results = []


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode() or "null"), r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return json.loads(raw or "null"), e.code
        except Exception:
            return raw, e.code


def login(email, pwd="123456"):
    d, _ = call("POST", "/api/auth/login", body={"email": email, "password": pwd})
    return (d or {}).get("data", {}).get("token")


def case(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + ((" :: " + str(detail)[:130]) if detail else ""))


print("=" * 62)
utok = login("user@test.com")
ctok = login("consultant@test.com")
case("用户登录", bool(utok))
case("咨询师登录", bool(ctok))

d, _ = call("GET", "/api/counselor/list?page=1&page_size=10", utok)
items = (d or {}).get("data", {}).get("items", [])
me = next((x for x in items if x.get("id") == 1), items[0])
cid = me["id"]
day = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
d, _ = call("GET", "/api/counselor/%s/slots?date=%s" % (cid, day), utok)
slots = (d or {}).get("data") or []
free = [s["time"].split("-")[0] for s in slots if s.get("available")]

# 用户下两单：一单接受、一单拒绝
created = []
for i in range(2):
    d, c = call("POST", "/api/appointment/create", utok, {
        "counselor_id": cid, "consultation_type": "video",
        "appointment_date": "%sT%s:00" % (day, free[i]),
        "problem_description": "这是学生的备注第%d单" % (i + 1),
    })
    aid = ((d or {}).get("data") or {}).get("id")
    created.append(aid)
case("1 学生创建两笔预约", len([x for x in created if x]) == 2, created)

# 咨询师订单列表
d, c = call("GET", "/api/consultation/counselor/orders?page_size=100", ctok)
orders = ((d or {}).get("data") or {}).get("items", [])
case("2 咨询师订单列表", c == 200 and len(orders) >= 2, "共 %d 笔" % len(orders))
if orders:
    o = orders[0]
    case("3 订单含学生信息", bool(o.get("user_info") or o.get("user")),
         "user_info=%s" % str(o.get("user_info"))[:80])
    case("4 订单含学生备注", any(x.get("problem_description") for x in orders),
         "notes=%s" % next((x.get("problem_description") for x in orders if x.get("problem_description")), None))

# 状态筛选计数
for st in ["pending", "confirmed"]:
    d, c = call("GET", "/api/consultation/counselor/orders?status=%s&page_size=1" % st, ctok)
    print("     %-10s total=%s" % (st, (d or {}).get("data", {}).get("total")))

# 接受第 1 单
d, c = call("POST", "/api/consultation/order/%s/handle" % created[0], ctok, {"action": "agree"})
case("5 接受预约", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

# 拒绝第 2 单（带原因）
d, c = call("POST", "/api/consultation/order/%s/handle" % created[1], ctok,
            {"action": "reject", "reason": "该时段已有安排"})
case("6 拒绝预约（带原因）", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

d, c = call("GET", "/api/appointment/%s" % created[1], utok)
o2 = (d or {}).get("data") or {}
case("7 拒绝后状态为 cancelled 且写回原因",
     o2.get("status") == "cancelled" and bool(o2.get("cancel_reason")),
     "status=%s reason=%s" % (o2.get("status"), o2.get("cancel_reason")))

# 对话：学生先发，咨询师回复
d, c = call("POST", "/api/consultation/%s/message" % created[0], utok,
            {"content": "老师好，最近总是睡不着。", "message_type": "text"})
case("8 学生发送首条消息", c == 200, "HTTP %s" % c)

d, c = call("GET", "/api/appointment/%s" % created[0], ctok)
st = ((d or {}).get("data") or {}).get("status")
case("9 咨询师可看到 in_progress 状态", st == "in_progress", "status=%s" % st)

d, c = call("POST", "/api/consultation/%s/message" % created[0], ctok,
            {"content": "我们先从作息记录开始，可以吗？", "message_type": "text"})
case("10 咨询师回复消息", c == 200, "HTTP %s" % c)

# 咨询师添加备注
d, c = call("POST", "/api/consultation/%s/note" % created[0], ctok,
            {"note": "主诉入睡困难，建议作息记录两周"})
case("11 咨询师添加备注", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

# 消息列表（咨询师视角）
d, c = call("GET", "/api/consultation/%s/messages?limit=2000" % created[0], ctok)
msgs = ((d or {}).get("data") or {}).get("items", [])
senders = [m.get("sender_type") for m in msgs]
case("12 咨询师可读取双方消息",
     c == 200 and "user" in senders and "counselor" in senders,
     "共 %d 条 senders=%s" % (len(msgs), senders))

# 咨询师结束
d, c = call("POST", "/api/consultation/%s/end" % created[0], ctok)
case("13 咨询师结束咨询", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

d, c = call("GET", "/api/appointment/%s" % created[0], utok)
case("14 结束后状态 completed",
     ((d or {}).get("data") or {}).get("status") == "completed",
     "status=%s" % ((d or {}).get("data") or {}).get("status"))

# 越权：普通用户访问咨询师订单
d, c = call("GET", "/api/consultation/counselor/orders", utok)
case("15 学生访问咨询师订单被拒 403", c == 403, "HTTP %s" % c)

print("=" * 62)
p = sum(1 for _, ok, _ in results if ok)
print("结果：%d PASS / %d FAIL / 共 %d" % (p, len(results) - p, len(results)))
for n, ok, dt in results:
    if not ok:
        print("  FAIL:", n, "::", str(dt)[:150])
print("\n[清理] ids =", created)
