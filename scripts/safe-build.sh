#!/usr/bin/env bash
#
# 安全构建脚本：强制「一个一个」串行构建，避免 3.4GB 小内存机器
# 在「前后端同时构建 + 服务还在运行」时被内存压垮、整机卡死/重启。
#
# 它做的事，对每个服务严格按顺序：
#   1) 先停掉该容器，腾出运行时占用的内存
#   2) 单独构建该服务的镜像（不并行其他服务）
#   3) 重新启动并等待就绪
#   4) 打印内存水位，再进入下一个
#
# 用法：
#   ./scripts/safe-build.sh                 # 默认依次：backend → frontend
#   ./scripts/safe-build.sh frontend        # 只构建前端
#   ./scripts/safe-build.sh backend frontend
#
# 注意：构建期间被构建的那个服务会短暂停机（用短暂停机换「不卡死整机」）。
set -uo pipefail

# 切到项目根目录（docker-compose.yml 所在）
cd "$(dirname "$0")/.." || exit 1

# 要构建的服务，默认 backend 然后 frontend
SERVICES=("$@")
if [ ${#SERVICES[@]} -eq 0 ]; then
  SERVICES=(backend frontend)
fi

echo "==> 计划串行构建（严格一个一个来）: ${SERVICES[*]}"
echo "==> 当前内存："
free -h | head -2

for svc in "${SERVICES[@]}"; do
  cname="abaojie-${svc}"
  echo ""
  echo "================ [${svc}] 开始 ================"

  echo "--> 1/3 停止 ${svc}，腾出内存"
  docker compose stop "${svc}" 2>/dev/null || true
  free -h | head -2

  echo "--> 2/3 单独构建 ${svc}（不与其他服务并行）"
  if ! docker compose build "${svc}"; then
    echo "!! ${svc} 构建失败，已保留旧容器停止状态。请检查后重试。"
    echo "!! 重新拉起旧镜像： docker compose up -d ${svc}"
    exit 1
  fi

  echo "--> 3/3 启动 ${svc} 并等待就绪"
  docker compose up -d "${svc}"

  # 最多等约 3 分钟；有健康检查的等 healthy，没有的等容器 running
  ok=""
  for _ in $(seq 1 36); do
    health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${cname}" 2>/dev/null || echo "missing")
    running=$(docker inspect -f '{{.State.Running}}' "${cname}" 2>/dev/null || echo "false")
    if { [ "${health}" = "healthy" ] || [ "${health}" = "none" ]; } && [ "${running}" = "true" ]; then
      ok="yes"; break
    fi
    sleep 5
  done

  if [ "${ok}" = "yes" ]; then
    echo "    ${svc} 已就绪 (health=${health})"
  else
    echo "    ⚠ ${svc} 启动后未在预期时间内就绪，请用 docker compose logs ${svc} 排查"
  fi

  echo "--> 内存水位："
  free -h | head -3
  echo "================ [${svc}] 完成 ================"
done

echo ""
echo "==> 全部串行构建完成（始终一个一个，未并行）。"
docker compose ps
