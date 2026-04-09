from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    unit_price: float


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    unit_price: Optional[float] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    unit_price: float
    created_at: datetime

    class Config:
        from_attributes = True
