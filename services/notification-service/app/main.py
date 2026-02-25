"""
Notification Service - Phase V

This service handles multi-channel notification delivery:
- Subscribes to reminders topic via Dapr Pub/Sub
- Sends notifications via Email, Push, or In-App
- Tracks delivery status
- Logs all delivery attempts with structured logging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import structlog

from app.config import settings
from app.routes import health, dapr, api
from app.repositories import database

# Configure structured logging
def setup_logging():
    """Configure structured logging for the service."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level
    )
    
    return structlog.get_logger(settings.SERVICE_NAME)


logger = setup_logging()


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    application = FastAPI(
        title=settings.SERVICE_NAME,
        description="Notification Service for Phase V - Multi-channel notification delivery",
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
    application.include_router(api.router, tags=["API"])
    
    # Startup event
    @application.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        log = structlog.get_logger(settings.SERVICE_NAME)
        log.info(
            "starting_notification_service",
            service=settings.SERVICE_NAME,
            version="5.0.0",
            port=settings.APP_PORT,
            dapr_pubsub=settings.DAPR_PUBSUB_NAME,
            subscribed_topics=[settings.KAFKA_TOPIC_REMINDERS, settings.KAFKA_TOPIC_TASK_EVENTS]
        )
        await database.init_db()
        log.info("database_connection_initialized")
    
    # Shutdown event
    @application.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        log = structlog.get_logger(settings.SERVICE_NAME)
        log.info("stopping_notification_service")
        await database.close_db()
        log.info("database_connection_closed")
    
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
