#!/usr/bin/env bash
# ============================================================
# db-restore.sh — 数据库恢复工具
#
# 用法：
#   db-restore.sh list                        — 列出可用备份
#   db-restore.sh full   [backup_file.sql.gz] — 从全量备份恢复
#   db-restore.sh pitr   <"YYYY-MM-DD HH:MM:SS"> — 时间点恢复
#   db-restore.sh rollback <minutes>          — 回滚最近 N 分钟的误操作
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="$(dirname "$SCRIPT_DIR")/backups"
FULL_DIR="$BACKUP_ROOT/full"
BINLOG_DIR="$BACKUP_ROOT/binlogs"

CONTAINER="abaojie-mysql"
DB_USER="root"
ENV_FILE="$(dirname "$SCRIPT_DIR")/.env"
if [[ -f "$ENV_FILE" ]]; then
  DB_PASS="$(grep '^MYSQL_ROOT_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'")"
  DB_NAME="$(grep '^MYSQL_DATABASE='      "$ENV_FILE" | cut -d= -f2- | tr -d '"'"'")"
fi
DB_PASS="${DB_PASS:-}"
DB_NAME="${DB_NAME:-abaojie}"

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'
ts()      { date '+%Y-%m-%d %H:%M:%S'; }
log()     { echo -e "[$(ts)] $*"; }
warn()    { echo -e "${YELLOW}[$(ts)] WARNING: $*${NC}"; }
success() { echo -e "${GREEN}[$(ts)] OK: $*${NC}"; }
die()     { echo -e "${RED}[$(ts)] ERROR: $*${NC}"; exit 1; }

require_container() {
  docker inspect "$CONTAINER" > /dev/null 2>&1 || die "容器 $CONTAINER 不存在或未运行"
}

confirm() {
  echo -e "${RED}$1${NC}"
  read -r -p "确认继续？输入 YES 继续，其他任意键取消：" ans
  [[ "$ans" == "YES" ]] || { log "已取消"; exit 0; }
}

mysql_exec() {
  docker exec -i "$CONTAINER" mysql -uroot -p"${DB_PASS}" 2>/dev/null
}

mysql_cmd() {
  docker exec "$CONTAINER" mysql -uroot -p"${DB_PASS}" -e "$1" 2>/dev/null
}

# ── 1. 列出备份 ──────────────────────────────────────────────
cmd_list() {
  echo ""
  echo "═══════════════════════════════════════════"
  echo "  全量备份列表"
  echo "═══════════════════════════════════════════"
  local found=0
  while IFS= read -r f; do
    local sz; sz="$(du -sh "$f" | cut -f1)"
    local ts_str; ts_str="$(stat -c%y "$f" | cut -d. -f1)"
    # 从文件名提取 binlog 位置
    local meta="${f%.sql.gz}.meta.txt"
    local pos=""
    [[ -f "$meta" ]] && pos="$(grep -oP 'Position: \K\d+' "$meta" 2>/dev/null | head -1 || true)"
    printf "  %-50s  %5s  %s  pos=%s\n" "$(basename "$f")" "$sz" "$ts_str" "${pos:-(无 meta)}"
    (( found++ )) || true
  done < <(ls -t "$FULL_DIR"/full_*.sql.gz 2>/dev/null)
  [[ $found -eq 0 ]] && echo "  (暂无全量备份，请先运行 db-backup.sh full)"

  echo ""
  echo "═══════════════════════════════════════════"
  echo "  Binlog 副本列表（最近 10 个）"
  echo "═══════════════════════════════════════════"
  ls -lht "$BINLOG_DIR"/binlog.* 2>/dev/null | head -10 || echo "  (暂无 binlog 副本)"
  echo ""
}

# ── 2. 全量恢复 ──────────────────────────────────────────────
cmd_full() {
  require_container
  local dump_file="${1:-}"

  # 未指定则用最新的
  if [[ -z "$dump_file" ]]; then
    dump_file="$(ls -t "$FULL_DIR"/full_*.sql.gz 2>/dev/null | head -1 || true)"
    [[ -n "$dump_file" ]] || die "找不到全量备份文件，请先运行 db-backup.sh full"
  fi
  [[ -f "$dump_file" ]] || die "备份文件不存在：$dump_file"

  local sz; sz="$(du -sh "$dump_file" | cut -f1)"
  confirm "⚠️  即将将数据库 $DB_NAME 恢复到备份：$(basename "$dump_file")（$sz）。当前所有数据将被覆盖！"

  log "开始全量恢复 | file=$(basename "$dump_file")"

  # 停止后端避免写入干扰
  warn "建议先停止后端服务：docker stop abaojie-backend"
  read -r -p "后端已停止？输入 ok 继续，skip 跳过停止步骤：" ans
  [[ "$ans" == "ok" ]] || warn "跳过停止后端，恢复期间可能有写入冲突"

  # 重建数据库
  mysql_cmd "DROP DATABASE IF EXISTS \`$DB_NAME\`; CREATE DATABASE \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
  log "数据库已清空，开始导入..."

  zcat "$dump_file" | docker exec -i "$CONTAINER" \
    mysql -uroot -p"${DB_PASS}" "$DB_NAME" 2>/dev/null

  success "全量恢复完成 | db=$DB_NAME"
  log "如需继续 PITR，请用 db-restore.sh pitr \"<目标时间>\""
}

# ── 3. PITR 时间点恢复 ──────────────────────────────────────
cmd_pitr() {
  require_container
  local target_time="${1:-}"
  [[ -n "$target_time" ]] || die "用法: db-restore.sh pitr \"YYYY-MM-DD HH:MM:SS\""

  # 找最新全量备份（比目标时间早的）
  local dump_file
  dump_file="$(ls -t "$FULL_DIR"/full_*.sql.gz 2>/dev/null | head -1 || true)"
  [[ -n "$dump_file" ]] || die "找不到全量备份"

  # 从 meta 获取全量备份时的 binlog 位置
  local meta="${dump_file%.sql.gz}.meta.txt"
  local binlog_start_file binlog_start_pos
  if [[ -f "$meta" ]]; then
    binlog_start_file="$(grep -oP 'File: \K\S+' "$meta" 2>/dev/null | head -1 || true)"
    binlog_start_pos="$(grep -oP 'Position: \K\d+' "$meta" 2>/dev/null | head -1 || true)"
  fi
  # 也可以从 dump 文件本身提取 --master-data=2 注释
  if [[ -z "$binlog_start_pos" ]]; then
    local master_line
    master_line="$(zcat "$dump_file" | grep '^-- CHANGE MASTER' | head -1 || true)"
    binlog_start_file="$(echo "$master_line" | grep -oP "MASTER_LOG_FILE='\\K[^']+" || true)"
    binlog_start_pos="$(echo "$master_line"  | grep -oP "MASTER_LOG_POS=\\K\d+" || true)"
  fi

  log "PITR 参数 | target=$target_time full=$(basename "$dump_file") binlog_start=$binlog_start_file:$binlog_start_pos"

  confirm "⚠️  即将执行 PITR，将数据恢复到 $target_time。当前数据库将被覆盖！"

  # Step 1: 先做全量恢复
  log "Step 1/2: 全量恢复..."
  zcat "$dump_file" | docker exec -i "$CONTAINER" \
    mysql -uroot -p"${DB_PASS}" --init-command="DROP DATABASE IF EXISTS \`$DB_NAME\`; CREATE DATABASE \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
    2>/dev/null || \
  ( mysql_cmd "DROP DATABASE IF EXISTS \`$DB_NAME\`; CREATE DATABASE \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" && \
    zcat "$dump_file" | docker exec -i "$CONTAINER" mysql -uroot -p"${DB_PASS}" "$DB_NAME" 2>/dev/null )

  success "全量恢复完成"

  # Step 2: 应用 binlog 直到目标时间
  log "Step 2/2: 应用 binlog 增量（截止 $target_time）..."

  # 找到所有比全量备份新的 binlog 副本
  local binlogs=()
  while IFS= read -r bf; do
    binlogs+=("$bf")
  done < <(ls -v "$BINLOG_DIR"/binlog.* 2>/dev/null)

  if [[ ${#binlogs[@]} -eq 0 ]]; then
    warn "未找到 binlog 副本（$BINLOG_DIR），跳过增量回放"
    warn "如 binlog 仍在容器内，可用容器内 mysqlbinlog 手动应用"
  else
    # 将 binlog 文件拼接后通过 mysqlbinlog 过滤时间范围，然后导入
    local binlog_args=()
    for bf in "${binlogs[@]}"; do
      binlog_args+=("$bf")
    done

    docker run --rm \
      --network container:"$CONTAINER" \
      -v "$BINLOG_DIR":/binlogs:ro \
      mysql:8.0 \
      mysqlbinlog \
        --start-position="${binlog_start_pos:-4}" \
        --stop-datetime="$target_time" \
        --base64-output=DECODE-ROWS \
        -v \
        $(for bf in "${binlogs[@]}"; do echo "/binlogs/$(basename "$bf")"; done) \
      | docker exec -i "$CONTAINER" mysql -uroot -p"${DB_PASS}" "$DB_NAME" 2>/dev/null

    success "binlog 增量应用完成，已恢复到 $target_time"
  fi
}

# ── 4. 误操作快速回滚（生成反向 SQL 预览）────────────────────
cmd_rollback() {
  require_container
  local minutes="${1:-10}"
  local stop_time="${2:-}"
  local start_time
  start_time="$(date -d "-${minutes} minutes" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || \
               date -v-${minutes}M '+%Y-%m-%d %H:%M:%S' 2>/dev/null)"

  log "提取最近 ${minutes} 分钟的 DML 操作（$start_time 至现在）..."

  local out_file="$BACKUP_ROOT/rollback_preview_$(date '+%Y%m%d_%H%M%S').sql"

  # 先刷新 binlog 以便拿到最新内容
  mysql_cmd "FLUSH BINARY LOGS;" 2>/dev/null

  # 从容器内 binlog 提取指定时间范围的语句（ROW 格式，解码为可读 SQL）
  docker exec "$CONTAINER" \
    mysqlbinlog \
      --start-datetime="$start_time" \
      --base64-output=DECODE-ROWS \
      -v \
      /var/lib/mysql/binlog.000001 \
      /var/lib/mysql/binlog.000002 \
      2>/dev/null > "$out_file" || true

  if [[ ! -s "$out_file" ]]; then
    warn "未找到该时间段的 binlog 操作"
    rm -f "$out_file"
    return
  fi

  local lines
  lines="$(wc -l < "$out_file")"
  success "已提取 $lines 行 binlog 操作 → $out_file"
  echo ""
  echo "═══════════════════════════════════════════"
  echo "  最近操作预览（前 60 行）"
  echo "═══════════════════════════════════════════"
  head -60 "$out_file"
  echo ""
  echo "──────────────────────────────────────────"
  echo "提示："
  echo "  1. 上方是最近 ${minutes} 分钟的所有 DML 操作"
  echo "  2. 定位到误操作的 binlog 位置号（# at XXXXXX）"
  echo "  3. 用以下命令恢复到误操作前的时间点："
  echo "     $0 pitr \"<误操作前的时间戳>\""
  echo "  4. 完整日志已保存到：$out_file"
}

# ── 入口 ─────────────────────────────────────────────────────
case "${1:-help}" in
  list)       cmd_list ;;
  full)       cmd_full     "${2:-}" ;;
  pitr)       cmd_pitr     "${2:-}" ;;
  rollback)   cmd_rollback "${2:-10}" ;;
  *)
    echo "用法: $0 {list|full|pitr|rollback}"
    echo "  list              — 列出所有可用备份"
    echo "  full [file]       — 从全量备份恢复（不加参数则用最新）"
    echo "  pitr \"YYYY-MM-DD HH:MM:SS\"  — 时间点恢复"
    echo "  rollback [N]      — 查看并回滚最近 N 分钟（默认10）的误操作"
    exit 1
    ;;
esac
