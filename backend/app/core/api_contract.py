"""
A 线维护的公共接口约定（错误码统一，G8）。

后端成功响应沿用 ``{code:200, message, data}``；失败原本直接抛
HTTPException 产生 ``{"detail": ...}``，与成功结构双轨，导致 B/C/D/E
各自处理时口径不一。这里在应用入口统一补齐失败响应结构：

    {code, message, data: null, detail}

**保留 detail 原始字段**，其他业务线已有的 ``error.response.data.detail``
读取方式完全不受影响；新增的 code/message 供新代码统一使用。
本模块不改动任何业务 router。
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _to_message(detail) -> str:
    if isinstance(detail, str) and detail:
        return detail
    if isinstance(detail, dict):
        value = detail.get("message") or detail.get("detail")
        if isinstance(value, str) and value:
            return value
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict):
            return str(first.get("msg") or "请求参数校验失败")
    return "请求失败"


def install_api_contract(app: FastAPI) -> None:
    """在应用入口挂载统一错误响应，保持 HTTP 状态码不变。"""

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
        detail = exc.detail
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": _to_message(detail),
                "data": None,
                # 向后兼容：其他业务线可能直接读取 detail
                "detail": jsonable_encoder(detail),
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = jsonable_encoder(exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "请求参数校验失败",
                "data": None,
                "detail": errors,
                "errors": errors,
            },
        )

    return None
