"""管理端：注册设置"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.register_config import RegisterConfig
from app.models.user import User
from app.utils.crud import row_to_dict
from app.utils.response import success

router = APIRouter(prefix="/api/admin/register/config", tags=["管理端-注册设置"])


@router.get("")
async def get_register_config(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(RegisterConfig))).scalars().all()
    items = [row_to_dict(r) for r in rows]
    return success({"list": items})


class RegisterConfigBody(BaseModel):
    register_enabled: str | None = None
    register_methods: str | None = None
    invite_code_required: str | None = None
    default_free_chats: str | None = None
    terms_url: str | None = None
    privacy_url: str | None = None
    sms_enabled: str | None = None
    sms_provider: str | None = None
    sms_access_key: str | None = None
    sms_access_secret: str | None = None
    sms_sign_name: str | None = None
    sms_sdk_app_id: str | None = None
    sms_template_code: str | None = None
    email_enabled: str | None = None
    smtp_host: str | None = None
    smtp_port: str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None


@router.put("")
async def update_register_config(body: RegisterConfigBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    affected_users = 0
    synced_default_free_chats: int | None = None
    for key, value in data.items():
        row = (await db.execute(select(RegisterConfig).where(RegisterConfig.config_key == key))).scalar_one_or_none()
        if row:
            row.config_value = value
            row.updated_by = admin["admin_id"]
        else:
            db.add(RegisterConfig(config_key=key, config_value=value, updated_by=admin["admin_id"]))
    if "default_free_chats" in data:
        synced_default_free_chats = int(data["default_free_chats"])
        result = await db.execute(
            update(User)
            .where(User.subscribe_plan == "free")
            .values(free_chats_left=synced_default_free_chats)
        )
        affected_users = result.rowcount or 0
        logger.info("[注册设置] 保存并同步免费次数=%s，影响用户数=%s，admin_id=%s", synced_default_free_chats, affected_users, admin["admin_id"])
    rows = (await db.execute(select(RegisterConfig))).scalars().all()
    return success({"list": [row_to_dict(r) for r in rows], "affected_users": affected_users, "default_free_chats": synced_default_free_chats})


@router.post("/sync-free-chats")
async def sync_free_chats_to_existing_users(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    row = (
        await db.execute(
            select(RegisterConfig).where(RegisterConfig.config_key == "default_free_chats")
        )
    ).scalar_one_or_none()
    default_free_chats = int(row.config_value) if row and row.config_value is not None else 3
    result = await db.execute(
        update(User)
        .where(User.subscribe_plan == "free")
        .values(free_chats_left=default_free_chats)
    )
    logger.info("[注册设置] 手动同步免费次数=%s，影响用户数=%s，admin_id=%s", default_free_chats, result.rowcount, admin["admin_id"])
    return success({"default_free_chats": default_free_chats, "affected_users": result.rowcount}, "同步成功")
