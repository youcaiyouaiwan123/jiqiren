"""extend payments for subscribe orders

Revision ID: 20260414_04
Revises: 20260414_03
Create Date: 2026-04-15 01:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260414_04"
down_revision: Union[str, Sequence[str], None] = "20260414_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns("payments")}

    if "plan_id" not in columns:
        op.add_column("payments", sa.Column("plan_id", sa.BigInteger(), nullable=True))
    if "channel" not in columns:
        op.add_column("payments", sa.Column("channel", sa.String(length=20), nullable=True))
    if "order_no" not in columns:
        op.add_column("payments", sa.Column("order_no", sa.String(length=64), nullable=True))
    if "remark" not in columns:
        op.add_column("payments", sa.Column("remark", sa.String(length=200), nullable=True))
    if "paid_at" not in columns:
        op.add_column("payments", sa.Column("paid_at", sa.DateTime(), nullable=True))
    if "updated_at" not in columns:
        op.add_column("payments", sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False))

    inspector = sa.inspect(bind)
    indexes = {item["name"] for item in inspector.get_indexes("payments")}
    if "idx_pay_order_no" not in indexes:
        op.create_index("idx_pay_order_no", "payments", ["order_no"], unique=False)
    if "idx_pay_status_created" not in indexes:
        op.create_index("idx_pay_status_created", "payments", ["status", "created_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {item["name"] for item in inspector.get_indexes("payments")}
    if "idx_pay_status_created" in indexes:
        op.drop_index("idx_pay_status_created", table_name="payments")
    if "idx_pay_order_no" in indexes:
        op.drop_index("idx_pay_order_no", table_name="payments")

    columns = {item["name"] for item in inspector.get_columns("payments")}
    for name in ["updated_at", "paid_at", "remark", "order_no", "channel", "plan_id"]:
        if name in columns:
            op.drop_column("payments", name)
