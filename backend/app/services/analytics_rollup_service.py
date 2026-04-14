from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics_daily import AnalyticsDaily
from app.models.analytics_model_daily import AnalyticsModelDaily
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.token_usage import TokenUsage
from app.models.user import User


def parse_datetime_value(value: str | None) -> datetime | None:
    if not value:
        return None

    raw = value.strip()
    if not raw:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def parse_datetime_range(
    start_date: str | None,
    end_date: str | None,
    *,
    default_days: int | None = None,
) -> tuple[datetime | None, datetime | None]:
    start_dt = parse_datetime_value(start_date)
    end_dt = parse_datetime_value(end_date)

    if end_dt and len((end_date or "").strip()) <= 10:
        end_dt += timedelta(days=1)

    if default_days is None or start_dt or end_dt:
        return start_dt, end_dt

    end_dt = datetime.combine(datetime.utcnow().date() + timedelta(days=1), time.min)
    start_dt = end_dt - timedelta(days=default_days)
    return start_dt, end_dt


def resolve_rollup_day_range(
    start_date: str | None,
    end_date: str | None,
    *,
    default_days: int,
) -> tuple[date, date]:
    start_dt, end_dt = parse_datetime_range(start_date, end_date, default_days=default_days)
    if start_dt is None and end_dt is None:
        end_day = datetime.utcnow().date()
        return end_day - timedelta(days=default_days - 1), end_day

    if end_dt is None:
        end_dt = datetime.combine(datetime.utcnow().date() + timedelta(days=1), time.min)
    if start_dt is None:
        start_dt = end_dt - timedelta(days=default_days)

    start_day = start_dt.date()
    end_day = (end_dt - timedelta(microseconds=1)).date()
    if end_day < start_day:
        end_day = start_day
    return start_day, end_day


def day_range_bounds(start_day: date, end_day: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day + timedelta(days=1), time.min)
    return start_dt, end_dt


def _coerce_day(value) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    raise TypeError(f"Unsupported day value: {value!r}")


def _empty_daily_row(stat_date: date) -> dict:
    return {
        "stat_date": stat_date,
        "new_users": 0,
        "active_users": 0,
        "conversation_count": 0,
        "message_count": 0,
        "request_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": Decimal("0"),
    }


async def rebuild_daily_rollups(db: AsyncSession, start_day: date, end_day: date) -> None:
    start_dt, end_dt = day_range_bounds(start_day, end_day)
    daily_rows: dict[date, dict] = {}

    cursor = start_day
    while cursor <= end_day:
        daily_rows[cursor] = _empty_daily_row(cursor)
        cursor += timedelta(days=1)

    user_rows = (
        await db.execute(
            select(
                func.date(User.created_at).label("stat_date"),
                func.count(User.id).label("new_users"),
            )
            .where(User.created_at >= start_dt, User.created_at < end_dt)
            .group_by(func.date(User.created_at))
        )
    ).all()
    for row in user_rows:
        daily_rows[_coerce_day(row.stat_date)]["new_users"] = row.new_users

    conversation_rows = (
        await db.execute(
            select(
                func.date(Conversation.created_at).label("stat_date"),
                func.count(Conversation.id).label("conversation_count"),
            )
            .where(Conversation.created_at >= start_dt, Conversation.created_at < end_dt)
            .group_by(func.date(Conversation.created_at))
        )
    ).all()
    for row in conversation_rows:
        daily_rows[_coerce_day(row.stat_date)]["conversation_count"] = row.conversation_count

    message_rows = (
        await db.execute(
            select(
                func.date(Message.created_at).label("stat_date"),
                func.count(Message.id).label("message_count"),
                func.count(func.distinct(Message.user_id)).label("active_users"),
            )
            .where(Message.created_at >= start_dt, Message.created_at < end_dt)
            .group_by(func.date(Message.created_at))
        )
    ).all()
    for row in message_rows:
        bucket = daily_rows[_coerce_day(row.stat_date)]
        bucket["message_count"] = row.message_count
        bucket["active_users"] = row.active_users

    token_rows = (
        await db.execute(
            select(
                func.date(TokenUsage.created_at).label("stat_date"),
                func.count(TokenUsage.id).label("request_count"),
                func.coalesce(func.sum(TokenUsage.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(TokenUsage.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(TokenUsage.cost_usd), 0).label("cost_usd"),
            )
            .where(TokenUsage.created_at >= start_dt, TokenUsage.created_at < end_dt)
            .group_by(func.date(TokenUsage.created_at))
        )
    ).all()
    for row in token_rows:
        bucket = daily_rows[_coerce_day(row.stat_date)]
        bucket["request_count"] = row.request_count
        bucket["input_tokens"] = row.input_tokens
        bucket["output_tokens"] = row.output_tokens
        bucket["cost_usd"] = row.cost_usd or Decimal("0")

    await db.execute(
        delete(AnalyticsDaily).where(
            AnalyticsDaily.stat_date >= start_day,
            AnalyticsDaily.stat_date <= end_day,
        )
    )
    await db.execute(insert(AnalyticsDaily), list(daily_rows.values()))


async def rebuild_model_rollups(db: AsyncSession, start_day: date, end_day: date) -> None:
    start_dt, end_dt = day_range_bounds(start_day, end_day)

    model_rows = (
        await db.execute(
            select(
                func.date(TokenUsage.created_at).label("stat_date"),
                func.coalesce(TokenUsage.model, "unknown").label("model"),
                func.count(TokenUsage.id).label("request_count"),
                func.count(func.distinct(TokenUsage.user_id)).label("user_count"),
                func.coalesce(func.sum(TokenUsage.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(TokenUsage.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(TokenUsage.cost_usd), 0).label("cost_usd"),
            )
            .where(TokenUsage.created_at >= start_dt, TokenUsage.created_at < end_dt)
            .group_by(func.date(TokenUsage.created_at), func.coalesce(TokenUsage.model, "unknown"))
        )
    ).all()

    await db.execute(
        delete(AnalyticsModelDaily).where(
            AnalyticsModelDaily.stat_date >= start_day,
            AnalyticsModelDaily.stat_date <= end_day,
        )
    )

    if not model_rows:
        return

    payload = [
        {
            "stat_date": _coerce_day(row.stat_date),
            "model": row.model,
            "request_count": row.request_count,
            "user_count": row.user_count,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "cost_usd": row.cost_usd or Decimal("0"),
        }
        for row in model_rows
    ]
    await db.execute(insert(AnalyticsModelDaily), payload)


async def ensure_rollups(
    db: AsyncSession,
    start_day: date,
    end_day: date,
    *,
    include_models: bool = True,
) -> None:
    await rebuild_daily_rollups(db, start_day, end_day)
    if include_models:
        await rebuild_model_rollups(db, start_day, end_day)


async def ensure_rollup_coverage(
    db: AsyncSession,
    *,
    include_models: bool = True,
    recent_days: int = 7,
) -> tuple[date, date]:
    today = datetime.utcnow().date()
    base_mins = []
    for model in (User, Conversation, Message, TokenUsage):
        first_created_at = (await db.execute(select(func.min(model.created_at)))).scalar_one_or_none()
        if first_created_at:
            base_mins.append(first_created_at.date())

    base_start = min(base_mins) if base_mins else today
    rollup_min, rollup_max = (
        await db.execute(select(func.min(AnalyticsDaily.stat_date), func.max(AnalyticsDaily.stat_date)))
    ).one()

    if rollup_min is None or rollup_max is None or rollup_min > base_start:
        await ensure_rollups(db, base_start, today, include_models=include_models)
        return base_start, today

    if rollup_max < today:
        await ensure_rollups(db, rollup_max + timedelta(days=1), today, include_models=include_models)

    recent_start = max(base_start, today - timedelta(days=max(recent_days, 1) - 1))
    await ensure_rollups(db, recent_start, today, include_models=include_models)
    return base_start, today
