"""initial schema and analytics foundation

Revision ID: 20260414_01
Revises:
Create Date: 2026-04-14 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260414_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_SQL: list[tuple[str, str]] = [
    ("admins", """CREATE TABLE admins (id BIGINT NOT NULL AUTO_INCREMENT, username VARCHAR(50) NOT NULL, password_hash VARCHAR(255) NOT NULL, `role` ENUM('super','normal') NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (username))"""),
    ("analytics_daily", """CREATE TABLE analytics_daily (stat_date DATE NOT NULL, new_users BIGINT NOT NULL, active_users BIGINT NOT NULL, conversation_count BIGINT NOT NULL, message_count BIGINT NOT NULL, request_count BIGINT NOT NULL, input_tokens BIGINT NOT NULL, output_tokens BIGINT NOT NULL, cost_usd DECIMAL(18, 6) NOT NULL, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (stat_date))"""),
    ("analytics_model_daily", """CREATE TABLE analytics_model_daily (stat_date DATE NOT NULL, model VARCHAR(100) NOT NULL, request_count BIGINT NOT NULL, user_count BIGINT NOT NULL, input_tokens BIGINT NOT NULL, output_tokens BIGINT NOT NULL, cost_usd DECIMAL(18, 6) NOT NULL, updated_at DATETIME NOT NULL DEFAULT now(), CONSTRAINT pk_analytics_model_daily PRIMARY KEY (stat_date, model))"""),
    ("feishu_routes", """CREATE TABLE feishu_routes (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, app_id VARCHAR(100) NOT NULL, app_secret VARCHAR(200) NOT NULL, app_token VARCHAR(100) NOT NULL, table_id VARCHAR(100) NOT NULL, route_rule JSON, is_active INTEGER NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id))"""),
    ("llm_providers", """CREATE TABLE llm_providers (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(50) NOT NULL, provider VARCHAR(50) NOT NULL, api_url VARCHAR(500) NOT NULL, api_key VARCHAR(500) NOT NULL, model VARCHAR(100) NOT NULL, is_default INTEGER NOT NULL, is_active INTEGER NOT NULL, input_price DECIMAL(10, 4) COMMENT '输入价格 USD/百万tokens', output_price DECIMAL(10, 4) COMMENT '输出价格 USD/百万tokens', extra_config JSON, created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id))"""),
    ("plans", """CREATE TABLE plans (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(50) NOT NULL, type ENUM('monthly','yearly','custom') NOT NULL, price DECIMAL(10, 2) NOT NULL, duration_days INTEGER NOT NULL, chat_limit INTEGER NOT NULL, description VARCHAR(500), is_active INTEGER NOT NULL, sort_order INTEGER NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id))"""),
    ("users", """CREATE TABLE users (id BIGINT NOT NULL AUTO_INCREMENT, phone VARCHAR(20), email VARCHAR(100), password_hash VARCHAR(255) NOT NULL, nickname VARCHAR(50), avatar_url VARCHAR(500), free_chats_left INTEGER NOT NULL, subscribe_plan ENUM('free','monthly','yearly') NOT NULL, subscribe_expire DATETIME, status ENUM('active','banned') NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (phone), UNIQUE (email))"""),
    ("ai_config", """CREATE TABLE ai_config (id BIGINT NOT NULL AUTO_INCREMENT, config_key VARCHAR(50) NOT NULL, config_value TEXT NOT NULL, description VARCHAR(200), updated_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (config_key), FOREIGN KEY(updated_by) REFERENCES admins (id))"""),
    ("announcements", """CREATE TABLE announcements (id BIGINT NOT NULL AUTO_INCREMENT, title VARCHAR(200) NOT NULL, content TEXT NOT NULL, type ENUM('notice','maintenance','update') NOT NULL, is_pinned INTEGER NOT NULL, status ENUM('draft','published','archived') NOT NULL, publish_at DATETIME, expire_at DATETIME, created_by BIGINT, created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(created_by) REFERENCES admins (id))"""),
    ("banned_words", """CREATE TABLE banned_words (id BIGINT NOT NULL AUTO_INCREMENT, word VARCHAR(100) NOT NULL, match_type ENUM('exact','contains','regex') NOT NULL, action ENUM('reject','replace','warn') NOT NULL, replace_with VARCHAR(100), is_active INTEGER NOT NULL, created_by BIGINT, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(created_by) REFERENCES admins (id))"""),
    ("conversations", """CREATE TABLE conversations (id BIGINT NOT NULL AUTO_INCREMENT, user_id BIGINT NOT NULL, title VARCHAR(200), created_at DATETIME NOT NULL DEFAULT now(), updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES users (id))"""),
    ("expire_reminder_config", """CREATE TABLE expire_reminder_config (id BIGINT NOT NULL AUTO_INCREMENT, days_before INTEGER NOT NULL, channel ENUM('site','sms','email') NOT NULL, template TEXT NOT NULL, is_active INTEGER NOT NULL, created_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(created_by) REFERENCES admins (id))"""),
    ("invite_codes", """CREATE TABLE invite_codes (id BIGINT NOT NULL AUTO_INCREMENT, code VARCHAR(50) NOT NULL, status ENUM('active','used','disabled','expired') NOT NULL, created_by BIGINT, used_by BIGINT, used_at DATETIME, remark VARCHAR(200), expire_at DATETIME, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (code), FOREIGN KEY(created_by) REFERENCES admins (id), FOREIGN KEY(used_by) REFERENCES users (id))"""),
    ("knowledge_config", """CREATE TABLE knowledge_config (id BIGINT NOT NULL AUTO_INCREMENT, config_key VARCHAR(50) NOT NULL, config_value TEXT NOT NULL, description VARCHAR(200), updated_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (config_key), FOREIGN KEY(updated_by) REFERENCES admins (id))"""),
    ("payment_config", """CREATE TABLE payment_config (id BIGINT NOT NULL AUTO_INCREMENT, channel ENUM('wechat','alipay') NOT NULL, merchant_id VARCHAR(100), api_key VARCHAR(500), api_secret VARCHAR(500), notify_url VARCHAR(500), is_active INTEGER NOT NULL, extra_config JSON, updated_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(updated_by) REFERENCES admins (id))"""),
    ("payments", """CREATE TABLE payments (id BIGINT NOT NULL AUTO_INCREMENT, user_id BIGINT NOT NULL, type ENUM('subscribe','redeem') NOT NULL, plan ENUM('monthly','yearly'), amount DECIMAL(10, 2), redeem_code VARCHAR(50), status ENUM('pending','success','failed') NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES users (id))"""),
    ("redeem_codes", """CREATE TABLE redeem_codes (id BIGINT NOT NULL AUTO_INCREMENT, code VARCHAR(50) NOT NULL, type ENUM('days','chats') NOT NULL, value INTEGER NOT NULL, status ENUM('unused','used','expired') NOT NULL, created_by BIGINT, used_by BIGINT, used_at DATETIME, expire_at DATETIME, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (code), FOREIGN KEY(created_by) REFERENCES admins (id), FOREIGN KEY(used_by) REFERENCES users (id))"""),
    ("register_config", """CREATE TABLE register_config (id BIGINT NOT NULL AUTO_INCREMENT, config_key VARCHAR(50) NOT NULL, config_value TEXT NOT NULL, description VARCHAR(200), updated_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), UNIQUE (config_key), FOREIGN KEY(updated_by) REFERENCES admins (id))"""),
    ("token_usage", """CREATE TABLE token_usage (id BIGINT NOT NULL AUTO_INCREMENT, user_id BIGINT NOT NULL, message_id BIGINT, model VARCHAR(50), input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL, cost_usd DECIMAL(10, 6), created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES users (id))"""),
    ("wecom_config", """CREATE TABLE wecom_config (id BIGINT NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, webhook_url VARCHAR(500) NOT NULL, notify_types JSON, is_active INTEGER NOT NULL, created_by BIGINT, updated_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(created_by) REFERENCES admins (id))"""),
    ("messages", """CREATE TABLE messages (id BIGINT NOT NULL AUTO_INCREMENT, conversation_id BIGINT NOT NULL, user_id BIGINT NOT NULL, `role` ENUM('user','assistant') NOT NULL, content TEXT NOT NULL, images JSON, docs JSON, input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL, feishu_synced INTEGER NOT NULL, created_at DATETIME NOT NULL DEFAULT now(), PRIMARY KEY (id), FOREIGN KEY(conversation_id) REFERENCES conversations (id), FOREIGN KEY(user_id) REFERENCES users (id))"""),
]

INDEX_SQL: dict[str, list[tuple[str, str]]] = {
    "llm_providers": [
        ("idx_llm_active", "CREATE INDEX idx_llm_active ON llm_providers (is_active)"),
        ("idx_llm_default", "CREATE INDEX idx_llm_default ON llm_providers (is_default)"),
    ],
    "users": [
        ("idx_status", "CREATE INDEX idx_status ON users (status)"),
        ("idx_user_subscribe_plan", "CREATE INDEX idx_user_subscribe_plan ON users (subscribe_plan)"),
        ("idx_phone", "CREATE INDEX idx_phone ON users (phone)"),
        ("idx_user_created_at", "CREATE INDEX idx_user_created_at ON users (created_at)"),
    ],
    "announcements": [
        ("idx_ann_publish", "CREATE INDEX idx_ann_publish ON announcements (publish_at)"),
        ("idx_ann_status", "CREATE INDEX idx_ann_status ON announcements (status)"),
    ],
    "banned_words": [
        ("idx_bw_active", "CREATE INDEX idx_bw_active ON banned_words (is_active)"),
    ],
    "conversations": [
        ("idx_conv_created_at", "CREATE INDEX idx_conv_created_at ON conversations (created_at)"),
        ("idx_conv_user", "CREATE INDEX idx_conv_user ON conversations (user_id)"),
        ("idx_conv_user_updated_id", "CREATE INDEX idx_conv_user_updated_id ON conversations (user_id, updated_at, id)"),
    ],
    "invite_codes": [
        ("idx_ic_status", "CREATE INDEX idx_ic_status ON invite_codes (status)"),
        ("idx_ic_code", "CREATE INDEX idx_ic_code ON invite_codes (code)"),
    ],
    "payments": [
        ("idx_pay_user", "CREATE INDEX idx_pay_user ON payments (user_id)"),
    ],
    "redeem_codes": [
        ("idx_rc_status", "CREATE INDEX idx_rc_status ON redeem_codes (status)"),
        ("idx_rc_code", "CREATE INDEX idx_rc_code ON redeem_codes (code)"),
    ],
    "token_usage": [
        ("idx_tu_date", "CREATE INDEX idx_tu_date ON token_usage (created_at)"),
        ("idx_tu_message", "CREATE INDEX idx_tu_message ON token_usage (message_id)"),
        ("idx_tu_date_model", "CREATE INDEX idx_tu_date_model ON token_usage (created_at, model)"),
        ("idx_tu_user", "CREATE INDEX idx_tu_user ON token_usage (user_id)"),
    ],
    "messages": [
        ("idx_msg_sync", "CREATE INDEX idx_msg_sync ON messages (feishu_synced)"),
        ("idx_msg_conv_created_id", "CREATE INDEX idx_msg_conv_created_id ON messages (conversation_id, created_at, id)"),
        ("idx_msg_created_user", "CREATE INDEX idx_msg_created_user ON messages (created_at, user_id)"),
        ("idx_msg_user", "CREATE INDEX idx_msg_user ON messages (user_id)"),
        ("idx_msg_role_created", "CREATE INDEX idx_msg_role_created ON messages (`role`, created_at)"),
        ("idx_msg_conv", "CREATE INDEX idx_msg_conv ON messages (conversation_id)"),
    ],
}

DROP_ORDER = [
    "messages",
    "wecom_config",
    "token_usage",
    "register_config",
    "redeem_codes",
    "payments",
    "payment_config",
    "knowledge_config",
    "invite_codes",
    "expire_reminder_config",
    "conversations",
    "banned_words",
    "announcements",
    "ai_config",
    "users",
    "plans",
    "llm_providers",
    "feishu_routes",
    "analytics_model_daily",
    "analytics_daily",
    "admins",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name, ddl in TABLE_SQL:
        if table_name not in existing_tables:
            op.execute(sa.text(ddl))
            existing_tables.add(table_name)

    inspector = sa.inspect(bind)
    for table_name, index_items in INDEX_SQL.items():
        if table_name not in existing_tables:
            continue
        existing_indexes = {item["name"] for item in inspector.get_indexes(table_name)}
        for index_name, ddl in index_items:
            if index_name not in existing_indexes:
                op.execute(sa.text(ddl))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name in DROP_ORDER:
        if table_name in existing_tables:
            op.execute(sa.text(f"DROP TABLE IF EXISTS `{table_name}`"))
