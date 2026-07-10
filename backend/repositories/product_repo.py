import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.product import Product
from models.product_detail import ProductDetail


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self, skip: int = 0, limit: int = 20) -> Sequence[Product]:
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.detail))
            .offset(skip)
            .limit(limit)
        )
        return result.unique().scalars().all()

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.detail))
            .where(Product.id == product_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_name(self, name: str) -> Product | None:
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.detail))
            .where(Product.product_name.ilike(name))
        )
        return result.unique().scalar_one_or_none()

    async def search(self, query: str, limit: int = 10) -> Sequence[Product]:
        stmt = (
            select(Product)
            .options(joinedload(Product.detail))
            .where(
                Product.product_name.ilike(f"%{query}%")
                | Product.description.ilike(f"%{query}%")
                | Product.category.ilike(f"%{query}%")
                | Product.manufacturer.ilike(f"%{query}%")
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
