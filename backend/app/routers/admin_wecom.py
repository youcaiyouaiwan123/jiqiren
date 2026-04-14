"""管理端：企微配置"""
import logging

import httpx
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.wecom_config import WecomConfig
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin/wecom/config", tags=["管理端-企微配置"])


class WecomBody(BaseModel):
    name: str | None = None
    webhook_url: str | None = None
    notify_types: list[str] | None = None
    is_active: int | None = None


@router.get("")
async def list_wecom(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, WecomConfig, page=pager.page, page_size=pager.page_size)


@router.post("")
async def create_wecom(body: WecomBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["created_by"] = admin["admin_id"]
    return await generic_create(db, WecomConfig, data)


@router.put("/{pk}")
async def update_wecom(pk: int, body: WecomBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_update(db, WecomConfig, pk, body.model_dump(exclude_none=True))


@router.delete("/{pk}")
async def delete_wecom(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, WecomConfig, pk)


@router.post("/{pk}/test")
async def test_wecom(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(WecomConfig, pk)
    if not row:
        return fail(1004, "资源不存在")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                row.webhook_url,
                json={"msgtype": "text", "text": {"content": "【AI客服系统】企微推送测试消息"}},
            )
            if resp.status_code == 200:
                return success({"success": True, "message": "测试消息发送成功"})
            return fail(5002, f"发送失败: HTTP {resp.status_code}")
    except Exception as e:
        return fail(5002, f"发送失败: {str(e)}")
