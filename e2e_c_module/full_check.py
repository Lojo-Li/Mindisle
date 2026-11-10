"""全功能验证：覆盖三个模块（A鉴权 / B排班 / C预约对话 / D量表 / E AI）的 HTTP 层行为"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000"

results = []


def call(method, path, token=None, body=None, timeout=20):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return -1, {"error": str(e)}


def case(tid, name, expect, ok, actual=""):
    results.append({"id": tid, "name": name, "expect": expect, "ok": bool(ok), "actual": str(actual)[:180]})
    print(("  PASS  " if ok else "  FAIL  ") + "%s %s :: %s" % (tid, name, actual))


def login(email, pwd="123456"):
    c, d = call("POST", "/api/auth/login", body={"email": email, "password": pwd})
    if c == 200:
        return (d.get("data") or {}).get("token")
    return None


print("=" * 70)
print("A 线 · 鉴权")
print("=" * 70)
ut = login("user@test.com")
ct = login("consultant@test.com")
at = login("admin@soulstation.com", "admin123")
case("AUTH-01", "学生登录", "有 token", bool(ut), (ut or "")[:16])
case("AUTH-02", "咨询师登录", "有 token", bool(ct), (ct or "")[:16])
case("AUTH-03", "管理员登录", "有 token", bool(at), (at or "")[:16])

c, _ = call("POST", "/api/auth/login", body={"email": "user@test.com", "password": "wrong"})
case("AUTH-04", "错误密码被拒", "4xx", 400 <= c < 500, "HTTP %s" % c)

c, _ = call("GET", "/api/appointment/user/list")
case("AUTH-05", "未登录访问受保护接口", "401/403", c in (401, 403), "HTTP %s" % c)

# 没有 /api/auth/me，改用受保护接口验证 token 有效性
c, d = call("GET", "/api/user/profile", ut)
case("AUTH-06", "token 可访问受保护接口", "200", c == 200, "HTTP %s" % c)

print()
print("=" * 70)
print("B 线 · 排班")
print("=" * 70)
d1 = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
c, d = call("POST", "/api/counselor/schedule/publish", ct,
            {"slots": [{"date": d1, "start_time": "09:00", "end_time": "12:00"}]})
created = (d.get("data") or {}).get("created") if c == 200 else None
case("SCH-01", "发布 09:00-12:00 拆成 3 个子时段", "created=3", created == 3, "created=%s HTTP=%s" % (created, c))

c, d = call("POST", "/api/counselor/schedule/publish", ct,
            {"slots": [{"date": d1, "start_time": "10:00", "end_time": "11:00"}]})
skipped = (d.get("data") or {}).get("skipped") if c == 200 else None
case("SCH-02", "重复时段被跳过", "skipped>=1", skipped is not None and skipped >= 1, "skipped=%s" % skipped)

past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
c, d = call("POST", "/api/counselor/schedule/publish", ct,
            {"slots": [{"date": past, "start_time": "09:00", "end_time": "10:00"}]})
case("SCH-03", "过去时段被拒绝", "created=0 或有 conflicts", 
     c == 200 and ((d.get("data") or {}).get("created") == 0), 
     json.dumps(d.get("data"), ensure_ascii=False)[:80])

c, d = call("POST", "/api/counselor/schedule/publish", ut,
            {"slots": [{"date": d1, "start_time": "15:00", "end_time": "16:00"}]})
case("SCH-04", "学生无权发布时段(被拒即可)", "4xx", 400 <= c < 500, "HTTP %s %s" % (c, d.get("message")))

c, d = call("GET", "/api/counselor/schedule/list?start_date=%s&end_date=%s" % (d1, d1), ct)
items = (d.get("data") or []) if c == 200 else []
case("SCH-05", "查询已发布时段", ">=3 条", len(items) >= 3, "共 %d 条" % len(items))

print()
print("=" * 70)
print("C 线 · 预约 / 对话 / 评价")
print("=" * 70)
c, d = call("GET", "/api/counselor/1/slots?date=" + d1, ut)
slots = (d.get("data") or []) if c == 200 else []
avail = [s for s in slots if s.get("available")]
case("APPT-01", "学生查询可约时段", ">=3 个", len(avail) >= 3, "共 %d 个可约" % len(avail))
case("APPT-02", "时段价格为 0（公益免费）", "price=0",
     bool(avail) and all(s.get("price") == 0 for s in avail),
     str([s.get("price") for s in avail[:3]]))

body = {"counselor_id": 1, "consultation_type": "video",
        "appointment_date": d1 + "T09:00:00", "problem_description": "全功能测试预约"}
c, d = call("POST", "/api/appointment/create", ut, body)
aid = (d.get("data") or {}).get("id") if c == 200 else None
case("APPT-03", "创建预约", "200 + id", c == 200 and aid, "id=%s HTTP=%s" % (aid, c))
case("APPT-04", "预约价格为 0", "price=0",
     c == 200 and (d.get("data") or {}).get("price") == 0,
     "price=%s" % ((d.get("data") or {}).get("price")))

c, d = call("POST", "/api/appointment/create", ut, body)
case("APPT-05", "同时段重复预约被拒", "400", c == 400, "HTTP %s %s" % (c, d.get("message")))

c, d = call("POST", "/api/appointment/create", ut,
            {**body, "appointment_date": d1 + "T20:00:00"})
case("APPT-06", "未发布时段被拒", "400", c == 400, "HTTP %s %s" % (c, d.get("message")))

if aid:
    c, d = call("POST", "/api/consultation/order/%s/handle" % aid, ct, {"action": "agree"})
    case("APPT-07", "咨询师接单", "200", c == 200, "HTTP %s" % c)

    st = login("student1@test.com")
    c, _ = call("GET", "/api/appointment/%s" % aid, st)
    case("APPT-08", "他人查看预约详情 403", "403", c == 403, "HTTP %s" % c)

    c, _ = call("GET", "/api/consultation/counselor/orders", ut)
    case("APPT-09", "学生访问咨询师订单 403", "403", c == 403, "HTTP %s" % c)

    c, d = call("POST", "/api/consultation/%s/message" % aid, ut,
                {"content": "全功能测试消息", "message_type": "text"})
    case("MSG-01", "学生发消息", "200", c == 200, "HTTP %s" % c)

    c, d = call("GET", "/api/appointment/%s" % aid, ut)
    status_after = (d.get("data") or {}).get("status")
    case("MSG-02", "首条消息触发 confirmed→in_progress", "in_progress",
         status_after == "in_progress", "status=%s" % status_after)

    c, d = call("POST", "/api/consultation/%s/message" % aid, ct,
                {"content": "咨询师回复", "message_type": "text"})
    case("MSG-03", "咨询师回复", "200", c == 200, "HTTP %s" % c)

    c, d = call("GET", "/api/consultation/%s/messages?limit=100" % aid, ut)
    msgs = (d.get("data") or {}).get("items", []) if c == 200 else []
    case("MSG-04", "消息列表含双方消息", ">=3 条",
         len(msgs) >= 3, "共 %d 条" % len(msgs))

    c, d = call("POST", "/api/consultation/%s/end" % aid, ct)
    case("MSG-05", "结束咨询", "200", c == 200, "HTTP %s %s" % (c, d.get("message")))

    c, d = call("POST", "/api/appointment/%s/review" % aid, ut,
                {"rating": 5, "comment": "全功能测试评价", "tags": ["专业度高"], "is_anonymous": False})
    case("REV-01", "提交评价", "200", c == 200, "HTTP %s %s" % (c, d.get("message")))

    c, d = call("POST", "/api/appointment/%s/review" % aid, ut,
                {"rating": 4, "comment": "重复评价", "is_anonymous": False})
    case("REV-02", "重复评价被拒", "400", c == 400, "HTTP %s" % c)

    c, d = call("GET", "/api/counselor/1", ut)
    rc = (d.get("data") or {}).get("review_count")
    case("REV-03", "评价后统计立即更新", "review_count>=1",
         rc is not None and rc >= 1, "review_count=%s" % rc)

print()
print("=" * 70)
print("D 线 · 心理量表")
print("=" * 70)
c, d = call("GET", "/api/test/list", ut)
tests = (d.get("data") or {}).get("items", d.get("data") or []) if c == 200 else []
if isinstance(tests, dict):
    tests = tests.get("items", [])
case("TEST-01", "量表列表", ">=9 套", c == 200 and len(tests) >= 9, "HTTP %s 共 %s 套" % (c, len(tests)))

if tests:
    tid0 = tests[0].get("id")
    c, d = call("GET", "/api/test/%s" % tid0, ut)
    total_q = (d.get("data") or {}).get("total_questions") if c == 200 else None
    case("TEST-02a", "量表详情返回元信息", "total_questions>0",
         c == 200 and total_q and int(total_q) > 0, "total_questions=%s" % total_q)

    # 题目由 /start 返回
    c, d = call("POST", "/api/test/%s/start" % tid0, ut, {})
    qs = (d.get("data") or {}).get("questions", []) if c == 200 else []
    case("TEST-02b", "开始答题返回题目", ">0 题",
         c == 200 and len(qs) > 0, "共 %d 题" % len(qs))

c, d = call("GET", "/api/test/history", ut)
case("TEST-03", "测评历史", "200", c == 200, "HTTP %s" % c)

print()
print("=" * 70)
print("E 线 · AI 支持")
print("=" * 70)
c, d = call("GET", "/api/chat/list", ut)
case("AI-01", "会话列表", "200 + 数组",
     c == 200 and isinstance(d.get("data"), list), "HTTP %s 共 %s 条" % (c, len(d.get("data") or [])))

print()
print("=" * 70)
print("整体页面可访问性")
print("=" * 70)
for p in ["/login", "/workspace/home", "/workspace/booking", "/workspace/appointments",
          "/workspace/records", "/workspace/assess", "/workspace/lamp",
          "/counselor/dashboard", "/counselor/dashboard/schedule",
          "/counselor/dashboard/sessions", "/counselor/dashboard/profile"]:
    req = urllib.request.Request("http://localhost:5173" + p)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = -1
    case("UI-" + p.replace("/", "_"), "页面可访问 " + p, "200", code == 200, "HTTP %s" % code)

passed = sum(1 for r in results if r["ok"])
print()
print("=" * 70)
print("结果：%d PASS / %d FAIL / 共 %d" % (passed, len(results) - passed, len(results)))
if len(results) - passed:
    print("失败项：")
    for r in results:
        if not r["ok"]:
            print("  - %s %s :: %s" % (r["id"], r["name"], r["actual"]))

json.dump({"results": results,
           "stats": {"pass": passed, "fail": len(results) - passed, "total": len(results)}},
          open("results_full_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
