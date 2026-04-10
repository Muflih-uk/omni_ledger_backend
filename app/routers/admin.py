from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, hash_password
from app.database.session import get_db
from app.models.admin import Admin
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/admin/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    payload = decode_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        name=user_data.name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(
    user_id: int,
    updates: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updates.name:
        user.name = updates.name
    if updates.phone:
        user.phone = updates.phone
    if updates.password:
        user.password_hash = hash_password(updates.password)
    if updates.is_active is not None:
        user.is_active = updates.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}
