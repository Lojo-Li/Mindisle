# -*- coding: utf-8 -*-
"""P2 测试专用后端启动器（隔离邮件服务）。

不修改任何业务代码、不修改 .env、不引入新依赖（仅用标准库 unittest.mock）：
- 替换 EmailService.create_smtp_connection 为 MagicMock 上下文管理器；
- 替换 3 个发信入口为只记录事件的桩，绝不调用真实 SMTP；
- 事件写入 mail_mock_events.jsonl（只记录事件名、是否带收件地址、域名，不记录邮箱明文）。

正式环境仍按原配置启动，不使用本脚本。
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent / "backend"
EVENTS = HERE / "mail_mock_events.jsonl"

sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from app.services.email_service import EmailService  # noqa: E402


def _record(event, kwargs):
    email = str(kwargs.get("email") or "")
    line = {
        "event": event,
        "has_email": bool(email),
        "domain": email.split("@")[-1] if "@" in email else "",
        "has_appointment_no": bool(kwargs.get("appointment_no")),
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def _fake_smtp():
    server = MagicMock()
    server.__enter__.return_value = server
    return server


def _stub(event):
    def _noop(**kwargs):
        _record(event, kwargs)
        return True
    return staticmethod(_noop)


patch.object(EmailService, "create_smtp_connection", side_effect=_fake_smtp).start()
patch.object(EmailService, "send_appointment_confirmation_user",
             new=_stub("confirmation_user")).start()
patch.object(EmailService, "send_appointment_confirmation_counselor",
             new=_stub("confirmation_counselor")).start()
patch.object(EmailService, "send_appointment_cancelled",
             new=_stub("cancelled")).start()

print("[E2E] MAIL_MOCK_ENABLED: SMTP + 3 senders patched, no real mail", flush=True)

import uvicorn  # noqa: E402

uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="warning")
