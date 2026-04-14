"""add analytics user daily rollup table

Revision ID: 20260414_02
Revises: 20260414_01
Create Date: 2026-04-14 22:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260414_02"
down_revision: Union[str, Sequence[str], None] = "20260414_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    if "analytics_user_daily" not in existing_tables:
        op.execute(
            sa.text(
                """
                CREATE TABLE analytics_user_daily (
                    stat_date DATE NOT NULL,
                    user_id BIGINT NOT NULL,
                    updated_at DATETIME NOT NULL DEFAULT now(),
                    CONSTRAINT pk_analytics_user_daily PRIMARY KEY (stat_date, user_id)
                )
                """
            )
        )

    inspector = sa.inspect(bind)
    existing_indexes = {item["name"] for item in inspector.get_indexes("analytics_user_daily")}
    if "idx_analytics_user_daily_user_date" not in existing_indexes:
        op.execute(
            sa.text(
                "CREATE INDEX idx_analytics_user_daily_user_date ON analytics_user_daily (user_id, stat_date)"
            )
        )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS `analytics_user_daily`"))
