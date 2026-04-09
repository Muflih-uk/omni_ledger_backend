from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
from app.models.admin import Admin
from app.routers import admin as admin_router
from app.routers import auth, bills, items

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        existing = db.query(Admin).first()
        if not existing:
            db.add(
                Admin(
                    name="Super Admin",
                    email="admin@omniledger.com",
                    password_hash=hash_password("Admin@123"),
                )
            )
            db.commit()
            print("✅ Default admin created: admin@shop.com / Admin@123")
    finally:
        db.close()

    yield


app = FastAPI(
    title="Omni Ledger",
    description="A complete billing system for shop owners",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin_router.router)
app.include_router(items.router)
app.include_router(bills.router)


@app.get("/")
def root():
    return {"message": "Billing System API is running 🚀"}
