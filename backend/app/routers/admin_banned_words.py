"""管理端：禁用词管理"""
import logging

from fastapi import APIRouter, Depends, Query

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.banned_word import BannedWord
from app.utils.crud import generic_create, generic_delete, generic_list, generic_update
from app.utils.response import success

router = APIRouter(prefix="/api/admin/banned-words", tags=["管理端-禁用词"])


class BannedWordBody(BaseModel):
    word: str | None = None
    match_type: str | None = None
    action: str | None = None
    replace_with: str | None = None
    is_active: int | None = None


class BatchImportBody(BaseModel):
    words: list[str]
    match_type: str = "contains"
    action: str = "reject"


@router.get("")
async def list_banned_words(
    keyword: str | None = None,
    admin: dict = Depends(get_current_admin),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if keyword:
        filters.append(BannedWord.word.contains(keyword, autoescape=True))
    return await generic_list(db, BannedWord, page=pager.page, page_size=pager.page_size, filters=filters)


@router.post("")
async def create_banned_word(body: BannedWordBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    data["created_by"] = admin["admin_id"]
    return await generic_create(db, BannedWord, data)


@router.post("/batch")
async def batch_import(body: BatchImportBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    existing = {r.word for r in (await db.execute(select(BannedWord.word))).all()}
    imported = 0
    skipped_words = []
    for w in body.words[:500]:
        if w in existing:
            skipped_words.append(w)
            continue
        db.add(BannedWord(word=w, match_type=body.match_type, action=body.action, created_by=admin["admin_id"]))
        existing.add(w)
        imported += 1
    await db.flush()
    return success({"imported": imported, "skipped": len(skipped_words), "skipped_words": skipped_words})


@router.put("/{pk}")
async def update_banned_word(pk: int, body: BannedWordBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_update(db, BannedWord, pk, body.model_dump(exclude_none=True))


@router.delete("/{pk}")
async def delete_banned_word(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, BannedWord, pk)
