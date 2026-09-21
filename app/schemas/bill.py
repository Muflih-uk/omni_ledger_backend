from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.bill import PaymentStatus


class BillItemInput(BaseModel):
    item_id: int
    quantity: int


class BillCreate(BaseModel):
    customer_name: str
    customer_phone: str
    items: List[BillItemInput]
    payment_status: PaymentStatus = PaymentStatus.unpaid


class BillItemResponse(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    total_amount: float
    payment_status: PaymentStatus
    created_at: Optional[datetime]
    items: List[BillItemResponse] = []

    class Config:
        from_attributes = True
