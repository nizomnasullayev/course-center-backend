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
    """Register a new user with phone and password"""
    # Check if user already exists
    existing_user = user_crud.get_by_phone(db, user_data.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Create user (password will be hashed in CRUD)
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        password=user_data.password,
        role=UserRole.STUDENT,  # New registrations default to student
        parents_phone=user_data.parents_phone
    )
    
    new_user = user_crud.create(db, user_create)
    return new_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login with phone number and password"""
    # Get user by phone
    user = user_crud.get_by_phone(db, credentials.phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has a password (not Google-only account)
    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google authentication. Please login with Google."
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
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
    # Verify Firebase token
    user_info = firebase_auth.verify_id_token(auth_data.id_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Use email as phone_number fallback if phone not available
    phone_or_email = user_info.get('phone_number') or user_info.get('email')
    if not phone_or_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No phone number or email found in Google account"
        )
    
    # Check if user exists
    user = user_crud.get_by_phone(db, phone_or_email)
    
    # If user doesn't exist, create new user
    if not user:
        from app.schemas.user import UserCreate
        user_create = UserCreate(
            full_name=user_info.get('name') or 'Google User',
            phone_number=phone_or_email,
            password=None,  # No password for Google auth
            role=UserRole.STUDENT
        )
        user = user_crud.create(db, user_create)
    
    # Check if user is active
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
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