#!/usr/bin/env python3
"""
Quick test script to verify the backend setup
This doesn't require a database connection
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.models.user import User, UserRole
        print("✅ Models import successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from app.schemas.user import UserCreate, UserUpdate, UserResponse
        print("✅ Schemas import successfully")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
        print("✅ Auth schemas import successfully")
    except Exception as e:
        print(f"❌ Auth schemas import failed: {e}")
        return False
    
    try:
        from app.utils.security import get_password_hash, verify_password
        print("✅ Security utils import successfully")
    except Exception as e:
        print(f"❌ Security utils import failed: {e}")
        return False
    
    try:
        from app.utils.jwt import create_access_token, decode_access_token
        print("✅ JWT utils import successfully")
    except Exception as e:
        print(f"❌ JWT utils import failed: {e}")
        return False
    
    return True


def test_password_hashing():
    """Test password hashing functionality"""
    print("\nTesting password hashing...")
    
    try:
        from app.utils.security import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        if verify_password(password, hashed):
            print("✅ Password hashing works correctly")
            return True
        else:
            print("❌ Password verification failed")
            return False
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        return False


def test_jwt_tokens():
    """Test JWT token creation and decoding"""
    print("\nTesting JWT tokens...")
    
    try:
        # Mock settings for testing
        import os
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        
        from app.utils.jwt import create_access_token, decode_access_token
        
        test_data = {"sub": "test-user-id", "role": "student"}
        token = create_access_token(test_data)
        
        decoded = decode_access_token(token)
        
        if decoded and decoded.get("sub") == "test-user-id":
            print("✅ JWT token creation and decoding works")
            return True
        else:
            print("❌ JWT token decoding failed")
            return False
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False


def test_pydantic_validation():
    """Test Pydantic schema validation"""
    print("\nTesting Pydantic validation...")
    
    try:
        from app.schemas.user import UserCreate
        from app.models.user import UserRole
        
        # Valid user data
        user_data = UserCreate(
            full_name="Test User",
            phone_number="+998901234567",
            password="password123",
            role=UserRole.STUDENT
        )
        print("✅ Pydantic validation works correctly")
        
        # Test invalid phone
        try:
            invalid_user = UserCreate(
                full_name="Test",
                phone_number="invalid",
                password="pass",
                role=UserRole.STUDENT
            )
            print("❌ Should have failed validation for invalid phone")
            return False
        except:
            print("✅ Pydantic validation catches invalid phone")
        
        return True
    except Exception as e:
        print(f"❌ Pydantic validation test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Course Center Backend - Setup Verification")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_password_hashing()
    all_passed &= test_jwt_tokens()
    all_passed &= test_pydantic_validation()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Setup looks good.")
        print("\nNext steps:")
        print("1. Setup your .env file with database credentials")
        print("2. Run: alembic upgrade head")
        print("3. Run: uvicorn app.main:app --reload")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 50)