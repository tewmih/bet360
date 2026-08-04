from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.logging import logger
from app.schemas.auth import RegisterRequest, RegisterResponse, TokenResponse, AuthResponse


class AuthService:
    """Authentication service for user registration and login."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        """Register a new user."""
        # Check if email exists
        existing_email = await self.user_repo.get_by_email(data.email)
        if existing_email:
            logger.warning(f"Registration attempt with existing email: {data.email}")
            raise ValueError(f"Email '{data.email}' is already registered")
        
        # Check if phone exists
        existing_phone = await self.user_repo.get_by_phone(data.phone_number)
        if existing_phone:
            logger.warning(f"Registration attempt with existing phone: {data.phone_number}")
            raise ValueError(f"Phone number '{data.phone_number}' is already registered")
        
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
            # return user + token
            return AuthResponse(
                user= user_response,
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
        user = await self.user_repo.get_by_email_or_phone(identifier)  # ← Fixed: await + correct method name

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
            user = await self.user_repo.get_by_id(user_uuid)  # ← Fixed: added await

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