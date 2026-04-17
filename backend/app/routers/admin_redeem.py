"""管理端：兑换码管理"""
import csv
import io
import logging
import secrets

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.redeem_code import RedeemCode
from app.utils.crud import generic_delete, generic_list
from app.utils.response import fail, success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/redeem-codes", tags=["管理端-兑换码"])


class GenerateRedeemBody(BaseModel):
    type: str = "days"
    value: int = 30
    count: int = 1
    expire_at: str | None = None


class BatchVoidBody(BaseModel):
    ids: list[int] | None = None
    select_all: bool = False
    status_filter: str | None = None


def _gen_code() -> str:
    return "-".join(secrets.token_hex(2).upper() for _ in range(3))


@router.get("")
async def list_redeem_codes(
    status: str | None = None,
    admin: dict = Depends(get_current_admin),
    pager: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    filters = [RedeemCode.status == status] if status else []
    return await generic_list(db, RedeemCode, page=pager.page, page_size=pager.page_size, filters=filters, order_by=RedeemCode.created_at.desc())


@router.post("/generate")
async def generate_codes(body: GenerateRedeemBody, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    codes = []
    for _ in range(min(body.count, 100)):
        code = _gen_code()
        rc = RedeemCode(
            code=code,
            type=body.type,
            value=body.value,
            created_by=admin["admin_id"],
            expire_at=body.expire_at,
        )
        db.add(rc)
        codes.append(code)
    await db.flush()
    return success({"codes": codes, "count": len(codes)})


# ── 批量作废（必须在 /{pk} 之前注册） ─────────────────────────────

@router.put("/batch-void")
async def batch_void(
    body: BatchVoidBody,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not body.select_all and not body.ids:
        return fail(1001, "请指定作废范围")

    stmt = (
        update(RedeemCode)
        .where(RedeemCode.status == "unused")
        .values(status="expired")
        .execution_options(synchronize_session=False)
    )
    if not body.select_all:
        stmt = stmt.where(RedeemCode.id.in_(body.ids))

    result = await db.execute(stmt)
    logger.info("[兑换码] 批量作废 | admin=%s voided=%d select_all=%s",
                admin.get("username"), result.rowcount, body.select_all)
    return success({"voided": result.rowcount})


# ── 批量导出 CSV（必须在 /{pk} 之前注册） ───────────────────────────

@router.get("/export")
async def export_codes(
    ids: str | None = None,
    select_all: bool = False,
    status_filter: str | None = None,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not select_all and not ids:
        return fail(1001, "请指定导出范围")

    query = select(RedeemCode).order_by(RedeemCode.created_at.desc())
    if select_all:
        if status_filter:
            query = query.where(RedeemCode.status == status_filter)
    else:
        id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
        if not id_list:
            return fail(1001, "无效的 ID 列表")
        query = query.where(RedeemCode.id.in_(id_list))

    rows = (await db.execute(query)).scalars().all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "兑换码", "类型", "值", "状态", "使用者ID", "使用时间", "过期时间", "创建时间"])
    status_label = {"unused": "未使用", "used": "已使用", "expired": "已过期"}
    for r in rows:
        writer.writerow([
            r.id, r.code,
            "天数" if r.type == "days" else "次数",
            r.value,
            status_label.get(r.status, r.status),
            r.used_by or "",
            str(r.used_at)[:19] if r.used_at else "",
            str(r.expire_at)[:19] if r.expire_at else "",
            str(r.created_at)[:19] if r.created_at else "",
        ])

    content = buf.getvalue().encode("utf-8-sig")  # BOM for Excel
    logger.info("[兑换码] 导出 | admin=%s rows=%d select_all=%s", admin.get("username"), len(rows), select_all)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="redeem_codes.csv"'},
    )


@router.delete("/{pk}")
async def delete_redeem_code(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, RedeemCode, pk)
