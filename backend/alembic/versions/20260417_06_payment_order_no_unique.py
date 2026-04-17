"""add unique constraint on payments.order_no

Revision ID: 20260417_06
Revises: 20260415_05
Create Date: 2026-04-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260417_06"
down_revision: Union[str, Sequence[str], None] = "20260415_05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraints = {c["name"] for c in inspector.get_unique_constraints("payments")}
    indexes = {i["name"] for i in inspector.get_indexes("payments")}

    if "uq_pay_order_no" not in unique_constraints and "uq_pay_order_no" not in indexes:
        op.create_index("uq_pay_order_no", "payments", ["order_no"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {i["name"] for i in inspector.get_indexes("payments")}

    if "uq_pay_order_no" in indexes:
        op.drop_index("uq_pay_order_no", table_name="payments")
