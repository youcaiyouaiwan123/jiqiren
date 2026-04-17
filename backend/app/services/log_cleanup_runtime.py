"""日志生命周期 Worker

策略：以每天为单位压缩，保留最近 7 天（上一周）日志后删除。

每次运行（启动后 30s 首次，之后每 24h 一次）：
  1. 压缩昨日及更早未压缩的 app.log.DATE / error.log.DATE → .gz
  2. 删除所有超过 LOG_KEEP_DAYS 天的日志文件（.gz 和明文均删）

日志文件命名约定（来自 TimedRotatingFileHandler，suffix="%Y-%m-%d"）：
  当前日志 ：app.log          （不处理）
  已切割日志：app.log.2026-04-16        → 压缩为 app.log.2026-04-16.gz
  已压缩日志：app.log.2026-04-16.gz     → 超期后删除
"""
from __future__ import annotations

import asyncio
import gzip
import logging
import re
import shutil
from datetime import date, timedelta

from app.config import get_settings
from app.core.logging_config import LOG_DIR

logger = logging.getLogger(__name__)

_LOG_NAME_RE = re.compile(r"^(?:app|error)\.log\.(\d{4}-\d{2}-\d{2})(\.gz)?$")

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None

_STARTUP_DELAY_SECS = 30   # 应用完全就绪后再执行首次清理
_INTERVAL_SECS = 86400     # 24 小时


def _run_cleanup_once() -> None:
    """压缩昨日日志 + 删除超期文件（同步，在线程中调用）。"""
    settings = get_settings()
    keep_days: int = max(settings.LOG_KEEP_DAYS, 1)
    today = date.today()
    cutoff = today - timedelta(days=keep_days)

    log_dir = LOG_DIR
    compressed, deleted, skipped = 0, 0, 0

    for f in sorted(log_dir.iterdir()):
        m = _LOG_NAME_RE.match(f.name)
        if not m:
            continue
        try:
            file_date = date.fromisoformat(m.group(1))
        except ValueError:
            continue

        is_gz = m.group(2) == ".gz"

        # ── 步骤 1：压缩未压缩的已切割日志（今天的 app.log 不在此列） ──────
        if not is_gz and file_date < today:
            gz_path = f.with_suffix(f.suffix + ".gz")
            if gz_path.exists():
                # 已有对应压缩文件，只删明文
                f.unlink()
                skipped += 1
            else:
                try:
                    with open(f, "rb") as fi, gzip.open(gz_path, "wb") as fo:
                        shutil.copyfileobj(fi, fo)
                    f.unlink()
                    compressed += 1
                    logger.info("[LogCleanup] 压缩 %s → %s", f.name, gz_path.name)
                except Exception:
                    logger.exception("[LogCleanup] 压缩失败: %s", f.name)

        # ── 步骤 2：删除超期文件（压缩和明文都删） ───────────────────────────
        elif file_date < cutoff:
            try:
                f.unlink()
                deleted += 1
                logger.info("[LogCleanup] 删除过期日志: %s (date=%s < cutoff=%s)", f.name, file_date, cutoff)
            except Exception:
                logger.exception("[LogCleanup] 删除失败: %s", f.name)

    logger.info(
        "[LogCleanup] 完成 | keep_days=%d cutoff=%s compressed=%d deleted=%d skipped=%d",
        keep_days, cutoff, compressed, deleted, skipped,
    )


async def _run_cleanup_once_async() -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_cleanup_once)


async def start_log_cleanup_worker() -> None:
    global _worker_task, _stop_event
    if _worker_task and not _worker_task.done():
        return
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info("[LogCleanup] worker 已启动 | startup_delay=%ds interval=%dh",
                _STARTUP_DELAY_SECS, _INTERVAL_SECS // 3600)


async def stop_log_cleanup_worker() -> None:
    global _worker_task, _stop_event
    if _stop_event:
        _stop_event.set()
    if _worker_task:
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
    _stop_event = None
    logger.info("[LogCleanup] worker 已停止")


async def _worker_loop() -> None:
    # 延迟首次执行，等待应用完全就绪
    try:
        await asyncio.wait_for(_stop_event.wait(), timeout=_STARTUP_DELAY_SECS)  # type: ignore
        return  # stop_event 在延迟期间触发，直接退出
    except asyncio.TimeoutError:
        pass

    while _stop_event and not _stop_event.is_set():
        try:
            await _run_cleanup_once_async()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[LogCleanup] 清理失败")

        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=_INTERVAL_SECS)
        except asyncio.TimeoutError:
            continue
