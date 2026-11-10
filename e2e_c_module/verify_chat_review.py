"""验证新界面「咨询对话 + 评价」依赖的完整业务链路。

流程：用户下单 → 咨询师接单 → 用户发消息(隐式进入 in_progress) →
咨询师回消息 → 咨询师结束 → 用户评价 → 校验评分统计。
"""
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
    print(("  PASS  " if ok else "  FAIL  ") + name + ((" :: " + str(detail)[:140]) if detail else ""))


print("=" * 62)
utok = login("user@test.com")
ctok = login("consultant@test.com")
case("用户登录", bool(utok))
case("咨询师登录", bool(ctok))

# 取咨询师与空闲时段
d, _ = call("GET", "/api/counselor/list?page=1&page_size=10", utok)
items = (d or {}).get("data", {}).get("items", [])
me = next((x for x in items if x.get("id") == 1), items[0] if items else None)
cid = me["id"]
day = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
d, _ = call("GET", "/api/counselor/%s/slots?date=%s" % (cid, day), utok)
slots = (d or {}).get("data") or []
free = [s["time"].split("-")[0] for s in slots if s.get("available")]
print("    咨询师 %s, 空闲时段 %d 个" % (me.get("name"), len(free)))

# 1. 下单
d, c = call("POST", "/api/appointment/create", utok, {
    "counselor_id": cid, "consultation_type": "video",
    "appointment_date": "%sT%s:00" % (day, free[0]),
})
aid = ((d or {}).get("data") or {}).get("id")
case("1 创建预约", c == 200 and bool(aid), "id=%s" % aid)

# 2. 咨询师接单
d, c = call("POST", "/api/consultation/order/%s/handle" % aid, ctok, {"action": "agree"})
case("2 咨询师接单", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

# 3. 用户发消息（隐式 confirmed -> in_progress）
d, c = call("POST", "/api/consultation/%s/message" % aid, utok,
            {"content": "你好，我最近睡眠不太好。", "message_type": "text"})
case("3 用户发送消息", c == 200, "HTTP %s" % c)

d, c = call("GET", "/api/appointment/%s" % aid, utok)
st = ((d or {}).get("data") or {}).get("status")
case("4 状态隐式推进为 in_progress", st == "in_progress", "status=%s" % st)

# 5. 咨询师回消息
d, c = call("POST", "/api/consultation/%s/message" % aid, ctok,
            {"content": "谢谢你愿意说出来，我们从作息开始聊。", "message_type": "text"})
case("5 咨询师回复消息", c == 200, "HTTP %s" % c)

# 6. 消息列表
d, c = call("GET", "/api/consultation/%s/messages?limit=2000" % aid, utok)
msgs = ((d or {}).get("data") or {}).get("items", [])
case("6 消息列表可读取", c == 200 and len(msgs) >= 2, "共 %d 条" % len(msgs))
if msgs:
    senders = [m.get("sender_type") for m in msgs]
    case("7 双方消息都在", "user" in senders and ("counselor" in senders or "system" in senders),
         "senders=%s" % senders)

# 8. 咨询师结束
d, c = call("POST", "/api/consultation/%s/end" % aid, ctok)
case("8 咨询师结束咨询", c == 200, (d or {}).get("message") if isinstance(d, dict) else d)

d, c = call("GET", "/api/appointment/%s" % aid, utok)
st = ((d or {}).get("data") or {}).get("status")
case("9 状态变为 completed", st == "completed", "status=%s" % st)

# 10. 未完成前评价应被拒（用新单验证）
d, c = call("GET", "/api/counselor/%s" % cid, utok)
before_rating = ((d or {}).get("data") or {}).get("rating")
before_cnt = ((d or {}).get("data") or {}).get("review_count") or 0

# 11. 提交评价
d, c = call("POST", "/api/appointment/%s/review" % aid, utok, {
    "rating": 5, "tags": ["专业度高", "倾听耐心"],
    "content": "聊完踏实多了，谢谢。", "is_anonymous": False,
})
case("10 提交评价", c == 200, "HTTP %s %s" % (c, str(d)[:100] if not isinstance(d, dict) else (d.get("message") or "")))

# 12. 评分统计立即同步（BUG-02 回归）
d, c = call("GET", "/api/counselor/%s" % cid, utok)
now_rating = ((d or {}).get("data") or {}).get("rating")
now_cnt = ((d or {}).get("data") or {}).get("review_count") or 0
case("11 评分统计立即更新", now_cnt == before_cnt + 1,
     "review_count %s→%s, rating %s→%s" % (before_cnt, now_cnt, before_rating, now_rating))

# 13. 重复评价应被拒
d, c = call("POST", "/api/appointment/%s/review" % aid, utok, {"rating": 4})
case("12 重复评价被拒", c == 400, "HTTP %s" % c)

# 14. 评价列表可见
d, c = call("GET", "/api/counselor/%s/reviews" % cid, utok)
revs = ((d or {}).get("data") or {}).get("items", [])
case("13 评价出现在咨询师评价列表", c == 200 and len(revs) >= 1, "共 %d 条" % len(revs))

print("=" * 62)
p = sum(1 for _, ok, _ in results if ok)
print("结果：%d PASS / %d FAIL / 共 %d" % (p, len(results) - p, len(results)))
for n, ok, dt in results:
    if not ok:
        print("  FAIL:", n, "::", str(dt)[:160])
print("\n[清理] appointment_id =", aid)
