import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.ai_config import AiConfig
from app.services.embedding_service import embed_texts
from app.services.knowledge_config_service import build_effective_knowledge_config, load_knowledge_config_map
from app.services.knowledge_index import add_knowledge_chunks, reset_knowledge_index
from app.services.knowledge_loader import load_knowledge_chunks

logger = logging.getLogger(__name__)
settings = get_settings()

_BATCH_SIZE = 32


async def reindex_knowledge(db: AsyncSession) -> dict[str, Any]:
    knowledge_cfg = await load_knowledge_config_map(db)
    runtime_cfg = build_effective_knowledge_config(knowledge_cfg)
    vault_path = Path(runtime_cfg["vault_path"])
    index_dir = Path(runtime_cfg["index_dir"])

    logger.info("[知识库] 开始重建索引 | vault=%s index=%s", vault_path, index_dir)
    chunks, stats = load_knowledge_chunks(vault_path)
    logger.info(
        "[知识库] 文档扫描完成 | files=%s published=%s skipped=%s chunks=%s",
        stats["files"],
        stats["published_files"],
        stats["skipped_files"],
        stats["chunks"],
    )

    logger.info("[知识库] 清空旧索引 | index=%s", index_dir)
    reset_knowledge_index(index_dir)

    ai_cfg_rows = (await db.execute(select(AiConfig))).scalars().all()
    ai_cfg = {row.config_key: row.config_value for row in ai_cfg_rows}
    provider_name = (ai_cfg.get("knowledge_embedding_provider") or settings.KNOWLEDGE_EMBEDDING_PROVIDER).strip()
    model_name = (ai_cfg.get("knowledge_embedding_model") or settings.KNOWLEDGE_EMBEDDING_MODEL).strip() or None
    logger.info("[知识库] Embedding 配置 | provider=%s model=%s", provider_name, model_name or "(默认)")

    if not chunks:
        logger.info("[知识库] 未找到可索引内容，已清空索引")
        return {
            **runtime_cfg,
            "embedding_provider": provider_name,
            "embedding_model": model_name or "",
            **stats,
        }

    for offset in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[offset: offset + _BATCH_SIZE]
        texts = [
            "\n".join(
                part for part in [
                    item["title"],
                    f"别名：{'、'.join(item['aliases'])}" if item["aliases"] else "",
                    item["content"],
                ]
                if part
            )
            for item in batch
        ]
        embeddings = await embed_texts(
            db,
            texts,
            provider_name=provider_name,
            model_name=model_name,
        )
        if len(embeddings) != len(batch):
            raise RuntimeError("知识库 embedding 返回数量异常，请检查 embedding 配置")
        add_knowledge_chunks(
            index_dir=index_dir,
            ids=[item["id"] for item in batch],
            documents=[item["content"] for item in batch],
            embeddings=embeddings,
            metadatas=[
                {
                    "title": item["title"],
                    "source_file": item["source_file"],
                    "source_title": item["source_title"],
                    "tags": ",".join(item["tags"]),
                }
                for item in batch
            ],
        )
        logger.info("[知识库] 已索引 %s/%s chunks", min(offset + _BATCH_SIZE, len(chunks)), len(chunks))

    logger.info("[知识库] 索引重建完成")
    return {
        **runtime_cfg,
        "embedding_provider": provider_name,
        "embedding_model": model_name or "",
        **stats,
    }
