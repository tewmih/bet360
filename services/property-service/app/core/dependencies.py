from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.security import decode_token
from app.db.session import get_db
from app.core.logging import logger

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Validate JWT token and return current user information."""
    token = credentials.credentials
    
    try:
        # Decode and validate token
        payload = decode_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token: missing user information"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate UUID format
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token: malformed user ID"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"User authenticated: {email} (ID: {user_uuid})")
        
        return {
            "id": user_uuid,
            "email": email,
            "role": role or "tenant",
        }
        
    except JWTError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_ERROR",
                "message": "Authentication failed"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UUID:
    """Get the current user's ID."""
    return current_user["id"]


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, or None otherwise."""
    if not credentials:
        return None
    
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not user_id:
            return None
        
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None
        
        return {
            "id": user_uuid,
            "email": email,
            "role": role or "tenant",
        }
    except JWTError:
        return None