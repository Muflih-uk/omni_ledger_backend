from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import Base, engine
from app.routers import auth, bills, items

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Omni Ledger",
    description="A complete billing system for shop owners",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(bills.router)


@app.get("/")
def root():
    return {"message": "Billing System API is running 🚀"}