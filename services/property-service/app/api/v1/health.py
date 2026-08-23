from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "property-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }