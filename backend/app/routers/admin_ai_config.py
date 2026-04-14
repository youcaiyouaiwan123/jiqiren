"""管理端：AI 配置"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.ai_config import AiConfig
from app.utils.crud import row_to_dict
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin/ai/config", tags=["管理端-AI配置"])

VALID_KEYS = {
    "system_prompt",
    "temperature",
    "max_tokens",
    "faq_enabled",
    "doc_recommend",
    "knowledge_enabled",
    "knowledge_top_k",
    "knowledge_min_score",
    "knowledge_embedding_provider",
    "knowledge_embedding_model",
}


@router.get("")
async def list_ai_config(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(AiConfig))).scalars().all()
    items = [row_to_dict(r) for r in rows]
    return success({"list": items})


class AiConfigBody(BaseModel):
    value: str


@router.put("/{key}")
async def update_ai_config(key: str, body: AiConfigBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    if key not in VALID_KEYS:
        return fail(1004, f"无效的配置项: {key}")
    row = (await db.execute(select(AiConfig).where(AiConfig.config_key == key))).scalar_one_or_none()
    if not row:
        row = AiConfig(config_key=key, config_value=body.value, updated_by=admin["admin_id"])
        db.add(row)
    else:
        row.config_value = body.value
        row.updated_by = admin["admin_id"]
    await db.flush()
    await db.refresh(row)
    logger.info("[AI配置] 更新成功 | admin_id=%s key=%s value=%s", admin["admin_id"], key, body.value)
    return success(row_to_dict(row))
