from typing import List, Optional

from sqlalchemy import select, Select
from sqlalchemy.orm import joinedload

from database import get_session, Receipt as ReceiptDBModel, Product as ProductDBModel, ReceiptProductAssociation
from dto import ReceiptCreate, Receipt, Payment, PaymentType, ProductAggregated, ReceiptFilters
from repositories.product import ProductRepository


class ReceiptRepository:
    @classmethod
    def _apply_filters(cls, statement: Select, filters: ReceiptFilters) -> Select:
        statement = statement.order_by(ReceiptDBModel.id)
        if filters.limit is not None:
            statement = statement.limit(filters.limit)
        if filters.offset is not None:
            statement = statement.offset(filters.offset)
        if filters.user_id is not None:
            statement = statement.where(ReceiptDBModel.user_id == filters.user_id)
        if filters.max_created_at is not None:
            statement = statement.where(ReceiptDBModel.created_at <= filters.max_created_at)
        if filters.min_created_at is not None:
            statement = statement.where(ReceiptDBModel.created_at >= filters.min_created_at)
        if filters.payment_type is not None:
            statement = statement.where(ReceiptDBModel.payment_type == filters.payment_type.value)
        if filters.max_total is not None:
            statement = statement.where(ReceiptDBModel.total <= filters.max_total)
        if filters.min_total is not None:
            statement = statement.where(ReceiptDBModel.total >= filters.min_total)
        if filters.public_token is not None:
            statement = statement.where(ReceiptDBModel.public_token == filters.public_token)
        return statement

    @classmethod
    def _prepare_receipt(cls, record: ReceiptDBModel) -> Receipt:
        receipt = Receipt(
            id=record.id,
            created_at=record.created_at,
            payment=Payment(
                amount=record.amount_paid,
                type=PaymentType(record.payment_type)
            ),
            products=[
                ProductAggregated(
                    name=association.product.name,
                    price=association.product.price,
                    quantity=association.quantity,
                    weight=association.weight,
                    total=association.total,
                )
                for association in record.products
            ],
            rest=record.rest,
            total=record.total,
            public_token=record.public_token,
        )
        return receipt

    @classmethod
    async def get_by_id(cls, receipt_id: int) -> Receipt:
        statement = (
            select(ReceiptDBModel)
            .options(
                joinedload(ReceiptDBModel.products)
                .joinedload(ReceiptProductAssociation.product))
            .where(ReceiptDBModel.id == receipt_id)
        )
        async with get_session() as session:
            data = (await session.execute(statement)).scalars().first()

        if not data:
            raise ValueError(f"Receipt with id {receipt_id} not found")

        receipt = cls._prepare_receipt(data)
        return receipt

    @classmethod
    async def get(cls, filters: Optional[ReceiptFilters] = None) -> List[Receipt]:
        statement = (
            select(ReceiptDBModel)
            .options(
                joinedload(ReceiptDBModel.products)
                .joinedload(ReceiptProductAssociation.product)
            )
        )
        statement = cls._apply_filters(statement, filters)
        async with get_session() as session:
            data = (await session.execute(statement)).unique().scalars().all()

        receipts = [cls._prepare_receipt(row) for row in data]

        return receipts

    @classmethod
    async def save(cls, receipt: ReceiptCreate, user_id: int) -> Receipt:
        amount_paid = receipt["payment"]["amount"]
        total = sum([p["price"] * p.get("quantity", 1) for p in receipt["products"]])
        rest = amount_paid - total
        receipt_entity = ReceiptDBModel(
            user_id=user_id,
            total=total,
            amount_paid=amount_paid,
            payment_type=receipt["payment"]["type"].value,
            rest=rest,
        )
        products_to_create = [
            ProductDBModel(
                name=product["name"],
                price=product["price"],
            )
            for product in receipt["products"]
            if not (await ProductRepository.exists(product))
        ]

        async with get_session() as session:
            session.add(receipt_entity)
            await session.flush()
            receipt_id = receipt_entity.id

            for product in products_to_create:
                session.add(product)
            await session.commit()

            for product in receipt["products"]:
                product_id = await ProductRepository.get_id_by_name(product["name"])

                if not product_id:
                    raise ValueError(f"Product '{product['name']}' not found.")

                receipt_product = ReceiptProductAssociation(
                    receipt_id=receipt_id,
                    product_id=product_id,
                    quantity=product.get("quantity", 1),
                    weight=product.get("weight"),
                    total=product["price"] * product.get("quantity", 1),
                )
                session.add(receipt_product)

            await session.commit()

        created_receipt = await cls.get_by_id(receipt_id)

        return created_receipt
