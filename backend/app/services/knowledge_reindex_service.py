import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.ai_config import AiConfig
from app.models.token_usage import TokenUsage
from app.services.embedding_service import embed_texts
from app.services.knowledge_config_service import build_effective_knowledge_config, load_knowledge_config_map
from app.services.knowledge_index import add_knowledge_chunks, reset_knowledge_index
from app.services.knowledge_loader import load_knowledge_chunks

logger = logging.getLogger(__name__)
settings = get_settings()

_BATCH_SIZE = 10


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

    emb_tokens_total = 0
    emb_meta: dict[str, Any] = {}
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
            runtime_meta=emb_meta,
        )
        emb_tokens_total += emb_meta.get("tokens") or 0
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
    # 记录本次重建索引的 embedding 用量（embedding 费用大头在这里）。
    # user_id=None 表示系统级用量，不归属具体用户；仍会按模型计入费用统计。
    if emb_tokens_total > 0:
        emb_price = float(emb_meta.get("input_price") or 0)
        emb_model = emb_meta.get("model") or model_name or "embedding"
        try:
            db.add(
                TokenUsage(
                    user_id=None,
                    message_id=None,
                    model=emb_model,
                    input_tokens=emb_tokens_total,
                    output_tokens=0,
                    cost_usd=round(emb_tokens_total * emb_price / 1_000_000, 6),
                )
            )
            await db.flush()
            logger.info("[知识库] 已记录重建索引 embedding 用量 | model=%s tokens=%s", emb_model, emb_tokens_total)
        except Exception:
            logger.exception("[知识库] 记录 embedding 用量失败（不影响索引结果）")
    # 文档可能新增/修改了链接，清空「相关链接」缓存，下次提问时按新文档重建
    try:
        from app.services.ai_service import clear_link_caches
        clear_link_caches()
    except Exception:
        logger.exception("[知识库] 清空链接缓存失败（不影响索引结果）")
    return {
        **runtime_cfg,
        "embedding_provider": provider_name,
        "embedding_model": model_name or "",
        **stats,
    }
