from app.core.dependencies import get_current_user
from app.core.exceptions import RefreshTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import ChangePasswordRequest, RefreshRequest, RefreshResponse, RegisterResponse, RegisterRequest, TokenResponse, AuthResponse
from app.services import AuthService
from app.core.logging import logger

router = APIRouter()

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account with email, phone, and password.",
    description="Create a new user account with email, phone, and password.",
)
async def register( data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register(data)
        return user
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during registration {e}",
            )
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and get JWT tokens",
    description="Authenticate with email or phone and password.",
)
async def login(
    identifier: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email or phone and password.
    **identifier**: Email or phone number
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate(identifier, password)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a refresh token.",
)
async def refresh_token(
    data: RefreshRequest,
    db:AsyncSession = Depends(get_db),
):
    """Refresh token"""

    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_access_token(data.refresh_token)
        return result
    except RefreshTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during token refresh",
        )

@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user's password with current password verification."
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change the current user password"""
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(current_user["id"], data.current_password, data.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during password change {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )