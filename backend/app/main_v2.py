import asyncio
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.config import get_settings
from app.core.database import async_session, engine
from app.core.logging_config import setup_logging
from app.core.redis import close_redis, init_redis
from app.core.security import hash_password
from app.models import *  # noqa: F401,F403
from app.services.feishu_sync_runtime import start_feishu_sync_worker, stop_feishu_sync_worker
from app.services.knowledge_config_service import (
    build_effective_knowledge_config,
    load_knowledge_config_map,
    seed_knowledge_config_defaults,
)

setup_logging()

logger = logging.getLogger(__name__)
settings = get_settings()


async def _seed_db() -> None:
    logger.info("开始检查数据库种子数据")
    try:
        async with async_session() as session:
            from app.models.admin import Admin
            from app.models.ai_config import AiConfig
            from app.models.register_config import RegisterConfig

            exists = (await session.execute(select(Admin).where(Admin.username == "admin"))).scalar_one_or_none()
            if not exists:
                session.add(Admin(username="admin", password_hash=hash_password("admin123"), role="super"))

            register_defaults = {
                "register_enabled": "true",
                "register_methods": "phone,email",
                "invite_code_required": "false",
                "default_free_chats": "3",
                "terms_url": "",
                "privacy_url": "",
                "sms_enabled": "false",
                "sms_provider": "",
                "sms_access_key": "",
                "sms_access_secret": "",
                "sms_sign_name": "",
                "sms_sdk_app_id": "",
                "sms_template_code": "",
                "email_enabled": "false",
                "smtp_host": "",
                "smtp_port": "465",
                "smtp_user": "",
                "smtp_password": "",
                "smtp_from": "",
            }
            for key, value in register_defaults.items():
                row = (
                    await session.execute(select(RegisterConfig).where(RegisterConfig.config_key == key))
                ).scalar_one_or_none()
                if not row:
                    session.add(RegisterConfig(config_key=key, config_value=value, description=key))

            ai_defaults = {
                "system_prompt": "你是一个专业的客服助手，请依据 FAQ 与文档库回答用户问题。",
                "temperature": "0.7",
                "max_tokens": "2048",
                "faq_enabled": "true",
                "doc_recommend": "true",
                "knowledge_enabled": "false",
                "knowledge_top_k": "3",
                "knowledge_min_score": "0.35",
                "knowledge_embedding_provider": settings.KNOWLEDGE_EMBEDDING_PROVIDER,
                "knowledge_embedding_model": settings.KNOWLEDGE_EMBEDDING_MODEL,
            }
            for key, value in ai_defaults.items():
                row = (await session.execute(select(AiConfig).where(AiConfig.config_key == key))).scalar_one_or_none()
                if not row:
                    session.add(AiConfig(config_key=key, config_value=value, description=key))

            await seed_knowledge_config_defaults(session)
            await session.commit()
    except Exception:
        logger.exception("数据库种子初始化失败，请先执行 alembic upgrade head")
        raise

    logger.info("数据库种子数据检查完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("========== 应用启动 ==========")
    redis_conn = await init_redis()
    if redis_conn:
        logger.info("Redis connected")
    else:
        logger.warning("Redis unavailable, verification-code and Feishu async features are disabled")

    await _seed_db()
    await start_feishu_sync_worker()

    async with async_session() as session:
        knowledge_cfg = await load_knowledge_config_map(session)
        runtime_cfg = build_effective_knowledge_config(knowledge_cfg)
        logger.info("知识库目录 | vault=%s index=%s", runtime_cfg["vault_path"], runtime_cfg["index_dir"])

    try:
        from app.services.stt_service import _load_model

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _load_model)
        logger.info("STT 模型预加载完成")
    except Exception as exc:
        logger.warning("STT 模型预加载失败，首次使用时会重试: %s", exc)

    logger.info("========== 应用就绪 ==========")
    yield
    logger.info("========== 应用关闭 ==========")
    await stop_feishu_sync_worker()
    await close_redis()
    await engine.dispose()
    logger.info("Redis 连接已关闭")


app = FastAPI(
    title="AI 智能客服系统",
    description="基于飞书多维表格与 AI 的智能客服平台",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.deps import BizException
from app.utils.response import fail as _fail


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    logger.warning("BizException | %s %s | code=%s msg=%s", request.method, request.url.path, exc.code, exc.message)
    return JSONResponse(status_code=200, content=_fail(exc.code, exc.message))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("UnhandledException | %s %s | %s: %s", request.method, request.url.path, type(exc).__name__, exc)
    return JSONResponse(status_code=500, content=_fail(5000, "服务器内部错误"))


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    method = request.method
    path = request.url.path
    skip_log = path in ("/api/health",) or path.startswith("/docs") or path.startswith("/openapi")
    if not skip_log:
        logger.info(">>> %s %s", method, path)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("!!! %s %s middleware error: %s", method, path, exc)
        raise
    elapsed = round((time.time() - start) * 1000, 1)
    if not skip_log:
        logger.info("<<< %s %s | %s | %sms", method, path, response.status_code, elapsed)
    return response


from app.routers import (
    admin_ai_config,
    admin_announcements,
    admin_auth,
    admin_banned_words,
    admin_expire_reminders,
    admin_feishu,
    admin_invite_codes,
    admin_knowledge,
    admin_knowledge_files,
    admin_llm,
    admin_payment_config,
    admin_plans,
    admin_redeem,
    admin_register,
    admin_users,
    admin_wecom,
    admin_analytics_v2 as admin_analytics,
    admin_token_usage_v2 as admin_token_usage,
    auth,
    chat_v2 as chat,
    image_proxy,
    public,
    subscribe,
)

for router in [
    auth.router,
    chat.router,
    public.router,
    subscribe.router,
    image_proxy.router,
    admin_auth.router,
    admin_users.router,
    admin_analytics.router,
    admin_token_usage.router,
    admin_llm.router,
    admin_ai_config.router,
    admin_knowledge.router,
    admin_knowledge_files.router,
    admin_announcements.router,
    admin_banned_words.router,
    admin_redeem.router,
    admin_invite_codes.router,
    admin_feishu.router,
    admin_register.router,
    admin_payment_config.router,
    admin_plans.router,
    admin_wecom.router,
    admin_expire_reminders.router,
]:
    app.include_router(router)


uploads_dir = Path(__file__).resolve().parents[1] / "uploads" / "chat_images"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/chat/uploads", StaticFiles(directory=str(uploads_dir)), name="chat_uploads")


@app.get("/api/health")
async def health_check():
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}
