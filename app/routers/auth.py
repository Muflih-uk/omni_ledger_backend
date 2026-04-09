from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.database.session import get_db
from app.models.admin import Admin
from app.models.user import User
from app.schemas.auth import AdminLoginRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


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


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == request.email).first()

    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    return {"access_token": token, "token_type": "bearer", "role": "admin"}
