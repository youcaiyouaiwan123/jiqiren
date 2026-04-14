from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from app.config import get_settings
from app.core.database import async_session
from app.services.analytics_rollup_service import ensure_rollup_coverage

logger = logging.getLogger(__name__)

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


async def _refresh_rollups_once() -> None:
    settings = get_settings()
    async with async_session() as session:
        start_day, end_day = await ensure_rollup_coverage(
            session,
            include_models=True,
            recent_days=settings.ANALYTICS_ROLLUP_RECENT_DAYS,
        )
        await session.commit()
    logger.info(
        "[Analytics Rollup] refreshed | start=%s end=%s recent_days=%s at=%s",
        start_day,
        end_day,
        settings.ANALYTICS_ROLLUP_RECENT_DAYS,
        datetime.utcnow().isoformat(timespec="seconds"),
    )


async def start_analytics_rollup_worker() -> None:
    global _worker_task, _stop_event
    if _worker_task and not _worker_task.done():
        return
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info("[Analytics Rollup] worker started")


async def stop_analytics_rollup_worker() -> None:
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
    logger.info("[Analytics Rollup] worker stopped")


async def _worker_loop() -> None:
    settings = get_settings()
    interval_seconds = max(settings.ANALYTICS_ROLLUP_REFRESH_MINUTES, 1) * 60

    while _stop_event and not _stop_event.is_set():
        try:
            await _refresh_rollups_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[Analytics Rollup] refresh failed")

        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
