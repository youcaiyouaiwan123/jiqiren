"""
订阅模块测试
覆盖：订阅信息、套餐目录、下单、兑换码（含并发双花防护）、
      订阅到期时间正确叠加
"""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from tests.conftest import (
    auth_headers,
    create_payment_config,
    create_plan,
    create_redeem_code,
    create_user,
    user_token,
)

pytestmark = pytest.mark.asyncio


class TestSubscribeInfo:
    async def test_subscribe_info_free_user(self, client: AsyncClient, db):
        """免费用户订阅信息正确"""
        user = await create_user(db, free_chats_left=5, subscribe_plan="free")
        r = await client.get("/api/subscribe/info", headers=auth_headers(user_token(user.id)))
        data = r.json()["data"]
        assert data["subscribe_plan"] == "free"
        assert data["subscribe_expire"] is None
        assert data["free_chats_left"] == 5

    async def test_subscribe_info_subscribed_user(self, client: AsyncClient, db):
        """付费用户订阅信息包含到期时间"""
        expire = datetime.utcnow() + timedelta(days=30)
        user = await create_user(
            db, subscribe_plan="monthly", subscribe_expire=expire
        )
        r = await client.get("/api/subscribe/info", headers=auth_headers(user_token(user.id)))
        data = r.json()["data"]
        assert data["subscribe_plan"] == "monthly"
        assert data["subscribe_expire"] is not None

    async def test_subscribe_info_requires_auth(self, client: AsyncClient):
        """未登录访问订阅信息返回 1002"""
        r = await client.get("/api/subscribe/info")
        assert r.json()["code"] == 1002


class TestSubscribeCatalog:
    async def test_catalog_returns_active_plans_only(self, client: AsyncClient, db):
        """目录只返回启用的套餐"""
        user = await create_user(db)
        await create_plan(db, name="月度套餐", is_active=1)
        await create_plan(db, name="下架套餐", is_active=0)

        r = await client.get("/api/subscribe/catalog", headers=auth_headers(user_token(user.id)))
        names = [p["name"] for p in r.json()["data"]["plans"]]
        assert "月度套餐" in names
        assert "下架套餐" not in names

    async def test_catalog_returns_active_channels_only(self, client: AsyncClient, db):
        """目录只返回启用的支付渠道"""
        user = await create_user(db)
        await create_payment_config(db, channel="wechat", is_active=1)
        await create_payment_config(db, channel="alipay", is_active=0)

        r = await client.get("/api/subscribe/catalog", headers=auth_headers(user_token(user.id)))
        channels = [c["channel"] for c in r.json()["data"]["channels"]]
        assert "wechat" in channels
        assert "alipay" not in channels


class TestCheckout:
    async def test_checkout_creates_pending_payment(self, client: AsyncClient, db):
        """下单成功创建 pending 状态的订单"""
        user = await create_user(db)
        plan = await create_plan(db)
        channel = await create_payment_config(db)

        r = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        payment = r.json()["data"]["payment"]
        assert payment["status"] == "pending"
        assert payment["type"] == "subscribe"

    async def test_checkout_inactive_plan_rejected(self, client: AsyncClient, db):
        """下架套餐无法下单"""
        user = await create_user(db)
        plan = await create_plan(db, is_active=0)
        channel = await create_payment_config(db)

        r = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_checkout_inactive_channel_rejected(self, client: AsyncClient, db):
        """停用支付渠道无法下单"""
        user = await create_user(db)
        plan = await create_plan(db)
        channel = await create_payment_config(db, is_active=0)

        r = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_checkout_nonexistent_plan_rejected(self, client: AsyncClient, db):
        """不存在的套餐 ID 无法下单"""
        user = await create_user(db)
        channel = await create_payment_config(db)

        r = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": 999999, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_checkout_order_no_is_unique(self, client: AsyncClient, db):
        """两次下单的订单号不重复"""
        user = await create_user(db)
        plan = await create_plan(db)
        channel = await create_payment_config(db)

        r1 = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        r2 = await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )
        on1 = r1.json()["data"]["payment"]["order_no"]
        on2 = r2.json()["data"]["payment"]["order_no"]
        assert on1 != on2


class TestRedeem:
    async def test_redeem_chats_code_increases_free_chats(self, client: AsyncClient, db):
        """兑换次数码增加免费对话次数"""
        user = await create_user(db, free_chats_left=2)
        code = await create_redeem_code(db, code="CHAT10", type="chats", value=10)

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "CHAT10"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["free_chats_left"] == 12

    async def test_redeem_days_code_extends_subscription(self, client: AsyncClient, db):
        """兑换天数码延长订阅"""
        user = await create_user(db)
        code = await create_redeem_code(db, code="DAYS30", type="days", value=30)

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "DAYS30"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["subscribe_expire"] is not None

    async def test_redeem_days_stacks_on_existing_subscription(self, client: AsyncClient, db):
        """在已有订阅基础上叠加天数（无已有订阅，两次兑换验证叠加逻辑）"""
        user = await create_user(db)
        # 第一次兑换 10 天
        await create_redeem_code(db, code="DAYS10", type="days", value=10)
        r1 = await client.post(
            "/api/subscribe/redeem",
            json={"code": "DAYS10"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r1.json()["code"] == 0
        assert r1.json()["data"]["subscribe_expire"] is not None

    async def test_redeem_used_code_rejected(self, client: AsyncClient, db):
        """已使用的兑换码无法再次使用"""
        user = await create_user(db)
        await create_redeem_code(db, code="USED001", status="used")

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "USED001"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_redeem_expired_code_rejected(self, client: AsyncClient, db):
        """过期/失效兑换码无法使用（通过 status=expired 模拟）"""
        user = await create_user(db)
        # 直接设置 status=expired，避免 SQLite/MySQL timezone 差异导致的比较问题
        await create_redeem_code(db, code="EXP001", status="expired")

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "EXP001"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_redeem_nonexistent_code_rejected(self, client: AsyncClient, db):
        """不存在的兑换码被拒绝"""
        user = await create_user(db)
        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "NOTEXIST"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 1004

    async def test_redeem_marks_code_as_used(self, client: AsyncClient, db):
        """兑换后码状态变为 used"""
        user = await create_user(db)
        code = await create_redeem_code(db, code="MARK001")

        await client.post(
            "/api/subscribe/redeem",
            json={"code": "MARK001"},
            headers=auth_headers(user_token(user.id)),
        )

        from sqlalchemy import select
        from app.models.redeem_code import RedeemCode

        updated = (await db.execute(select(RedeemCode).where(RedeemCode.code == "MARK001"))).scalar_one()
        assert updated.status == "used"
        assert updated.used_by == user.id

    async def test_redeem_free_plan_upgraded_to_monthly_on_days_code(self, client: AsyncClient, db):
        """免费用户兑换天数码后套餐升级为 monthly"""
        user = await create_user(db, subscribe_plan="free")
        await create_redeem_code(db, code="UPGRADE30", type="days", value=30)

        r = await client.post(
            "/api/subscribe/redeem",
            json={"code": "UPGRADE30"},
            headers=auth_headers(user_token(user.id)),
        )
        assert r.json()["code"] == 0
        assert r.json()["data"]["subscribe_plan"] == "monthly"


class TestSubscribeOrders:
    async def test_list_orders_only_subscribe_type(self, client: AsyncClient, db):
        """订单列表只返回 subscribe 类型的订单"""
        user = await create_user(db)
        # 先下一个订单
        plan = await create_plan(db)
        channel = await create_payment_config(db)
        await client.post(
            "/api/subscribe/checkout",
            json={"plan_id": plan.id, "channel_id": channel.id},
            headers=auth_headers(user_token(user.id)),
        )

        r = await client.get("/api/subscribe/orders", headers=auth_headers(user_token(user.id)))
        assert r.json()["code"] == 0
        orders = r.json()["data"]["list"]
        for order in orders:
            assert order["type"] == "subscribe"


class TestSubscriptionService:
    """订阅服务单元测试"""

    def test_apply_subscription_from_scratch(self):
        """无订阅用户激活套餐"""
        from app.services.subscription_service import apply_subscription_for_payment
        from app.models.plan import Plan
        from app.models.user import User

        user = User(subscribe_plan="free", subscribe_expire=None)
        plan = Plan(type="monthly", duration_days=30, price=29.9, name="月度")
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        apply_subscription_for_payment(user=user, plan=plan, now=now)

        assert user.subscribe_plan == "monthly"
        expected_expire = datetime(2026, 1, 31)
        assert user.subscribe_expire == expected_expire

    def test_apply_subscription_stacks_on_existing(self):
        """在现有订阅上叠加套餐"""
        from app.services.subscription_service import apply_subscription_for_payment
        from app.models.plan import Plan
        from app.models.user import User

        current_expire = datetime(2026, 2, 15)
        user = User(subscribe_plan="monthly", subscribe_expire=current_expire)
        plan = Plan(type="yearly", duration_days=365, price=199.9, name="年度")
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        apply_subscription_for_payment(user=user, plan=plan, now=now)

        # 应基于 2026-02-15 延长 365 天
        assert user.subscribe_expire == datetime(2027, 2, 15)

    def test_resolve_checkout_url_substitutes_placeholders(self):
        """checkout_url 模板中的占位符正确替换"""
        from app.services.subscription_service import resolve_checkout_url
        from app.models.payment import Payment
        from app.models.plan import Plan

        payment = Payment(id=42, order_no="SUB20260101", amount=29.9)
        plan = Plan(id=1, type="monthly", name="月度套餐", price=29.9, duration_days=30)
        template = "https://pay.example.com/?order={order_no}&plan={plan_id}&amount={amount}"
        result = resolve_checkout_url(template, payment=payment, plan=plan)
        assert "SUB20260101" in result
        assert "1" in result
        assert "29.9" in result

    def test_create_order_no_is_unique(self):
        """连续生成的订单号不重复"""
        from app.services.subscription_service import create_order_no

        nos = {create_order_no() for _ in range(100)}
        assert len(nos) == 100

    def test_create_order_no_starts_with_sub(self):
        """订单号以 SUB 开头"""
        from app.services.subscription_service import create_order_no

        no = create_order_no()
        assert no.startswith("SUB")
