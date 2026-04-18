"""立体化日志配置

三层覆盖：
  系统层   — 应用启动/关闭、Worker 状态、DB/Redis 连接（由 lifespan 记录）
  应用层   — 每条 HTTP 请求/响应（由 trace_and_log_middleware 记录，含 TraceId/IP/UA）
  业务层   — 认证、对话、订阅、飞书同步等业务事件（各 router/service 自行记录）

三个输出端：
  console   — INFO+，人类可读，含 trace_id
  app.log   — DEBUG+，JSON Lines，含 trace_id；按天切割，backupCount=0（由 LogCleanupWorker 管理）
  error.log — ERROR+，JSON Lines；按天切割，backupCount=0；可选推企微告警

告警（可选）：
  设置环境变量 WECOM_ALERT_WEBHOOK=<企微机器人 webhook URL> 后，
  ERROR+ 事件经去重（每类错误 5 分钟内只推一次）后异步推送到企微。
"""
from __future__ import annotations

import gzip
import json
import logging
import os
import queue
import shutil
import sys
import threading
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.core.trace import get_trace_id

# ── 路径 ──────────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE = str(LOG_DIR / "app.log")
ERROR_LOG_FILE = str(LOG_DIR / "error.log")

# ── 格式 ──────────────────────────────────────────────────────────────────────
_CONSOLE_FMT = "%(asctime)s | %(levelname)-7s | %(trace_id)-16s | %(name)s:%(lineno)d | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


class _TraceIdFilter(logging.Filter):
    """把当前协程的 TraceId 注入每条 LogRecord，无需手动传参。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()  # type: ignore[attr-defined]
        return True


class _JsonFormatter(logging.Formatter):
    """JSON Lines 格式，每条日志一行，便于 jq / grep 解析和日志平台接入。

    输出样例：
    {"ts":"2026-04-17T10:23:45.123","level":"INFO","trace":"a1b2c3d4e5f60001",
     "logger":"app.routers.chat_v2","line":301,"msg":"[对话] 发送 | user_id=42"}
    """

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S.") + f"{record.msecs:03.0f}"
        data: dict = {
            "ts": ts,
            "level": record.levelname,
            "trace": getattr(record, "trace_id", "-"),
            "logger": record.name,
            "line": record.lineno,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)


class _WeComAlertHandler(logging.Handler):
    """ERROR+ 事件异步推送企微 Webhook（每来源 5 分钟内最多推一次，防刷屏）。

    不依赖 httpx 等三方库，使用标准库 urllib.request 发送。
    发送操作在独立的 daemon 线程中完成，不阻塞主线程。
    """

    _COOLDOWN = 300   # seconds
    _MAX_QUEUE = 30

    def __init__(self, webhook_url: str) -> None:
        super().__init__(level=logging.ERROR)
        self._url = webhook_url
        self._q: queue.Queue[dict] = queue.Queue(maxsize=self._MAX_QUEUE)
        self._rate: dict[str, float] = {}
        self._lock = threading.Lock()
        threading.Thread(target=self._send_loop, daemon=True, name="wecom-alert").start()

    def emit(self, record: logging.LogRecord) -> None:
        key = f"{record.name}:{record.lineno}"
        now = time.monotonic()
        with self._lock:
            if len(self._rate) > 500:
                self._rate = {k: v for k, v in self._rate.items() if now - v < self._COOLDOWN * 2}
            if now - self._rate.get(key, 0.0) < self._COOLDOWN:
                return
            self._rate[key] = now
        try:
            self._q.put_nowait({
                "level": record.levelname,
                "trace": getattr(record, "trace_id", "-"),
                "logger": f"{record.name}:{record.lineno}",
                "msg": record.getMessage()[:500],
            })
        except queue.Full:
            pass

    def _send_loop(self) -> None:
        import urllib.request as _req

        while True:
            item = self._q.get()
            try:
                content = (
                    f"## [{item['level']}] 智能客服告警\n"
                    f"> **trace**: `{item['trace']}`\n"
                    f"> **logger**: `{item['logger']}`\n"
                    f"> {item['msg']}"
                )
                body = json.dumps(
                    {"msgtype": "markdown", "markdown": {"content": content}},
                    ensure_ascii=False,
                ).encode("utf-8")
                request = _req.Request(
                    self._url,
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                _req.urlopen(request, timeout=5)
            except Exception:
                pass


# ── 公开接口 ──────────────────────────────────────────────────────────────────

def setup_logging(level: str | None = None) -> None:
    """初始化全局日志，应在应用启动最早期调用一次。"""
    log_level_name = (level or os.getenv("LOG_LEVEL", "DEBUG")).upper()
    log_level = getattr(logging, log_level_name, logging.DEBUG)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()

    # 热重载保护：已有 TimedRotatingFileHandler 则跳过重复初始化
    if any(isinstance(h, TimedRotatingFileHandler) for h in root.handlers):
        return

    root.setLevel(log_level)

    trace_filter = _TraceIdFilter()
    json_formatter = _JsonFormatter()
    console_formatter = logging.Formatter(_CONSOLE_FMT, datefmt=_DATE_FMT)

    # ── 控制台：INFO+，人类可读 ──────────────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(console_formatter)
    console.addFilter(trace_filter)
    root.addHandler(console)

    # ── app.log：DEBUG+，JSON Lines，按天切割 ───────────────────────────────
    # backupCount=0 = 不自动删除旧文件，由 LogCleanupWorker 负责压缩和清理
    app_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=0, encoding="utf-8", utc=False,
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(json_formatter)
    app_handler.addFilter(trace_filter)
    app_handler.suffix = "%Y-%m-%d"
    root.addHandler(app_handler)

    # ── error.log：ERROR+，JSON Lines，按天切割 ─────────────────────────────
    error_handler = TimedRotatingFileHandler(
        ERROR_LOG_FILE, when="midnight", interval=1, backupCount=0, encoding="utf-8", utc=False,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(trace_filter)
    error_handler.suffix = "%Y-%m-%d"
    root.addHandler(error_handler)

    # ── 企微告警（可选）──────────────────────────────────────────────────────
    webhook = os.getenv("WECOM_ALERT_WEBHOOK", "").strip()
    if webhook:
        wecom = _WeComAlertHandler(webhook)
        wecom.addFilter(trace_filter)
        root.addHandler(wecom)
        logging.getLogger(__name__).info("企微告警已启用 | webhook 已配置")

    # ── 降低第三方库噪音 ─────────────────────────────────────────────────────
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "aiomysql", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "日志系统初始化完成 | level=%s | app=%s | error=%s | wecom=%s",
        log_level_name, LOG_FILE, ERROR_LOG_FILE, "on" if webhook else "off",
    )
