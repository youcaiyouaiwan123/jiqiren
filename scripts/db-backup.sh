#!/usr/bin/env bash
# ============================================================
# db-backup.sh — MySQL 全量 + Binlog 增量备份
#
# 用法：
#   db-backup.sh full      — 执行全量备份（建议每日 cron）
#   db-backup.sh binlog    — 刷新并拷贝最新 binlog（建议每小时 cron）
#   db-backup.sh clean     — 清理过期备份（> FULL_KEEP_DAYS 天的全量）
#
# 依赖：docker（abaojie-mysql 容器运行中）
# ============================================================
set -euo pipefail

# ── 配置 ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="$(dirname "$SCRIPT_DIR")/backups"
FULL_DIR="$BACKUP_ROOT/full"
BINLOG_DIR="$BACKUP_ROOT/binlogs"
LOG_FILE="$BACKUP_ROOT/backup.log"

CONTAINER="abaojie-mysql"
DB_USER="root"
# 从 .env 读取密码（脚本与 .env 同层级的上上级目录）
ENV_FILE="$(dirname "$SCRIPT_DIR")/.env"
if [[ -f "$ENV_FILE" ]]; then
  DB_PASS="$(grep '^MYSQL_ROOT_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'")"
  DB_NAME="$(grep '^MYSQL_DATABASE='      "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'")"
fi
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-abaojie}"

FULL_KEEP_DAYS=7        # 全量备份保留天数
BINLOG_KEEP_DAYS=7      # binlog 副本保留天数

# ── 工具函数 ──────────────────────────────────────────────────
ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG_FILE"; }
die() { log "ERROR: $*"; exit 1; }

require_container() {
  docker inspect "$CONTAINER" > /dev/null 2>&1 || die "容器 $CONTAINER 不存在或未运行"
}

mysql_cmd() {
  docker exec "$CONTAINER" mysql -uroot -p"${DB_PASS}" -e "$1" 2>/dev/null
}

# ── 全量备份 ──────────────────────────────────────────────────
cmd_full() {
  require_container
  local stamp
  stamp="$(date '+%Y%m%d_%H%M%S')"
  local dump_file="$FULL_DIR/full_${stamp}.sql.gz"
  local meta_file="$FULL_DIR/full_${stamp}.meta.txt"

  log "=== 开始全量备份 | db=$DB_NAME stamp=$stamp ==="

  # 记录备份前的 binlog 位置（PITR 起始点）
  local binlog_status
  binlog_status="$(mysql_cmd 'SHOW MASTER STATUS\G' 2>/dev/null)"
  echo "$binlog_status" > "$meta_file"
  log "binlog 位置已记录 → $meta_file"

  # mysqldump 关键参数说明：
  #   --single-transaction : InnoDB 一致性快照，不锁表
  #   --master-data=2      : 在 dump 注释中记录 binlog 文件名+位置（PITR 必需）
  #   --routines/triggers  : 包含存储过程和触发器
  docker exec "$CONTAINER" \
    mysqldump -uroot -p"${DB_PASS}" \
      --single-transaction \
      --master-data=2 \
      --routines \
      --triggers \
      --events \
      --set-gtid-purged=OFF \
      "$DB_NAME" \
    | gzip -9 > "$dump_file"

  local size
  size="$(du -sh "$dump_file" | cut -f1)"
  log "全量备份完成 | 文件=$dump_file 大小=$size"

  # 顺手做一次 binlog 刷新，让本次全量成为一个干净的切割点
  mysql_cmd "FLUSH BINARY LOGS;" 2>/dev/null && log "binlog 已刷新"

  # 写最新备份路径（供 restore 脚本使用）
  echo "$dump_file" > "$BACKUP_ROOT/latest_full.txt"
  log "=== 全量备份结束 ==="
}

# ── 增量（binlog）备份 ────────────────────────────────────────
cmd_binlog() {
  require_container

  log "=== 开始 binlog 增量备份 ==="

  # 刷新让当前 binlog 归档，MySQL 切到新文件
  mysql_cmd "FLUSH BINARY LOGS;" 2>/dev/null

  # 获取容器内所有 binlog 文件名
  local binlog_files
  binlog_files="$(docker exec "$CONTAINER" \
    mysql -uroot -p"${DB_PASS}" -e "SHOW BINARY LOGS;" 2>/dev/null \
    | awk 'NR>1 {print $1}')"

  local copied=0
  while IFS= read -r bfile; do
    local dest="$BINLOG_DIR/$bfile"
    # 已存在且大小一致则跳过
    local src_size
    src_size="$(docker exec "$CONTAINER" stat -c%s "/var/lib/mysql/$bfile" 2>/dev/null || echo 0)"
    local dst_size=0
    [[ -f "$dest" ]] && dst_size="$(stat -c%s "$dest")"

    if [[ "$src_size" != "$dst_size" ]]; then
      docker cp "$CONTAINER:/var/lib/mysql/$bfile" "$dest"
      log "  拷贝 binlog: $bfile (${src_size} bytes)"
      (( copied++ )) || true
    fi
  done <<< "$binlog_files"

  log "binlog 增量备份完成 | 新增/更新 $copied 个文件"
  log "=== binlog 备份结束 ==="
}

# ── 清理过期备份 ──────────────────────────────────────────────
cmd_clean() {
  log "=== 清理过期备份 (全量>${FULL_KEEP_DAYS}天, binlog>${BINLOG_KEEP_DAYS}天) ==="
  local count=0

  while IFS= read -r f; do
    rm -f "$f"
    log "  删除: $f"
    (( count++ )) || true
  done < <(find "$FULL_DIR" -name "full_*.sql.gz" -mtime "+${FULL_KEEP_DAYS}" 2>/dev/null)

  while IFS= read -r f; do
    rm -f "$f"
    (( count++ )) || true
  done < <(find "$BINLOG_DIR" -name "binlog.*" -mtime "+${BINLOG_KEEP_DAYS}" 2>/dev/null)

  log "清理完成，共删除 $count 个文件"
}

# ── 状态摘要 ──────────────────────────────────────────────────
cmd_status() {
  echo ""
  echo "╔═══════════════════════════════════════╗"
  echo "║         数据库备份状态摘要             ║"
  echo "╚═══════════════════════════════════════╝"
  echo ""
  echo "── 全量备份 ($FULL_DIR) ──"
  ls -lht "$FULL_DIR"/full_*.sql.gz 2>/dev/null | head -7 || echo "  (暂无全量备份)"
  echo ""
  echo "── Binlog 副本 ($BINLOG_DIR) ──"
  ls -lht "$BINLOG_DIR"/binlog.* 2>/dev/null | head -10 || echo "  (暂无 binlog 副本)"
  echo ""
  echo "── 最新全量备份路径 ──"
  cat "$BACKUP_ROOT/latest_full.txt" 2>/dev/null || echo "  (未知)"
  echo ""
  echo "── 容器内当前 binlog ──"
  mysql_cmd "SHOW BINARY LOGS;" 2>/dev/null || echo "  (容器未运行)"
  echo ""
}

# ── 入口 ─────────────────────────────────────────────────────
mkdir -p "$FULL_DIR" "$BINLOG_DIR"

case "${1:-help}" in
  full)    cmd_full   ;;
  binlog)  cmd_binlog ;;
  clean)   cmd_clean  ;;
  status)  cmd_status ;;
  *)
    echo "用法: $0 {full|binlog|clean|status}"
    echo "  full   — 全量备份（每日 cron）"
    echo "  binlog — 增量 binlog 备份（每小时 cron）"
    echo "  clean  — 清理过期文件"
    echo "  status — 查看备份状态"
    exit 1
    ;;
esac
