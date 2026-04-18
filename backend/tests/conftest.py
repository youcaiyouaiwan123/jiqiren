"""
测试基础设施：SQLite 内存库 + fakeredis + FastAPI TestClient
所有测试共享同一套 fixture 体系。
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest


class LuaCapableFakeRedis(fakeredis.aioredis.FakeRedis):
    """扩展 fakeredis：实现项目使用的两段 Lua 脚本（atomic_incr + consume_verify_code）"""

    async def eval(self, script: str, numkeys: int, *keys_and_args):
        # atomic_incr：INCR key, if n==1 then EXPIRE
        if "INCR" in script and "EXPIRE" in script and "return n" in script:
            key = keys_and_args[0]
            ttl = int(keys_and_args[1])
            n = await self.incr(key)
            if n == 1:
                await self.expire(key, ttl)
            return n
        # consume_verify_code：GET, compare, DEL
        if "DEL" in script and "current ~= ARGV[1]" in script:
            key = keys_and_args[0]
            expected = keys_and_args[1]
            current = await self.get(key)
            if current is None:
                return 0
            if current != expected:
                return -1
            await self.delete(key)
            return 1
        raise NotImplementedError(f"Unknown Lua script in tests")
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# ── 覆盖数据库 URL（SQLite 内存），必须在 app 导入前设置 ──────────────────────
os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_USER", "root")
os.environ.setdefault("MYSQL_PASSWORD", "test")
os.environ.setdefault("MYSQL_DATABASE", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("REDIS_HOST", "localhost")

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# SQLite 不支持 BIGINT 自增主键，必须编译为 INTEGER
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import BigInteger as _BigInteger


@compiles(_BigInteger, "sqlite")
def _sqlite_bigint(element, compiler, **kw):
    return "INTEGER"


test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# ── 覆盖配置 lru_cache ────────────────────────────────────────────────────────
from app.config import Settings, get_settings
from app.core import database as _db_module
from app.core import redis as _redis_module

get_settings.cache_clear()


def _make_test_settings():
    s = Settings(
        MYSQL_HOST="localhost",
        MYSQL_PORT=3306,
        MYSQL_USER="root",
        MYSQL_PASSWORD="test",
        MYSQL_DATABASE="test",
        JWT_SECRET="test-secret-key-for-testing-only",
        JWT_ACCESS_EXPIRE_MINUTES=120,
        JWT_REFRESH_EXPIRE_DAYS=7,
        REDIS_HOST="localhost",
    )
    return s


_test_settings = _make_test_settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


import app.models.admin  # noqa: F401
import app.models.ai_config  # noqa: F401
import app.models.analytics_daily  # noqa: F401
import app.models.analytics_model_daily  # noqa: F401
import app.models.analytics_user_daily  # noqa: F401
import app.models.announcement  # noqa: F401
import app.models.banned_word  # noqa: F401
import app.models.conversation  # noqa: F401
import app.models.expire_reminder  # noqa: F401
import app.models.feishu_route  # noqa: F401
import app.models.invite_code  # noqa: F401
import app.models.knowledge_config  # noqa: F401
import app.models.llm_provider  # noqa: F401
import app.models.message  # noqa: F401
import app.models.message_feedback  # noqa: F401
import app.models.payment  # noqa: F401
import app.models.payment_config  # noqa: F401
import app.models.plan  # noqa: F401
import app.models.redeem_code  # noqa: F401
import app.models.register_config  # noqa: F401
import app.models.token_usage  # noqa: F401
import app.models.user  # noqa: F401
import app.models.wecom_config  # noqa: F401


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """会话级别：创建所有表"""
    from app.core.database import Base

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """每个测试前清空所有表，保证隔离"""
    from app.core.database import Base

    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def fake_redis():
    """fakeredis with Lua eval support（原子计数器 + 验证码消费）"""
    server = LuaCapableFakeRedis(decode_responses=True)
    yield server
    await server.aclose()


@pytest_asyncio.fixture
async def client(db, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    from app.core.database import get_db
    from app.main_v2 import app
    import app.core.redis as redis_mod

    async def override_get_db():
        yield db

    redis_mod.redis_client = fake_redis
    app.dependency_overrides[get_db] = override_get_db

    with patch.object(_db_module, "async_session", TestSessionLocal):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()
    redis_mod.redis_client = None


# ── 工具函数 ──────────────────────────────────────────────────────────────────

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.admin import Admin
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.redeem_code import RedeemCode
from app.models.llm_provider import LlmProvider
from app.models.plan import Plan
from app.models.payment_config import PaymentConfig


async def create_user(
    db: AsyncSession,
    *,
    phone: str = "13800000001",
    email: str | None = None,
    password: str = "Password123",
    nickname: str = "测试用户",
    free_chats_left: int = 5,
    subscribe_plan: str = "free",
    subscribe_expire: datetime | None = None,
    status: str = "active",
) -> User:
    user = User(
        phone=phone,
        email=email,
        password_hash=hash_password(password),
        nickname=nickname,
        free_chats_left=free_chats_left,
        subscribe_plan=subscribe_plan,
        subscribe_expire=subscribe_expire,
        status=status,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_admin(
    db: AsyncSession,
    *,
    username: str = "admin",
    password: str = "Admin@123456",
    role: str = "super",
) -> Admin:
    admin = Admin(
        username=username,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


def user_token(user_id: int) -> str:
    return create_access_token({"user_id": user_id, "role": "user"})


def admin_token(admin_id: int, role: str = "super") -> str:
    return create_access_token({"admin_id": admin_id, "role": "admin", "admin_role": role})


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def create_conversation(
    db: AsyncSession, user_id: int, title: str = "测试会话"
) -> Conversation:
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def create_message(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    role: str = "user",
    content: str = "测试消息",
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def create_redeem_code(
    db: AsyncSession,
    *,
    code: str = "TEST001",
    type: str = "chats",
    value: int = 10,
    status: str = "unused",
    expire_at: datetime | None = None,
) -> RedeemCode:
    rc = RedeemCode(
        code=code,
        type=type,
        value=value,
        status=status,
        expire_at=expire_at,
    )
    db.add(rc)
    await db.commit()
    await db.refresh(rc)
    return rc


async def create_llm_provider(
    db: AsyncSession,
    *,
    name: str = "Test Claude",
    provider: str = "claude",
    api_url: str = "https://api.anthropic.com",
    api_key: str = "sk-test",
    model: str = "claude-3-haiku-20240307",
    is_default: int = 1,
    is_active: int = 1,
) -> LlmProvider:
    llm = LlmProvider(
        name=name,
        provider=provider,
        api_url=api_url,
        api_key=api_key,
        model=model,
        is_default=is_default,
        is_active=is_active,
    )
    db.add(llm)
    await db.commit()
    await db.refresh(llm)
    return llm


async def create_plan(
    db: AsyncSession,
    *,
    name: str = "月度会员",
    type: str = "monthly",
    price: float = 29.9,
    duration_days: int = 30,
    is_active: int = 1,
) -> Plan:
    plan = Plan(
        name=name,
        type=type,
        price=price,
        duration_days=duration_days,
        is_active=is_active,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def create_payment_config(
    db: AsyncSession,
    *,
    channel: str = "wechat",
    is_active: int = 1,
    extra_config: dict | None = None,
) -> PaymentConfig:
    cfg = PaymentConfig(
        channel=channel,
        is_active=is_active,
        extra_config=extra_config or {"display_name": "微信支付", "checkout_url": ""},
    )
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return cfg
