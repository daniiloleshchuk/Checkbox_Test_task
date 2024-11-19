from typing import TypedDict, Optional


class ProductAggregated(TypedDict):
    name: str
    price: float
    quantity: Optional[int]
    weight: Optional[float]
    total: Optional[float]


class Product(TypedDict):
    name: str
    price: float
