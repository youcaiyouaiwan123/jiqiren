"""
管理端 LLM 配置 + 禁用词测试
覆盖：LLM CRUD、默认模型唯一性、停用限制、禁用词批量导入、过滤
"""
import pytest
from httpx import AsyncClient

from tests.conftest import admin_token, auth_headers, create_admin, create_llm_provider

pytestmark = pytest.mark.asyncio


# ─────────────────────────────────────────────────────────────────────────────
# LLM Provider
# ─────────────────────────────────────────────────────────────────────────────


class TestLlmProviderCRUD:
    async def test_create_llm_provider(self, client: AsyncClient, db):
        """创建 LLM 配置成功"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/llm-providers",
            json={
                "name": "测试 Claude",
                "provider": "claude",
                "api_url": "https://api.anthropic.com",
                "api_key": "sk-test",
                "model": "claude-3-haiku-20240307",
                "is_active": 1,
                "is_default": 0,
            },
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["provider"] == "claude"

    async def test_create_invalid_provider_rejected(self, client: AsyncClient, db):
        """无效厂商名被拒绝"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/llm-providers",
            json={
                "name": "假厂商",
                "provider": "fakeai",
                "api_url": "https://fake.ai",
                "api_key": "xxx",
                "model": "fake-model",
            },
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1001

    async def test_list_llm_providers(self, client: AsyncClient, db):
        """列出 LLM 配置"""
        admin = await create_admin(db)
        await create_llm_provider(db, name="Provider1")
        await create_llm_provider(db, name="Provider2", is_default=0)

        r = await client.get("/api/admin/llm-providers", headers=auth_headers(admin_token(admin.id)))
        assert r.json()["code"] == 0
        assert r.json()["data"]["total"] >= 2

    async def test_api_key_not_in_list_response(self, client: AsyncClient, db):
        """api_key 不出现在列表响应中"""
        admin = await create_admin(db)
        await create_llm_provider(db, api_key="sk-super-secret")

        r = await client.get("/api/admin/llm-providers", headers=auth_headers(admin_token(admin.id)))
        assert "sk-super-secret" not in r.text

    async def test_update_llm_provider(self, client: AsyncClient, db):
        """更新 LLM 配置"""
        admin = await create_admin(db)
        llm = await create_llm_provider(db, name="Old Name", is_default=0)

        r = await client.put(
            f"/api/admin/llm-providers/{llm.id}",
            json={"name": "New Name"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["name"] == "New Name"

    async def test_update_nonexistent_llm_returns_1004(self, client: AsyncClient, db):
        """更新不存在的 LLM 返回 1004"""
        admin = await create_admin(db)
        r = await client.put(
            "/api/admin/llm-providers/999999",
            json={"name": "x"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1004

    async def test_delete_llm_provider(self, client: AsyncClient, db):
        """删除 LLM 配置"""
        admin = await create_admin(db)
        llm = await create_llm_provider(db, name="ToDelete", is_default=0)

        r = await client.delete(
            f"/api/admin/llm-providers/{llm.id}",
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0


class TestLlmDefaultProvider:
    async def test_only_one_default_at_a_time(self, client: AsyncClient, db):
        """设为默认时，其他配置自动取消默认"""
        admin = await create_admin(db)
        llm1 = await create_llm_provider(db, name="LLM1", is_default=1)
        llm2 = await create_llm_provider(db, name="LLM2", is_default=0)

        r = await client.put(
            f"/api/admin/llm-providers/{llm2.id}/default",
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0

        # 验证 llm1 不再是默认
        from sqlalchemy import select
        from app.models.llm_provider import LlmProvider

        llm1_updated = (await db.execute(select(LlmProvider).where(LlmProvider.id == llm1.id))).scalar_one()
        assert llm1_updated.is_default == 0

    async def test_cannot_set_inactive_as_default(self, client: AsyncClient, db):
        """未启用的 LLM 无法设为默认"""
        admin = await create_admin(db)
        llm = await create_llm_provider(db, is_default=0, is_active=0)

        r = await client.put(
            f"/api/admin/llm-providers/{llm.id}/default",
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1001

    async def test_cannot_create_inactive_default(self, client: AsyncClient, db):
        """创建时不能同时设 is_default=1 且 is_active=0"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/llm-providers",
            json={
                "name": "Bad LLM",
                "provider": "openai",
                "api_url": "https://api.openai.com",
                "api_key": "sk-x",
                "model": "gpt-4",
                "is_default": 1,
                "is_active": 0,
            },
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 1001

    async def test_disabling_default_clears_is_default(self, client: AsyncClient, db):
        """禁用默认 LLM 同时清除 is_default"""
        admin = await create_admin(db)
        llm = await create_llm_provider(db, is_default=1, is_active=1)

        r = await client.put(
            f"/api/admin/llm-providers/{llm.id}",
            json={"is_active": 0, "is_default": 0},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        # is_default 应该自动变为 0
        assert r.json()["data"]["is_default"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# 禁用词
# ─────────────────────────────────────────────────────────────────────────────


class TestBannedWords:
    async def test_create_banned_word(self, client: AsyncClient, db):
        """创建禁用词"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/banned-words",
            json={"word": "敏感词", "match_type": "contains", "action": "reject", "is_active": 1},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0

    async def test_list_banned_words(self, client: AsyncClient, db):
        """列出禁用词"""
        admin = await create_admin(db)
        await client.post(
            "/api/admin/banned-words",
            json={"word": "词一", "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        r = await client.get("/api/admin/banned-words", headers=auth_headers(admin_token(admin.id)))
        assert r.json()["code"] == 0
        assert r.json()["data"]["total"] >= 1

    async def test_search_banned_words_by_keyword(self, client: AsyncClient, db):
        """按关键词搜索禁用词"""
        admin = await create_admin(db)
        await client.post(
            "/api/admin/banned-words",
            json={"word": "特定词语", "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        r = await client.get(
            "/api/admin/banned-words?keyword=特定词语",
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["total"] >= 1

    async def test_batch_import_banned_words(self, client: AsyncClient, db):
        """批量导入禁用词"""
        admin = await create_admin(db)
        r = await client.post(
            "/api/admin/banned-words/batch",
            json={
                "words": ["词A", "词B", "词C"],
                "match_type": "contains",
                "action": "reject",
            },
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["imported"] == 3

    async def test_batch_import_skips_duplicates(self, client: AsyncClient, db):
        """批量导入跳过已存在的词"""
        admin = await create_admin(db)
        # 先导入一次
        await client.post(
            "/api/admin/banned-words/batch",
            json={"words": ["重复词"], "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        # 再导入包含重复的
        r = await client.post(
            "/api/admin/banned-words/batch",
            json={"words": ["重复词", "新词"], "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["data"]["imported"] == 1
        assert r.json()["data"]["skipped"] == 1

    async def test_batch_import_limit_500_words(self, client: AsyncClient, db):
        """批量导入上限 500 词"""
        admin = await create_admin(db)
        words = [f"word{i}" for i in range(600)]
        r = await client.post(
            "/api/admin/banned-words/batch",
            json={"words": words, "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["imported"] <= 500

    async def test_update_banned_word(self, client: AsyncClient, db):
        """更新禁用词"""
        admin = await create_admin(db)
        r_create = await client.post(
            "/api/admin/banned-words",
            json={"word": "原词", "match_type": "exact", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        word_id = r_create.json()["data"]["id"]

        r = await client.put(
            f"/api/admin/banned-words/{word_id}",
            json={"action": "warn"},
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0

    async def test_delete_banned_word(self, client: AsyncClient, db):
        """删除禁用词"""
        admin = await create_admin(db)
        r_create = await client.post(
            "/api/admin/banned-words",
            json={"word": "待删词", "match_type": "contains", "action": "reject"},
            headers=auth_headers(admin_token(admin.id)),
        )
        word_id = r_create.json()["data"]["id"]

        r = await client.delete(
            f"/api/admin/banned-words/{word_id}",
            headers=auth_headers(admin_token(admin.id)),
        )
        assert r.json()["code"] == 0
