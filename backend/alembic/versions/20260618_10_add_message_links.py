"""add messages.links column for related document links

Revision ID: 20260618_10
Revises: 20260417_09
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa

revision = "20260618_10"
down_revision = "20260417_09"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "messages",
        sa.Column("links", sa.JSON(), nullable=True, comment="AI 回答的相关文档链接 [{title,url}]，来自知识库原文"),
    )


def downgrade():
    op.drop_column("messages", "links")
