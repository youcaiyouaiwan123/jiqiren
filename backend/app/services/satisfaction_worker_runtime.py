"""满意度评分 Worker：每分钟轮询到期条目，触发评分并写入 DB + 飞书"""
import asyncio
import logging

from app.core.redis import get_redis
from app.services.satisfaction_service import pop_due_message_ids, score_and_persist

logger = logging.getLogger(__name__)

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


async def start_satisfaction_worker() -> None:
    global _worker_task, _stop_event
    if _worker_task and not _worker_task.done():
        return
    redis = get_redis(required=False)
    if redis is None:
        logger.warning("[满意度 Worker] Redis 不可用，worker 未启动")
        return
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info("[满意度 Worker] 已启动")


async def stop_satisfaction_worker() -> None:
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
    logger.info("[满意度 Worker] 已停止")


async def _worker_loop() -> None:
    while _stop_event and not _stop_event.is_set():
        try:
            ids = await pop_due_message_ids(batch=20)
            for ai_msg_id in ids:
                try:
                    await score_and_persist(ai_msg_id)
                except Exception:
                    logger.exception("[满意度 Worker] 单条评分失败 | ai_msg_id=%s", ai_msg_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[满意度 Worker] 主循环异常")
        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass
