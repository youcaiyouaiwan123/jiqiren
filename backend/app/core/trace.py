"""请求级 TraceId 管理。

每个 HTTP 请求在 middleware 中调用 set_trace_id() 写入当前协程的 ContextVar，
后续所有同协程代码（路由、服务、ORM 回调）均可通过 get_trace_id() 无参读取。
TraceIdFilter 会把它自动注入到每条 LogRecord，无需手动传参。
"""
import uuid
from contextvars import ContextVar

_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    return _trace_id_var.get()


def set_trace_id(tid: str) -> None:
    _trace_id_var.set(tid)


def new_trace_id() -> str:
    """生成 16 位十六进制 TraceId（64-bit 随机，碰撞概率可忽略）。"""
    return uuid.uuid4().hex[:16]
