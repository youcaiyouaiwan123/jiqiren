-- =============================================================================
-- 分库分表与性能优化参考手册
-- 适用：MySQL 8.0 | jiqiren 答疑机器人
--
-- 目录：
--   §1  热表按月分区（Phase 1 触发阈值：messages > 500 万行）
--   §2  每月自动添加新分区（定时任务）
--   §3  主从读写分离（Phase 2 触发阈值：messages > 5000 万行）
--   §4  按 user_id Hash 分库（Phase 3 触发阈值：messages > 2 亿行）
--   §5  零停机迁移流程（pt-online-schema-change）
-- =============================================================================


-- =============================================================================
-- §1  热表按月 RANGE 分区（messages / token_usage）
--
-- 前置说明：
--   - MySQL RANGE 分区要求分区键必须是 PRIMARY KEY 的一部分
--   - 当前热表 PK 是单列 id，需要改为复合 PK (id, created_at)
--   - 直接 ALTER TABLE 会全表锁，必须用 §5 中的零停机方案
--   - 以下 DDL 适用于全新部署或已完成 §5 切换后的目标表
-- =============================================================================

-- messages 热表带月分区版
CREATE TABLE messages_hot (
    id              BIGINT       NOT NULL AUTO_INCREMENT,
    conversation_id BIGINT       NOT NULL,
    user_id         BIGINT       NOT NULL,
    role            VARCHAR(20)  NOT NULL,
    content         LONGTEXT     NOT NULL,
    images          JSON,
    docs            JSON,
    input_tokens    INT          NOT NULL DEFAULT 0,
    output_tokens   INT          NOT NULL DEFAULT 0,
    feishu_synced   INT          NOT NULL DEFAULT 0,
    created_at      DATETIME     NOT NULL,
    PRIMARY KEY (id, created_at),          -- 复合 PK，分区强制要求
    KEY idx_msg_conv (conversation_id),
    KEY idx_msg_user (user_id),
    KEY idx_msg_sync (feishu_synced),
    KEY idx_msg_conv_created_id (conversation_id, created_at, id),
    KEY idx_msg_created_user    (created_at, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
PARTITION BY RANGE COLUMNS(created_at) (
    PARTITION p_2026_01 VALUES LESS THAN ('2026-02-01'),
    PARTITION p_2026_02 VALUES LESS THAN ('2026-03-01'),
    PARTITION p_2026_03 VALUES LESS THAN ('2026-04-01'),
    PARTITION p_2026_04 VALUES LESS THAN ('2026-05-01'),
    PARTITION p_2026_05 VALUES LESS THAN ('2026-06-01'),
    PARTITION p_2026_06 VALUES LESS THAN ('2026-07-01'),
    PARTITION p_2026_07 VALUES LESS THAN ('2026-08-01'),
    PARTITION p_2026_08 VALUES LESS THAN ('2026-09-01'),
    PARTITION p_2026_09 VALUES LESS THAN ('2026-10-01'),
    PARTITION p_2026_10 VALUES LESS THAN ('2026-11-01'),
    PARTITION p_2026_11 VALUES LESS THAN ('2026-12-01'),
    PARTITION p_2026_12 VALUES LESS THAN ('2027-01-01'),
    PARTITION p_future  VALUES LESS THAN MAXVALUE
);

-- token_usage 热表带月分区版
CREATE TABLE token_usage_hot (
    id            BIGINT        NOT NULL AUTO_INCREMENT,
    user_id       BIGINT        NOT NULL,
    message_id    BIGINT,
    model         VARCHAR(50),
    input_tokens  INT           NOT NULL,
    output_tokens INT           NOT NULL,
    cost_usd      DECIMAL(10,6),
    created_at    DATETIME      NOT NULL,
    PRIMARY KEY (id, created_at),
    KEY idx_tu_user       (user_id),
    KEY idx_tu_date       (created_at),
    KEY idx_tu_date_model (created_at, model),
    KEY idx_tu_message    (message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
PARTITION BY RANGE COLUMNS(created_at) (
    PARTITION p_2026_01 VALUES LESS THAN ('2026-02-01'),
    -- ... 同上，按月延续 ...
    PARTITION p_future  VALUES LESS THAN MAXVALUE
);


-- =============================================================================
-- §2  每月自动添加新分区（在 MySQL Event Scheduler 或外部 Cron 中执行）
--
-- 将以下调用加入每月 1 日的 Cron：
--   mysql -u root -p<password> <db> < add_next_month_partition.sql
-- =============================================================================

-- 示例：在 2026-12 末为 2027-01 添加分区（需替换日期后执行）
ALTER TABLE messages
    REORGANIZE PARTITION p_future INTO (
        PARTITION p_2027_01 VALUES LESS THAN ('2027-02-01'),
        PARTITION p_future  VALUES LESS THAN MAXVALUE
    );

ALTER TABLE token_usage
    REORGANIZE PARTITION p_future INTO (
        PARTITION p_2027_01 VALUES LESS THAN ('2027-02-01'),
        PARTITION p_future  VALUES LESS THAN MAXVALUE
    );

-- 查看当前分区状态
SELECT
    PARTITION_NAME,
    TABLE_ROWS,
    PARTITION_DESCRIPTION
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_NAME IN ('messages', 'token_usage')
  AND TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME, PARTITION_ORDINAL_POSITION;


-- =============================================================================
-- §3  主从读写分离（Phase 2，配合 SQLAlchemy 多引擎路由）
--
-- MySQL 配置（my.cnf - 主库）：
--   server-id = 1
--   log_bin   = mysql-bin
--   binlog_format = ROW
--
-- MySQL 配置（my.cnf - 从库）：
--   server-id = 2
--   relay_log = relay-bin
--   read_only = ON
--
-- 应用侧改动：见 backend/app/core/database_replica.py（按需添加）
-- 路由规则：
--   写操作（INSERT/UPDATE/DELETE）→ 主库引擎 engine_primary
--   读操作（SELECT）              → 从库引擎 engine_replica
--
-- 参考（SQLAlchemy 文档）：
--   https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html#partitioning-strategies
-- =============================================================================

-- 主库：创建复制账号
CREATE USER 'replica'@'%' IDENTIFIED BY 'replica_password';
GRANT REPLICATION SLAVE ON *.* TO 'replica'@'%';
FLUSH PRIVILEGES;

-- 主库：查看 binlog 位置
SHOW MASTER STATUS;

-- 从库：配置复制源
CHANGE MASTER TO
    MASTER_HOST='<主库 IP>',
    MASTER_USER='replica',
    MASTER_PASSWORD='replica_password',
    MASTER_LOG_FILE='mysql-bin.000001',  -- 替换为 SHOW MASTER STATUS 的值
    MASTER_LOG_POS=154;

START SLAVE;
SHOW SLAVE STATUS\G


-- =============================================================================
-- §4  按 user_id Hash 分库（Phase 3，使用 ShardingSphere 或应用层路由）
--
-- 分片键：user_id（所有热表都有 user_id，同一用户数据落同一分片）
-- 分片数：建议从 4 个分片起步，按需翻倍
-- 路由规则：shard_id = user_id % 4
--
-- ShardingSphere 配置片段（sharding-jdbc.yaml）：
-- =============================================================================

/*
rules:
  - !SHARDING
    tables:
      messages:
        actualDataNodes: ds_${0..3}.messages_${0..3}
        tableStrategy:
          standard:
            shardingColumn: user_id
            shardingAlgorithmName: hash_mod
        keyGenerateStrategy:
          column: id
          keyGeneratorName: snowflake
      token_usage:
        actualDataNodes: ds_${0..3}.token_usage_${0..3}
        tableStrategy:
          standard:
            shardingColumn: user_id
            shardingAlgorithmName: hash_mod
      conversations:
        actualDataNodes: ds_${0..3}.conversations_${0..3}
        tableStrategy:
          standard:
            shardingColumn: user_id
            shardingAlgorithmName: hash_mod
    shardingAlgorithms:
      hash_mod:
        type: HASH_MOD
        props:
          sharding-count: 4
    keyGenerators:
      snowflake:
        type: SNOWFLAKE
*/


-- =============================================================================
-- §5  零停机迁移：现有大表加分区（使用 pt-online-schema-change）
--
-- 场景：messages 表已有大量数据，需要改复合 PK 并加分区，不能停服
-- 工具：Percona pt-online-schema-change（pt-osc）
--
-- 步骤：
--   1. 创建目标分区表（新名称）
--   2. pt-osc 将数据增量同步到新表（通过触发器捕获变更）
--   3. 原子重命名：messages → messages_old, messages_hot → messages
--   4. 验证数据一致性后，DROP messages_old
-- =============================================================================

-- Step 1: 创建带分区的目标表（见 §1 的 messages_hot DDL）

-- Step 2: 使用 pt-osc 增量同步（在 Shell 中执行）
/*
pt-online-schema-change \
    --host=127.0.0.1 \
    --user=root \
    --password=<password> \
    --database=<db_name> \
    --table=messages \
    --alter="ENGINE=InnoDB" \
    --new-table-name=messages_new \
    --no-drop-old-table \
    --execute

# pt-osc 会：
#   a. 创建 _messages_new 影子表（无分区但带触发器）
#   b. 拷贝历史数据（分块 INSERT SELECT，不锁表）
#   c. 最终原子 RENAME: messages → _messages_old, _messages_new → messages
*/

-- Step 3: 手动将数据从 messages（已改名为 _messages_old）迁至分区表
/*
# 如果需要分区表，先手动建 messages_partitioned（见 §1）
# 然后批量迁移：

INSERT INTO messages_partitioned
SELECT * FROM _messages_old
WHERE id BETWEEN 1 AND 100000;   -- 按批次执行，每批 10-20 万行

# 确认行数一致后：
RENAME TABLE messages TO messages_no_partition,
             messages_partitioned TO messages;
DROP TABLE messages_no_partition;  -- 确认无误后执行
*/

-- Step 4: 验证
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM _messages_old;  -- 应相等

-- 查询性能验证（应走分区裁剪）
EXPLAIN SELECT * FROM messages
WHERE created_at BETWEEN '2026-04-01' AND '2026-04-30'
  AND user_id = 123;
-- 观察 partitions 列，应只扫描 p_2026_04，不是全部分区
