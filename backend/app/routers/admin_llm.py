"""管理端：大模型配置 CRUD"""
import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.llm_provider import LlmProvider
from app.utils.crud import generic_delete, generic_list, row_to_dict
from app.utils.response import fail, success

router = APIRouter(prefix="/api/admin/llm-providers", tags=["管理端-大模型配置"])

VALID_PROVIDERS = {"claude", "anthropic", "openai", "gpt", "gemini", "google", "zhipu", "glm"}


class LlmBody(BaseModel):
    name: str | None = None
    provider: str | None = None
    api_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    priority: int | None = None
    input_price: float | None = None
    output_price: float | None = None
    is_default: int | None = None
    is_active: int | None = None
    extra_config: dict | None = None


def _normalized_provider(value: str | None) -> str | None:
    if value is None:
        return None
    provider = value.strip().lower()
    return provider or None


async def _unset_other_defaults(db: AsyncSession, current_id: int):
    await db.execute(
        update(LlmProvider)
        .where(LlmProvider.id != current_id)
        .values(is_default=0)
    )


@router.get("")
async def list_llm(admin: dict = Depends(get_current_admin), pager: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await generic_list(db, LlmProvider, page=pager.page, page_size=pager.page_size, exclude_cols={"api_key"})


@router.post("")
async def create_llm(body: LlmBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    provider = _normalized_provider(data.get("provider"))
    if provider:
        if provider not in VALID_PROVIDERS:
            return fail(1001, f"不支持的模型厂商: {provider}")
        data["provider"] = provider
    if data.get("is_default") == 1 and data.get("is_active", 1) != 1:
        return fail(1001, "默认模型必须处于启用状态")
    row = LlmProvider(**data)
    db.add(row)
    await db.flush()
    if row.is_default:
        await _unset_other_defaults(db, row.id)
    await db.refresh(row)
    return success(row_to_dict(row, {"api_key"}))


@router.put("/{pk}")
async def update_llm(pk: int, body: LlmBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    row = await db.get(LlmProvider, pk)
    if not row:
        return fail(1004, "资源不存在")
    provider = _normalized_provider(data.get("provider"))
    if provider:
        if provider not in VALID_PROVIDERS:
            return fail(1001, f"不支持的模型厂商: {provider}")
        data["provider"] = provider
    next_is_active = data.get("is_active", row.is_active)
    next_is_default = data.get("is_default", row.is_default)
    if next_is_default == 1 and next_is_active != 1:
        return fail(1001, "默认模型必须处于启用状态")
    if next_is_active != 1 and row.is_default and "is_default" not in data:
        data["is_default"] = 0
    for k, v in data.items():
        if v is not None:
            setattr(row, k, v)
    await db.flush()
    if row.is_default:
        await _unset_other_defaults(db, row.id)
    await db.refresh(row)
    return success(row_to_dict(row, {"api_key"}))


@router.put("/{pk}/default")
async def set_default(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(LlmProvider, pk)
    if not row:
        return fail(1004, "资源不存在")
    if not row.is_active:
        return fail(1001, "该模型未启用，无法设为默认")
    await db.execute(update(LlmProvider).values(is_default=0))
    row.is_default = 1
    await db.flush()
    return success({"id": row.id, "is_default": True})


@router.delete("/{pk}")
async def delete_llm(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, LlmProvider, pk)
