import asyncio
import logging

from app.core.database import async_session, engine
from app.services.data_lifecycle_service import collect_archive_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    async with async_session() as session:
        report = await collect_archive_report(session)
    await engine.dispose()
    logger.info(
        "[Lifecycle] archive candidates | messages=%s before=%s | token_usage=%s before=%s | conversations=%s before=%s",
        report.message_candidates,
        report.message_cutoff.date(),
        report.token_usage_candidates,
        report.token_usage_cutoff.date(),
        report.conversation_candidates,
        report.conversation_cutoff.date(),
    )


if __name__ == "__main__":
    asyncio.run(main())
