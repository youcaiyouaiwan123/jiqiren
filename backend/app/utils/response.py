"""统一响应格式"""
import uuid
from typing import Any

from app.core.trace import get_trace_id


def success(data: Any = None, message: str = "ok") -> dict:
    _tid = get_trace_id()
    return {
        "code": 0,
        "message": message,
        "data": data,
        "request_id": _tid if _tid != "-" else str(uuid.uuid4()),
    }


def fail(code: int = 1001, message: str = "请求失败", data: Any = None) -> dict:
    _tid = get_trace_id()
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": _tid if _tid != "-" else str(uuid.uuid4()),
    }


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
