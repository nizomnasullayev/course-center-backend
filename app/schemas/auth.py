from pydantic import BaseModel, Field
from typing import Optional
# Import UserBase to share the validation logic
from app.schemas.user import UserBase 

class LoginRequest(BaseModel):
    # Changed from phone_number to identifier to support both email or phone
    identifier: str = Field(..., min_length=1, description="Email or Phone Number")
    password: str = Field(..., min_length=1)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str

class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Firebase ID token")

# Inheriting from UserBase automatically includes:
# full_name, email, phone_number, and parents_phone (plus validations!)
class RegisterRequest(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class TokenPayload(BaseModel):
    sub: str  # user_id
    role: str
    exp: int