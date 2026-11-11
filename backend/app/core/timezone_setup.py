"""时区处理：确保全站时间按北京时间存储与展示。

背景
----
项目所有时间字段都用 ``Column(DateTime, server_default=func.now())``，
语义是"本地时间"：

- 本地开发用 MySQL，``NOW()`` 返回数据库服务器本地时间（北京时间）→ 正常
- 部署到 SQLite 时，``CURRENT_TIMESTAMP`` 恒为 UTC → 时间比北京时间慢 8 小时
  （曾出现聊天时间戳显示 04:49，实际 12:51）

历史数据可能是 UTC 也可能是本地时间，无法安全地批量转换，
因此这里的策略是：**保证从现在开始写入的时间都是北京时间**。

做法
----
1. 进程时区锁定为 Asia/Shanghai（Linux 下 time.tzset() 生效）
2. SQLite 库的表默认值由 CURRENT_TIMESTAMP 重建为 datetime('now','localtime')
   幂等：已是 localtime 的表会被跳过
"""

from __future__ import annotations

import os
import re
import time

TZ_NAME = "Asia/Shanghai"


def apply_timezone() -> None:
    """把进程时区设为北京时间。需在导入应用模块前调用。"""
    os.environ["TZ"] = TZ_NAME
    try:
        time.tzset()  # 仅 Unix 有效
    except AttributeError:
        # Windows 无 tzset，系统本地时区即北京时间，无需处理
        pass


def fix_sqlite_time_defaults(database_url: str, verbose: bool = True) -> int:
    """把 SQLite 表的时间默认值从 UTC 改为本地时间。

    返回修正的表数量。非 SQLite 或文件不存在时返回 0。
    """
    import sqlite3

    def log(msg: str) -> None:
        if verbose:
            print(f"[tz] {msg}", flush=True)

    if not database_url.startswith("sqlite"):
        log("非 SQLite，跳过")
        return 0

    path = database_url.split("///", 1)[-1]
    if not os.path.exists(path):
        log(f"SQLite 文件不存在，跳过: {path}")
        return 0

    con = sqlite3.connect(path)
    try:
        cur = con.cursor()
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        targets = [(n, s) for n, s in cur.fetchall()
                   if s and "CURRENT_TIMESTAMP" in s.upper()]
        if not targets:
            log("时间默认值已是本地时间")
            return 0

        fixed = 0
        for name, ddl in targets:
            new_ddl = re.sub(
                r"DEFAULT\s+\(?\s*CURRENT_TIMESTAMP\s*\)?",
                "DEFAULT (datetime('now','localtime'))",
                ddl,
                flags=re.IGNORECASE,
            )
            if new_ddl == ddl:
                continue

            tmp = f"__{name}_tznew"
            create_sql = (new_ddl
                          .replace(f"CREATE TABLE {name}", f"CREATE TABLE {tmp}", 1)
                          .replace(f'CREATE TABLE "{name}"', f'CREATE TABLE "{tmp}"', 1))
            cur.execute(f'DROP TABLE IF EXISTS "{tmp}"')
            cur.execute(create_sql)

            cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{name}")').fetchall()]
            collist = ", ".join(f'"{c}"' for c in cols)
            cur.execute(f'INSERT INTO "{tmp}" ({collist}) SELECT {collist} FROM "{name}"')
            cur.execute(f'DROP TABLE "{name}"')
            cur.execute(f'ALTER TABLE "{tmp}" RENAME TO "{name}"')

            # 重建索引（原 DDL 里没有索引定义，从 sqlite_master 补回）
            cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? "
                "AND sql IS NOT NULL", (name,))
            for (idx_sql,) in cur.fetchall():
                try:
                    cur.execute(idx_sql)
                except sqlite3.Error:
                    pass
            fixed += 1

        con.commit()
        log(f"已修正 {fixed} 张表的时间默认值为本地时间")
        return fixed
    except Exception as exc:  # noqa: BLE001
        con.rollback()
        log(f"修正失败（不影响启动）: {exc!r}")
        return 0
    finally:
        con.close()
