"""管理端：套餐管理"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.plan import Plan
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update

router = APIRouter(prefix="/api/admin/plans", tags=["管理端-套餐管理"])


class PlanBody(BaseModel):
    name: str | None = None
    type: str | None = None
    price: float | None = None
    duration_days: int | None = None
    chat_limit: int | None = None
    description: str | None = None
    display_config: dict | None = None
    is_active: int | None = None
    sort_order: int | None = None


@router.get("")
async def list_plans(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, Plan, page=pager.page, page_size=pager.page_size, order_by=Plan.sort_order.asc())


@router.post("")
async def create_plan(body: PlanBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_create(db, Plan, body.model_dump(exclude_none=True))


@router.put("/{pk}")
async def update_plan(pk: int, body: PlanBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_update(db, Plan, pk, body.model_dump(exclude_none=True))


@router.delete("/{pk}")
async def delete_plan(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, Plan, pk)
