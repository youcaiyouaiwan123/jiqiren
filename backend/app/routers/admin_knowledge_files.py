import logging

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import BizException, PageParams, get_current_admin
from app.services.knowledge_config_service import build_effective_knowledge_config, load_knowledge_config_map
from app.services.knowledge_file_service import (
    create_knowledge_file,
    delete_knowledge_file,
    get_knowledge_file_detail,
    import_knowledge_files,
    list_knowledge_files,
    update_knowledge_file,
)
from app.utils.response import paginate, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/knowledge/files", tags=["管理端-知识库文档"])


class KnowledgeFileCreateBody(BaseModel):
    path: str
    content: str


class KnowledgeFileUpdateBody(BaseModel):
    path: str
    content: str
    new_path: str | None = None


async def _runtime_vault_path(db: AsyncSession) -> str:
    knowledge_cfg = await load_knowledge_config_map(db)
    runtime_cfg = build_effective_knowledge_config(knowledge_cfg)
    return runtime_cfg["vault_path"]


def _normalize_filter_text(value: str | None) -> str:
    return str(value or "").strip().lower()


def _filter_knowledge_files(items: list[dict], keyword: str | None, status: str | None) -> list[dict]:
    keyword_text = _normalize_filter_text(keyword)
    status_text = _normalize_filter_text(status)
    if status_text == "all":
        status_text = ""
    result: list[dict] = []
    for item in items:
        if status_text and _normalize_filter_text(item.get("status")) != status_text:
            continue
        if keyword_text:
            haystack = " ".join(
                [
                    str(item.get("path") or ""),
                    str(item.get("title") or ""),
                    str(item.get("summary") or ""),
                    " ".join(str(tag) for tag in (item.get("tags") or [])),
                    " ".join(str(alias) for alias in (item.get("aliases") or [])),
                ]
            ).lower()
            if keyword_text not in haystack:
                continue
        result.append(item)
    result.sort(key=lambda row: (str(row.get("updated_at") or ""), str(row.get("path") or "")), reverse=True)
    return result


def _build_stats(items: list[dict]) -> dict:
    latest_updated_at = max((str(item.get("updated_at") or "") for item in items), default="")
    return {
        "total": len(items),
        "published": sum(1 for item in items if str(item.get("status") or "") == "published"),
        "draft": sum(1 for item in items if str(item.get("status") or "") == "draft"),
        "archived": sum(1 for item in items if str(item.get("status") or "") == "archived"),
        "total_size": sum(int(item.get("size") or 0) for item in items),
        "latest_updated_at": latest_updated_at or None,
    }


@router.get("")
async def get_knowledge_files(
    keyword: str = Query(""),
    status: str = Query("all"),
    pager: PageParams = Depends(),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    vault_path = await _runtime_vault_path(db)
    items = list_knowledge_files(vault_path)
    stats = _build_stats(items)
    filtered = _filter_knowledge_files(items, keyword=keyword, status=status)
    page_items = filtered[pager.offset:pager.offset + pager.page_size]
    logger.debug(
        "[知识库文档] 列表读取 | admin_id=%s total=%s filtered=%s page=%s page_size=%s vault=%s",
        admin["admin_id"],
        len(items),
        len(filtered),
        pager.page,
        pager.page_size,
        vault_path,
    )
    return success(
        {
            **paginate(page_items, len(filtered), pager.page, pager.page_size),
            "vault_path": vault_path,
            "stats": stats,
        }
    )


@router.get("/detail")
async def get_knowledge_file(path: str = Query(...), admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    vault_path = await _runtime_vault_path(db)
    try:
        result = get_knowledge_file_detail(vault_path, path)
    except FileNotFoundError as exc:
        raise BizException(4004, f"知识文档不存在: {exc.args[0]}") from exc
    except ValueError as exc:
        raise BizException(4001, str(exc)) from exc
    logger.debug("[知识库文档] 读取详情 | admin_id=%s path=%s", admin["admin_id"], result["path"])
    return success(result)


@router.post("")
async def create_file(body: KnowledgeFileCreateBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    vault_path = await _runtime_vault_path(db)
    try:
        result = create_knowledge_file(vault_path, body.path, body.content)
    except FileExistsError as exc:
        raise BizException(4009, f"知识文档已存在: {exc.args[0]}") from exc
    except ValueError as exc:
        raise BizException(4001, str(exc)) from exc
    logger.info("[知识库文档] 新建成功 | admin_id=%s path=%s", admin["admin_id"], result["path"])
    return success(result, "文档已创建，如需更新向量索引请手动重建")


@router.put("")
async def update_file(body: KnowledgeFileUpdateBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    vault_path = await _runtime_vault_path(db)
    try:
        result = update_knowledge_file(vault_path, body.path, body.content, body.new_path)
    except FileNotFoundError as exc:
        raise BizException(4004, f"知识文档不存在: {exc.args[0]}") from exc
    except FileExistsError as exc:
        raise BizException(4009, f"目标文档已存在: {exc.args[0]}") from exc
    except ValueError as exc:
        raise BizException(4001, str(exc)) from exc
    logger.info("[知识库文档] 更新成功 | admin_id=%s path=%s", admin["admin_id"], result["path"])
    return success(result, "文档已保存，如需更新向量索引请手动重建")


@router.delete("")
async def delete_file(path: str = Query(...), admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    vault_path = await _runtime_vault_path(db)
    try:
        result = delete_knowledge_file(vault_path, path)
    except FileNotFoundError as exc:
        raise BizException(4004, f"知识文档不存在: {exc.args[0]}") from exc
    except ValueError as exc:
        raise BizException(4001, str(exc)) from exc
    logger.info("[知识库文档] 删除成功 | admin_id=%s path=%s", admin["admin_id"], result["path"])
    return success(result, "文档已删除，如需更新向量索引请手动重建")


@router.post("/import")
async def import_files(
    files: list[UploadFile] = File(...),
    target_dir: str = Form(""),
    overwrite: bool = Form(False),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    vault_path = await _runtime_vault_path(db)
    payload: list[dict[str, object]] = []
    for upload in files:
        payload.append({"filename": upload.filename or "", "content": await upload.read()})
    try:
        result = import_knowledge_files(vault_path, payload, target_dir=target_dir, overwrite=overwrite)
    except ValueError as exc:
        raise BizException(4001, str(exc)) from exc
    logger.info(
        "[知识库文档] 导入完成 | admin_id=%s total=%s imported=%s skipped=%s target_dir=%s",
        admin["admin_id"],
        result["total"],
        result["imported_count"],
        result["skipped_count"],
        result["target_dir"],
    )
    return success(result, "导入完成，如需更新向量索引请手动重建")
