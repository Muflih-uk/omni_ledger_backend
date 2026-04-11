from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.bill import Bill, BillItem, PaymentStatus
from app.models.item import Item
from app.routers.items import get_current_user_id
from app.schemas.bill import BillCreate, BillResponse
from app.services.sms import send_bill_sms

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.post("", response_model=BillResponse)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    total = 0.0
    bill_items_to_create = []

    for entry in bill_data.items:
        item = db.query(Item).filter(Item.id == entry.item_id).first()
        if not item:
            raise HTTPException(
                status_code=404, detail=f"Item {entry.item_name} not found"
            )

        line_price = item.unit_price * entry.quantity
        total += line_price
        bill_items_to_create.append(
            {"item_id": item.id, "quantity": entry.quantity, "price": line_price}
        )

    new_bill = Bill(
        customer_name=bill_data.customer_name,
        customer_phone=bill_data.customer_phone,
        total_amount=total,
        payment_status=bill_data.payment_status,
        owner_id=user_id,
    )
    db.add(new_bill)
    db.flush()

    for bi in bill_items_to_create:
        db.add(BillItem(bill_id=new_bill.id, **bi))

    db.commit()
    db.refresh(new_bill)
    return _format_bill(new_bill, db)


@router.get("", response_model=List[BillResponse])
def get_bills(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    bills = db.query(Bill).filter(Bill.owner_id == user_id).all()
    return [_format_bill(b, db) for b in bills]


@router.get("/paid", response_model=List[BillResponse])
def get_paid_bills(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    bills = (
        db.query(Bill)
        .filter(Bill.owner_id == user_id, Bill.payment_status == "paid")
        .all()
    )
    return [_format_bill(b, db) for b in bills]


@router.get("/unpaid", response_model=List[BillResponse])
def get_unpaid_bills(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    bills = (
        db.query(Bill)
        .filter(Bill.owner_id == user_id, Bill.payment_status == "unpaid")
        .all()
    )
    return [_format_bill(b, db) for b in bills]


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.owner_id == user_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return _format_bill(bill, db)


@router.patch("/{bill_id}/payment-status", response_model=BillResponse)
def toggle_payment_status(
    bill_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.owner_id == user_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.payment_status = (
        PaymentStatus.unpaid
        if bill.payment_status == PaymentStatus.paid
        else PaymentStatus.paid
    )
    db.commit()
    db.refresh(bill)
    return _format_bill(bill, db)


@router.post("/{bill_id}/send-sms")
def send_sms(
    bill_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.owner_id == user_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    formatted = _format_bill(bill, db)
    result = send_bill_sms(formatted)
    return {"message": result}


def _format_bill(bill: Bill, db: Session) -> dict:
    items = []
    for bi in bill.bill_items:
        item = db.query(Item).filter(Item.id == bi.item_id).first()
        items.append(
            {
                "id": bi.id,
                "item_id": bi.item_id,
                "item_name": item.name if item else "Unknown",
                "quantity": bi.quantity,
                "price": bi.price,
            }
        )
    return {
        "id": bill.id,
        "customer_name": bill.customer_name,
        "customer_phone": bill.customer_phone,
        "total_amount": bill.total_amount,
        "payment_status": bill.payment_status,
        "created_at": bill.created_at,
        "items": items,
    }
