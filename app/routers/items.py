from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database.session import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["Items"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])


@router.post("", response_model=ItemResponse)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    new_item = Item(name=item_data.name, unit_price=item_data.unit_price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("", response_model=List[ItemResponse])
def get_items(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):

    query = db.query(Item)
    return query.all()


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    updates: ItemUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if updates.name:
        item.name = updates.name
    if updates.unit_price is not None:
        item.unit_price = updates.unit_price
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed"}
