from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from app.config import get_settings
from app.core.database import async_session
from app.services.data_lifecycle_service import execute_archive

logger = logging.getLogger(__name__)

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


async def _run_archive_once() -> None:
    async with async_session() as session:
        result = await execute_archive(session)
    logger.info(
        "[Archive] done | msgs=%d tu=%d convs=%d elapsed=%.1fs at=%s",
        result.messages_archived,
        result.token_usage_archived,
        result.conversations_archived,
        result.duration_seconds,
        datetime.utcnow().isoformat(timespec="seconds"),
    )


async def start_archive_worker() -> None:
    global _worker_task, _stop_event
    settings = get_settings()
    if not settings.ARCHIVE_ENABLED:
        logger.info("[Archive] worker disabled (ARCHIVE_ENABLED=false)")
        return
    if _worker_task and not _worker_task.done():
        return
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info(
        "[Archive] worker started | interval=%dh batch=%d",
        settings.ARCHIVE_INTERVAL_HOURS,
        settings.ARCHIVE_BATCH_SIZE,
    )


async def stop_archive_worker() -> None:
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
    logger.info("[Archive] worker stopped")


async def _worker_loop() -> None:
    settings = get_settings()
    interval_seconds = max(settings.ARCHIVE_INTERVAL_HOURS, 1) * 3600

    while _stop_event and not _stop_event.is_set():
        try:
            await _run_archive_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[Archive] run failed")

        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
