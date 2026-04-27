import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_safe_password(password: str) -> str:
    """
    Bcrypt only considers the first 72 bytes of the password.
    For longer passwords, pre-hash to a fixed-length hex digest to avoid runtime errors
    and preserve entropy for long inputs.
    """
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) <= 72:
        return password
    return hashlib.sha256(pw_bytes).hexdigest()


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(_bcrypt_safe_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(_bcrypt_safe_password(plain_password), hashed_password)
