from jose import jwt
from typing import Dict, Any
from app.core.config import settings


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])