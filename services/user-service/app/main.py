from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.db.session import Base, engine

from app.api.v1 import health_router, auth_router, user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    
    Startup:
        - Log service start
        - Initialize database tables (Alembic handles this in production)
    
    Shutdown:
        - Dispose database connections
        - Log service shutdown
    """
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v1.0.0")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🐛 Debug mode: {settings.debug}")

    # create databsase tables (if not using Alembic migrations)
    # for production, we assume Alembic handles migrations, so this is commented out
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("📊 Database tables verified")

    yield  # Service runs here

    # Shutdown
    logger.info(f"🛑 Shutting down {settings.app_name} v1.0.0")
    await engine.dispose()
    logger.info("🔌 Database connections closed")

    # create fastapi application instance
app = FastAPI(
    title=settings.app_name,
    description="User management and authentication service for Bet360",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Register routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])

@app.get("/")
async def root():
    """
    Root endpoint for the User Service API.
    """
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": "1.0.0",
        "environment": settings.environment,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z"    
    }

@app.get("/api/v1/version")
async def get_version():
    """
    Endpoint to get the current version of the User Service API.
    """
    return {
        "version": "1.0.0",
        "environment": settings.environment,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }   