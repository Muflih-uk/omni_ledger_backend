import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    unpaid = "unpaid"


class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="bills")
    bill_items = relationship(
        "BillItem", back_populates="bill", cascade="all, delete-orphan"
    )


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey="bills.id")
    item_id = Column(Integer, ForeignKey="items.id")
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)

    bill = relationship("Bill", back_populates="bill_items")
    item = relationship("Item", back_populates="bill_items")
