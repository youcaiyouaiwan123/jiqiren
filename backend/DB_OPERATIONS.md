# DB Operations

## Startup

- Run `python -m alembic -c alembic.ini upgrade head` before starting the app.
- The backend startup now launches an analytics rollup worker automatically.

## Analytics Rollups

- Manual full rebuild:
  - `python -m app.scripts.rebuild_analytics_rollups --full`
- Manual recent rebuild:
  - `python -m app.scripts.rebuild_analytics_rollups --days 30`
- Manual date range rebuild:
  - `python -m app.scripts.rebuild_analytics_rollups --start-date 2026-04-01 --end-date 2026-04-14`

## Lifecycle Report

- Inspect archive candidates:
  - `python -m app.scripts.report_data_lifecycle`

Current lifecycle knobs live in `.env`:

- `ANALYTICS_ROLLUP_REFRESH_MINUTES`
- `ANALYTICS_ROLLUP_RECENT_DAYS`
- `MESSAGE_ARCHIVE_AFTER_DAYS`
- `TOKEN_USAGE_ARCHIVE_AFTER_DAYS`
- `CONVERSATION_ARCHIVE_AFTER_DAYS`

## Current Boundaries

- `admin analytics` and `token usage` summary endpoints already prefer rollup tables.
- `top-users` and `hot-questions` still aggregate from raw `messages`; if admin traffic or data volume grows further, move them to dedicated aggregate tables.
- Chat history APIs still use offset pagination. If single-user history grows very large, switch to cursor pagination.
