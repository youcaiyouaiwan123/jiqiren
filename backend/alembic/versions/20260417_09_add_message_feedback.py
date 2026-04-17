"""add message_feedback table and messages.feishu_record_id

Revision ID: 20260417_09
Revises: 20260417_08
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa

revision = "20260417_09"
down_revision = "20260417_08"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "messages",
        sa.Column("feishu_record_id", sa.String(100), nullable=True, comment="飞书多维表格 record_id，用于后续更新"),
    )

    op.create_table(
        "message_feedback",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("message_id", sa.BigInteger, sa.ForeignKey("messages.id"), nullable=False, unique=True),
        sa.Column("user_id", sa.BigInteger, nullable=False),
        sa.Column("conversation_id", sa.BigInteger, nullable=False),
        sa.Column("rating", sa.String(10), nullable=True, comment="用户显式反馈: like/dislike"),
        sa.Column("satisfaction_level", sa.String(10), nullable=True, comment="满意度: high/medium/low"),
        sa.Column("scored_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("idx_mf_user", "message_feedback", ["user_id"])
    op.create_index("idx_mf_conv", "message_feedback", ["conversation_id"])


def downgrade():
    op.drop_index("idx_mf_conv", "message_feedback")
    op.drop_index("idx_mf_user", "message_feedback")
    op.drop_table("message_feedback")
    op.drop_column("messages", "feishu_record_id")
