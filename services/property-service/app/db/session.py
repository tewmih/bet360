from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..core.config import settings

#Engine - manages the connection pool
engine = create_async_engine(
    settings.database_url,
    echo = settings.debug,
    future = True,
    pool_pre_ping = True,
)

# Session
async_session_maker = async_sessionmaker(
    engine,
    class_= AsyncSession,
    expire_on_commit= False,
    autoflush= False,
    autocommit= False,
)

# Base
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for dependency injection."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()