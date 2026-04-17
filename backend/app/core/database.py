import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_async_engine(
    settings.mysql_dsn,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,    # 取连接前先 ping，避免 "MySQL has gone away"
    pool_recycle=1800,     # 30 分钟回收空闲连接，防止 MySQL wait_timeout 断开
    pool_timeout=30,       # 等待可用连接最多 30 秒，超时抛出而非阻塞
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("[DB] 会话异常回滚")
            raise
