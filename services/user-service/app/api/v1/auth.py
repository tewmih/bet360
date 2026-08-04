from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import RegisterResponse, RegisterRequest, TokenResponse, AuthResponse
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
            detail="An unexpected error occurred during registration",
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

