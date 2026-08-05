import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from jose import JWTError

from app.repositories.user_repository import UserRepository
from app.core.security import decode_token, hash_password, verify_password, create_access_token, create_refresh_token
from app.core.logging import logger
from app.schemas.auth import RefreshResponse, RegisterRequest, RegisterResponse, TokenResponse, AuthResponse
from app.core.exceptions import (
    EmailAlreadyExistsError,
    PhoneAlreadyExistsError,
    InvalidCredentialsError,
    RefreshTokenError,
)


class AuthService:
    """Authentication service for user registration and login."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """Register a new user."""
        # Check if email exists
        existing_email = await self.user_repo.get_by_email(data.email)
        if existing_email:
            logger.warning(f"Registration attempt with existing email: {data.email}")
            raise EmailAlreadyExistsError(data.email)
        
        # Check if phone exists
        existing_phone = await self.user_repo.get_by_phone(data.phone_number)
        if existing_phone:
            logger.warning(f"Registration attempt with existing phone: {data.phone_number}")
            raise PhoneAlreadyExistsError(data.phone_number)
        
        # Hash password
        hashed_password = hash_password(data.password)

        # Create user data
        user_data = {
            "full_name": data.full_name,
            "email": data.email,
            "phone_number": data.phone_number,
            "hashed_password": hashed_password,
            "role": "tenant",
            "is_verified": False,
            "is_active": True,
            "trust_score": 0,
        }

        try:
            user = await self.user_repo.create(user_data)

            # Generate access token
            access_token = create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "access"
            })

            # Generate refresh token
            refresh_token = create_refresh_token({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "refresh",
            })
            
            logger.info(f"User registered: {user.email}, ID: {user.id}")

            # Prepare response
            user_response = RegisterResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                phone_number=user.phone_number,
                role=user.role,
                is_verified=user.is_verified,
                is_active=user.is_active,
                trust_score=user.trust_score,
                created_at=user.created_at,
            )
            
            # Return user + token
            return AuthResponse(
                user=user_response,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error during registration: {e}")
            raise ValueError("Registration failed due to duplicate information")

    async def authenticate(self, identifier: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user using email or phone and password."""
        # Find user by email or phone
        user = await self.user_repo.get_by_email_or_phone(identifier)

        if not user:
            logger.warning(f"Login attempt with unknown identifier: {identifier}")
            return None

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt by inactive user: {user.email}")
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login attempt with invalid password: {user.email}")
            return None
        
        # Generate tokens
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "access"
        })
        
        refresh_token = create_refresh_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "refresh"
        })

        logger.info(f"User authenticated: {user.email}")
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def get_current_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current user by ID."""
        import uuid
        try:
            user_uuid = uuid.UUID(user_id)
            user = await self.user_repo.get_by_id(user_uuid)

            if user:
                return {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "is_verified": user.is_verified,
                    "is_active": user.is_active,
                    "trust_score": user.trust_score,
                    "created_at": user.created_at,
                }
            return None
        except ValueError:
            logger.error(f"Invalid UUID format: {user_id}")
        return None
    
    async def refresh_access_token(self, refresh_token: str) -> RefreshResponse:
        """Refresh access token using a valid refresh token."""

        try:
            # Decode and validate the refresh token
            payload = decode_token(refresh_token)

            # Check token type
            if payload.get("type") != "refresh":
                logger.warning("Attempted to use non-refresh token for refresh")
                raise RefreshTokenError("Invalid token type")
            
            # Get user ID from token
            user_id = payload.get("sub")

            if not user_id:
                logger.warning("Refresh token missing subject")
                raise RefreshTokenError("Invalid token")
            
            # Validate UUID format
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logger.warning(f"Invalid UUID in refresh token: {user_id}")
                raise RefreshTokenError("Invalid token")

            # Check if user exists
            user =  await self.user_repo.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found for refresh token: {user_id}")
                raise RefreshTokenError("User not found")

            if not user.is_active:
                logger.warning(f"Inactive user attemptted to refresh {user.email}")
                raise RefreshTokenError("User account is not active")
            # Generate new access token
            new_access_token = create_access_token({
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "access"
            })
            logger.info(f"Access token refreshed for user: {user.email}")

            return {
                "access_token":new_access_token,
                "type": "bearer"
            }
        except JWTError as e:
            logger.warning(f"Invalid JWT in refresh attempt: {e}")
            raise RefreshTokenError()

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user's password."""
        # check user exists
        try:
            user_uuid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except (ValueError, AttributeError, TypeError):
            logger.error(f"Invalid user id: {user_id}")
            raise ValueError("Invalid user ID")
        user = await self.user_repo.get_by_id(user_uuid)
        if not user:
            logger.warning(f"User not found for password change: {user_id}")
            raise ValueError("User not found")
        #check the current password is the same as the database password
        if not verify_password(current_password, user.hashed_password):
            logger.warning(f"Invalid current password for user: {user.email}")
            raise ValueError("Current password is incorrect")
        # reject reusing the password that is already stored
        if verify_password(new_password, user.hashed_password):
            logger.warning(f"Password change rejected, new password matches current: {user.email}")
            raise ValueError("New password must be different from the current password")
        # hash the new password
        new_hash = hash_password(new_password)
        # update database
        await self.user_repo.update(user, {"hashed_password": new_hash})

        logger.info(f"Password changed for user: {user.email}")

        return True