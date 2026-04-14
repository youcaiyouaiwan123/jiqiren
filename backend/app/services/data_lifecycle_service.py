from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.token_usage import TokenUsage


@dataclass(frozen=True)
class ArchiveReport:
    message_cutoff: datetime
    token_usage_cutoff: datetime
    conversation_cutoff: datetime
    message_candidates: int
    token_usage_candidates: int
    conversation_candidates: int


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
