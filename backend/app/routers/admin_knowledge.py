import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import BizException, get_current_admin
from app.models.knowledge_config import KnowledgeConfig
from app.services.knowledge_config_service import build_effective_knowledge_config, load_knowledge_config_map
from app.services.knowledge_git_service import GitSyncError, git_sync
from app.services.knowledge_reindex_service import reindex_knowledge
from app.utils.crud import row_to_dict
from app.utils.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/knowledge/config", tags=["管理端-知识源配置"])


class KnowledgeConfigBody(BaseModel):
    vault_path: str | None = None
    index_dir: str | None = None
    git_repo_url: str | None = None
    git_branch: str | None = None


async def _serialize_config(db: AsyncSession) -> dict:
    rows = (
        await db.execute(
            select(KnowledgeConfig).order_by(KnowledgeConfig.id.asc())
        )
    ).scalars().all()
    config_map = await load_knowledge_config_map(db)
    return success(
        {
            "list": [row_to_dict(row) for row in rows],
            "effective": build_effective_knowledge_config(config_map),
        }
    )


@router.get("")
async def get_knowledge_config(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    logger.debug("[知识源配置] 读取配置 | admin_id=%s", admin["admin_id"])
    return await _serialize_config(db)


@router.put("")
async def update_knowledge_config(body: KnowledgeConfigBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    for key, value in data.items():
        normalized = str(value or "").strip()
        row = (await db.execute(select(KnowledgeConfig).where(KnowledgeConfig.config_key == key))).scalar_one_or_none()
        if row:
            row.config_value = normalized
            row.updated_by = admin["admin_id"]
        else:
            db.add(KnowledgeConfig(config_key=key, config_value=normalized, description=key, updated_by=admin["admin_id"]))
    logger.info("[知识源配置] 保存成功 | admin_id=%s keys=%s", admin["admin_id"], list(data.keys()))
    return await _serialize_config(db)


@router.post("/reindex")
async def trigger_reindex(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    try:
        result = await reindex_knowledge(db)
    except RuntimeError as exc:
        logger.warning("[知识源配置] 重建索引失败 | admin_id=%s error=%s", admin["admin_id"], exc)
        raise BizException(4001, str(exc)) from exc
    logger.info("[知识源配置] 管理端触发重建索引 | admin_id=%s vault=%s index=%s chunks=%s", admin["admin_id"], result["vault_path"], result["index_dir"], result["chunks"])
    return success(result, "索引重建完成")


@router.post("/sync")
async def trigger_sync(admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    """Git pull 同步知识仓库，然后自动重建索引"""
    logger.info("[知识源配置] 管理端触发同步+重建 | admin_id=%s", admin["admin_id"])
    knowledge_cfg = await load_knowledge_config_map(db)
    runtime_cfg = build_effective_knowledge_config(knowledge_cfg)

    try:
        git_result = await git_sync(
            vault_path=runtime_cfg["vault_path"],
            repo_url=runtime_cfg["git_repo_url"],
            branch=runtime_cfg["git_branch"],
        )
    except GitSyncError as exc:
        logger.warning("[知识源配置] Git 同步失败 | admin_id=%s error=%s", admin["admin_id"], exc)
        raise BizException(4002, str(exc)) from exc

    logger.info("[知识源配置] Git 同步完成，开始重建索引 | action=%s", git_result["action"])
    try:
        reindex_result = await reindex_knowledge(db)
    except RuntimeError as exc:
        logger.warning("[知识源配置] 同步后重建索引失败 | admin_id=%s error=%s", admin["admin_id"], exc)
        raise BizException(4001, str(exc)) from exc

    combined = {
        "git": git_result,
        "reindex": reindex_result,
    }
    logger.info(
        "[知识源配置] 同步+重建 | admin_id=%s action=%s chunks=%s",
        admin["admin_id"], git_result["action"], reindex_result["chunks"],
    )
    return success(combined, f"Git {git_result['action']} 完成，索引重建完成")
