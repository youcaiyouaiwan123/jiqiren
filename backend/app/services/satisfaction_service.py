"""满意度评分服务：评分逻辑 + Redis 延迟队列工具函数"""
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.redis import get_redis
from app.models.message import Message
from app.models.message_feedback import MessageFeedback

logger = logging.getLogger(__name__)

PENDING_KEY = "satisfaction:pending"

THANKS_WORDS = {
    "谢谢", "感谢", "非常感谢", "太感谢", "谢谢你", "谢谢了",
    "thank", "thanks", "解决了", "完美", "明白了", "懂了", "好的谢谢",
}

FALLBACK_PATTERNS = [
    "很抱歉，我无法",
    "我没有相关信息",
    "建议联系人工客服",
    "暂时无法回答",
    "AI 暂时繁忙",
]

RAPID_QUESTION_WINDOW_SECS = 60
RAPID_QUESTION_THRESHOLD = 3


async def enqueue_satisfaction_scoring(
    *,
    ai_message_id: int,
    conv_id: int,
    user_id: int,
    delay_secs: int = 600,
) -> None:
    redis = get_redis(required=False)
    if redis is None:
        return
    score = time.time() + delay_secs
    await redis.zadd(PENDING_KEY, {str(ai_message_id): score})


async def cancel_satisfaction_scoring(ai_message_id: int) -> None:
    redis = get_redis(required=False)
    if redis is None:
        return
    await redis.zrem(PENDING_KEY, str(ai_message_id))


async def pop_due_message_ids(batch: int = 20) -> list[int]:
    redis = get_redis(required=False)
    if redis is None:
        return []
    now = time.time()
    items = await redis.zrangebyscore(PENDING_KEY, min=0, max=now, start=0, num=batch)
    if not items:
        return []
    pipe = redis.pipeline(transaction=False)
    for item in items:
        pipe.zrem(PENDING_KEY, item)
    await pipe.execute()
    return [int(item) for item in items]


def _contains_thanks(text: str) -> bool:
    lower = text.lower()
    return any(w in lower for w in THANKS_WORDS)


def _is_fallback_response(content: str) -> bool:
    return any(p in content for p in FALLBACK_PATTERNS)


async def _compute_level(ai_msg: Message, db: AsyncSession) -> str:
    # 显式反馈优先
    fb = (await db.execute(
        select(MessageFeedback).where(MessageFeedback.message_id == ai_msg.id)
    )).scalar_one_or_none()
    if fb and fb.rating == "like":
        return "high"
    if fb and fb.rating == "dislike":
        return "low"

    # AI 内容为兜底回复 → 低
    if _is_fallback_response(ai_msg.content or ""):
        return "low"

    # 查询该 AI 消息之后的用户消息（10 分钟内）
    window_end = ai_msg.created_at + timedelta(seconds=600)
    next_user_msgs = (await db.execute(
        select(Message)
        .where(
            Message.conversation_id == ai_msg.conversation_id,
            Message.role == "user",
            Message.created_at > ai_msg.created_at,
            Message.created_at <= window_end,
        )
        .order_by(Message.created_at.asc())
        .limit(10)
    )).scalars().all()

    if next_user_msgs:
        # 感谢词检测（第一条）
        if _contains_thanks(next_user_msgs[0].content or ""):
            return "high"

        # 快速追问（60s 内 ≥ 3 条）
        rapid = [
            m for m in next_user_msgs
            if (m.created_at - ai_msg.created_at).total_seconds() <= RAPID_QUESTION_WINDOW_SECS
        ]
        if len(rapid) >= RAPID_QUESTION_THRESHOLD:
            return "low"

    return "medium"


async def score_and_persist(ai_message_id: int) -> None:
    async with async_session() as db:
        ai_msg = await db.get(Message, ai_message_id)
        if not ai_msg:
            logger.warning("[满意度] 消息不存在，跳过 | ai_msg_id=%s", ai_message_id)
            return

        # 已评分则跳过
        existing = (await db.execute(
            select(MessageFeedback).where(MessageFeedback.message_id == ai_message_id)
        )).scalar_one_or_none()
        if existing and existing.satisfaction_level:
            return

        level = await _compute_level(ai_msg, db)
        now = datetime.utcnow()

        if existing:
            existing.satisfaction_level = level
            existing.scored_at = now
        else:
            db.add(MessageFeedback(
                message_id=ai_message_id,
                user_id=ai_msg.user_id,
                conversation_id=ai_msg.conversation_id,
                satisfaction_level=level,
                scored_at=now,
            ))
        await db.commit()
        logger.info("[满意度] 评分完成 | ai_msg_id=%s level=%s", ai_message_id, level)

    await _update_feishu(ai_message_id, level)


async def score_explicit(
    *,
    ai_message_id: int,
    user_id: int,
    conv_id: int,
    rating: str,
    db: AsyncSession,
) -> str:
    """用户主动点赞/踩时立即更新 DB，返回最终 satisfaction_level。"""
    level = "high" if rating == "like" else "low"
    now = datetime.utcnow()

    existing = (await db.execute(
        select(MessageFeedback).where(MessageFeedback.message_id == ai_message_id)
    )).scalar_one_or_none()
    if existing:
        existing.rating = rating
        existing.satisfaction_level = level
        existing.scored_at = now
    else:
        db.add(MessageFeedback(
            message_id=ai_message_id,
            user_id=user_id,
            conversation_id=conv_id,
            rating=rating,
            satisfaction_level=level,
            scored_at=now,
        ))
    await db.commit()

    await cancel_satisfaction_scoring(ai_message_id)
    await _update_feishu(ai_message_id, level)
    return level


async def _update_feishu(ai_message_id: int, level: str) -> None:
    level_label = {"high": "高", "medium": "中", "low": "低"}.get(level, level)
    try:
        async with async_session() as db:
            ai_msg = await db.get(Message, ai_message_id)
            if not ai_msg or not ai_msg.feishu_record_id:
                return

            from app.models.feishu_route import FeishuRoute
            from app.services.feishu_sync_runtime import _select_route
            route = await _select_route("conversation_record")
            if not route:
                return

            from app.services.feishu_service import update_bitable_record
            await update_bitable_record(
                app_id=route.app_id,
                app_secret=route.app_secret,
                app_token=route.app_token,
                table_id=route.table_id,
                record_id=ai_msg.feishu_record_id,
                fields={"satisfaction_level": level_label},
            )
            logger.info("[满意度] 飞书更新完成 | ai_msg_id=%s level=%s", ai_message_id, level_label)
    except Exception:
        logger.exception("[满意度] 飞书更新失败 | ai_msg_id=%s", ai_message_id)
