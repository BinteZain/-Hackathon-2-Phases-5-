"""Health check routes."""

from fastapi import APIRouter
from datetime import datetime
from app.models.events import HealthResponse
from app.config import settings
import structlog

router = APIRouter()
logger = structlog.get_logger(settings.SERVICE_NAME)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    logger.debug("health_check_requested")
    
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
    logger.debug("readiness_check_requested")
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint.
    
    Returns:
        Live status
    """
    logger.debug("liveness_check_requested")
    
    return {"status": "live"}
