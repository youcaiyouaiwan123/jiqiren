# ========= backend image =========
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Shanghai

# 系统依赖：
#  - ffmpeg：faster-whisper 解码音频
#  - curl：容器内健康检查
#  - dos2unix：修正 Windows 上提交的 CRLF 脚本
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖（利用 docker cache）
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# 再拷贝项目代码
COPY . /app

# 确保运行时目录存在
RUN mkdir -p /app/uploads /app/logs /app/data

EXPOSE 8015

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN dos2unix /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

# start-period 设长一些：首次启动时 lifespan 会预加载 faster-whisper 模型，
# 国内网络首次可能需要 2-5 分钟从 HuggingFace 下载
HEALTHCHECK --interval=15s --timeout=5s --start-period=300s --retries=10 \
    CMD curl -fsS http://127.0.0.1:8015/api/health >/dev/null || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
# --proxy-headers + --forwarded-allow-ips 保证 nginx 反代时能拿到真实客户端 IP，
# 否则后端基于 IP 的频控（_ip_rate_key）会把所有用户合并成一个 IP 计数
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8015", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
