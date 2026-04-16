"""add user admin management fields

Revision ID: 20260415_05
Revises: 20260414_04
Create Date: 2026-04-15 22:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260415_05"
down_revision: Union[str, Sequence[str], None] = "20260414_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns("users")}

    if "remark" not in columns:
        op.add_column("users", sa.Column("remark", sa.String(length=200), nullable=True))
    if "deleted_at" not in columns:
        op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    inspector = sa.inspect(bind)
    indexes = {item["name"] for item in inspector.get_indexes("users")}
    if "idx_user_deleted_at" not in indexes:
        op.create_index("idx_user_deleted_at", "users", ["deleted_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {item["name"] for item in inspector.get_indexes("users")}
    if "idx_user_deleted_at" in indexes:
        op.drop_index("idx_user_deleted_at", table_name="users")

    columns = {item["name"] for item in inspector.get_columns("users")}
    if "deleted_at" in columns:
        op.drop_column("users", "deleted_at")
    if "remark" in columns:
        op.drop_column("users", "remark")
