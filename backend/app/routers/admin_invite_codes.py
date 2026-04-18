import logging
from datetime import datetime
import csv
import io
import secrets

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.invite_code import InviteCode
from app.utils.crud import generic_delete, row_to_dict
from app.utils.response import fail, paginate, success

router = APIRouter(prefix="/api/admin/invite-codes", tags=["管理端-邀请码"])


class GenerateInviteBody(BaseModel):
    count: int = 10
    expire_at: str | None = None
    remark: str | None = None


class UpdateInviteStatusBody(BaseModel):
    status: str


def _normalize_invite_code(code: str | None) -> str:
    return (code or "").strip().upper().replace(" ", "")


def _gen_code() -> str:
    return "INV-" + "-".join(secrets.token_hex(2).upper() for _ in range(2))


def _parse_expire_at(expire_at: str | None) -> datetime | None:
    if not expire_at:
        return None
    try:
        return datetime.fromisoformat(expire_at.strip())
    except ValueError:
        return None


def _display_status(row: InviteCode, now: datetime) -> str:
    if row.status == "active" and row.expire_at and row.expire_at < now:
        return "expired"
    return row.status


@router.get("")
async def list_invite_codes(
    status: str | None = None,
    keyword: str | None = None,
    admin: dict = Depends(get_current_admin),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now()
    stmt = select(InviteCode)
    if keyword:
        stmt = stmt.where(InviteCode.code.contains(_normalize_invite_code(keyword), autoescape=True))
    if status == "expired":
        stmt = stmt.where(
            or_(
                InviteCode.status == "expired",
                and_(InviteCode.status == "active", InviteCode.expire_at.is_not(None), InviteCode.expire_at < now),
            )
        )
    elif status:
        stmt = stmt.where(InviteCode.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    rows = (
        await db.execute(
            stmt.order_by(InviteCode.created_at.desc()).offset((pager.page - 1) * pager.page_size).limit(pager.page_size)
        )
    ).scalars().all()
    items = []
    for row in rows:
        item = row_to_dict(row)
        item["status"] = _display_status(row, now)
        items.append(item)
    return success(paginate(items, total, pager.page, pager.page_size))


@router.post("/generate")
async def generate_invite_codes(body: GenerateInviteBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    if body.count < 1 or body.count > 100:
        return fail(1001, "生成数量必须在 1 到 100 之间")
    expire_at = _parse_expire_at(body.expire_at)
    if body.expire_at and not expire_at:
        return fail(1001, "过期时间格式不正确")
    if expire_at and expire_at <= datetime.now():
        return fail(1001, "过期时间必须晚于当前时间")
    codes: list[str] = []
    generated: set[str] = set()
    while len(codes) < body.count:
        code = _gen_code()
        if code in generated:
            continue
        generated.add(code)
        remark = (body.remark or "").strip()[:200] or None
        db.add(InviteCode(code=code, created_by=admin["admin_id"], expire_at=expire_at, remark=remark))
        codes.append(code)
    await db.flush()
    return success({"codes": codes, "count": len(codes)})


@router.put("/{pk}/status")
async def update_invite_code_status(
    pk: int,
    body: UpdateInviteStatusBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if body.status not in {"active", "disabled"}:
        return fail(1001, "状态仅支持 active 或 disabled")
    row = await db.get(InviteCode, pk)
    if not row:
        return fail(1004, "资源不存在")
    if _display_status(row, datetime.now()) in {"used", "expired"}:
        return fail(1022, "当前邀请码状态不可修改")
    row.status = body.status
    await db.flush()
    item = row_to_dict(row)
    item["status"] = _display_status(row, datetime.now())
    return success(item)


@router.get("/export")
async def export_invite_codes(
    status: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now()
    stmt = select(InviteCode)
    if status == "expired":
        stmt = stmt.where(
            or_(
                InviteCode.status == "expired",
                and_(InviteCode.status == "active", InviteCode.expire_at.is_not(None), InviteCode.expire_at < now),
            )
        )
    elif status:
        stmt = stmt.where(InviteCode.status == status)
    rows = (await db.execute(stmt.order_by(InviteCode.created_at.desc()))).scalars().all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["邀请码", "状态", "备注", "使用用户ID", "使用时间", "过期时间", "创建时间"])
    status_map = {"active": "可使用", "used": "已使用", "disabled": "已禁用", "expired": "已过期"}
    for row in rows:
        display = _display_status(row, now)
        writer.writerow([
            row.code,
            status_map.get(display, display),
            row.remark or "",
            row.used_by or "",
            row.used_at.isoformat() if row.used_at else "",
            row.expire_at.isoformat() if row.expire_at else "",
            row.created_at.isoformat() if row.created_at else "",
        ])
    buf.seek(0)
    # Add BOM for Excel UTF-8 compatibility
    content = "\ufeff" + buf.getvalue()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=invite_codes.csv"},
    )


@router.delete("/{pk}")
async def delete_invite_code(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, InviteCode, pk)
