"""Revision 07: 创建冷区归档表（按年 RANGE 分区）

使用原生 SQL CREATE TABLE ... PARTITION BY RANGE COLUMNS(created_at)：
- SQLAlchemy DDL 不支持 MySQL 分区语法，改用 op.execute() 直接执行
- 复合主键 (id, created_at) 是 MySQL RANGE 分区的强制要求
- 归档表无外键约束，避免主表软删除行导致的约束冲突
"""

from __future__ import annotations

from alembic import op

revision = "20260417_07"
down_revision = "20260417_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS messages_archive (
            id              BIGINT      NOT NULL,
            conversation_id BIGINT      NOT NULL,
            user_id         BIGINT      NOT NULL,
            role            VARCHAR(20) NOT NULL,
            content         LONGTEXT    NOT NULL,
            images          JSON,
            docs            JSON,
            input_tokens    INT         NOT NULL DEFAULT 0,
            output_tokens   INT         NOT NULL DEFAULT 0,
            feishu_synced   INT         NOT NULL DEFAULT 0,
            created_at      DATETIME    NOT NULL,
            PRIMARY KEY (id, created_at),
            KEY idx_arch_msg_conv (conversation_id),
            KEY idx_arch_msg_user_date (user_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        PARTITION BY RANGE COLUMNS(created_at) (
            PARTITION p_before_2026 VALUES LESS THAN ('2026-01-01'),
            PARTITION p_2026       VALUES LESS THAN ('2027-01-01'),
            PARTITION p_2027       VALUES LESS THAN ('2028-01-01'),
            PARTITION p_2028       VALUES LESS THAN ('2029-01-01'),
            PARTITION p_future     VALUES LESS THAN MAXVALUE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS token_usage_archive (
            id            BIGINT        NOT NULL,
            user_id       BIGINT        NOT NULL,
            message_id    BIGINT,
            model         VARCHAR(50),
            input_tokens  INT           NOT NULL,
            output_tokens INT           NOT NULL,
            cost_usd      DECIMAL(10,6),
            created_at    DATETIME      NOT NULL,
            PRIMARY KEY (id, created_at),
            KEY idx_arch_tu_user_date  (user_id, created_at),
            KEY idx_arch_tu_model_date (model,   created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        PARTITION BY RANGE COLUMNS(created_at) (
            PARTITION p_before_2026 VALUES LESS THAN ('2026-01-01'),
            PARTITION p_2026       VALUES LESS THAN ('2027-01-01'),
            PARTITION p_2027       VALUES LESS THAN ('2028-01-01'),
            PARTITION p_2028       VALUES LESS THAN ('2029-01-01'),
            PARTITION p_future     VALUES LESS THAN MAXVALUE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS conversations_archive (
            id         BIGINT       NOT NULL,
            user_id    BIGINT       NOT NULL,
            title      VARCHAR(200),
            created_at DATETIME     NOT NULL,
            updated_at DATETIME     NOT NULL,
            PRIMARY KEY (id, created_at),
            KEY idx_arch_conv_user_date (user_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        PARTITION BY RANGE COLUMNS(created_at) (
            PARTITION p_before_2026 VALUES LESS THAN ('2026-01-01'),
            PARTITION p_2026       VALUES LESS THAN ('2027-01-01'),
            PARTITION p_2027       VALUES LESS THAN ('2028-01-01'),
            PARTITION p_2028       VALUES LESS THAN ('2029-01-01'),
            PARTITION p_future     VALUES LESS THAN MAXVALUE
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS messages_archive")
    op.execute("DROP TABLE IF EXISTS token_usage_archive")
    op.execute("DROP TABLE IF EXISTS conversations_archive")
