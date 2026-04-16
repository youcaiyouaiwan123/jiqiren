#!/bin/sh
set -e

echo "==> 等待 MySQL 准备就绪..."
# docker-compose 里已经 depends_on healthcheck，这里做二次保险
python - <<'PY'
import os, time, socket
host = os.environ.get("MYSQL_HOST", "mysql")
port = int(os.environ.get("MYSQL_PORT", "3306"))
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"MySQL {host}:{port} 可连接")
            break
    except OSError:
        print(f"[{i+1}/60] MySQL {host}:{port} 未就绪, 1s 后重试...")
        time.sleep(1)
else:
    raise SystemExit("MySQL 连接超时")
PY

echo "==> 执行数据库迁移 alembic upgrade head"
alembic -c alembic.ini upgrade head

echo "==> 启动应用: $@"
exec "$@"
