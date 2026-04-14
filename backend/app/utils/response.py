"""统一响应格式"""
import uuid
from typing import Any


def success(data: Any = None, message: str = "ok") -> dict:
    return {
        "code": 0,
        "message": message,
        "data": data,
        "request_id": str(uuid.uuid4()),
    }


def fail(code: int = 1001, message: str = "请求失败", data: Any = None) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": str(uuid.uuid4()),
    }


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
