from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.db.session import engine
from app.db.base import Base
from app.api.v1 import health_router, listings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v1.0.0")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🐛 Debug mode: {settings.debug}")
    logger.info(f"🔌 Port: {settings.service_port}")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("📊 Database tables verified")

    yield  # Service runs here

    # Shutdown
    logger.info("🛑 Shutting down...")
    await engine.dispose()
    logger.info("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Property management and listing service for Bet360",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Register routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(listings_router, prefix="/api/v1", tags=["Listings"])


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/v1/version")
async def get_version():
    """Version endpoint for API versioning."""
    return {
        "version": "1.0.0",
        "service": "property-service",
        "api_version": "v1",
    }