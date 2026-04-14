"""管理端：支付设置"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.payment_config import PaymentConfig
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update, row_to_dict
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin/payment/config", tags=["管理端-支付设置"])


class PaymentConfigBody(BaseModel):
    channel: str | None = None
    merchant_id: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    notify_url: str | None = None
    is_active: int | None = None
    extra_config: dict | None = None


@router.get("")
async def list_config(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, PaymentConfig, page=pager.page, page_size=pager.page_size, exclude_cols={"api_key", "api_secret"})


@router.post("")
async def create_config(body: PaymentConfigBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["updated_by"] = admin["admin_id"]
    return await generic_create(db, PaymentConfig, data)


@router.put("/{pk}")
async def update_config(pk: int, body: PaymentConfigBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["updated_by"] = admin["admin_id"]
    return await generic_update(db, PaymentConfig, pk, data)


@router.delete("/{pk}")
async def delete_config(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, PaymentConfig, pk)
