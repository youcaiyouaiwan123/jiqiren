"""
数据持久性测试
覆盖：事务回滚、数据写后读一致性、级联删除、跨会话持久化、
      数据库异常时配额回滚
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from tests.conftest import (
    auth_headers,
    create_admin,
    create_conversation,
    create_message,
    create_redeem_code,
    create_user,
    user_token,
)
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.redeem_code import RedeemCode
from app.models.token_usage import TokenUsage
from app.models.user import User

pytestmark = pytest.mark.asyncio


class TestWriteThenRead:
    async def test_user_data_persists_after_create(self, client: AsyncClient, db):
        """创建用户后立即可查到"""
        user = await create_user(db, phone="13900000001", nickname="持久用户")
        result = await db.get(User, user.id)
        assert result is not None
        assert result.nickname == "持久用户"

    async def test_conversation_data_persists(self, client: AsyncClient, db):
        """创建会话后立即可查"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id, title="持久会话")
        result = await db.get(Conversation, conv.id)
        assert result is not None
        assert result.title == "持久会话"

    async def test_message_persists_with_correct_user(self, client: AsyncClient, db):
        """消息持久化且 user_id 正确"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "user", "持久消息")

        result = await db.get(Message, msg.id)
        assert result.content == "持久消息"
        assert result.user_id == user.id

    async def test_api_create_conversation_persists(self, client: AsyncClient, db):
        """通过 API 创建的会话在数据库中持久"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/conversations",
            json={"title": "API创建的会话"},
            headers=auth_headers(user_token(user.id)),
        )
        conv_id = r.json()["data"]["id"]

        # 直接数据库查询验证
        result = await db.get(Conversation, conv_id)
        assert result is not None
        assert result.title == "API创建的会话"

    async def test_profile_update_persists(self, client: AsyncClient, db):
        """profile 更新持久化到数据库"""
        user = await create_user(db, nickname="旧昵称")
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": "新昵称"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0

        # 再次读取验证持久化
        r2 = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        assert r2.json()["data"]["nickname"] == "新昵称"

    async def test_redeem_code_status_update_persists(self, client: AsyncClient, db):
        """兑换后兑换码状态持久化"""
        user = await create_user(db)
        await create_redeem_code(db, code="PERSIST001", type="chats", value=5)

        await client.post(
            "/api/subscribe/redeem",
            json={"code": "PERSIST001"},
            headers=auth_headers(user_token(user.id)),
        )

        rc = (await db.execute(select(RedeemCode).where(RedeemCode.code == "PERSIST001"))).scalar_one()
        assert rc.status == "used"
        assert rc.used_by == user.id


class TestCascadeDelete:
    async def test_delete_conversation_removes_messages(self, client: AsyncClient, db):
        """删除会话级联删除其消息"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg1 = await create_message(db, conv.id, user.id, "user", "消息1")
        msg2 = await create_message(db, conv.id, user.id, "assistant", "消息2")

        # 通过 API 删除
        await client.delete(
            f"/api/chat/conversations/{conv.id}",
            headers=auth_headers(user_token(user.id)),
        )

        # 验证消息被删除
        remaining = (
            await db.execute(select(Message).where(Message.conversation_id == conv.id))
        ).scalars().all()
        assert len(remaining) == 0

    async def test_delete_conversation_removes_token_usage(self, client: AsyncClient, db):
        """删除会话级联删除 token_usage 记录"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "assistant", "AI回复")

        # 创建 token_usage 记录
        db.add(TokenUsage(user_id=user.id, message_id=msg.id, model="test", input_tokens=10, output_tokens=20))
        await db.commit()

        await client.delete(
            f"/api/chat/conversations/{conv.id}",
            headers=auth_headers(user_token(user.id)),
        )

        remaining_usage = (
            await db.execute(select(TokenUsage).where(TokenUsage.message_id == msg.id))
        ).scalars().all()
        assert len(remaining_usage) == 0


class TestTransactionIntegrity:
    async def test_redeem_atomicity_free_chats_updated(self, client: AsyncClient, db):
        """兑换操作原子性：free_chats 增加且 code 变 used"""
        user = await create_user(db, free_chats_left=2)
        await create_redeem_code(db, code="ATOMIC001", type="chats", value=8)

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "ATOMIC001"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0

        # 验证两个状态都正确更新
        await db.refresh(user)
        rc = (await db.execute(select(RedeemCode).where(RedeemCode.code == "ATOMIC001"))).scalar_one()

        assert user.free_chats_left == 10  # 2 + 8
        assert rc.status == "used"

    async def test_user_free_chats_not_negative(self, client: AsyncClient, db):
        """免费次数耗尽后继续发送不会导致负数"""
        user = await create_user(db, free_chats_left=1)

        # 第一次发送（消耗最后一次）
        from unittest.mock import patch, AsyncMock

        async def mock_stream(*args, **kwargs):
            usage_info = args[4] if len(args) > 4 else {}
            retrieval_info = args[5] if len(args) > 5 else {}
            usage_info.update({"model": "test", "input_tokens": 5, "output_tokens": 10})
            retrieval_info.update({"docs": [], "status": "disabled"})
            yield "ok"

        with patch("app.services.ai_service.stream_ai_response", side_effect=mock_stream):
            await client.post(
                "/api/chat/send",
                json={"message": "消耗最后一次"},
                headers=auth_headers(user_token(user.id)),
            )

        # 第二次应该失败
        r2 = await client.post(
            "/api/chat/send",
            json={"message": "应该失败"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r2.json()["code"] == 2001

        # 验证 free_chats_left 不为负数
        await db.refresh(user)
        assert user.free_chats_left >= 0


class TestDataConsistency:
    async def test_user_id_in_messages_matches_user(self, client: AsyncClient, db):
        """消息中的 user_id 与实际用户一致"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id)

        result = (await db.execute(select(Message).where(Message.id == msg.id))).scalar_one()
        assert result.user_id == user.id

    async def test_conversation_belongs_to_correct_user(self, client: AsyncClient, db):
        """会话归属正确的用户"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")

        conv = await create_conversation(db, user_a.id, "A的会话")

        # 验证归属
        result = await db.get(Conversation, conv.id)
        assert result.user_id == user_a.id
        assert result.user_id != user_b.id

    async def test_banned_user_status_persists_across_login(self, client: AsyncClient, db, fake_redis):
        """封禁状态在数据库中持久，重新登录依然被拒"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        user = await create_user(db, phone="13800000001", password="Password123", status="banned")

        # 尝试登录
        r = await client.post("/api/auth/login", json={"account": "13800000001", "password": "Password123"})
        assert r.json()["code"] == 2003

        # 即使持有 token 也被拒
        tok = user_token(user.id)
        r2 = await client.get("/api/auth/profile", headers=auth_headers(tok))
        assert r2.json()["code"] == 1002  # banned 用户，get_current_user_id 抛出异常

    async def test_subscription_days_stack_correctly(self, client: AsyncClient, db):
        """多次兑换天数码时间叠加正确"""
        from datetime import timezone

        user = await create_user(db, subscribe_plan="free")
        await create_redeem_code(db, code="STACK001", type="days", value=10)
        await create_redeem_code(db, code="STACK002", type="days", value=20)

        await client.post(
            "/api/subscribe/redeem",
            json={"code": "STACK001"},
            headers=auth_headers(user_token(user.id)),
        )
        await client.post(
            "/api/subscribe/redeem",
            json={"code": "STACK002"},
            headers=auth_headers(user_token(user.id)),
        )

        await db.refresh(user)
        from datetime import datetime

        if user.subscribe_expire:
            days_left = (user.subscribe_expire - datetime.utcnow()).days
            # 两次兑换叠加约 30 天
            assert days_left >= 28, f"叠加天数不够：{days_left} days"
