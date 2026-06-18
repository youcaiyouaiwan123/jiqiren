"""make token_usage.user_id nullable for system-level usage (e.g. reindex embedding)

Revision ID: 20260618_11
Revises: 20260618_10
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa

revision = "20260618_11"
down_revision = "20260618_10"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "token_usage",
        "user_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "token_usage",
        "user_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )
