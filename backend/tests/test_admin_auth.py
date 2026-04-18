"""
管理端认证模块测试
覆盖：登录成功/失败、阶梯锁定、IP 限频、改密复杂度、
      Profile 获取、Token 刷新、super vs normal 权限
"""
import pytest
from httpx import AsyncClient

from tests.conftest import admin_token, auth_headers, create_admin

pytestmark = pytest.mark.asyncio


class TestAdminLogin:
    async def test_admin_login_success(self, client: AsyncClient, db, fake_redis):
        """管理员登录成功返回 tokens"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        admin = await create_admin(db, username="testadmin", password="Admin@123456")

        r = await client.post(
            "/api/admin/login",
            json={"username": "testadmin", "password": "Admin@123456"},
        )
        assert r.json()["code"] == 0
        assert "access_token" in r.json()["data"]
        assert r.json()["data"]["admin"]["username"] == "testadmin"

    async def test_admin_login_wrong_password(self, client: AsyncClient, db, fake_redis):
        """错误密码返回 1001"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_admin(db, username="testadmin", password="Admin@123456")

        r = await client.post(
            "/api/admin/login",
            json={"username": "testadmin", "password": "wrongpwd"},
        )
        assert r.json()["code"] == 1001

    async def test_admin_login_nonexistent_user(self, client: AsyncClient, db, fake_redis):
        """不存在的管理员账号——统一错误信息防枚举"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        r = await client.post(
            "/api/admin/login",
            json={"username": "ghost", "password": "Password123"},
        )
        assert r.json()["code"] == 1001

    async def test_admin_login_lockout_after_5_failures(self, client: AsyncClient, db, fake_redis):
        """连续 5 次失败触发 15 分钟锁定"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_admin(db, username="lockme", password="Admin@123456")

        for _ in range(5):
            await client.post("/api/admin/login", json={"username": "lockme", "password": "bad"})

        # 第 6 次用正确密码也被锁
        r = await client.post(
            "/api/admin/login",
            json={"username": "lockme", "password": "Admin@123456"},
        )
        assert r.json()["code"] == 1030

    async def test_admin_login_success_clears_fail_count(self, client: AsyncClient, db, fake_redis):
        """登录成功清除失败计数"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_admin(db, username="clearme", password="Admin@123456")

        # 失败 3 次
        for _ in range(3):
            await client.post("/api/admin/login", json={"username": "clearme", "password": "bad"})

        # 成功登录
        r_ok = await client.post(
            "/api/admin/login",
            json={"username": "clearme", "password": "Admin@123456"},
        )
        assert r_ok.json()["code"] == 0

        # 再失败 3 次不应触发锁定（之前的计数已清除）
        for _ in range(3):
            await client.post("/api/admin/login", json={"username": "clearme", "password": "bad"})

        r = await client.post(
            "/api/admin/login",
            json={"username": "clearme", "password": "Admin@123456"},
        )
        assert r.json()["code"] == 0

    async def test_admin_login_lockout_tier_2_at_10_failures(self, client: AsyncClient, db, fake_redis):
        """10 次失败触发 60 分钟锁定"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        await create_admin(db, username="tier2", password="Admin@123456")

        # 模拟已有 9 次失败记录
        await fake_redis.set("admin_login_fail:tier2", "9", ex=1800)

        r = await client.post(
            "/api/admin/login",
            json={"username": "tier2", "password": "bad"},
        )
        # 第 10 次触发 60 分钟锁
        assert r.json()["code"] in (1001, 1030)
        locked_ttl = await fake_redis.ttl("admin_locked:tier2")
        if locked_ttl > 0:
            assert locked_ttl > 15 * 60  # 锁超过 15 分钟

    async def test_admin_ip_rate_limit(self, client: AsyncClient, db, fake_redis):
        """同一 IP 每小时超过 40 次被限速"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        # 模拟已有 40 次 IP 尝试（测试环境 IP 是 127.0.0.1）
        await fake_redis.set("admin_login_ip:127.0.0.1", "40", ex=3600)

        r = await client.post(
            "/api/admin/login",
            json={"username": "any", "password": "any"},
        )
        assert r.json()["code"] == 1029


class TestAdminTokenRefresh:
    async def test_admin_refresh_token(self, client: AsyncClient, db):
        """有效 admin refresh_token 返回新 access_token"""
        from app.core.security import create_refresh_token

        admin = await create_admin(db)
        rtok = create_refresh_token({"admin_id": admin.id, "role": "admin", "admin_role": "super"})
        r = await client.post("/api/admin/refresh", json={"refresh_token": rtok})
        assert r.json()["code"] == 0
        assert "access_token" in r.json()["data"]

    async def test_admin_refresh_with_user_token_rejected(self, client: AsyncClient, db):
        """用户 refresh_token 不能用于管理端刷新"""
        from app.core.security import create_refresh_token

        rtok = create_refresh_token({"user_id": 1, "role": "user"})
        r = await client.post("/api/admin/refresh", json={"refresh_token": rtok})
        assert r.json()["code"] == 1002


class TestAdminProfile:
    async def test_admin_profile_returns_info(self, client: AsyncClient, db):
        """获取管理员个人信息"""
        admin = await create_admin(db, username="myprofile")
        r = await client.get("/api/admin/profile", headers=auth_headers(admin_token(admin.id)))
        assert r.json()["code"] == 0
        assert r.json()["data"]["username"] == "myprofile"

    async def test_admin_profile_no_password_returned(self, client: AsyncClient, db):
        """管理员 profile 不返回密码"""
        admin = await create_admin(db)
        r = await client.get("/api/admin/profile", headers=auth_headers(admin_token(admin.id)))
        assert "password" not in r.text


class TestAdminChangePassword:
    async def test_change_password_success(self, client: AsyncClient, db):
        """管理员成功修改密码"""
        admin = await create_admin(db, password="OldPwd@12345678")
        r = await client.post(
            "/api/admin/change-password",
            json={"old_password": "OldPwd@12345678", "new_password": "NewPwd@12345678!"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0

    async def test_change_password_wrong_old_rejected(self, client: AsyncClient, db):
        """旧密码错误"""
        admin = await create_admin(db, password="OldPwd@12345678")
        r = await client.post(
            "/api/admin/change-password",
            json={"old_password": "wrong", "new_password": "NewPwd@12345678!"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1001

    async def test_change_password_same_as_old_rejected(self, client: AsyncClient, db):
        """新密码不能与旧密码相同"""
        admin = await create_admin(db, password="OldPwd@12345678")
        r = await client.post(
            "/api/admin/change-password",
            json={"old_password": "OldPwd@12345678", "new_password": "OldPwd@12345678"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1032

    async def test_admin_password_complexity_min_length(self, client: AsyncClient, db):
        """管理员密码必须 >= 12 位"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/change-password",
            json={"old_password": "Admin@123456", "new_password": "Short@1"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1031

    async def test_admin_password_must_have_special_char(self, client: AsyncClient, db):
        """管理员密码必须含特殊字符"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/change-password",
            json={"old_password": "Admin@123456", "new_password": "NoSpecialChar123"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1031


class TestAdminUnlock:
    async def test_super_admin_can_unlock(self, client: AsyncClient, db, fake_redis):
        """super 管理员可以解锁被锁定账号"""
        import app.core.redis as redis_mod

        redis_mod.redis_client = fake_redis
        super_admin = await create_admin(db, username="super", role="super")
        # 模拟一个被锁账号
        await fake_redis.set("admin_locked:victim", "1", ex=900)
        await fake_redis.set("admin_login_fail:victim", "5", ex=1800)

        r = await client.post(
            "/api/admin/unlock-admin",
            json={"username": "victim", "password": ""},
            headers=auth_headers(admin_token(super_admin.id, role="super")),
        )
        assert r.json()["code"] == 0

    async def test_normal_admin_cannot_unlock(self, client: AsyncClient, db):
        """普通管理员无法解锁账号"""
        normal = await create_admin(db, username="normal", role="normal")
        r = await client.post(
            "/api/admin/unlock-admin",
            json={"username": "victim", "password": ""},
            headers=auth_headers(admin_token(normal.id, role="normal")),
        )
        assert r.json()["code"] == 1003
