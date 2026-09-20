from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True