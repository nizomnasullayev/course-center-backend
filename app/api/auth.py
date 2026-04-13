from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    GoogleAuthRequest,
    RegisterRequest
)
from app.schemas.user import UserResponse
from app.crud.user import user_crud
from app.utils.security import verify_password
from app.utils.jwt import create_access_token
from app.utils.firebase import firebase_auth
from app.config import settings
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email, phone, and password"""
    
    if user_crud.get_by_phone(db, user_data.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    if user_crud.get_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        full_name=user_data.full_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=user_data.password,
        role=UserRole.STUDENT,
        parents_phone=user_data.parents_phone
    )
    
    return user_crud.create(db, user_create)


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login with either phone number or email"""
    
    user = user_crud.get_by_email(db, credentials.identifier)
    
    if not user:
        user = user_crud.get_by_phone(db, credentials.identifier)
        
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google authentication. Please login with Google."
        )
    
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        role=user.role.value,
        full_name=user.full_name
    )

@router.post("/google", response_model=LoginResponse)
def google_auth(auth_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google Firebase ID token"""
    
    # 1. Verify Firebase token using our utility
    user_info = firebase_auth.verify_id_token(auth_data.id_token)
    
    # 2. Extract user info from decoded token
    email = user_info.get('email')
    full_name = user_info.get('name') or 'Google User'
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email found in Google account"
        )
    
    # 3. Check if user exists by email
    user = user_crud.get_by_email(db, email)
    
    # 4. If user doesn't exist, register them automatically
    if not user:
        from app.schemas.user import UserCreate
        
        # We generate a fallback unique phone number for Google users 
        # since your DB requires it and Google might not provide it.
        fallback_phone = user_info.get('phone_number') or f"G-{email}"
        
        user_create = UserCreate(
            full_name=full_name,
            email=email,
            phone_number=fallback_phone,
            password=None,  # No password needed for Google auth users
            role=UserRole.STUDENT
        )
        user = user_crud.create(db, user_create)
    
    # 5. Check if user is active
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # 6. Create your backend's internal access token (JWT)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        role=user.role.value,
        full_name=user.full_name
    )