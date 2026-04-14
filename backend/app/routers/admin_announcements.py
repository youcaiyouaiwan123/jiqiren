"""管理端：公告管理"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.announcement import Announcement
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update
from app.utils.response import success

router = APIRouter(prefix="/api/admin/announcements", tags=["管理端-公告管理"])


class AnnouncementBody(BaseModel):
    title: str | None = None
    content: str | None = None
    type: str | None = None
    is_pinned: int | None = None
    status: str | None = None
    publish_at: str | None = None
    expire_at: str | None = None


@router.get("")
async def list_announcements(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, Announcement, page=pager.page, page_size=pager.page_size, order_by=Announcement.created_at.desc())


@router.post("")
async def create_announcement(body: AnnouncementBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["created_by"] = admin["admin_id"]
    return await generic_create(db, Announcement, data)


@router.put("/{pk}")
async def update_announcement(pk: int, body: AnnouncementBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_update(db, Announcement, pk, body.model_dump(exclude_none=True))


@router.put("/{pk}/publish")
async def publish_announcement(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Announcement, pk)
    if not row:
        from app.utils.response import fail
        return fail(1004, "资源不存在")
    row.status = "published"
    await db.flush()
    await db.refresh(row)
    from app.utils.crud import row_to_dict
    return success(row_to_dict(row))


@router.delete("/{pk}")
async def delete_announcement(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, Announcement, pk)
