from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Firebase ID token")


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)


class TokenPayload(BaseModel):
    sub: str  # user_id
    role: str
    exp: int