from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from app.db.session import get_db
from app.core.logging import logger


router = APIRouter()
@router.get("/health", status_code=status.HTTP_200_OK, summary="Health Check", description="Check the health of the service")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify the service is running.
    Returns a simple message indicating the service is healthy.
    """

    # check database connection
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        overall_status = "healthy"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        db_status = "disconnected"
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "service": "user-service",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }