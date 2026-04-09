from datetime import datetime

from pydantic import BaseModel


class AdminCreate(BaseModel):
    name: str
    email: str
    password: str


class AdminResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
