import argparse
import asyncio
import logging

from app.core.database import async_session, engine
from app.services.analytics_rollup_service import ensure_rollup_coverage, ensure_rollups, resolve_rollup_day_range

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild analytics daily rollups")
    parser.add_argument("--days", type=int, default=30, help="Default days to rebuild when no explicit range is provided")
    parser.add_argument("--start-date", type=str, default=None, help="Start date, format YYYY-MM-DD")
    parser.add_argument("--end-date", type=str, default=None, help="End date, format YYYY-MM-DD")
    parser.add_argument("--full", action="store_true", help="Backfill from the earliest business data to today")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    async with async_session() as session:
        if args.full:
            start_day, end_day = await ensure_rollup_coverage(session, include_models=True)
        else:
            start_day, end_day = resolve_rollup_day_range(args.start_date, args.end_date, default_days=args.days)
            await ensure_rollups(session, start_day, end_day, include_models=True)
        await session.commit()
    await engine.dispose()
    logger.info("[Analytics Rollup] rebuild finished | start=%s end=%s", start_day, end_day)


if __name__ == "__main__":
    asyncio.run(main())
