"""用户端公开接口：公告、套餐列表"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.announcement import Announcement
from app.models.plan import Plan
from app.utils.crud import row_to_dict
from app.utils.response import success

router = APIRouter(prefix="/api", tags=["用户端公开"])


@router.get("/announcements")
async def active_announcements(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    stmt = (
        select(Announcement)
        .where(
            Announcement.status == "published",
        )
        .order_by(Announcement.is_pinned.desc(), Announcement.publish_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    items = [row_to_dict(r, exclude={"created_by"}) for r in rows]
    return success({"list": items})


@router.get("/plans")
async def active_plans(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(Plan).where(Plan.is_active == 1).order_by(Plan.sort_order.asc())
        )
    ).scalars().all()
    items = [row_to_dict(r) for r in rows]
    return success({"list": items})
