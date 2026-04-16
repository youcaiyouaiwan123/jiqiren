"""用户认证：注册/登录/刷新Token/获取个人信息/注册配置/发送验证码"""
from datetime import datetime
import hashlib
import importlib.util
import json
import logging
import re
import secrets
import smtplib
import ssl
from email.message import EmailMessage

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.invite_code import InviteCode
from app.models.user import User
from app.models.register_config import RegisterConfig
from app.utils.response import fail, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


# ---------- Schemas ----------

class SendCodeBody(BaseModel):
    target: str
    type: str = "phone"


class RegisterBody(BaseModel):
    phone: str | None = None
    email: str | None = None
    password: str
    nickname: str | None = None
    invite_code: str | None = None
    verify_code: str | None = None


class LoginBody(BaseModel):
    account: str
    password: str


class RefreshBody(BaseModel):
    refresh_token: str


# ---------- helpers ----------

def _mask_phone(phone: str | None) -> str | None:
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def _mask_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    return local[:2] + "**@" + domain


def _user_dict(u: User, mask: bool = True) -> dict:
    return {
        "id": u.id,
        "nickname": u.nickname,
        "phone": _mask_phone(u.phone) if mask else u.phone,
        "email": _mask_email(u.email) if mask else u.email,
        "avatar_url": u.avatar_url,
        "free_chats_left": u.free_chats_left,
        "subscribe_plan": u.subscribe_plan,
        "subscribe_expire": u.subscribe_expire.isoformat() if u.subscribe_expire else None,
        "status": u.status,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


async def _get_all_register_config(db: AsyncSession) -> dict:
    """获取全量注册配置（含短信/邮件敏感字段，仅后端内部使用）"""
    rows = (await db.execute(select(RegisterConfig))).scalars().all()
    cfg = {r.config_key: r.config_value for r in rows}
    full_cfg = {
        "register_enabled": cfg.get("register_enabled", "true") == "true",
        "register_methods": [],
        "invite_code_required": cfg.get("invite_code_required", "false") == "true",
        "default_free_chats": int(cfg.get("default_free_chats", "3")),
        "terms_url": cfg.get("terms_url", ""),
        "privacy_url": cfg.get("privacy_url", ""),
        "sms_enabled": cfg.get("sms_enabled", "false") == "true",
        "sms_provider": cfg.get("sms_provider", ""),
        "sms_access_key": cfg.get("sms_access_key", ""),
        "sms_access_secret": cfg.get("sms_access_secret", ""),
        "sms_sign_name": cfg.get("sms_sign_name", ""),
        "sms_sdk_app_id": cfg.get("sms_sdk_app_id", ""),
        "sms_template_code": cfg.get("sms_template_code", ""),
        "email_enabled": cfg.get("email_enabled", "false") == "true",
        "smtp_host": cfg.get("smtp_host", ""),
        "smtp_port": cfg.get("smtp_port", "465"),
        "smtp_user": cfg.get("smtp_user", ""),
        "smtp_password": cfg.get("smtp_password", ""),
        "smtp_from": cfg.get("smtp_from", ""),
    }
    full_cfg["register_methods"] = _available_register_methods(full_cfg)
    return full_cfg


_PUBLIC_CONFIG_KEYS = {
    "register_enabled", "register_methods", "invite_code_required",
    "default_free_chats", "terms_url", "privacy_url",
}


def _public_register_config(full_cfg: dict) -> dict:
    """过滤出可以暴露给前端用户的配置（排除敏感字段）"""
    public_cfg = {k: v for k, v in full_cfg.items() if k in _PUBLIC_CONFIG_KEYS}
    available_methods = _available_register_methods(full_cfg)
    public_cfg["register_methods"] = available_methods
    public_cfg["register_enabled"] = bool(public_cfg.get("register_enabled")) and bool(available_methods)
    return public_cfg


PHONE_PATTERN = re.compile(r"^1\d{10}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SUPPORTED_VERIFY_TYPES = {"phone", "email"}


def _normalize_phone(phone: str | None) -> str | None:
    if phone is None:
        return None
    normalized = phone.strip().replace(" ", "")
    return normalized or None


def _normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    normalized = email.strip().lower()
    return normalized or None


def _normalize_invite_code(invite_code: str | None) -> str | None:
    if invite_code is None:
        return None
    normalized = invite_code.strip().upper().replace(" ", "")
    return normalized or None


def _normalize_target(target: str, target_type: str) -> str:
    if target_type == "email":
        return _normalize_email(target) or ""
    return _normalize_phone(target) or ""


def _is_valid_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.fullmatch(phone))


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email))


def _sms_provider(cfg: dict) -> str:
    return (cfg.get("sms_provider") or "").strip().lower()


def _sms_sdk_available(provider: str) -> bool:
    if provider == "aliyun":
        return (
            importlib.util.find_spec("aliyunsdkcore") is not None
            and importlib.util.find_spec("aliyunsdkdysmsapi") is not None
        )
    if provider == "tencent":
        return importlib.util.find_spec("tencentcloud") is not None
    return False


def _sms_channel_error_message(cfg: dict) -> str:
    if not cfg.get("sms_enabled"):
        return "短信服务未启用"
    provider = _sms_provider(cfg)
    if provider == "aliyun":
        if not all([
            (cfg.get("sms_access_key") or "").strip(),
            (cfg.get("sms_access_secret") or "").strip(),
            (cfg.get("sms_sign_name") or "").strip(),
            (cfg.get("sms_template_code") or "").strip(),
        ]):
            return "阿里云短信配置不完整"
        if not _sms_sdk_available(provider):
            return "阿里云短信 SDK 未安装"
        return "短信服务尚未接入"
    if provider == "tencent":
        if not all([
            (cfg.get("sms_access_key") or "").strip(),
            (cfg.get("sms_access_secret") or "").strip(),
            (cfg.get("sms_sdk_app_id") or "").strip(),
            (cfg.get("sms_sign_name") or "").strip(),
            (cfg.get("sms_template_code") or "").strip(),
        ]):
            return "腾讯云短信配置不完整"
        if not _sms_sdk_available(provider):
            return "腾讯云短信 SDK 未安装"
        return "短信服务尚未接入"
    return "短信服务商未配置"


def _sms_channel_available(cfg: dict) -> bool:
    if not cfg.get("sms_enabled"):
        return False
    provider = _sms_provider(cfg)
    if provider == "aliyun":
        return all([
            (cfg.get("sms_access_key") or "").strip(),
            (cfg.get("sms_access_secret") or "").strip(),
            (cfg.get("sms_sign_name") or "").strip(),
            (cfg.get("sms_template_code") or "").strip(),
        ]) and _sms_sdk_available(provider)
    if provider == "tencent":
        return all([
            (cfg.get("sms_access_key") or "").strip(),
            (cfg.get("sms_access_secret") or "").strip(),
            (cfg.get("sms_sdk_app_id") or "").strip(),
            (cfg.get("sms_sign_name") or "").strip(),
            (cfg.get("sms_template_code") or "").strip(),
        ]) and _sms_sdk_available(provider)
    return False


def _email_channel_available(cfg: dict) -> bool:
    return bool(cfg.get("email_enabled")) and bool(cfg.get("smtp_host")) and bool(cfg.get("smtp_from") or cfg.get("smtp_user"))


def _available_register_methods(cfg: dict) -> list[str]:
    methods: list[str] = []
    if _sms_channel_available(cfg):
        methods.append("phone")
    if _email_channel_available(cfg):
        methods.append("email")
    return methods


# ---------- 验证码相关 ----------

VERIFY_CODE_PREFIX = "verify_code:"
VERIFY_CODE_TTL = 300
VERIFY_CODE_COOLDOWN = 60
VERIFY_CODE_IP_WINDOW = 3600
VERIFY_CODE_IP_MAX = 10


def _verify_code_key(target_type: str, target: str) -> str:
    return f"{VERIFY_CODE_PREFIX}{target_type}:{target}"


def _cooldown_key(target_type: str, target: str) -> str:
    return f"{VERIFY_CODE_PREFIX}cd:{target_type}:{target}"


def _ip_rate_key(target_type: str, client_ip: str) -> str:
    return f"{VERIFY_CODE_PREFIX}ip:{target_type}:{client_ip}"


def _client_ip(request: Request) -> str:
    forwarded_for = (request.headers.get("x-forwarded-for") or "").split(",", 1)[0].strip()
    if forwarded_for:
        return forwarded_for
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _generate_code(length: int = 6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def _send_aliyun_sms_sync(phone: str, code: str, cfg: dict) -> None:
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
    except ImportError as exc:
        raise RuntimeError("阿里云短信 SDK 未安装") from exc

    client = AcsClient(
        (cfg.get("sms_access_key") or "").strip(),
        (cfg.get("sms_access_secret") or "").strip(),
        "cn-hangzhou",
    )
    request = SendSmsRequest()
    request.set_accept_format("json")
    request.set_PhoneNumbers(phone)
    request.set_SignName((cfg.get("sms_sign_name") or "").strip())
    request.set_TemplateCode((cfg.get("sms_template_code") or "").strip())
    request.set_TemplateParam(json.dumps({"code": code}, ensure_ascii=False))

    response = client.do_action_with_exception(request)
    payload = json.loads(response.decode("utf-8"))
    if payload.get("Code") != "OK":
        raise ValueError(f"阿里云短信发送失败: {payload.get('Code')} {payload.get('Message')}")


def _send_tencent_sms_sync(phone: str, code: str, cfg: dict) -> None:
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.sms.v20210111 import models, sms_client
    except ImportError as exc:
        raise RuntimeError("腾讯云短信 SDK 未安装") from exc

    cred = credential.Credential(
        (cfg.get("sms_access_key") or "").strip(),
        (cfg.get("sms_access_secret") or "").strip(),
    )
    http_profile = HttpProfile()
    http_profile.endpoint = "sms.tencentcloudapi.com"
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client = sms_client.SmsClient(cred, "ap-guangzhou", client_profile)
    req = models.SendSmsRequest()
    req.from_json_string(json.dumps({
        "PhoneNumberSet": [f"+86{phone}"],
        "SmsSdkAppId": (cfg.get("sms_sdk_app_id") or "").strip(),
        "SignName": (cfg.get("sms_sign_name") or "").strip(),
        "TemplateId": (cfg.get("sms_template_code") or "").strip(),
        "TemplateParamSet": [code],
    }))
    resp = client.SendSms(req)
    payload = json.loads(resp.to_json_string())
    status_list = payload.get("SendStatusSet") or []
    first_status = status_list[0] if status_list else {}
    if first_status.get("Code") != "Ok":
        raise ValueError(f"腾讯云短信发送失败: {first_status.get('Code')} {first_status.get('Message')}")


async def _send_sms(phone: str, code: str, cfg: dict) -> bool:
    provider = _sms_provider(cfg)
    if not provider:
        logger.warning("[SMS] 短信服务未配置: phone=%s", phone)
        return False
    if provider not in {"aliyun", "tencent"}:
        logger.error("[SMS] provider=%s 暂未支持，无法发送验证码到: %s", provider, phone)
        return False
    if not _sms_channel_available(cfg):
        logger.warning("[SMS] %s: provider=%s, phone=%s", _sms_channel_error_message(cfg), provider, phone)
        return False
    try:
        if provider == "aliyun":
            await run_in_threadpool(_send_aliyun_sms_sync, phone, code, cfg)
        else:
            await run_in_threadpool(_send_tencent_sms_sync, phone, code, cfg)
        logger.info("[SMS] provider=%s 已发送验证码到: %s", provider, phone)
        return True
    except Exception:
        logger.exception("[SMS] provider=%s 短信发送失败: phone=%s", provider, phone)
        return False


def _send_email_code_sync(email: str, code: str, cfg: dict) -> None:
    smtp_host = cfg.get("smtp_host", "")
    smtp_port = int(cfg.get("smtp_port") or 465)
    smtp_user = cfg.get("smtp_user", "")
    smtp_password = cfg.get("smtp_password", "")
    from_addr = cfg.get("smtp_from", "") or smtp_user
    if not smtp_host or not from_addr:
        raise ValueError("SMTP 配置不完整")

    message = EmailMessage()
    message["From"] = from_addr
    message["To"] = email
    message["Subject"] = "注册验证码"
    message.set_content(f"您的验证码是：{code}，5 分钟内有效。")

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ssl.create_default_context()) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
        return

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        try:
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
        except smtplib.SMTPNotSupportedError:
            pass
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(message)


async def _send_email_code(email: str, code: str, cfg: dict) -> bool:
    smtp_host = cfg.get("smtp_host", "")
    if not smtp_host:
        logger.warning("[EMAIL] 邮件服务未配置: email=%s", email)
        return False
    try:
        await run_in_threadpool(_send_email_code_sync, email, code, cfg)
        logger.info("[EMAIL] SMTP=%s 已发送验证码到: %s", smtp_host, email)
        return True
    except Exception:
        logger.exception("[EMAIL] 邮件发送失败: email=%s", email)
        return False


# ---------- Routes ----------

@router.get("/register-config")
async def get_register_config(db: AsyncSession = Depends(get_db)):
    full_cfg = await _get_all_register_config(db)
    return success(_public_register_config(full_cfg))


@router.post("/send-code")
async def send_verify_code(body: SendCodeBody, request: Request, db: AsyncSession = Depends(get_db)):
    """发送注册验证码（手机短信 / 邮箱）"""
    cfg = await _get_all_register_config(db)
    if not cfg["register_enabled"]:
        return fail(1006, "注册功能已关闭")
    if body.type not in SUPPORTED_VERIFY_TYPES:
        return fail(1012, "验证码类型不支持")
    target = _normalize_target(body.target, body.type)
    if not target:
        return fail(1001, "手机号或邮箱不能为空")
    if body.type == "phone":
        if not _is_valid_phone(target):
            return fail(1013, "手机号格式不正确")
        if not _sms_channel_available(cfg):
            return fail(1017, _sms_channel_error_message(cfg))
        if "phone" not in cfg["register_methods"]:
            return fail(1007, "该注册方式暂不支持")
        exists = (await db.execute(select(User).where(User.phone == target, User.deleted_at.is_(None)))).scalar_one_or_none()
        if exists:
            return fail(1005, "该手机号已注册")
    else:
        if "email" not in cfg["register_methods"]:
            return fail(1007, "该注册方式暂不支持")
        if not _is_valid_email(target):
            return fail(1015, "邮箱格式不正确")
        if not _email_channel_available(cfg):
            return fail(1016, "邮件服务未配置")
        exists = (await db.execute(select(User).where(User.email == target, User.deleted_at.is_(None)))).scalar_one_or_none()
        if exists:
            return fail(1005, "该邮箱已注册")
    redis = get_redis(required=False)
    if redis is None:
        return fail(5003, "验证码服务暂不可用，请稍后重试")
    client_ip = _client_ip(request)
    if client_ip != "unknown":
        ip_key = _ip_rate_key(body.type, client_ip)
        ip_count = await redis.incr(ip_key)
        if ip_count == 1:
            await redis.expire(ip_key, VERIFY_CODE_IP_WINDOW)
        if ip_count > VERIFY_CODE_IP_MAX:
            ttl = max(await redis.ttl(ip_key), 1)
            return fail(1022, f"当前 IP 请求过于频繁，请 {ttl} 秒后重试")
    cooldown_key = _cooldown_key(body.type, target)
    if await redis.exists(cooldown_key):
        ttl = await redis.ttl(cooldown_key)
        return fail(1009, f"发送太频繁，请 {ttl} 秒后重试")
    code = _generate_code()
    if body.type == "email":
        ok = await _send_email_code(target, code, cfg)
    else:
        ok = await _send_sms(target, code, cfg)
    if not ok:
        return fail(5002, "验证码发送失败，请稍后重试")
    code_key = _verify_code_key(body.type, target)
    await redis.set(code_key, code, ex=VERIFY_CODE_TTL)
    await redis.set(cooldown_key, "1", ex=VERIFY_CODE_COOLDOWN)
    return success({"message": "验证码已发送", "expires_in": VERIFY_CODE_TTL})


@router.post("/register")
async def register(body: RegisterBody, db: AsyncSession = Depends(get_db)):
    cfg = await _get_all_register_config(db)
    phone = _normalize_phone(body.phone)
    email = _normalize_email(body.email)
    invite_code = _normalize_invite_code(body.invite_code)
    verify_code = (body.verify_code or "").strip()
    if not cfg["register_enabled"]:
        return fail(1006, "注册功能已关闭")
    if len(body.password) < 6:
        return fail(1019, "密码长度不能少于 6 位")
    if phone and email:
        return fail(1018, "请仅选择一种注册方式")
    if not phone and not email:
        return fail(1001, "手机号和邮箱至少填一个")
    if phone and not _is_valid_phone(phone):
        return fail(1013, "手机号格式不正确")
    if email and not _is_valid_email(email):
        return fail(1015, "邮箱格式不正确")
    if phone and not _sms_channel_available(cfg):
        return fail(1017, _sms_channel_error_message(cfg))
    if phone and "phone" not in cfg["register_methods"]:
        return fail(1007, "该注册方式暂不支持")
    if email and "email" not in cfg["register_methods"]:
        return fail(1007, "该注册方式暂不支持")
    if email and not _email_channel_available(cfg):
        return fail(1016, "邮件服务未配置")
    invite: InviteCode | None = None
    if cfg["invite_code_required"] and not invite_code:
        return fail(1008, "邀请码不能为空")
    if cfg["invite_code_required"]:
        invite = (
            await db.execute(
                select(InviteCode)
                .where(InviteCode.code == invite_code)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not invite:
            return fail(1020, "邀请码无效")
        if invite.status == "disabled":
            return fail(1021, "邀请码已禁用")
        if invite.status == "used":
            return fail(1021, "邀请码已使用")
        if invite.status == "expired" or (invite.expire_at and invite.expire_at < datetime.now()):
            return fail(1021, "邀请码已过期")
    if not verify_code:
        return fail(1010, "请输入验证码")
    # 唯一性校验
    if phone:
        exists = (await db.execute(select(User).where(User.phone == phone, User.deleted_at.is_(None)))).scalar_one_or_none()
        if exists:
            return fail(1005, "该手机号已注册")
    if email:
        exists = (await db.execute(select(User).where(User.email == email, User.deleted_at.is_(None)))).scalar_one_or_none()
        if exists:
            return fail(1005, "该邮箱已注册")
    target_type = "phone" if phone else "email"
    target = phone or email or ""
    redis = get_redis(required=False)
    if redis is None:
        return fail(5003, "验证码服务暂不可用，请稍后重试")
    code_key = _verify_code_key(target_type, target)
    consume_result = await redis.eval(
        """
        local current = redis.call('GET', KEYS[1])
        if not current then return 0 end
        if current ~= ARGV[1] then return -1 end
        redis.call('DEL', KEYS[1])
        return 1
        """,
        1,
        code_key,
        verify_code,
    )
    if consume_result != 1:
        return fail(1011, "验证码错误或已过期")
    identifier = target
    stable_hash = hashlib.md5(identifier.encode()).hexdigest()[-4:]
    nickname = body.nickname or f"用户{stable_hash}"
    user = User(
        phone=phone,
        email=email,
        password_hash=hash_password(body.password),
        nickname=nickname,
        free_chats_left=cfg["default_free_chats"],
    )
    db.add(user)
    try:
        await db.flush()
    except Exception:
        await db.rollback()
        return fail(1005, "该账号已注册")
    if invite:
        invite.status = "used"
        invite.used_by = user.id
        invite.used_at = datetime.now()
    return success({"user_id": user.id, "nickname": user.nickname, "free_chats_left": user.free_chats_left})


@router.post("/login")
async def login(body: LoginBody, db: AsyncSession = Depends(get_db)):
    account = body.account.strip()
    if "@" in account:
        stmt = select(User).where(User.email == account.lower())
    else:
        stmt = select(User).where(User.phone == account.replace(" ", ""))
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        return fail(1004, "账号不存在")
    if user.deleted_at is not None:
        return fail(1004, "账号已注销")
    if not verify_password(body.password, user.password_hash):
        return fail(1001, "密码错误")
    if user.status == "banned":
        return fail(2003, "账号已被封禁")
    token_data = {"user_id": user.id, "role": "user"}
    return success({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": 7200,
        "user": _user_dict(user),
    })


@router.post("/refresh")
async def refresh_token(body: RefreshBody):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        return fail(1002, "refresh_token 无效或已过期")
    token_data = {"user_id": payload["user_id"], "role": "user"}
    return success({
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": 7200,
    })


@router.get("/profile", tags=["用户"])
async def get_profile(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        return fail(1004, "用户不存在")
    return success(_user_dict(user))
