"""Revision 08: llm_providers 表增加 priority 字段

priority 控制多 Key 的尝试顺序：数字越小越先试，默认 100。
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260417_08"
down_revision = "20260417_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "llm_providers",
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100", comment="尝试优先级，数字越小越先被选用"),
    )


def downgrade() -> None:
    op.drop_column("llm_providers", "priority")
