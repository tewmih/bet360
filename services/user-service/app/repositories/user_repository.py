from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Optional

from app.models.user import User
from app.core.logging import logger

class UserRepository:
    """
     Repository for User database operations.
     accepts dictionary of user data and creates a new user in the database.
     returns the created user object or raises an IntegrityError if the user already exists.
    """

    def __init__(self, db: AsyncSession):
          self.db = db

    async def create(self, user_data: dict) -> User:
        """Create a new user in the database."""

        try: 
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"User created with ID: {user.id}")
            return user
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"IntegrityError while creating user: {e}")
            raise
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().one_or_none()
        logger.debug(f"User lookup by email: {email} -> {'found' if user else 'not found'}")
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.one_or_none()
        logger.debug(f"User lookup by ID: {user_id} -> {'found' if user else 'not found'}")
        return user

    async def get_by_email_or_phone(self, identifier: str) -> Optional[User]:
        """Get user by email or phone"""
        result = await self.db.execute(
            select(User).where(
               ( User.email == identifier) | (User.phone_number == identifier)
            )
        )
        user = result.one_or_none()
        logger.debug(f"User lookup by identifier: {identifier} -> {'found' if user else 'not found'}")
        return user

    async def update(self, user: User, update_data: dict) -> User:
        """Update a user's fields."""
        for key, value in update_data:
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.execute()
        await self.db.refresh(user)
        logger.info(f"User updated: {user.email}")
        return user