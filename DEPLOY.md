# Docker 部署指南（一键全栈）

本项目提供基于 Docker Compose 的全栈部署方案，包含：

- **mysql** (MySQL 8.0)
- **redis** (Redis 7)
- **backend** (FastAPI + uvicorn，端口 8015，容器内)
- **frontend** (nginx 提供静态资源 + 反向代理 `/api` 到 backend，默认暴露 80)

---

## 1. 服务器准备

1. 安装 Docker 和 Docker Compose（v2）
   ```bash
   curl -fsSL https://get.docker.com | sh
   # 如使用非 root，将当前用户加入 docker 组后重新登录
   sudo usermod -aG docker $USER
   ```
2. 验证
   ```bash
   docker --version
   docker compose version
   ```

## 2. 获取代码

```bash
git clone https://github.com/youcaiyouaiwan123/jiqiren.git abaojie
cd abaojie
```

## 3. 配置环境变量

```bash
cp .env.docker.example .env
vim .env   # 修改下列关键项：
```

必须改：

- `MYSQL_ROOT_PASSWORD`：数据库 root 密码，**不要用默认值**
- `JWT_SECRET`：随机长字符串，生产环境必改
- `CLAUDE_API_KEY`：Claude 密钥（若启用）

可选：

- 飞书、知识库 embedding、git 仓库等

> 密码里**不要包含 `@ : / ?`** 这些 URL 特殊字符，后端 DSN 拼接未做 URL encode。

## 4. 一键启动

```bash
docker compose up -d --build
```

首次启动流程：

1. 拉 `mysql:8.0`、`redis:7-alpine`、`node:22-alpine`、`python:3.11-slim-bookworm`、`nginx:1.27-alpine`
2. 构建 backend 镜像（包含 pip 安装依赖）
3. 构建 frontend 镜像（包含 npm ci + vite build）
4. 启 mysql、redis，等健康检查通过
5. backend 容器启动时自动：
   - 等 MySQL 可连接
   - 执行 `alembic upgrade head` 做迁移
   - 启动 uvicorn
6. frontend nginx 监听 80 端口

查看状态：

```bash
docker compose ps
docker compose logs -f backend
```

## 5. 访问

- 前端页面：`http://服务器IP/`
- API 文档（需在 compose 打开 backend 的端口映射）：`http://服务器IP:8015/docs`

## 6. 常用运维命令

```bash
# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 重启单个服务
docker compose restart backend

# 代码更新后重新构建
git pull
docker compose up -d --build

# 停止 / 删除
docker compose stop
docker compose down           # 保留数据卷
docker compose down -v        # 同时删除数据卷（⚠️ 会清空数据库）

# 进入容器调试
docker compose exec backend bash
docker compose exec mysql mysql -uroot -p

# 手动执行迁移
docker compose exec backend alembic upgrade head
```

## 7. 数据持久化说明

以下内容不会随容器销毁丢失：

| 挂载路径 | 宿主机位置 | 说明 |
|---|---|---|
| `mysql_data` | docker volume | 数据库数据 |
| `redis_data` | docker volume | Redis 持久化（AOF） |
| `backend_data` | docker volume | chroma 索引等 |
| `whisper_cache` | docker volume | faster-whisper 模型缓存（避免每次重启重下） |
| `./backend/uploads` | 宿主机目录 | 用户上传的图片/音频 |
| `./backend/logs` | 宿主机目录 | 后端日志 |
| `./knowledge` | 宿主机目录 | 本地知识库 markdown |

### 备份建议

```bash
# MySQL 备份
docker compose exec mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --databases $MYSQL_DATABASE' > backup_$(date +%F).sql

# 整卷备份
docker run --rm -v abaojie_mysql_data:/data -v "$PWD":/backup alpine tar czf /backup/mysql_data_$(date +%F).tgz -C /data .
```

## 8. 上线后常见问题

- **端口 80 被占用**：在 `.env` 里改 `FRONTEND_PORT=8080`
- **MySQL 启动慢导致 backend 报连接拒绝**：`docker-entrypoint.sh` 已内置 60s 等待，一般不会；若仍失败重启 backend 即可
- **短信/邮件未配置**：登录到后台 → 注册配置页面在线配置，无需改代码
- **语音转写首次慢**：faster-whisper 模型首次会从 HuggingFace 下载，缓存在 `whisper_cache` volume 内，后续秒启

## 9. HTTPS（可选）

推荐用 Caddy / Traefik 做前置：

```bash
# 简化做法：docker 宿主上再跑一个 Caddy，反代到容器 80
# Caddyfile
your-domain.com {
    reverse_proxy 127.0.0.1:80
}
```

或在 `frontend/nginx.conf` 增加 443 监听 + certbot 证书挂载。需要我加的话告诉我域名。
