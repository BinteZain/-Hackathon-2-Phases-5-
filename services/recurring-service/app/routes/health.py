"""Health check routes."""

from fastapi import APIRouter
from datetime import datetime
from app.models.events import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version="5.0.0"
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    
    Returns:
        Ready status
    """
    # Check database connection, Dapr connectivity, etc.
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint.
    
    Returns:
        Live status
    """
    return {"status": "live"}
