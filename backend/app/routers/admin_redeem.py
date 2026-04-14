"""管理端：兑换码管理"""
import logging
import secrets

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PageParams, get_current_admin
from app.models.redeem_code import RedeemCode
from app.utils.crud import generic_delete, generic_list
from app.utils.response import success

router = APIRouter(prefix="/api/admin/redeem-codes", tags=["管理端-兑换码"])


class GenerateRedeemBody(BaseModel):
    type: str = "days"
    value: int = 30
    count: int = 1
    expire_at: str | None = None


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


@router.delete("/{pk}")
async def delete_redeem_code(pk: int, admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await generic_delete(db, RedeemCode, pk)
