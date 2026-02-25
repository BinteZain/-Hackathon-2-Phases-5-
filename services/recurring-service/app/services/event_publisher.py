"""
Event publisher service.

Publishes events to Kafka via Dapr Pub/Sub.
"""

import httpx
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

from app.config import settings
from app.models.events import (
    BaseEvent,
    TaskEvent,
    EventType,
    RecurringTaskEventData,
    EventMetadata,
    TaskCompletedData
)

logger = logging.getLogger(settings.SERVICE_NAME)


class EventPublisher:
    """Publish events to Kafka via Dapr Pub/Sub."""
    
    def __init__(self):
        self.dapr_base_url = settings.dapr_base_url
        self.pubsub_name = settings.DAPR_PUBSUB_NAME
        self.timeout_seconds = 30
    
    async def publish_event(
        self,
        topic: str,
        event_type: EventType,
        data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None
    ) -> bool:
        """
        Publish an event to Kafka via Dapr Pub/Sub.
        
        Args:
            topic: Kafka topic name
            event_type: Type of event
            data: Event payload data
            metadata: Optional event metadata
            
        Returns:
            True if published successfully
        """
        event = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "source": settings.SERVICE_NAME,
            "data": data,
            "metadata": {
                "correlationId": metadata.correlationId if metadata else str(uuid.uuid4()),
                "causationId": metadata.causationId if metadata else None,
                "tenantId": metadata.tenantId if metadata else None
            } if metadata else {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                url = f"{self.dapr_base_url}/v1.0/publish/{self.pubsub_name}/{topic}"
                
                logger.debug(f"Publishing event to {topic}: {event['eventId']}")
                
                response = await client.post(url, json=event)
                response.raise_for_status()
                
                logger.info(f"Event published successfully: {event['eventId']}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return False
    
    async def publish_task_created(
        self,
        task_data: RecurringTaskEventData,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish TASK_CREATED event for a new recurring occurrence.
        
        Args:
            task_data: Task data
            correlation_id: Optional correlation ID
            
        Returns:
            True if published successfully
        """
        metadata = EventMetadata(correlationId=correlation_id) if correlation_id else None
        
        data = {
            "taskId": task_data.taskId,
            "userId": task_data.userId,
            "title": task_data.title,
            "description": task_data.description,
            "priority": task_data.priority.value,
            "dueDate": task_data.dueDate.isoformat() if task_data.dueDate else None,
            "isRecurring": True,
            "recurringTaskId": task_data.recurringTaskId,
            "currentOccurrence": task_data.occurrenceNumber,
            "createdAt": task_data.createdAt.isoformat() if task_data.createdAt else datetime.utcnow().isoformat()
        }
        
        return await self.publish_event(
            topic=settings.KAFKA_TOPIC_TASK_EVENTS,
            event_type=EventType.TASK_CREATED,
            data=data,
            metadata=metadata
        )
    
    async def publish_task_conflict(
        self,
        task_id: str,
        user_id: str,
        conflict_type: str,
        resolution: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish TASK_CONFLICT_DETECTED event.
        
        Args:
            task_id: Task ID
            user_id: User ID
            conflict_type: Type of conflict
            resolution: Resolution strategy
            details: Conflict details
            correlation_id: Optional correlation ID
            
        Returns:
            True if published successfully
        """
        metadata = EventMetadata(correlationId=correlation_id) if correlation_id else None
        
        data = {
            "taskId": task_id,
            "userId": user_id,
            "conflictType": conflict_type,
            "resolution": resolution,
            "details": details
        }
        
        return await self.publish_event(
            topic=settings.KAFKA_TOPIC_TASK_UPDATES,
            event_type=EventType.TASK_CONFLICT_DETECTED,
            data=data,
            metadata=metadata
        )


# Singleton instance
event_publisher = EventPublisher()
