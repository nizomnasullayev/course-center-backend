from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import enum

class PaymentType(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    CLICK = "click"

class PaymentBase(BaseModel):
    student_id: UUID
    group_id: Optional[UUID] = None
    amount: float = Field(..., gt=0)
    payment_month: str
    type: PaymentType = PaymentType.CASH

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: UUID
    created_at: datetime
    student_name: Optional[str] = None
    group_name: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentPaginationResponse(BaseModel):
    total: int
    items: List[PaymentResponse]