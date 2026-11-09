"""C 模块端到端测试公共工具。

只读加载 backend/.env 中的 DATABASE_URL（凭据不会打印、不会写入报告/日志），
提供 MySQL 连接、查询与执行封装，以及一个简单的运行时结构探针。
"""
import re
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
ENV_FILE = BACKEND / ".env"
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

# 所有隔离测试数据的统一标识前缀
TEST_PREFIX = "E2E_C_"
TEST_EMAIL_DOMAIN = "e2e-c.invalid"


def load_env():
    env = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def db_config():
    url = load_env()["DATABASE_URL"]
    m = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", url)
    if not m:
        raise RuntimeError("DATABASE_URL 无法解析")
    return dict(
        host=m.group(3),
        port=int(m.group(4)),
        user=m.group(1),
        password=m.group(2),
        database=m.group(5).split("?")[0],
        charset="utf8mb4",
        autocommit=True,
    )


def connect():
    return pymysql.connect(**db_config())


def query(sql, args=None):
    conn = connect()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, args=None):
    conn = connect()
    try:
        with conn.cursor() as cur:
            affected = cur.execute(sql, args)
            last_id = cur.lastrowid
        conn.commit()
        return affected, last_id
    finally:
        conn.close()


def safe(v):
    """把 DB 返回的 datetime/decimal 等对象转成可 JSON 序列化值。"""
    if hasattr(v, "isoformat"):
        return v.isoformat(sep=" ")
    if hasattr(v, "__float__") and not isinstance(v, bool):
        try:
            return float(v)
        except Exception:
            pass
    return v


def row_dict(row):
    return {k: safe(v) for k, v in row.items()} if row else None


C_TABLES = [
    "users", "counselors", "appointments", "consultation_reviews",
    "consultation_messages", "counselor_inquiries", "inquiry_messages",
    "notifications",
]


def probe():
    cfg = db_config()
    print("DB_TARGET = %s:%s/%s (user=%s)" % (cfg["host"], cfg["port"], cfg["database"], cfg["user"]))
    print("MYSQL_VERSION =", query("SELECT VERSION() AS v")[0]["v"])
    print("DATABASE =", query("SELECT DATABASE() AS d")[0]["d"])
    print("\n-- 表与行数 --")
    for row in query(
        "SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA=%s ORDER BY TABLE_NAME", (cfg["database"],)
    ):
        print("  %-32s ~%s" % (row["TABLE_NAME"], row["TABLE_ROWS"]))
    print("\n-- C 模块关键表列 --")
    for table in ["users", "counselors", "appointments", "consultation_reviews", "consultation_messages"]:
        cols = query("SHOW COLUMNS FROM `%s`" % table)
        print("  [%s] %s" % (table, ", ".join("%s:%s" % (c["Field"], c["Type"]) for c in cols)))
    print("\n-- consultation_reviews 索引 --")
    for r in query("SHOW INDEX FROM consultation_reviews"):
        print("  %s unique=%s col=%s" % (r["Key_name"], "NO" if r["Non_unique"] == 0 else "YES", r["Column_name"]))
    print("\n-- appointments 索引 --")
    for r in query("SHOW INDEX FROM appointments"):
        print("  %s unique=%s col=%s" % (r["Key_name"], "NO" if r["Non_unique"] == 0 else "YES", r["Column_name"]))
    print("\n-- 现有隔离测试数据（应为空） --")
    print("  users E2E_C_:", query("SELECT COUNT(*) AS c FROM users WHERE email LIKE %s", (TEST_PREFIX + "%",))[0]["c"])
    print("  counselors E2E_C_:", query("SELECT COUNT(*) AS c FROM counselors WHERE name LIKE %s", (TEST_PREFIX + "%",))[0]["c"])
    print("\n-- 基线行数 --")
    for t in C_TABLES:
        try:
            print("  %-26s %s" % (t, query("SELECT COUNT(*) AS c FROM `%s`" % t)[0]["c"]))
        except Exception as e:
            print("  %-26s (表不存在或不可读: %s)" % (t, type(e).__name__))


def smtp_probe():
    """仅测量 SMTP 端口连通耗时，用于评估邮件副作用对接口耗时的影响。"""
    import socket
    import time
    for host, port in [("smtp.163.com", 465)]:
        s = socket.socket()
        s.settimeout(4)
        t = time.time()
        try:
            s.connect((host, port))
            print("SMTP_REACHABLE %s:%s in %.2fs" % (host, port, time.time() - t))
        except Exception as e:
            print("SMTP_BLOCKED %s:%s (%s) after %.2fs" % (host, port, type(e).__name__, time.time() - t))
        finally:
            s.close()


def existing_entities():
    print("USERS:", [
        {"id": r["id"], "role": r["role"], "status": r["status"],
         "is_deleted": r["is_deleted"], "email": "<masked>"}
        for r in query("SELECT id, role, status, is_deleted FROM users")
    ])
    print("COUNSELORS:", [
        {k: row_dict(r)[k] for k in ("id", "user_id", "name", "status", "application_status", "is_deleted", "price_video", "consultation_types")}
        for r in query("SELECT id, user_id, name, status, application_status, is_deleted, price_video, consultation_types FROM counselors")
    ])


if __name__ == "__main__":
    probe()
    smtp_probe()
    existing_entities()
