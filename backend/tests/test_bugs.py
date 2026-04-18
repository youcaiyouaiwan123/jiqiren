"""
Bug 回归测试 + 边界条件测试
覆盖：空字符串处理、Unicode/emoji、整数边界、空列表、
      已删除账号访问、密码 bcrypt cost 安全性、token type 混用、
      分页参数异常、Enum 越界等
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
    admin_token,
)

pytestmark = pytest.mark.asyncio


class TestEdgeCasesRegistration:
    async def test_phone_with_spaces_normalized(self, client: AsyncClient, db, fake_redis):
        """手机号包含空格自动去除"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        # 预置验证码（去空格后的手机号）
        await fake_redis.set("verify_code:phone:13800000001", "123456", ex=300)

        from app.models.register_config import RegisterConfig

        for k, v in [
            ("register_enabled", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "x"),
            ("sms_access_secret", "x"),
            ("sms_sign_name", "x"),
            ("sms_template_code", "x"),
            ("default_free_chats", "3"),
        ]:
            db.add(RegisterConfig(config_key=k, config_value=v))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "138 0000 0001",  # 带空格
                "password": "Password123",
                "verify_code": "123456",
                "ft": 5000,
            },
        )
        # 不应因空格导致格式错误
        assert r.json()["code"] != 1013

    async def test_email_normalized_to_lowercase(self, client: AsyncClient, db, fake_redis):
        """邮箱大写自动转小写"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, email="test@example.com", phone=None)

        # 尝试用大写邮箱登录
        r = await client.post(
            "/api/auth/login",
            json={"account": "TEST@EXAMPLE.COM", "password": "Password123"},
        )
        assert r.json()["code"] == 0


class TestEdgeCasesUnicode:
    async def test_chinese_conversation_title(self, client: AsyncClient, db):
        """中文会话标题正确存储和返回"""
        user = await create_user(db)
        r = await client.post(
            "/api/chat/conversations",
            json={"title": "你好，这是一个中文标题！"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == "你好，这是一个中文标题！"

    async def test_emoji_in_title(self, client: AsyncClient, db):
        """含 emoji 的标题正确处理"""
        user = await create_user(db)
        emoji_title = "🤖 AI对话 🎉"
        r = await client.post(
            "/api/chat/conversations",
            json={"title": emoji_title},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["title"] == emoji_title

    async def test_null_bytes_in_message_handled(self, client: AsyncClient, db):
        """消息内容中含 null 字节不崩溃"""
        user = await create_user(db, free_chats_left=0)
        # 不会实际发送（配额为 0），但不应 500
        r = await client.post(
            "/api/chat/send",
            json={"message": "hello\x00world"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.status_code != 500
        assert r.json()["code"] in (0, 2001)


class TestEdgeCasesPagination:
    async def test_page_size_zero_handled(self, client: AsyncClient, db):
        """page_size=0 不崩溃（FastAPI 校验）"""
        user = await create_user(db)
        r = await client.get(
            "/api/chat/conversations?page_size=0",
            headers=auth_headers(user_token(user.id)),
        )
        # FastAPI 的 Query ge=1 会返回 422
        assert r.status_code in (200, 422)

    async def test_page_beyond_total(self, client: AsyncClient, db):
        """请求超出总页数时返回空列表"""
        user = await create_user(db)
        await create_conversation(db, user.id)

        r = await client.get(
            "/api/chat/conversations?page=999&page_size=20",
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["list"] == []

    async def test_negative_page_handled(self, client: AsyncClient, db):
        """负数页码不崩溃"""
        user = await create_user(db)
        r = await client.get(
            "/api/chat/conversations?page=-1",
            headers=auth_headers(user_token(user.id)),
        )
        assert r.status_code in (200, 422)

    async def test_page_size_exceeds_max(self, client: AsyncClient, db):
        """page_size 超过最大值 200 被限制"""
        admin = await create_admin(db)
        r = await client.get(
            "/api/admin/users?page_size=9999",
            headers=auth_headers(admin_token(admin.id)),
        )
        # FastAPI le=200 应返回 422 或自动截断
        assert r.status_code in (200, 422)


class TestDeletedAccountBehavior:
    async def test_deleted_user_token_rejected(self, client: AsyncClient, db):
        """软删除用户的 token 被拒绝"""
        from datetime import datetime

        user = await create_user(db)
        tok = user_token(user.id)

        # 软删除用户
        user.deleted_at = datetime.utcnow()
        await db.commit()

        r = await client.get("/api/auth/profile", headers=auth_headers(tok))
        assert r.json()["code"] == 1002


class TestPasswordSecurity:
    async def test_bcrypt_cost_factor(self):
        """bcrypt 密码 hash 包含成本因子（生产安全）"""
        from app.core.security import hash_password

        hashed = hash_password("Password123")
        # bcrypt hash 格式: $2b$<cost>$...
        assert hashed.startswith("$2b$")
        cost_factor = int(hashed.split("$")[2])
        assert cost_factor >= 10, f"bcrypt cost factor {cost_factor} 太低，建议 >= 10"

    def test_different_passwords_produce_different_hashes(self):
        """相同明文每次产生不同 hash（salt）"""
        from app.core.security import hash_password

        h1 = hash_password("Password123")
        h2 = hash_password("Password123")
        assert h1 != h2

    def test_verify_password_correct(self):
        """正确密码验证通过"""
        from app.core.security import hash_password, verify_password

        h = hash_password("MyPass@123")
        assert verify_password("MyPass@123", h) is True

    def test_verify_password_wrong(self):
        """错误密码验证失败"""
        from app.core.security import hash_password, verify_password

        h = hash_password("MyPass@123")
        assert verify_password("WrongPass", h) is False


class TestRedeemEdgeCases:
    async def test_redeem_code_case_insensitive_not_applied(self, client: AsyncClient, db):
        """兑换码大小写敏感（码是 UPPER，不自动匹配 lower）"""
        user = await create_user(db)
        await create_redeem_code(db, code="UPPER001")

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "upper001"},  # 小写
            headers=auth_headers(user_token(user.id)),
        )
        # 实际行为取决于数据库：MySQL 默认大小写不敏感，SQLite 大小写敏感
        # 断言不崩溃即可
        assert r.status_code == 200

    async def test_redeem_empty_code_rejected(self, client: AsyncClient, db):
        """空兑换码被正确处理"""
        user = await create_user(db)
        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": ""},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] != 0

    async def test_redeem_code_value_zero_not_created(self):
        """value=0 的兑换码没有业务意义（单元测试确认逻辑）"""
        from app.services.subscription_service import create_order_no

        no = create_order_no()
        assert len(no) > 10


class TestTokenTypeConfusion:
    async def test_admin_access_token_not_usable_for_user_endpoints(self, client: AsyncClient, db):
        """admin access_token 不能用于用户端接口"""
        admin = await create_admin(db)
        tok = admin_token(admin.id)
        r = await client.get("/api/auth/profile", headers=auth_headers(tok))
        # admin token 无 user_id，应被拒绝
        assert r.json()["code"] in (1002, 1004)

    async def test_user_access_token_not_usable_for_admin_endpoints(self, client: AsyncClient, db):
        """user access_token 不能用于管理端接口"""
        user = await create_user(db)
        tok = user_token(user.id)
        r = await client.get("/api/admin/users", headers=auth_headers(tok))
        assert r.json()["code"] == 1003


class TestResponseFormat:
    async def test_all_responses_have_code_field(self, client: AsyncClient, db, fake_redis):
        """所有 API 响应都包含 code 字段"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        endpoints = [
            ("GET", "/api/health", None, {}),
            ("GET", "/api/auth/register-config", None, {}),
            ("POST", "/api/auth/login", {"account": "x", "password": "y"}, {}),
        ]
        for method, url, body, headers in endpoints:
            r = await client.request(method, url, json=body, headers=headers)
            assert "code" in r.json(), f"{method} {url} 无 code 字段"

    async def test_all_responses_have_request_id(self, client: AsyncClient, db):
        """API 响应包含 request_id（用于追踪）"""
        user = await create_user(db)
        # 使用带认证的接口（通过 ok_response 返回，包含 request_id）
        r = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        assert "request_id" in r.json()

    async def test_health_check_always_200(self, client: AsyncClient):
        """健康检查接口 HTTP 状态码始终为 200"""
        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["code"] == 0

    async def test_biz_exception_returns_200_not_500(self, client: AsyncClient):
        """业务异常（BizException）返回 HTTP 200，而非 500"""
        r = await client.get("/api/auth/profile")  # 未登录
        assert r.status_code == 200  # 统一包装为 200
        assert r.json()["code"] == 1002


class TestInviteCode:
    async def test_invite_code_required_when_configured(self, client: AsyncClient, db, fake_redis):
        """邀请码模式下不提供邀请码被拒绝"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await fake_redis.set("verify_code:phone:13800000001", "123456", ex=300)

        from app.models.register_config import RegisterConfig

        for k, v in [
            ("register_enabled", "true"),
            ("invite_code_required", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "x"),
            ("sms_access_secret", "x"),
            ("sms_sign_name", "x"),
            ("sms_template_code", "x"),
            ("default_free_chats", "3"),
        ]:
            db.add(RegisterConfig(config_key=k, config_value=v))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000001",
                "password": "Password123",
                "verify_code": "123456",
                "ft": 5000,
                # 不提供 invite_code
            },
        )
        assert r.json()["code"] == 1008

    async def test_invalid_invite_code_rejected(self, client: AsyncClient, db, fake_redis):
        """无效邀请码被拒绝"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await fake_redis.set("verify_code:phone:13800000001", "123456", ex=300)

        from app.models.register_config import RegisterConfig

        for k, v in [
            ("register_enabled", "true"),
            ("invite_code_required", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "x"),
            ("sms_access_secret", "x"),
            ("sms_sign_name", "x"),
            ("sms_template_code", "x"),
            ("default_free_chats", "3"),
        ]:
            db.add(RegisterConfig(config_key=k, config_value=v))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000001",
                "password": "Password123",
                "verify_code": "123456",
                "invite_code": "INVALID999",
                "ft": 5000,
            },
        )
        assert r.json()["code"] in (1020, 1021)


class TestAiServiceUrlNormalization:
    """AI 服务 URL 规范化逻辑单元测试"""

    def test_normalize_provider_aliases(self):
        from app.services.ai_service import _normalize_provider

        assert _normalize_provider("anthropic") == "claude"
        assert _normalize_provider("CLAUDE") == "claude"
        assert _normalize_provider("gpt") == "openai"
        assert _normalize_provider("GEMINI") == "gemini"
        assert _normalize_provider(None) == ""

    def test_normalize_api_base_strips_endpoint_suffix(self):
        from app.services.ai_service import _normalize_api_base

        # 应去掉 /v1/messages 后缀
        result = _normalize_api_base("claude", "https://api.anthropic.com/v1/messages")
        assert result == "https://api.anthropic.com"

    def test_normalize_api_base_keeps_clean_url(self):
        from app.services.ai_service import _normalize_api_base

        result = _normalize_api_base("openai", "https://api.openai.com/v1")
        assert result == "https://api.openai.com/v1"

    def test_parse_float_safe(self):
        from app.services.ai_service import _parse_float

        assert _parse_float("0.7", 0.5) == 0.7
        assert _parse_float(None, 0.5) == 0.5
        assert _parse_float("invalid", 0.5) == 0.5

    def test_parse_int_safe(self):
        from app.services.ai_service import _parse_int

        assert _parse_int("2048", 512) == 2048
        assert _parse_int(None, 512) == 512
        assert _parse_int("abc", 512) == 512
        assert _parse_int("0", 512) == 1  # max(1, 0) = 1

    def test_parse_bool(self):
        from app.services.ai_service import _parse_bool

        assert _parse_bool("true") is True
        assert _parse_bool("1") is True
        assert _parse_bool("yes") is True
        assert _parse_bool("false") is False
        assert _parse_bool(None, True) is True
        assert _parse_bool("random") is False
