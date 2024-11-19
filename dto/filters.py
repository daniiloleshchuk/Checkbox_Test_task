from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from dto import PaymentType


class PaginationFilters(BaseModel):
    limit: Optional[int] = Field(default=20, gt=0)
    offset: Optional[int] = Field(default=0, ge=0)


class CreatedAtFilters(BaseModel):
    max_created_at: Optional[datetime] = None
    min_created_at: Optional[datetime] = None


class ReceiptSwaggerFilters(PaginationFilters, CreatedAtFilters):
    payment_type: Optional[PaymentType] = None
    min_total: Optional[float] = None
    max_total: Optional[float] = None


class ReceiptFilters(ReceiptSwaggerFilters):
    user_id: Optional[int] = None
    public_token: Optional[str] = None
