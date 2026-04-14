"""通用 CRUD 工厂，减少管理端 router 样板代码"""
from typing import Any, Callable, Sequence, Type

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.response import fail, paginate, success


def row_to_dict(row: Any, exclude: set[str] | None = None) -> dict:
    """将 SQLAlchemy 模型实例转为 dict"""
    exclude = exclude or set()
    d = {}
    for col in row.__table__.columns:
        if col.name in exclude:
            continue
        val = getattr(row, col.name)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        d[col.name] = val
    return d


async def generic_list(
    db: AsyncSession,
    model: Type,
    *,
    page: int = 1,
    page_size: int = 20,
    order_by=None,
    filters: list | None = None,
    exclude_cols: set[str] | None = None,
) -> dict:
    stmt = select(model)
    if filters:
        for f in filters:
            stmt = stmt.where(f)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    if order_by is not None:
        stmt = stmt.order_by(order_by)
    offset = (page - 1) * page_size
    rows = (await db.execute(stmt.offset(offset).limit(page_size))).scalars().all()
    items = [row_to_dict(r, exclude_cols) for r in rows]
    return success(paginate(items, total, page, page_size))


async def generic_get(db: AsyncSession, model: Type, pk: int, exclude_cols: set[str] | None = None) -> dict:
    row = await db.get(model, pk)
    if not row:
        return fail(1004, "资源不存在")
    return success(row_to_dict(row, exclude_cols))


async def generic_create(db: AsyncSession, model: Type, data: dict) -> dict:
    row = model(**data)
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return success(row_to_dict(row))


async def generic_update(db: AsyncSession, model: Type, pk: int, data: dict) -> dict:
    row = await db.get(model, pk)
    if not row:
        return fail(1004, "资源不存在")
    for k, v in data.items():
        if v is not None:
            setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return success(row_to_dict(row))


async def generic_delete(db: AsyncSession, model: Type, pk: int) -> dict:
    row = await db.get(model, pk)
    if not row:
        return fail(1004, "资源不存在")
    await db.delete(row)
    return success(None, "删除成功")
