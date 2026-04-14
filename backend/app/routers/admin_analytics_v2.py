"""管理端：数据分析"""
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.analytics_daily import AnalyticsDaily
from app.models.analytics_model_daily import AnalyticsModelDaily
from app.models.message import Message
from app.models.user import User
from app.services.analytics_rollup_service import (
    ensure_rollup_coverage,
    ensure_rollups,
    parse_datetime_range,
    parse_datetime_value,
    resolve_rollup_day_range,
)
from app.utils.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/analytics", tags=["管理端数据分析"])


def _parse_dt(val: str | None) -> datetime | None:
    return parse_datetime_value(val)


def _parse_range(start_date: str | None, end_date: str | None):
    return parse_datetime_range(start_date, end_date)


def _date_filter(col, s, e):
    conds = []
    if s:
        conds.append(col >= s)
    if e:
        conds.append(col < e)
    return conds


@router.get("/overview")
async def overview(
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    s, e = _parse_range(start_date, end_date)
    today = datetime.utcnow().date()

    if start_date or end_date:
        start_day, end_day = resolve_rollup_day_range(start_date, end_date, default_days=1)
        await ensure_rollups(db, start_day, end_day, include_models=False)
        totals_stmt = (
            select(
                func.coalesce(func.sum(AnalyticsDaily.new_users), 0),
                func.coalesce(func.sum(AnalyticsDaily.conversation_count), 0),
                func.coalesce(func.sum(AnalyticsDaily.message_count), 0),
                func.coalesce(func.sum(AnalyticsDaily.input_tokens), 0),
                func.coalesce(func.sum(AnalyticsDaily.output_tokens), 0),
                func.coalesce(func.sum(AnalyticsDaily.cost_usd), 0),
            )
            .where(AnalyticsDaily.stat_date >= start_day)
            .where(AnalyticsDaily.stat_date <= end_day)
        )
    else:
        await ensure_rollup_coverage(db, include_models=False)
        totals_stmt = select(
            func.coalesce(func.sum(AnalyticsDaily.new_users), 0),
            func.coalesce(func.sum(AnalyticsDaily.conversation_count), 0),
            func.coalesce(func.sum(AnalyticsDaily.message_count), 0),
            func.coalesce(func.sum(AnalyticsDaily.input_tokens), 0),
            func.coalesce(func.sum(AnalyticsDaily.output_tokens), 0),
            func.coalesce(func.sum(AnalyticsDaily.cost_usd), 0),
        )

    totals = (await db.execute(totals_stmt)).one()

    await ensure_rollups(db, today, today, include_models=False)
    today_rollup = await db.get(AnalyticsDaily, today)

    active_stmt = select(func.count(distinct(Message.user_id)))
    for condition in _date_filter(Message.created_at, s, e):
        active_stmt = active_stmt.where(condition)
    active_users = (await db.execute(active_stmt)).scalar() or 0

    return success({
        "user_total": totals[0],
        "user_today": today_rollup.new_users if today_rollup else 0,
        "active_users": active_users,
        "active_users_today": today_rollup.active_users if today_rollup else 0,
        "conversation_total": totals[1],
        "conversation_today": today_rollup.conversation_count if today_rollup else 0,
        "message_total": totals[2],
        "message_today": today_rollup.message_count if today_rollup else 0,
        "token_input_total": totals[3],
        "token_output_total": totals[4],
        "cost_usd_total": float(totals[5] or 0),
        "cost_usd_today": float(today_rollup.cost_usd or 0) if today_rollup else 0.0,
    })


@router.get("/trends")
async def trends(
    days: int = Query(14, ge=1, le=90),
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    start_day, end_day = resolve_rollup_day_range(start_date, end_date, default_days=days)
    await ensure_rollups(db, start_day, end_day, include_models=False)
    rows = (
        await db.execute(
            select(AnalyticsDaily)
            .where(AnalyticsDaily.stat_date >= start_day)
            .where(AnalyticsDaily.stat_date <= end_day)
            .order_by(AnalyticsDaily.stat_date.asc())
        )
    ).scalars().all()

    return success({
        "items": [
            {
                "date": row.stat_date.isoformat(),
                "new_users": row.new_users,
                "active_users": row.active_users,
                "conversations": row.conversation_count,
                "messages": row.message_count,
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "cost_usd": float(row.cost_usd or 0),
            }
            for row in rows
        ]
    })


@router.get("/top-users")
async def top_users(
    top_n: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=90),
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    s, e = _parse_range(start_date, end_date)
    since = s or (datetime.utcnow() - timedelta(days=days))
    rows = (
        await db.execute(
            select(
                Message.user_id,
                User.nickname,
                User.phone,
                func.count().label("msg_count"),
                func.count(distinct(Message.conversation_id)).label("conv_count"),
            )
            .outerjoin(User, Message.user_id == User.id)
            .where(Message.created_at >= since)
            .where(Message.created_at < e if e else True)
            .group_by(Message.user_id, User.nickname, User.phone)
            .order_by(func.count().desc())
            .limit(top_n)
        )
    ).all()
    items = [
        {
            "rank": index + 1,
            "user_id": row.user_id,
            "nickname": row.nickname or "",
            "phone": row.phone or "",
            "msg_count": row.msg_count,
            "conv_count": row.conv_count,
        }
        for index, row in enumerate(rows)
    ]
    return success({"items": items, "days": days})


@router.get("/model-stats")
async def model_stats(
    days: int = Query(7, ge=1, le=90),
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    start_day, end_day = resolve_rollup_day_range(start_date, end_date, default_days=days)
    await ensure_rollups(db, start_day, end_day, include_models=True)
    rows = (
        await db.execute(
            select(
                AnalyticsModelDaily.model,
                func.coalesce(func.sum(AnalyticsModelDaily.request_count), 0).label("count"),
                func.coalesce(func.sum(AnalyticsModelDaily.user_count), 0).label("user_count"),
                func.coalesce(func.sum(AnalyticsModelDaily.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).label("cost_usd"),
            )
            .where(AnalyticsModelDaily.stat_date >= start_day)
            .where(AnalyticsModelDaily.stat_date <= end_day)
            .group_by(AnalyticsModelDaily.model)
            .order_by(func.coalesce(func.sum(AnalyticsModelDaily.request_count), 0).desc())
        )
    ).all()
    items = [
        {
            "model": row.model or "unknown",
            "count": row.count,
            "user_count": row.user_count,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "cost_usd": float(row.cost_usd or 0),
        }
        for row in rows
    ]
    return success({"items": items, "days": days})


@router.get("/hot-questions")
async def hot_questions(
    top_n: int = Query(20, ge=1, le=50),
    days: int = Query(7, ge=1),
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    s, e = _parse_range(start_date, end_date)
    since = s or (datetime.utcnow() - timedelta(days=days))
    rows = (
        await db.execute(
            select(
                Message.content,
                func.count().label("cnt"),
                func.count(distinct(Message.user_id)).label("user_cnt"),
            )
            .where(Message.role == "user", Message.created_at >= since)
            .where(Message.created_at < e if e else True)
            .group_by(Message.content)
            .order_by(func.count().desc())
            .limit(top_n)
        )
    ).all()
    items = [
        {"rank": index + 1, "question": row[0][:200], "count": row[1], "user_count": row[2]}
        for index, row in enumerate(rows)
    ]
    return success({"items": items, "days": days})
