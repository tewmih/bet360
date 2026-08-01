from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    return  jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes a JWT token and returns the payload.
    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise JWTError(f"Token decode error: {str(e)}") from e