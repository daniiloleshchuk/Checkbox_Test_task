from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette import status
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from dto import ReceiptSwaggerFilters
from dto.filters import ReceiptFilters
from dto.product import ProductAggregated
from dto.receipt import PaymentType, ReceiptCreate, Payment
from services import AuthService, UserService, ReceiptService

router = APIRouter()


class ProductCreateModel(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: Optional[int] = Field(gt=0, default=None)
    weight: Optional[float] = Field(gt=0, default=None)

    def to_dto(self):
        return ProductAggregated(
            name=self.name,
            price=self.price,
            quantity=self.quantity,
            weight=self.weight,
            total=None,
        )

    @model_validator(mode="after")
    def validate(self):
        if (not self.quantity and not self.weight) or (self.weight and self.quantity):
            raise ValueError("Product can have either weight or quantity")
        return self


class PaymentModel(BaseModel):
    type: PaymentType
    amount: float = Field(gt=0)

    def to_dto(self):
        return Payment(
            amount=self.amount,
            type=self.type,
        )


class ReceiptCreateModel(BaseModel):
    products: List[ProductCreateModel]
    payment: PaymentModel

    def to_dto(self):
        return ReceiptCreate(
            payment=self.payment.to_dto(),
            products=[p.to_dto() for p in self.products]
        )


@router.post("/", dependencies=[Depends(AuthService.authenticate)])
async def create_receipt(receipt: ReceiptCreateModel, request: Request):
    token = request.headers["authorization"].replace("Bearer ", "")
    payload = AuthService.authenticate(token)
    user_id = await UserService.get_id_by_login(payload["login"])
    dto = receipt.to_dto()
    try:
        receipt = await ReceiptService.create(dto, user_id)
        return {"data": receipt}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save the receipt: {str(e)}"
        )


@router.get("/", dependencies=[Depends(AuthService.authenticate)])
async def get_receipts(request: Request, filters: ReceiptSwaggerFilters = Depends()):
    token = request.headers["authorization"].replace("Bearer ", "")
    payload = AuthService.authenticate(token)
    user_id = await UserService.get_id_by_login(payload["login"])
    try:
        receipts = await ReceiptService.get(ReceiptFilters(
            **filters.dict(exclude_unset=True),
            user_id=user_id,
        ))
        return {"data": receipts, "count": len(receipts)}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch receipts: {str(e)}"
        )


@router.get("/{public_token}", response_class=PlainTextResponse)
async def get_receipt_by_token(public_token: str, line_width: int = 32):
    receipt = (await ReceiptService.get(ReceiptFilters(public_token=public_token)))[0]
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return ReceiptService.format_receipt(receipt, line_width=line_width)


