import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.knowledge_config import KnowledgeConfig

logger = logging.getLogger(__name__)
settings = get_settings()

KNOWLEDGE_CONFIG_DEFAULTS = {
    "vault_path": settings.knowledge_vault_path,
    "index_dir": settings.knowledge_index_dir,
    "git_repo_url": (settings.KNOWLEDGE_GIT_REPO_URL or "").strip(),
    "git_branch": (settings.KNOWLEDGE_GIT_BRANCH or "main").strip() or "main",
}

KNOWLEDGE_CONFIG_DESCRIPTIONS = {
    "vault_path": "Obsidian Vault 路径",
    "index_dir": "知识索引目录",
    "git_repo_url": "Git 仓库地址",
    "git_branch": "Git 分支",
}


def _resolve_path(value: str | None, fallback: str) -> str:
    raw = (value or "").strip() or fallback
    return str(Path(raw).expanduser().resolve())


async def list_knowledge_config_rows(db: AsyncSession) -> list[KnowledgeConfig]:
    return (
        await db.execute(
            select(KnowledgeConfig).order_by(KnowledgeConfig.id.asc())
        )
    ).scalars().all()


async def load_knowledge_config_map(db: AsyncSession) -> dict[str, str]:
    data = dict(KNOWLEDGE_CONFIG_DEFAULTS)
    rows = await list_knowledge_config_rows(db)
    overridden: list[str] = []
    for row in rows:
        if row.config_value and row.config_value != data.get(row.config_key):
            overridden.append(row.config_key)
        data[row.config_key] = row.config_value or ""
    if overridden:
        logger.debug("[知识源配置] 数据库覆盖了默认值 | keys=%s", overridden)
    return data


def build_effective_knowledge_config(config_map: dict[str, str] | None = None) -> dict[str, str]:
    data = dict(KNOWLEDGE_CONFIG_DEFAULTS)
    if config_map:
        data.update(config_map)
    result = {
        "vault_path": _resolve_path(data.get("vault_path"), settings.knowledge_vault_path),
        "index_dir": _resolve_path(data.get("index_dir"), settings.knowledge_index_dir),
        "git_repo_url": (data.get("git_repo_url") or "").strip(),
        "git_branch": (data.get("git_branch") or "main").strip() or "main",
    }
    logger.debug("[知识源配置] 生效配置 | vault=%s index=%s git=%s branch=%s", result["vault_path"], result["index_dir"], result["git_repo_url"] or "(未配置)", result["git_branch"])
    return result


async def seed_knowledge_config_defaults(db: AsyncSession) -> None:
    rows = await list_knowledge_config_rows(db)
    existing = {row.config_key for row in rows}
    seeded: list[str] = []
    for key, value in KNOWLEDGE_CONFIG_DEFAULTS.items():
        if key in existing:
            continue
        db.add(
            KnowledgeConfig(
                config_key=key,
                config_value=value,
                description=KNOWLEDGE_CONFIG_DESCRIPTIONS.get(key),
            )
        )
        seeded.append(key)
    if seeded:
        logger.info("[知识源配置] 种子数据已写入 | keys=%s", seeded)
    else:
        logger.debug("[知识源配置] 种子数据已存在，无需写入")
