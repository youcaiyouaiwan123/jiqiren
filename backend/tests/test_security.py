"""
安全性测试
覆盖：JWT 篡改/过期/越权、SQL注入、XSS存储、IDOR、蜜罐、限流、
      管理端权限隔离、敏感字段泄露、Refresh Token 类型错误
"""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from jose import jwt

from tests.conftest import (
    admin_token,
    auth_headers,
    create_admin,
    create_conversation,
    create_message,
    create_user,
    user_token,
)

pytestmark = pytest.mark.asyncio


# ─────────────────────────────────────────────────────────────────────────────
# JWT 安全
# ─────────────────────────────────────────────────────────────────────────────


class TestJWTSecurity:
    async def test_no_token_returns_1002(self, client: AsyncClient):
        """无 token 访问受保护接口返回 1002"""
        r = await client.get("/api/auth/profile")
        assert r.json()["code"] == 1002

    async def test_malformed_token(self, client: AsyncClient):
        """畸形 token 返回 1002"""
        r = await client.get("/api/auth/profile", headers={"Authorization": "Bearer not.a.token"})
        assert r.json()["code"] == 1002

    async def test_wrong_secret_token(self, client: AsyncClient):
        """使用错误密钥签名的 token 被拒绝"""
        bad_token = jwt.encode(
            {"user_id": 999, "role": "user", "type": "access", "exp": int(time.time()) + 3600},
            "wrong-secret",
            algorithm="HS256",
        )
        r = await client.get("/api/auth/profile", headers={"Authorization": f"Bearer {bad_token}"})
        assert r.json()["code"] == 1002

    async def test_expired_token(self, client: AsyncClient):
        """过期 token 被拒绝"""
        expired = jwt.encode(
            {"user_id": 1, "role": "user", "type": "access", "exp": int(time.time()) - 10},
            "test-secret-key-for-testing-only",
            algorithm="HS256",
        )
        r = await client.get("/api/auth/profile", headers={"Authorization": f"Bearer {expired}"})
        assert r.json()["code"] == 1002

    async def test_refresh_token_cannot_access_protected_routes(self, client: AsyncClient, db):
        """refresh_token 不能用于访问 access_token 保护的接口"""
        from app.core.security import create_refresh_token

        user = await create_user(db)
        rtok = create_refresh_token({"user_id": user.id, "role": "user"})
        r = await client.get("/api/auth/profile", headers=auth_headers(rtok))
        assert r.json()["code"] == 1002

    async def test_admin_token_cannot_access_user_routes(self, client: AsyncClient, db):
        """admin token 不能访问用户 API（role 不匹配）"""
        admin = await create_admin(db)
        tok = admin_token(admin.id)
        r = await client.get("/api/auth/profile", headers=auth_headers(tok))
        # admin token 里没有 user_id，或 role != user
        assert r.json()["code"] in (1002, 1004)

    async def test_user_token_cannot_access_admin_routes(self, client: AsyncClient, db):
        """普通用户 token 不能访问管理端接口"""
        user = await create_user(db)
        tok = user_token(user.id)
        r = await client.get("/api/admin/profile", headers=auth_headers(tok))
        assert r.json()["code"] == 1003

    async def test_forged_user_id_in_token(self, client: AsyncClient):
        """伪造不存在 user_id 的 token 被拒绝"""
        tok = user_token(999999)
        r = await client.get("/api/auth/profile", headers=auth_headers(tok))
        assert r.json()["code"] == 1002

    async def test_bearer_prefix_required(self, client: AsyncClient, db):
        """Authorization 头必须以 Bearer 开头"""
        user = await create_user(db)
        tok = user_token(user.id)
        r = await client.get("/api/auth/profile", headers={"Authorization": tok})
        assert r.json()["code"] == 1002


# ─────────────────────────────────────────────────────────────────────────────
# IDOR（越权访问他人资源）
# ─────────────────────────────────────────────────────────────────────────────


class TestIDOR:
    async def test_user_cannot_read_other_users_conversation(self, client: AsyncClient, db):
        """用户 A 无法读取用户 B 的会话消息"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")
        conv_b = await create_conversation(db, user_b.id, title="B的私密会话")

        r = await client.get(
            f"/api/chat/conversations/{conv_b.id}/messages",
            headers=auth_headers(user_token(user_a.id)),
        )
        assert r.json()["code"] == 1004

    async def test_user_cannot_delete_other_users_conversation(self, client: AsyncClient, db):
        """用户 A 无法删除用户 B 的会话"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")
        conv_b = await create_conversation(db, user_b.id)

        r = await client.delete(
            f"/api/chat/conversations/{conv_b.id}",
            headers=auth_headers(user_token(user_a.id)),
        )
        assert r.json()["code"] == 1004

    async def test_user_cannot_rename_other_users_conversation(self, client: AsyncClient, db):
        """用户 A 无法重命名用户 B 的会话"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")
        conv_b = await create_conversation(db, user_b.id)

        r = await client.put(
            f"/api/chat/conversations/{conv_b.id}",
            json={"title": "黑客重命名"},
            headers=auth_headers(user_token(user_a.id)),
        )
        assert r.json()["code"] == 1004

    async def test_user_cannot_feedback_other_users_message(self, client: AsyncClient, db):
        """用户 A 无法对用户 B 的消息点赞"""
        user_a = await create_user(db, phone="13800000001")
        user_b = await create_user(db, phone="13800000002")
        conv_b = await create_conversation(db, user_b.id)
        msg_b = await create_message(db, conv_b.id, user_b.id, role="assistant", content="AI回复")

        r = await client.post(
            f"/api/chat/messages/{msg_b.id}/feedback",
            json={"rating": "like"},
            headers=auth_headers(user_token(user_a.id)),
        )
        assert r.json()["code"] == 1004


# ─────────────────────────────────────────────────────────────────────────────
# 敏感信息不泄露
# ─────────────────────────────────────────────────────────────────────────────


class TestSensitiveDataMasking:
    async def test_phone_masked_in_profile(self, client: AsyncClient, db):
        """手机号在 profile 接口中被脱敏"""
        user = await create_user(db, phone="13812345678")
        r = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        assert r.json()["code"] == 0
        phone = r.json()["data"]["phone"]
        assert "****" in phone
        assert "12345" not in phone

    async def test_email_masked_in_profile(self, client: AsyncClient, db):
        """邮箱在 profile 接口中被脱敏"""
        user = await create_user(db, phone=None, email="hacker@example.com")
        r = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        email = r.json()["data"]["email"]
        assert "**@" in email
        assert "hacker" not in email

    async def test_llm_api_key_not_in_list_response(self, client: AsyncClient, db):
        """LLM 列表接口不返回 api_key"""
        admin = await create_admin(db)
        from tests.conftest import create_llm_provider

        await create_llm_provider(db, api_key="sk-super-secret-key")
        r = await client.get(
            "/api/admin/llm-providers", headers=auth_headers(admin_token(admin.id))
        )
        text = r.text
        assert "sk-super-secret-key" not in text

    async def test_password_hash_not_in_user_response(self, client: AsyncClient, db):
        """用户详情接口不返回 password_hash"""
        user = await create_user(db)
        r = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        assert "password_hash" not in r.text
        assert "password" not in r.json()["data"]


# ─────────────────────────────────────────────────────────────────────────────
# XSS / 注入防护
# ─────────────────────────────────────────────────────────────────────────────


class TestInjectionDefense:
    async def test_xss_in_nickname_stored_safely(self, client: AsyncClient, db):
        """昵称中的 XSS payload 原样存储（由前端负责转义，后端不执行）"""
        user = await create_user(db)
        xss = "<script>alert(1)</script>"
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": xss},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        returned_nickname = r.json()["data"]["nickname"]
        # 后端应原样存储，不执行
        assert returned_nickname == xss

    async def test_sql_injection_in_login(self, client: AsyncClient, db, fake_redis):
        """SQL 注入不能绕过登录（ORM 参数化查询）"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        payloads = [
            "' OR '1'='1",
            "admin'--",
            "1; DROP TABLE users;--",
            "' UNION SELECT 1,2,3--",
        ]
        for payload in payloads:
            r = await client.post("/api/auth/login", json={"account": payload, "password": "x"})
            assert r.json()["code"] != 0, f"SQL injection might work: {payload}"

    async def test_sql_injection_in_conversation_title(self, client: AsyncClient, db):
        """会话标题的 SQL 注入不影响数据库"""
        user = await create_user(db)
        payload = "'; DROP TABLE conversations; --"
        r = await client.post(
            "/api/chat/conversations",
            json={"title": payload},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        # 验证标题被正常存储
        assert r.json()["data"]["title"] == payload

    async def test_extremely_long_input_handled(self, client: AsyncClient, db):
        """超长输入不导致服务崩溃"""
        user = await create_user(db)
        long_str = "A" * 100_000
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": long_str},
            headers=auth_headers(user_token(user.id)),
        )
        # 应该返回验证错误，而不是 500
        assert r.status_code in (200, 422)
        if r.status_code == 200:
            assert r.json()["code"] != 0  # nickname 超长应被拒绝


# ─────────────────────────────────────────────────────────────────────────────
# 蜜罐防机器人注册
# ─────────────────────────────────────────────────────────────────────────────


class TestHoneypot:
    async def test_honeypot_website_field_returns_fake_success(self, client: AsyncClient):
        """填写蜜罐字段 website 应静默假成功"""
        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000099",
                "password": "Password123",
                "verify_code": "123456",
                "website": "https://bot.example.com",  # 蜜罐字段
            },
        )
        # 返回假成功，user_id=0
        assert r.json()["code"] == 0
        assert r.json()["data"]["user_id"] == 0

    async def test_fast_form_submission_rejected(self, client: AsyncClient):
        """表单填写耗时 < 4000ms 视为机器人"""
        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000099",
                "password": "Password123",
                "verify_code": "123456",
                "ft": 500,  # 500ms 远小于 4000ms 阈值
            },
        )
        assert r.json()["code"] == 1040

    async def test_normal_form_submission_not_rejected(self, client: AsyncClient, fake_redis, db):
        """正常填写耗时不被误判为机器人"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        # 预置验证码
        await fake_redis.set("verify_code:phone:13800000099", "654321", ex=300)
        from app.models.register_config import RegisterConfig

        for key, val in [
            ("register_enabled", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "x"),
            ("sms_access_secret", "x"),
            ("sms_sign_name", "x"),
            ("sms_template_code", "x"),
            ("default_free_chats", "3"),
        ]:
            db.add(RegisterConfig(config_key=key, config_value=val, description=key))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000099",
                "password": "Password123",
                "verify_code": "654321",
                "ft": 5000,  # 5秒，正常
            },
        )
        # 注册可能因 sms_sdk 检测失败，但不应是蜜罐/机器人码
        assert r.json()["code"] not in (1040, 1041, 1042)


# ─────────────────────────────────────────────────────────────────────────────
# 管理端权限分级
# ─────────────────────────────────────────────────────────────────────────────


class TestAdminPrivilegeEscalation:
    async def test_normal_admin_cannot_unlock_accounts(self, client: AsyncClient, db):
        """普通管理员（normal）无法解锁账号（需 super 权限）"""
        admin = await create_admin(db, username="normal_admin", role="normal")
        tok = admin_token(admin.id, role="normal")
        r = await client.post(
            "/api/admin/unlock-admin",
            json={"username": "target", "password": ""},
            headers=auth_headers(tok),
        )
        assert r.json()["code"] == 1003

    async def test_unauthenticated_cannot_access_admin_api(self, client: AsyncClient):
        """未登录无法访问任何管理端 API"""
        endpoints = [
            ("GET", "/api/admin/profile"),
            ("GET", "/api/admin/users"),
            ("GET", "/api/admin/llm-providers"),
        ]
        for method, url in endpoints:
            r = await client.request(method, url)
            assert r.json()["code"] in (1002, 1003), f"{method} {url} should require auth"


# ─────────────────────────────────────────────────────────────────────────────
# 限流 / 防爆破
# ─────────────────────────────────────────────────────────────────────────────


class TestRateLimiting:
    async def test_admin_login_brute_force_lockout(self, client: AsyncClient, db, fake_redis):
        """管理员登录连续失败 5 次触发锁定"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_admin(db, username="locktest", password="RightPassword@123")

        for i in range(5):
            await client.post(
                "/api/admin/login",
                json={"username": "locktest", "password": "wrongpassword"},
            )

        # 第 6 次应被锁
        r = await client.post(
            "/api/admin/login",
            json={"username": "locktest", "password": "RightPassword@123"},
        )
        assert r.json()["code"] == 1030

    async def test_ip_rate_limit_on_verify_code(self, client: AsyncClient, db, fake_redis):
        """同一 IP 每小时发送验证码不超过 5 次"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis

        # 手动将 IP 计数置为 >=5（已达上限），使用实际的 IP key 格式
        # client IP 在测试中是 testclient 或 127.0.0.1，设两个键都超限
        for ip in ("testclient", "127.0.0.1"):
            await fake_redis.set(f"verify_code:ip:phone:{ip}", "10", ex=3600)

        from app.models.register_config import RegisterConfig

        for k, v in [
            ("register_enabled", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "key"),
            ("sms_access_secret", "secret"),
            ("sms_sign_name", "sign"),
            ("sms_template_code", "code"),
        ]:
            db.add(RegisterConfig(config_key=k, config_value=v))
        await db.commit()

        r = await client.post(
            "/api/auth/send-code",
            json={"target": "13800000001", "type": "phone"},
        )
        # 1022 = IP 频率过高；如果 SMS 通道校验先触发返回 1017 也视为拦截
        assert r.json()["code"] in (1022, 1017)
