"""
统一日志配置
- 控制台：彩色输出，INFO 级别
- 文件：按日切割，保留 30 天，DEBUG 级别
- 日志目录：backend/logs/
"""
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "DEBUG") -> None:
    """初始化全局日志，应在应用启动最早期调用一次。"""
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.DEBUG))

    # 避免重复添加 handler（热重载场景）
    if root.handlers:
        return

    # ---- 控制台 handler ----
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
    root.addHandler(console)

    # ---- 文件 handler（按天切割，保留 30 天）----
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
    file_handler.suffix = "%Y-%m-%d"
    root.addHandler(file_handler)

    # 降低第三方库噪音
    for noisy in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine", "aiomysql", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("uvicorn").setLevel(logging.INFO)

    root.info("日志系统初始化完成 | level=%s | file=%s", level, LOG_FILE)
