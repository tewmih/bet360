from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
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
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Provide a database session for dependency injection."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()