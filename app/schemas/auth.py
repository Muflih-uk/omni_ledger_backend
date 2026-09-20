from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str