import uuid

from sqlalchemy import Column, Float, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from database.config import Base


class MixinBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)


class User(MixinBase):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    receipts = relationship("Receipt", back_populates="user")


class ReceiptProductAssociation(MixinBase):
    __tablename__ = "receipt_products"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=True, default=1)
    total = Column(Float, nullable=False)
    weight = Column(Float, nullable=True)

    receipt = relationship("Receipt", back_populates="products")
    product = relationship("Product")


class Product(MixinBase):
    __tablename__ = "products"

    name = Column(String, nullable=False, unique=True, index=True)
    price = Column(Float, nullable=False)


class Receipt(MixinBase):
    __tablename__ = "receipts"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_type = Column(String, nullable=False)
    rest = Column(Float, nullable=False)
    public_token = Column(String, unique=True, default=lambda: str(uuid.uuid4()))

    user = relationship("User", back_populates="receipts")
    products = relationship("ReceiptProductAssociation")
