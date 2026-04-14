"""add plan display config

Revision ID: 20260414_03
Revises: 20260414_02
Create Date: 2026-04-15 00:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260414_03"
down_revision: Union[str, Sequence[str], None] = "20260414_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns("plans")}
    if "display_config" not in columns:
        op.add_column("plans", sa.Column("display_config", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns("plans")}
    if "display_config" in columns:
        op.drop_column("plans", "display_config")
