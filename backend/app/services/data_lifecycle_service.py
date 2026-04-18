from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.conversation import Conversation
from app.models.conversation_archive import ConversationArchive
from app.models.message import Message
from app.models.message_archive import MessageArchive
from app.models.token_usage import TokenUsage
from app.models.token_usage_archive import TokenUsageArchive


@dataclass(frozen=True)
class ArchiveReport:
    message_cutoff: datetime
    token_usage_cutoff: datetime
    conversation_cutoff: datetime
    message_candidates: int
    token_usage_candidates: int
    conversation_candidates: int


@dataclass(frozen=True)
class ArchiveResult:
    messages_archived: int
    token_usage_archived: int
    conversations_archived: int
    duration_seconds: float


def build_archive_cutoffs(now: datetime | None = None) -> tuple[datetime, datetime, datetime]:
    settings = get_settings()
    now = now or datetime.utcnow()
    return (
        now - timedelta(days=max(settings.MESSAGE_ARCHIVE_AFTER_DAYS, 1)),
        now - timedelta(days=max(settings.TOKEN_USAGE_ARCHIVE_AFTER_DAYS, 1)),
        now - timedelta(days=max(settings.CONVERSATION_ARCHIVE_AFTER_DAYS, 1)),
    )


async def collect_archive_report(db: AsyncSession, now: datetime | None = None) -> ArchiveReport:
    message_cutoff, token_usage_cutoff, conversation_cutoff = build_archive_cutoffs(now)

    message_candidates = (
        await db.execute(select(func.count(Message.id)).where(Message.created_at < message_cutoff))
    ).scalar() or 0
    token_usage_candidates = (
        await db.execute(select(func.count(TokenUsage.id)).where(TokenUsage.created_at < token_usage_cutoff))
    ).scalar() or 0
    conversation_candidates = (
        await db.execute(select(func.count(Conversation.id)).where(Conversation.created_at < conversation_cutoff))
    ).scalar() or 0

    return ArchiveReport(
        message_cutoff=message_cutoff,
        token_usage_cutoff=token_usage_cutoff,
        conversation_cutoff=conversation_cutoff,
        message_candidates=message_candidates,
        token_usage_candidates=token_usage_candidates,
        conversation_candidates=conversation_candidates,
    )


async def execute_archive(
    db: AsyncSession,
    batch_size: int | None = None,
    now: datetime | None = None,
    dry_run: bool = False,
) -> ArchiveResult:
    """将超龄热区数据批量迁移至对应冷区归档表。

    迁移顺序：token_usage → messages → conversations
    先迁 token_usage/messages，最后迁 conversations，保持引用关系可追溯。
    每批次完成后立即 commit，减少锁持有时间，降低主库写压力。
    dry_run=True 时只统计候选行，不做实际迁移。
    """
    settings = get_settings()
    batch = batch_size or settings.ARCHIVE_BATCH_SIZE
    msg_cut, tu_cut, conv_cut = build_archive_cutoffs(now)
    t0 = time.monotonic()

    msgs_archived = await _archive_table(
        db=db,
        hot_model=Message,
        archive_model=MessageArchive,
        cutoff=msg_cut,
        batch_size=batch,
        dry_run=dry_run,
        col_names=[
            "id", "conversation_id", "user_id", "role", "content",
            "images", "docs", "input_tokens", "output_tokens", "feishu_synced", "created_at",
        ],
    )

    tu_archived = await _archive_table(
        db=db,
        hot_model=TokenUsage,
        archive_model=TokenUsageArchive,
        cutoff=tu_cut,
        batch_size=batch,
        dry_run=dry_run,
        col_names=["id", "user_id", "message_id", "model", "input_tokens", "output_tokens", "cost_usd", "created_at"],
    )

    conv_archived = await _archive_table(
        db=db,
        hot_model=Conversation,
        archive_model=ConversationArchive,
        cutoff=conv_cut,
        batch_size=batch,
        dry_run=dry_run,
        col_names=["id", "user_id", "title", "created_at", "updated_at"],
    )

    return ArchiveResult(
        messages_archived=msgs_archived,
        token_usage_archived=tu_archived,
        conversations_archived=conv_archived,
        duration_seconds=round(time.monotonic() - t0, 2),
    )


async def _archive_table(
    db: AsyncSession,
    hot_model,
    archive_model,
    cutoff: datetime,
    batch_size: int,
    dry_run: bool,
    col_names: list[str],
) -> int:
    """核心迁移逻辑：SELECT → INSERT archive → DELETE hot，按批次提交。"""
    total = 0
    hot_table = hot_model.__table__
    archive_table = archive_model.__table__

    while True:
        rows = (
            await db.execute(
                select(hot_table).where(hot_table.c.created_at < cutoff).limit(batch_size)
            )
        ).fetchall()

        if not rows:
            break

        if not dry_run:
            records = [dict(zip(col_names, row)) for row in rows]
            await db.execute(insert(archive_table).prefix_with("IGNORE").values(records))
            ids = [r[0] for r in rows]
            await db.execute(delete(hot_table).where(hot_table.c.id.in_(ids)))
            await db.commit()

        total += len(rows)

        if len(rows) < batch_size:
            break

    return total
