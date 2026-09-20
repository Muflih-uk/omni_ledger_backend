from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == request.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        name=request.name,
        phone=request.phone,
        password_hash=hash_password(request.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def user_login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == request.phone).first()

    if not user:
        raise HTTPException(status_code=401, detail="Phone number not registered")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": str(user.id), "role": "user"})
    return {"access_token": token, "token_type": "bearer", "role": "user"}