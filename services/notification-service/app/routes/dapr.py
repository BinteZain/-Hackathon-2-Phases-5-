"""
Dapr Pub/Sub subscription endpoints.

This module handles incoming events from Kafka via Dapr Pub/Sub.
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import structlog
import uuid

from app.config import settings
from app.models.events import (
    EventType,
    NotificationChannel,
    NotificationType,
    NotificationRequest
)
from app.services.notification import notification_service
from app.repositories import database

router = APIRouter()
logger = structlog.get_logger(settings.SERVICE_NAME)


@router.post("/dapr/subscribe/reminders")
async def subscribe_reminders(event: Dict[str, Any]):
    """
    Dapr subscription endpoint for reminders topic.
    
    This endpoint receives REMINDER_TRIGGERED events from Kafka via Dapr Pub/Sub
    and sends notifications via the configured channel.
    
    Args:
        event: Event payload from Dapr
        
    Returns:
        Success response
    """
    log = logger.bind(
        event_id=event.get("eventId", "unknown"),
        event_type=event.get("eventType")
    )
    
    try:
        log.info("received_reminder_event")
        
        event_type = event.get("eventType")
        event_data = event.get("data", {})
        event_metadata = event.get("metadata", {})
        
        # Only process REMINDER_TRIGGERED events
        if event_type != EventType.REMINDER_TRIGGERED.value:
            log.debug("ignoring_event_type", type=event_type)
            return {"status": "IGNORED", "reason": f"Not a REMINDER_TRIGGERED event"}
        
        # Extract required fields
        reminder_id = event_data.get("reminderId")
        task_id = event_data.get("taskId")
        user_id = event_data.get("userId")
        channel = event_data.get("channel", "IN_APP")
        message = event_data.get("message")
        title = event_data.get("title", "Task Reminder")
        triggered_at = event_data.get("triggeredAt")
        
        if not all([reminder_id, user_id, channel, message]):
            log.warning("missing_required_fields", fields=event_data.keys())
            return {"status": "ERROR", "reason": "Missing required fields"}
        
        log = log.bind(
            reminder_id=reminder_id,
            user_id=user_id,
            channel=channel,
            task_id=task_id
        )
        
        log.info("processing_reminder_notification")
        
        # Check user preferences
        preferences = await database.get_user_preferences(user_id)
        
        if preferences:
            # Check if channel is enabled
            if channel == "EMAIL" and not preferences.emailEnabled:
                log.info("email_notifications_disabled_for_user")
                return {"status": "SKIPPED", "reason": "Email notifications disabled"}
            
            if channel == "PUSH" and not preferences.pushEnabled:
                log.info("push_notifications_disabled_for_user")
                return {"status": "SKIPPED", "reason": "Push notifications disabled"}
            
            # Check quiet hours
            if preferences.quietHoursStart and preferences.quietHoursEnd:
                # Implement quiet hours logic here
                log.debug("quiet_hours_configured", 
                         start=preferences.quietHoursStart,
                         end=preferences.quietHoursEnd)
        
        # Create notification request
        request = NotificationRequest(
            userId=user_id,
            channel=NotificationChannel(channel),
            type=NotificationType.REMINDER,
            title=title,
            message=message,
            taskId=task_id,
            reminderId=reminder_id,
            metadata={
                "triggeredAt": triggered_at,
                "correlationId": event_metadata.get("correlationId", str(uuid.uuid4()))
            }
        )
        
        # Send notification
        response = await notification_service.send_notification(request)
        
        log.info(
            "reminder_notification_sent",
            notification_id=response.notificationId,
            status=response.status.value,
            message_id=response.messageId
        )
        
        return {
            "status": "SUCCESS",
            "notificationId": response.notificationId,
            "channel": channel,
            "deliveredAt": response.sentAt.isoformat() if response.sentAt else None
        }
        
    except Exception as e:
        log.exception("error_processing_reminder_event", error=str(e))
        # Don't raise exception - Dapr will retry
        return {"status": "ERROR", "reason": str(e)}


@router.post("/dapr/subscribe/task-events")
async def subscribe_task_events(event: Dict[str, Any]):
    """
    Dapr subscription endpoint for task-events topic.
    
    This endpoint receives TASK_CREATED events to send welcome notifications.
    
    Args:
        event: Event payload from Dapr
        
    Returns:
        Success response
    """
    log = logger.bind(
        event_id=event.get("eventId", "unknown"),
        event_type=event.get("eventType")
    )
    
    try:
        event_type = event.get("eventType")
        event_data = event.get("data", {})
        
        # Only process TASK_CREATED events
        if event_type != EventType.TASK_CREATED.value:
            log.debug("ignoring_event_type", type=event_type)
            return {"status": "IGNORED", "reason": f"Not a TASK_CREATED event"}
        
        # For now, we just log task creation events
        # In production, you could send welcome notifications for first task
        task_id = event_data.get("taskId")
        user_id = event_data.get("userId")
        title = event_data.get("title")
        
        log.info(
            "received_task_created_event",
            task_id=task_id,
            user_id=user_id,
            title=title
        )
        
        return {"status": "SUCCESS", "message": "Event received"}
        
    except Exception as e:
        log.exception("error_processing_task_event", error=str(e))
        return {"status": "ERROR", "reason": str(e)}


@router.get("/dapr/subscribe/reminders")
async def get_reminders_subscription():
    """
    Get reminders subscription metadata.
    
    Returns:
        Subscription metadata
    """
    return {
        "topic": settings.KAFKA_TOPIC_REMINDERS,
        "route": "/dapr/subscribe/reminders",
        "pubsubname": settings.DAPR_PUBSUB_NAME
    }


@router.get("/dapr/subscribe/task-events")
async def get_task_events_subscription():
    """
    Get task-events subscription metadata.
    
    Returns:
        Subscription metadata
    """
    return {
        "topic": settings.KAFKA_TOPIC_TASK_EVENTS,
        "route": "/dapr/subscribe/task-events",
        "pubsubname": settings.DAPR_PUBSUB_NAME
    }
