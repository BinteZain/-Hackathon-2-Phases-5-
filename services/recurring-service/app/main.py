"""
Recurring Task Service - Phase V

This service handles recurring task management:
- Subscribes to task-events via Dapr Pub/Sub
- Detects completed recurring tasks
- Calculates next occurrence using iCal RRule
- Creates new task instances
- Publishes TASK_CREATED events for new occurrences
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.config import settings
from app.routes import health, dapr
from app.repositories import database

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(settings.SERVICE_NAME)


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    application = FastAPI(
        title=settings.SERVICE_NAME,
        description="Recurring Task Management Service for Phase V",
        version="5.0.0",
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    application.include_router(health.router, tags=["Health"])
    application.include_router(dapr.router, tags=["Dapr"])
    
    # Startup event
    @application.on_event("startup")
    async def startup_event():
        """Initialize database connection on startup."""
        logger.info("Starting up recurring-service...")
        await database.init_db()
        logger.info("Database connection initialized")
        logger.info(f"Dapr Pub/Sub: {settings.DAPR_PUBSUB_NAME}")
        logger.info(f"Subscribed to topic: {settings.KAFKA_TOPIC_TASK_EVENTS}")
    
    # Shutdown event
    @application.on_event("shutdown")
    async def shutdown_event():
        """Close database connection on shutdown."""
        logger.info("Shutting down recurring-service...")
        await database.close_db()
        logger.info("Database connection closed")
    
    return application


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
