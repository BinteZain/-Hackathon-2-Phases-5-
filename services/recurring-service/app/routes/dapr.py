"""
Dapr Pub/Sub subscription endpoints.

This module handles incoming events from Kafka via Dapr Pub/Sub.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from app.config import settings
from app.models.events import EventType, TaskCompletedData
from app.services.recurrence import RecurrenceCalculator
from app.services.task_creator import task_creator
from app.services.event_publisher import event_publisher
from app.repositories import database

logger = logging.getLogger(settings.SERVICE_NAME)

router = APIRouter()


@router.post("/dapr/subscribe/task-events")
async def subscribe_task_events(event: Dict[str, Any]):
    """
    Dapr subscription endpoint for task-events topic.
    
    This endpoint receives all task events from Kafka via Dapr Pub/Sub.
    It filters for TASK_COMPLETED events on recurring tasks and generates
    the next occurrence.
    
    Args:
        event: Event payload from Dapr
        
    Returns:
        Success response
    """
    try:
        logger.debug(f"Received task event: {event.get('eventType')}")
        
        event_type = event.get("eventType")
        event_data = event.get("data", {})
        event_id = event.get("eventId", "unknown")
        
        # Only process TASK_COMPLETED events
        if event_type != EventType.TASK_COMPLETED.value:
            logger.debug(f"Ignoring event type: {event_type}")
            return {"status": "IGNORED", "reason": f"Not a TASK_COMPLETED event"}
        
        # Check if task is recurring
        is_recurring = event_data.get("isRecurring", False)
        if not is_recurring:
            logger.debug(f"Task is not recurring, skipping")
            return {"status": "IGNORED", "reason": "Task not recurring"}
        
        # Extract required fields
        task_id = event_data.get("taskId")
        user_id = event_data.get("userId")
        completed_at = event_data.get("completedAt")
        recurring_task_id = event_data.get("recurringTaskId")
        recurrence_rule = event_data.get("recurrenceRule")
        recurrence_start_date = event_data.get("recurrenceStartDate")
        timezone = event_data.get("timezone", "UTC")
        
        if not all([task_id, user_id, recurring_task_id, recurrence_rule]):
            logger.warning(f"Missing required fields in event: {event_data.keys()}")
            return {"status": "ERROR", "reason": "Missing required fields"}
        
        logger.info(
            f"Processing completed recurring task: {task_id} "
            f"(recurring: {recurring_task_id}, user: {user_id})"
        )
        
        # Get recurring task details from database
        recurring_task = await database.get_recurring_task(recurring_task_id)
        if not recurring_task:
            logger.warning(f"Recurring task not found: {recurring_task_id}")
            return {"status": "ERROR", "reason": "Recurring task not found"}
        
        # Get original task data
        original_task = await database.get_original_task(task_id)
        if not original_task:
            logger.warning(f"Original task not found: {task_id}")
            return {"status": "ERROR", "reason": "Original task not found"}
        
        # Check if max occurrences reached
        max_occurrences = recurring_task.get("maxOccurrences")
        current_occurrence = recurring_task.get("currentOccurrence", 0)
        
        if max_occurrences and current_occurrence >= max_occurrences:
            logger.info(f"Max occurrences ({max_occurrences}) reached for {recurring_task_id}")
            return {"status": "SUCCESS", "message": "Max occurrences reached"}
        
        # Calculate next occurrence date
        try:
            start_date = datetime.fromisoformat(recurrence_start_date.replace("Z", "+00:00"))
            next_occurrence = RecurrenceCalculator.calculate_next_occurrence(
                recurrence_rule=recurrence_rule,
                start_date=start_date,
                last_occurrence=datetime.fromisoformat(completed_at.replace("Z", "+00:00")) if completed_at else None,
                timezone=timezone
            )
        except Exception as e:
            logger.error(f"Failed to calculate next occurrence: {e}")
            return {"status": "ERROR", "reason": f"Calculation error: {str(e)}"}
        
        # Create new task instance
        new_task_id = await task_creator.create_task(
            user_id=user_id,
            title=original_task.get("title", "Recurring Task"),
            description=original_task.get("description", ""),
            due_date=next_occurrence,
            priority=original_task.get("priority", "NONE"),
            recurring_task_id=recurring_task_id,
            occurrence_number=current_occurrence + 1,
            original_task_data=original_task
        )
        
        if not new_task_id:
            logger.error("Failed to create new task instance")
            return {"status": "ERROR", "reason": "Failed to create task"}
        
        # Publish TASK_CREATED event for the new occurrence
        from app.models.events import RecurringTaskEventData, Priority
        
        task_event_data = RecurringTaskEventData(
            taskId=new_task_id,
            userId=user_id,
            title=original_task.get("title", "Recurring Task"),
            description=original_task.get("description"),
            priority=Priority(original_task.get("priority", "NONE")),
            dueDate=next_occurrence,
            isRecurring=True,
            recurringTaskId=recurring_task_id,
            occurrenceNumber=current_occurrence + 1
        )
        
        correlation_id = event.get("metadata", {}).get("correlationId", str(uuid.uuid4()))
        
        published = await event_publisher.publish_task_created(
            task_data=task_event_data,
            correlation_id=correlation_id
        )
        
        if not published:
            logger.warning("Failed to publish TASK_CREATED event")
        
        # Update recurring task metadata
        await database.update_recurring_task(
            recurring_task_id=recurring_task_id,
            last_generated_at=datetime.utcnow(),
            next_occurrence_at=next_occurrence,
            current_occurrence=current_occurrence + 1
        )
        
        logger.info(
            f"Successfully generated next occurrence: {new_task_id} "
            f"(due: {next_occurrence})"
        )
        
        return {
            "status": "SUCCESS",
            "message": "Next occurrence generated",
            "newTaskId": new_task_id,
            "nextOccurrence": next_occurrence.isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Error processing task event: {e}")
        # Don't raise exception - Dapr will retry
        return {"status": "ERROR", "reason": str(e)}


@router.get("/dapr/subscribe/task-events")
async def get_subscription():
    """
    Get subscription metadata (for Dapr).
    
    Returns:
        Subscription metadata
    """
    return {
        "topic": settings.KAFKA_TOPIC_TASK_EVENTS,
        "route": "/dapr/subscribe/task-events",
        "pubsubname": settings.DAPR_PUBSUB_NAME
    }
