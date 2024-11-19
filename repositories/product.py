from typing import Optional

from sqlalchemy import select

from database import get_session, Product as ProductDBModel
from dto import ProductAggregated


class ProductRepository:
    @classmethod
    async def exists(cls, product: ProductAggregated) -> bool:
        async with get_session() as session:
            data = (await session.execute(
                select(ProductDBModel).where(ProductDBModel.name == product["name"])
            )).scalars().first()
        return bool(data)

    @classmethod
    async def get_id_by_name(cls, name: str) -> Optional[str]:
        async with get_session() as session:
            product_id = (await session.execute(
                select(ProductDBModel.id).where(ProductDBModel.name == name)
            )).scalars().first()
        return product_id
