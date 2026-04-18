"""
认证模块测试
覆盖：注册、登录、token 刷新、profile 获取/更新、改密、重置密码
"""
import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, create_user, user_token

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_requires_phone_or_email(self, client: AsyncClient, db, fake_redis):
        """注册时 phone 和 email 至少填一个"""
        from app.models.register_config import RegisterConfig

        db.add(RegisterConfig(config_key="register_enabled", config_value="true"))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={"password": "Password123", "verify_code": "123456"},
        )
        assert r.json()["code"] == 1001

    async def test_register_cannot_provide_both_phone_and_email(self, client: AsyncClient, db):
        """不能同时提交 phone 和 email"""
        from app.models.register_config import RegisterConfig

        db.add(RegisterConfig(config_key="register_enabled", config_value="true"))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={
                "phone": "13800000001",
                "email": "x@x.com",
                "password": "Password123",
                "verify_code": "123456",
            },
        )
        assert r.json()["code"] == 1018

    async def test_register_invalid_phone_format(self, client: AsyncClient, db, fake_redis):
        """无效手机号格式被拒绝"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        from app.models.register_config import RegisterConfig

        for k, v in [
            ("register_enabled", "true"),
            ("sms_enabled", "true"),
            ("sms_provider", "aliyun"),
            ("sms_access_key", "x"),
            ("sms_access_secret", "x"),
            ("sms_sign_name", "x"),
            ("sms_template_code", "x"),
        ]:
            db.add(RegisterConfig(config_key=k, config_value=v))
        await db.commit()

        for bad_phone in ["123", "abc", "138000000001", "03800000001"]:
            r = await client.post(
                "/api/auth/register",
                json={"phone": bad_phone, "password": "Password123", "verify_code": "123456", "ft": 5000},
            )
            assert r.json()["code"] in (1013, 1007, 1017), f"bad_phone={bad_phone}"

    async def test_register_password_min_length(self, client: AsyncClient, db, fake_redis):
        """密码不能少于 6 位"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        from app.models.register_config import RegisterConfig

        db.add(RegisterConfig(config_key="register_enabled", config_value="true"))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={"phone": "13800000001", "password": "123", "verify_code": "123456", "ft": 5000},
        )
        assert r.json()["code"] == 1019

    async def test_register_disabled(self, client: AsyncClient, db, fake_redis):
        """注册关闭时返回 1006"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        from app.models.register_config import RegisterConfig

        db.add(RegisterConfig(config_key="register_enabled", config_value="false"))
        await db.commit()

        r = await client.post(
            "/api/auth/register",
            json={"phone": "13800000001", "password": "Password123", "verify_code": "123456", "ft": 5000},
        )
        assert r.json()["code"] == 1006

    async def test_register_duplicate_phone(self, client: AsyncClient, db, fake_redis):
        """重复手机号注册返回 1005"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone="13800000001")
        await fake_redis.set("verify_code:phone:13800000001", "654321", ex=300)

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
            json={"phone": "13800000001", "password": "Password123", "verify_code": "654321", "ft": 5000},
        )
        assert r.json()["code"] == 1005

    async def test_register_wrong_verify_code(self, client: AsyncClient, db, fake_redis):
        """错误验证码返回 1011"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await fake_redis.set("verify_code:phone:13800000001", "654321", ex=300)

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
            json={"phone": "13800000001", "password": "Password123", "verify_code": "000000", "ft": 5000},
        )
        assert r.json()["code"] == 1011

    async def test_register_verify_code_consumed_after_use(self, client: AsyncClient, db, fake_redis):
        """验证码使用一次后自动失效（防重放）"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await fake_redis.set("verify_code:phone:13900000001", "111222", ex=300)

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

        # 第一次使用
        r1 = await client.post(
            "/api/auth/register",
            json={"phone": "13900000001", "password": "Password123", "verify_code": "111222", "ft": 5000},
        )
        assert r1.json()["code"] == 0

        # 第二次相同验证码应失效
        r2 = await client.post(
            "/api/auth/register",
            json={"phone": "13900000001", "password": "Password123", "verify_code": "111222", "ft": 5000},
        )
        # 要么验证码失效 1011，要么账号已注册 1005
        assert r2.json()["code"] in (1005, 1011)


class TestLogin:
    async def test_login_success(self, client: AsyncClient, db, fake_redis):
        """正确账密登录返回 tokens"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone="13800000001", password="Password123")

        r = await client.post("/api/auth/login", json={"account": "13800000001", "password": "Password123"})
        data = r.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    async def test_login_wrong_password(self, client: AsyncClient, db, fake_redis):
        """错误密码返回 1001"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone="13800000001", password="Password123")

        r = await client.post("/api/auth/login", json={"account": "13800000001", "password": "wrong"})
        assert r.json()["code"] == 1001

    async def test_login_nonexistent_account(self, client: AsyncClient, db, fake_redis):
        """账号不存在返回 1004"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        r = await client.post("/api/auth/login", json={"account": "13899999999", "password": "Password123"})
        assert r.json()["code"] == 1004

    async def test_login_banned_user_rejected(self, client: AsyncClient, db, fake_redis):
        """封禁用户登录返回 2003"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone="13800000001", password="Password123", status="banned")

        r = await client.post("/api/auth/login", json={"account": "13800000001", "password": "Password123"})
        assert r.json()["code"] == 2003

    async def test_login_by_email(self, client: AsyncClient, db, fake_redis):
        """使用邮箱登录"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone=None, email="test@example.com", password="Password123")

        r = await client.post("/api/auth/login", json={"account": "test@example.com", "password": "Password123"})
        assert r.json()["code"] == 0

    async def test_login_response_contains_masked_user_info(self, client: AsyncClient, db, fake_redis):
        """登录响应中的用户信息已脱敏"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_user(db, phone="13812345678", password="Password123")

        r = await client.post("/api/auth/login", json={"account": "13812345678", "password": "Password123"})
        user_data = r.json()["data"]["user"]
        assert "****" in user_data["phone"]
        assert "password" not in user_data


class TestTokenRefresh:
    async def test_refresh_token_generates_new_access_token(self, client: AsyncClient, db):
        """有效 refresh_token 返回新 access_token"""
        from app.core.security import create_refresh_token

        user = await create_user(db)
        rtok = create_refresh_token({"user_id": user.id, "role": "user"})
        r = await client.post("/api/auth/refresh", json={"refresh_token": rtok})
        assert r.json()["code"] == 0
        assert "access_token" in r.json()["data"]

    async def test_invalid_refresh_token_rejected(self, client: AsyncClient):
        """无效 refresh_token 被拒绝"""
        r = await client.post("/api/auth/refresh", json={"refresh_token": "invalid.token.here"})
        assert r.json()["code"] == 1002

    async def test_access_token_cannot_be_used_as_refresh(self, client: AsyncClient, db):
        """access_token 不能作为 refresh_token 使用"""
        user = await create_user(db)
        atk = user_token(user.id)
        r = await client.post("/api/auth/refresh", json={"refresh_token": atk})
        assert r.json()["code"] == 1002


class TestProfile:
    async def test_get_profile_returns_user_info(self, client: AsyncClient, db):
        """获取个人信息成功"""
        user = await create_user(db, nickname="张三")
        r = await client.get("/api/auth/profile", headers=auth_headers(user_token(user.id)))
        assert r.json()["code"] == 0
        assert r.json()["data"]["nickname"] == "张三"

    async def test_update_nickname(self, client: AsyncClient, db):
        """更新昵称成功"""
        user = await create_user(db)
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": "新昵称"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["nickname"] == "新昵称"

    async def test_update_empty_nickname_rejected(self, client: AsyncClient, db):
        """空昵称被拒绝"""
        user = await create_user(db)
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": "   "},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1001

    async def test_update_too_long_nickname_rejected(self, client: AsyncClient, db):
        """超过 50 字的昵称被拒绝"""
        user = await create_user(db)
        r = await client.put(
            "/api/auth/profile",
            json={"nickname": "X" * 51},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1001


class TestChangePassword:
    async def test_change_password_success(self, client: AsyncClient, db, fake_redis):
        """修改密码成功"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        user = await create_user(db, password="OldPass123")
        r = await client.post(
            "/api/auth/change-password",
            json={"old_password": "OldPass123", "new_password": "NewPass@456A"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0

    async def test_change_password_wrong_old_password(self, client: AsyncClient, db):
        """旧密码错误被拒绝"""
        user = await create_user(db, password="OldPass123")
        r = await client.post(
            "/api/auth/change-password",
            json={"old_password": "WrongOld", "new_password": "NewPass@456A"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1001

    async def test_change_password_same_as_old_rejected(self, client: AsyncClient, db):
        """新密码不能与旧密码相同"""
        user = await create_user(db, password="OldPass123")
        r = await client.post(
            "/api/auth/change-password",
            json={"old_password": "OldPass123", "new_password": "OldPass123"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1032

    async def test_change_password_complexity_enforced(self, client: AsyncClient, db):
        """新密码必须满足复杂度要求（至少含大小写字母+数字）"""
        user = await create_user(db, password="OldPass123")
        r = await client.post(
            "/api/auth/change-password",
            json={"old_password": "OldPass123", "new_password": "alllower"},
            headers=auth_headers(user_token(user.id)),
        )
        # 不满足复杂度
        assert r.json()["code"] != 0


class TestRegisterConfig:
    async def test_get_register_config_public_only(self, client: AsyncClient, db):
        """注册配置接口只返回公开字段，不含 SMTP 密码等敏感字段"""
        from app.models.register_config import RegisterConfig

        db.add(RegisterConfig(config_key="register_enabled", config_value="true"))
        db.add(RegisterConfig(config_key="smtp_password", config_value="super_secret"))
        await db.commit()

        r = await client.get("/api/auth/register-config")
        text = r.text
        assert "super_secret" not in text
        assert "smtp_password" not in text
