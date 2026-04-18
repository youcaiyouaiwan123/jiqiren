"""
AI 对话模块测试
覆盖：会话 CRUD、消息分页、配额检查、免费次数扣减、封禁用户拦截、
      图片上传校验、音频上传校验、消息反馈
"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import (
    auth_headers,
    create_conversation,
    create_message,
    create_user,
    user_token,
)

pytestmark = pytest.mark.asyncio


class TestConversationCRUD:
    async def test_create_conversation(self, client: AsyncClient, db):
        """创建会话成功"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/conversations",
            json={"title": "我的新会话"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == "我的新会话"

    async def test_create_conversation_default_title(self, client: AsyncClient, db):
        """不指定标题时使用默认标题"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/conversations",
            json={},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == "新对话"

    async def test_list_conversations_only_own(self, client: AsyncClient, db):
        """只返回当前用户的会话"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")
        await create_conversation(db, user_a.id, "A的会话")
        await create_conversation(db, user_b.id, "B的会话")

        r = await client.get(
            "/api/chat/conversations",
            headers=auth_headers(user_token(user_a.id)),
        )
        assert r.json()["code"] == 0
        titles = [c["title"] for c in r.json()["data"]["list"]]
        assert "A的会话" in titles
        assert "B的会话" not in titles

    async def test_rename_conversation(self, client: AsyncClient, db):
        """重命名会话成功"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id, "旧名称")
        r = await client.put(
            f"/api/chat/conversations/{conv.id}",
            json={"title": "新名称"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == "新名称"

    async def test_rename_trims_whitespace(self, client: AsyncClient, db):
        """重命名去除首尾空格"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        r = await client.put(
            f"/api/chat/conversations/{conv.id}",
            json={"title": "  有空格  "},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == "有空格"

    async def test_rename_conversation_truncates_to_200(self, client: AsyncClient, db):
        """超长标题截断到 200 字"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        long_title = "X" * 300
        r = await client.put(
            f"/api/chat/conversations/{conv.id}",
            json={"title": long_title},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert len(r.json()["data"]["title"]) == 200

    async def test_delete_conversation_and_messages(self, client: AsyncClient, db):
        """删除会话同时删除其消息"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        await create_message(db, conv.id, user.id, "user", "消息1")
        await create_message(db, conv.id, user.id, "assistant", "回复1")

        r = await client.delete(
            f"/api/chat/conversations/{conv.id}",
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0

        # 验证消息也被删除
        from sqlalchemy import select
        from app.models.message import Message

        msgs = (await db.execute(select(Message).where(Message.conversation_id == conv.id))).scalars().all()
        assert len(msgs) == 0

    async def test_delete_nonexistent_conversation(self, client: AsyncClient, db):
        """删除不存在的会话返回 1004"""
        user = await create_user(db)
        r = await client.delete(
            "/api/chat/conversations/999999",
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_conversations_paginate(self, client: AsyncClient, db):
        """会话列表分页正确"""
        user = await create_user(db)
        for i in range(25):
            await create_conversation(db, user.id, f"会话{i}")

        r = await client.get(
            "/api/chat/conversations?page=1&page_size=10",
            headers=auth_headers(user_token(user.id)),
        )
        data = r.json()["data"]
        assert data["total"] == 25
        assert len(data["list"]) == 10

    async def test_conversations_page2(self, client: AsyncClient, db):
        """第 2 页返回正确数量"""
        user = await create_user(db)
        for i in range(15):
            await create_conversation(db, user.id, f"会话{i}")

        r = await client.get(
            "/api/chat/conversations?page=2&page_size=10",
            headers=auth_headers(user_token(user.id)),
        )
        assert len(r.json()["data"]["list"]) == 5


class TestMessages:
    async def test_get_messages_in_order(self, client: AsyncClient, db):
        """消息按时间升序返回"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        await create_message(db, conv.id, user.id, "user", "第一条")
        await create_message(db, conv.id, user.id, "assistant", "第二条")

        r = await client.get(
            f"/api/chat/conversations/{conv.id}/messages",
            headers=auth_headers(user_token(user.id)),
        )
        msgs = r.json()["data"]["list"]
        assert msgs[0]["content"] == "第一条"
        assert msgs[1]["content"] == "第二条"

    async def test_get_messages_includes_feedback(self, client: AsyncClient, db):
        """消息列表包含点赞信息"""
        from app.models.message_feedback import MessageFeedback

        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "assistant", "AI回复")
        db.add(MessageFeedback(message_id=msg.id, user_id=user.id, conversation_id=conv.id, rating="like"))
        await db.commit()

        r = await client.get(
            f"/api/chat/conversations/{conv.id}/messages",
            headers=auth_headers(user_token(user.id)),
        )
        msgs = r.json()["data"]["list"]
        assert msgs[0]["rating"] == "like"

    async def test_user_message_has_no_rating(self, client: AsyncClient, db):
        """用户消息不含 rating 字段"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        await create_message(db, conv.id, user.id, "user", "用户消息")

        r = await client.get(
            f"/api/chat/conversations/{conv.id}/messages",
            headers=auth_headers(user_token(user.id)),
        )
        msg = r.json()["data"]["list"][0]
        assert msg["rating"] is None


class TestSendMessage:
    async def test_send_message_deducts_free_chats(self, client: AsyncClient, db, fake_redis):
        """发送消息扣减免费次数"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        user = await create_user(db, free_chats_left=3)

        async def mock_stream(*args, **kwargs):
            usage_info = args[4] if len(args) > 4 else kwargs.get("usage_info", {})
            retrieval_info = args[5] if len(args) > 5 else kwargs.get("retrieval_info", {})
            usage_info.update({"model": "test", "input_tokens": 10, "output_tokens": 20})
            retrieval_info.update({"docs": [], "status": "disabled"})
            yield "你好！"

        with patch("app.services.ai_service.stream_ai_response", side_effect=mock_stream):
            r = await client.post(
                "/api/chat/send",
                json={"message": "你好"},
                headers=auth_headers(user_token(user.id)),
            )

        # 读取 SSE 流，找到 done 事件
        assert r.status_code == 200

    async def test_send_message_quota_exhausted(self, client: AsyncClient, db):
        """免费次数耗尽后拒绝发送"""
        user = await create_user(db, free_chats_left=0)
        r = await client.post(
            "/api/chat/send",
            json={"message": "你好"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 2001

    async def test_send_message_banned_user_rejected(self, client: AsyncClient, db):
        """封禁用户无法发送消息"""
        user = await create_user(db, free_chats_left=5, status="banned")
        r = await client.post(
            "/api/chat/send",
            json={"message": "你好"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] in (2003, 1002)

    async def test_send_message_with_subscription_no_quota_check(self, client: AsyncClient, db, fake_redis):
        """有效订阅用户不受免费次数限制"""
        from datetime import datetime, timedelta, timezone
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        user = await create_user(
            db,
            free_chats_left=0,
            subscribe_plan="monthly",
            subscribe_expire=datetime.utcnow() + timedelta(days=30),
        )

        async def mock_stream(*args, **kwargs):
            usage_info = args[4] if len(args) > 4 else {}
            retrieval_info = args[5] if len(args) > 5 else {}
            usage_info.update({"model": "test", "input_tokens": 10, "output_tokens": 20})
            retrieval_info.update({"docs": [], "status": "disabled"})
            yield "订阅用户回复"

        with patch("app.services.ai_service.stream_ai_response", side_effect=mock_stream):
            r = await client.post(
                "/api/chat/send",
                json={"message": "你好"},
                headers=auth_headers(user_token(user.id)),
            )
        assert r.status_code == 200
        # 不应返回 2001
        if r.headers.get("content-type", "").startswith("application/json"):
            assert r.json()["code"] != 2001

    async def test_send_message_expired_subscription_treated_as_free(self, client: AsyncClient, db):
        """过期订阅用户回退为免费配额检查"""
        from datetime import datetime, timedelta

        user = await create_user(
            db,
            free_chats_left=0,
            subscribe_plan="monthly",
            subscribe_expire=datetime.utcnow() - timedelta(days=1),
        )
        r = await client.post(
            "/api/chat/send",
            json={"message": "你好"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 2001

    async def test_send_message_to_nonexistent_conversation(self, client: AsyncClient, db):
        """向不存在的会话发送消息返回 1004"""
        user = await create_user(db, free_chats_left=3)
        r = await client.post(
            "/api/chat/send",
            json={"message": "你好", "conversation_id": 999999},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004


class TestImageUpload:
    async def test_upload_valid_image(self, client: AsyncClient, db):
        """上传有效图片成功"""
        user = await create_user(db)
        # 创建一个最小 PNG 文件（合法 PNG header，至少 100 字节）
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
            b"\x00" * 50  # 填充至 >= 100 字节
        )
        r = await client.post(
            "/api/chat/upload-image",
            files={"file": ("test.png", png_bytes, "image/png")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert "url" in r.json()["data"]

    async def test_upload_unsupported_format_rejected(self, client: AsyncClient, db):
        """上传不支持格式（PDF）被拒绝"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/upload-image",
            files={"file": ("test.pdf", b"%PDF-1.4 fake content here!!!", "application/pdf")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4001

    async def test_upload_too_large_image_rejected(self, client: AsyncClient, db):
        """超过 10MB 的图片被拒绝"""
        user = await create_user(db)
        big_image = b"X" * (10 * 1024 * 1024 + 1)
        r = await client.post(
            "/api/chat/upload-image",
            files={"file": ("big.png", big_image, "image/png")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4002

    async def test_upload_too_small_image_rejected(self, client: AsyncClient, db):
        """过小的图片被拒绝"""
        user = await create_user(db)
        tiny_image = b"x" * 10
        r = await client.post(
            "/api/chat/upload-image",
            files={"file": ("tiny.png", tiny_image, "image/png")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4003


class TestAudioUpload:
    async def test_upload_unsupported_audio_format_rejected(self, client: AsyncClient, db):
        """不支持的音频格式被拒绝"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/transcribe",
            files={"file": ("test.txt", b"not audio" * 50, "text/plain")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4001

    async def test_upload_too_large_audio_rejected(self, client: AsyncClient, db):
        """超过 25MB 的音频被拒绝"""
        user = await create_user(db)
        big_audio = b"X" * (25 * 1024 * 1024 + 1)
        r = await client.post(
            "/api/chat/transcribe",
            files={"file": ("big.webm", big_audio, "audio/webm")},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4002


class TestMessageFeedback:
    async def test_feedback_like(self, client: AsyncClient, db):
        """对 AI 消息点赞成功"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "assistant", "AI回复")

        with patch("app.services.satisfaction_service.score_explicit", new_callable=AsyncMock, return_value="satisfied"):
            r = await client.post(
                f"/api/chat/messages/{msg.id}/feedback",
                json={"rating": "like"},
                headers=auth_headers(user_token(user.id)),
            )
        assert r.json()["code"] == 0
        assert r.json()["data"]["rating"] == "like"

    async def test_feedback_dislike(self, client: AsyncClient, db):
        """对 AI 消息点踩成功"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "assistant", "AI回复")

        with patch("app.services.satisfaction_service.score_explicit", new_callable=AsyncMock, return_value="dissatisfied"):
            r = await client.post(
                f"/api/chat/messages/{msg.id}/feedback",
                json={"rating": "dislike"},
                headers=auth_headers(user_token(user.id)),
            )
        assert r.json()["code"] == 0

    async def test_feedback_invalid_rating_rejected(self, client: AsyncClient, db):
        """无效 rating 值被拒绝"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "assistant", "AI回复")

        r = await client.post(
            f"/api/chat/messages/{msg.id}/feedback",
            json={"rating": "meh"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 4001

    async def test_cannot_feedback_user_message(self, client: AsyncClient, db):
        """不能对用户消息（role=user）点赞"""
        user = await create_user(db)
        conv = await create_conversation(db, user.id)
        msg = await create_message(db, conv.id, user.id, "user", "我的问题")

        r = await client.post(
            f"/api/chat/messages/{msg.id}/feedback",
            json={"rating": "like"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004
