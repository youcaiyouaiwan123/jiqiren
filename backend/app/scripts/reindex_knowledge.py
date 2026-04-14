import asyncio
import logging

from app.core.database import async_session
from app.services.knowledge_reindex_service import reindex_knowledge

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    async with async_session() as db:
        result = await reindex_knowledge(db)
    logger.info("[知识库] 重建结果 | vault=%s index=%s files=%s chunks=%s", result["vault_path"], result["index_dir"], result["files"], result["chunks"])


if __name__ == "__main__":
    asyncio.run(main())
