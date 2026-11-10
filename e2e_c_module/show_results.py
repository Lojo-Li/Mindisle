# -*- coding: utf-8 -*-
"""只读汇总 results.json，输出紧凑证据供报告使用。"""
import json
from pathlib import Path

data = json.loads(Path(__file__).with_name("results.json").read_text(encoding="utf-8"))


def brief(c):
    body = (c["response"] or {}).get("body")
    if not isinstance(body, dict):
        return str(body)[:200]
    if "detail" in body:
        return "detail=" + str(body["detail"])[:260]
    out = ["code=%s" % body.get("code"), "msg=%s" % body.get("message")]
    d = body.get("data")
    if isinstance(d, dict):
        out.append("data.id=%s" % d.get("id"))
        out.append("data.status=%s" % d.get("status"))
        out.append("data.total=%s" % d.get("total"))
    elif isinstance(d, list):
        out.append("data=list(%s)" % len(d))
    return " ".join(out)


print("RUN_TAG=%s DATE=%s STATS=%s" % (data["run_tag"], data["test_date"], data["stats"]))
print("\n=== ALL CASES (id | status | HTTP | name | brief) ===")
for c in data["cases"]:
    print("%-7s %-13s %-5s %-48s %s" % (
        c["id"], c["status"], (c["response"] or {}).get("status"),
        c["name"][:48], brief(c)))

print("\n=== FAILED CASES FULL EVIDENCE ===")
for c in data["cases"]:
    if c["status"] != "FAIL":
        continue
    print("\n### %s %s" % (c["id"], c["name"]))
    print("  expected :", c["expected"])
    print("  request  :", json.dumps(c["request"], ensure_ascii=False)[:400])
    print("  http     :", (c["response"] or {}).get("status"),
          "elapsed_ms:", (c["response"] or {}).get("elapsed_ms"))
    print("  response :", json.dumps((c["response"] or {}).get("body"), ensure_ascii=False)[:500])
    print("  db       :", json.dumps(c["db"], ensure_ascii=False)[:900])
    print("  note     :", c["note"])

print("\n=== FEATURE GAP ===")
for c in data["cases"]:
    if c["status"] == "FEATURE_GAP":
        print(c["id"], c["name"], "|", c["note"])

print("\n=== CLEANUP CASE ===")
for c in data["cases"]:
    if c["id"] == "TC-049":
        print(json.dumps(c["db"], ensure_ascii=False, indent=1))
