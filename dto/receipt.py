from datetime import datetime
from enum import Enum
from typing import TypedDict, List

from dto.product import ProductAggregated


class PaymentType(str, Enum):
    CASH = "cash"
    CASHLESS = "cashless"


class Payment(TypedDict):
    type: PaymentType
    amount: float


class Receipt(TypedDict):
    id: int
    products: List[ProductAggregated]
    payment: Payment
    total: float
    rest: float
    created_at: datetime
    public_token: str


class ReceiptCreate(TypedDict):
    products: List[ProductAggregated]
    payment: Payment
