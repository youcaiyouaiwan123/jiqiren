"""管理端：Token 计费统计"""
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.analytics_daily import AnalyticsDaily
from app.models.analytics_model_daily import AnalyticsModelDaily
from app.models.token_usage import TokenUsage
from app.models.user import User
from app.services.analytics_rollup_service import (
    parse_datetime_range,
    refresh_recent_rollups_best_effort,
    refresh_rollups_for_range_best_effort,
    resolve_rollup_day_range,
)
from app.utils.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/token-usage", tags=["管理端Token计费"])


def _apply_direct_filters(stmt, start_dt, end_dt, keyword, model):
    if start_dt:
        stmt = stmt.where(TokenUsage.created_at >= start_dt)
    if end_dt:
        stmt = stmt.where(TokenUsage.created_at < end_dt)
    if model:
        stmt = stmt.where(TokenUsage.model == model)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(User.nickname.like(like) | User.phone.like(like))
    return stmt


@router.get("/summary")
async def token_summary(
    start_date: str | None = None,
    end_date: str | None = None,
    keyword: str | None = None,
    model: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not keyword:
        if start_date or end_date:
            start_day, end_day = resolve_rollup_day_range(start_date, end_date, default_days=30)
            await refresh_rollups_for_range_best_effort(db, start_day, end_day, include_models=bool(model))
        else:
            await refresh_recent_rollups_best_effort(db, include_models=True)
            start_day = end_day = None

        if model:
            stmt = select(
                func.coalesce(func.sum(AnalyticsModelDaily.input_tokens), 0).label("total_input"),
                func.coalesce(func.sum(AnalyticsModelDaily.output_tokens), 0).label("total_output"),
                func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).label("total_cost"),
                func.coalesce(func.sum(AnalyticsModelDaily.request_count), 0).label("request_count"),
            ).where(AnalyticsModelDaily.model == model)
            if start_day and end_day:
                stmt = stmt.where(AnalyticsModelDaily.stat_date >= start_day, AnalyticsModelDaily.stat_date <= end_day)
        else:
            stmt = select(
                func.coalesce(func.sum(AnalyticsDaily.input_tokens), 0).label("total_input"),
                func.coalesce(func.sum(AnalyticsDaily.output_tokens), 0).label("total_output"),
                func.coalesce(func.sum(AnalyticsDaily.cost_usd), 0).label("total_cost"),
                func.coalesce(func.sum(AnalyticsDaily.request_count), 0).label("request_count"),
            )
            if start_day and end_day:
                stmt = stmt.where(AnalyticsDaily.stat_date >= start_day, AnalyticsDaily.stat_date <= end_day)

        row = (await db.execute(stmt)).one()
        return success({
            "total_input_tokens": row.total_input,
            "total_output_tokens": row.total_output,
            "total_cost_usd": float(row.total_cost or 0),
            "request_count": row.request_count,
        })

    start_dt, end_dt = parse_datetime_range(start_date, end_date)
    stmt = select(
        func.coalesce(func.sum(TokenUsage.input_tokens), 0).label("total_input"),
        func.coalesce(func.sum(TokenUsage.output_tokens), 0).label("total_output"),
        func.coalesce(func.sum(TokenUsage.cost_usd), 0).label("total_cost"),
        func.count().label("request_count"),
    ).outerjoin(User, TokenUsage.user_id == User.id)
    stmt = _apply_direct_filters(stmt, start_dt, end_dt, keyword, model)
    row = (await db.execute(stmt)).one()
    return success({
        "total_input_tokens": row.total_input,
        "total_output_tokens": row.total_output,
        "total_cost_usd": float(row.total_cost or 0),
        "request_count": row.request_count,
    })


@router.get("/cost-by-model")
async def cost_by_model(
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if start_date or end_date:
        start_day, end_day = resolve_rollup_day_range(start_date, end_date, default_days=30)
        await refresh_rollups_for_range_best_effort(db, start_day, end_day, include_models=True)
        stmt = (
            select(
                AnalyticsModelDaily.model,
                func.coalesce(func.sum(AnalyticsModelDaily.request_count), 0).label("count"),
                func.coalesce(func.sum(AnalyticsModelDaily.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).label("cost_usd"),
            )
            .where(AnalyticsModelDaily.stat_date >= start_day)
            .where(AnalyticsModelDaily.stat_date <= end_day)
            .group_by(AnalyticsModelDaily.model)
            .order_by(func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).desc())
        )
    else:
        await refresh_recent_rollups_best_effort(db, include_models=True)
        stmt = (
            select(
                AnalyticsModelDaily.model,
                func.coalesce(func.sum(AnalyticsModelDaily.request_count), 0).label("count"),
                func.coalesce(func.sum(AnalyticsModelDaily.input_tokens), 0).label("input_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.output_tokens), 0).label("output_tokens"),
                func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).label("cost_usd"),
            )
            .group_by(AnalyticsModelDaily.model)
            .order_by(func.coalesce(func.sum(AnalyticsModelDaily.cost_usd), 0).desc())
        )

    rows = (await db.execute(stmt)).all()
    return success({
        "items": [
            {
                "model": row.model or "unknown",
                "count": row.count,
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "cost_usd": float(row.cost_usd or 0),
            }
            for row in rows
        ]
    })


@router.get("/daily")
async def token_daily(
    days: int = Query(7, ge=1, le=90),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    start_day, end_day = resolve_rollup_day_range(None, None, default_days=days)
    await refresh_rollups_for_range_best_effort(db, start_day, end_day, include_models=False)
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
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "cost_usd": float(row.cost_usd or 0),
                "request_count": row.request_count,
            }
            for row in rows
        ]
    })


@router.get("/list")
async def token_usage_list(
    start_date: str | None = None,
    end_date: str | None = None,
    keyword: str | None = Query(None, description="用户昵称或手机号模糊搜索"),
    model: str | None = None,
    page_params: PageParams = Depends(),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    start_dt, end_dt = parse_datetime_range(start_date, end_date)
    stmt = (
        select(
            TokenUsage.id,
            TokenUsage.user_id,
            User.nickname,
            User.phone,
            TokenUsage.model,
            TokenUsage.input_tokens,
            TokenUsage.output_tokens,
            TokenUsage.cost_usd,
            TokenUsage.created_at,
        )
        .outerjoin(User, TokenUsage.user_id == User.id)
    )
    count_stmt = select(func.count()).select_from(TokenUsage).outerjoin(User, TokenUsage.user_id == User.id)

    stmt = _apply_direct_filters(stmt, start_dt, end_dt, keyword, model)
    count_stmt = _apply_direct_filters(count_stmt, start_dt, end_dt, keyword, model)

    total = (await db.execute(count_stmt)).scalar() or 0
    rows = (
        await db.execute(
            stmt.order_by(TokenUsage.created_at.desc())
            .offset(page_params.offset)
            .limit(page_params.page_size)
        )
    ).all()

    return success({
        "items": [
            {
                "id": row.id,
                "user_id": row.user_id,
                "nickname": row.nickname or "",
                "phone": row.phone or "",
                "model": row.model or "",
                "input_tokens": row.input_tokens,
                "output_tokens": row.output_tokens,
                "cost_usd": float(row.cost_usd) if row.cost_usd else 0.0,
                "created_at": row.created_at.isoformat() if row.created_at else "",
            }
            for row in rows
        ],
        "total": total,
        "page": page_params.page,
        "page_size": page_params.page_size,
    })


@router.get("/models")
async def token_usage_models(
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(select(TokenUsage.model).where(TokenUsage.model.isnot(None)).distinct())
    ).scalars().all()
    return success({"models": sorted(rows)})
