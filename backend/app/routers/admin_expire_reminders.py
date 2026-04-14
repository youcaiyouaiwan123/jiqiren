"""管理端：到期提醒设置"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.expire_reminder import ExpireReminderConfig
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update

router = APIRouter(prefix="/api/admin/expire-reminders", tags=["管理端-到期提醒"])


class ReminderBody(BaseModel):
    days_before: int | None = None
    channel: str | None = None
    template: str | None = None
    is_active: int | None = None


@router.get("")
async def list_reminders(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, ExpireReminderConfig, page=pager.page, page_size=pager.page_size)


@router.post("")
async def create_reminder(body: ReminderBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["created_by"] = admin["admin_id"]
    return await generic_create(db, ExpireReminderConfig, data)


@router.put("/{pk}")
async def update_reminder(pk: int, body: ReminderBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_update(db, ExpireReminderConfig, pk, body.model_dump(exclude_none=True))


@router.delete("/{pk}")
async def delete_reminder(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, ExpireReminderConfig, pk)
