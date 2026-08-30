from typing import TypeVar
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

async def paginate(session: AsyncSession, query: Select[tuple[T]], page: int = 1, page_size: int = 50) -> tuple[list[T], int, int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    count_query = select(func.count()).select_from(query.subquery())
    total = int((await session.execute(count_query)).scalar_one())
    items = list((await session.execute(query.offset((page - 1) * page_size).limit(page_size))).scalars().all())
    return items, total, page_size
