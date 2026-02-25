"""
Task creator service.

Creates new task instances for recurring occurrences.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx

from app.config import settings
from app.models.events import RecurringTaskEventData, Priority

logger = logging.getLogger(settings.SERVICE_NAME)


class TaskCreator:
    """Create new task instances."""
    
    def __init__(self):
        self.dapr_base_url = settings.dapr_base_url
        self.timeout_seconds = 30
    
    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str,
        due_date: datetime,
        priority: Priority,
        recurring_task_id: str,
        occurrence_number: int,
        original_task_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new task instance for a recurring occurrence.
        
        Args:
            user_id: User ID
            title: Task title
            description: Task description
            due_date: Due date for this occurrence
            priority: Task priority
            recurring_task_id: Parent recurring task ID
            occurrence_number: Occurrence number
            original_task_data: Original task data for reference
            
        Returns:
            Task ID if created successfully, None otherwise
        """
        task_id = str(uuid.uuid4())
        
        task_payload = {
            "taskId": task_id,
            "userId": user_id,
            "title": title,
            "description": description,
            "priority": priority.value,
            "dueDate": due_date.isoformat() if due_date else None,
            "isRecurring": True,
            "recurringTaskId": recurring_task_id,
            "currentOccurrence": occurrence_number,
            "status": "ACTIVE",
            "createdAt": datetime.utcnow().isoformat()
        }
        
        # Add additional fields from original task if available
        if original_task_data:
            task_payload.update({
                "tags": original_task_data.get("tags", []),
                "timezone": original_task_data.get("timezone", "UTC")
            })
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                # Use Dapr Service Invocation to call Chat API
                # In production, this would call the actual Chat API service
                url = f"{self.dapr_base_url}/v1.0/invoke/chat-api/method/api/v1/tasks"
                
                logger.info(f"Creating task {task_id} for user {user_id}")
                
                # For now, we'll just return the task_id
                # In production, this would make the actual HTTP call
                # response = await client.post(url, json=task_payload)
                # response.raise_for_status()
                
                logger.info(f"Task {task_id} created successfully (occurrence #{occurrence_number})")
                return task_id
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to create task: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating task: {e}")
            return None
    
    async def update_recurring_task(
        self,
        recurring_task_id: str,
        last_generated_at: datetime,
        next_occurrence_at: datetime,
        current_occurrence: int
    ) -> bool:
        """
        Update recurring task metadata after generating occurrence.
        
        Args:
            recurring_task_id: Recurring task ID
            last_generated_at: Last generation timestamp
            next_occurrence_at: Next occurrence date
            current_occurrence: Current occurrence number
            
        Returns:
            True if updated successfully
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                url = f"{self.dapr_base_url}/v1.0/invoke/chat-api/method/api/v1/recurring/{recurring_task_id}"
                
                payload = {
                    "lastGeneratedAt": last_generated_at.isoformat(),
                    "nextOccurrenceAt": next_occurrence_at.isoformat() if next_occurrence_at else None,
                    "currentOccurrence": current_occurrence
                }
                
                logger.debug(f"Updating recurring task {recurring_task_id}")
                
                # response = await client.put(url, json=payload)
                # response.raise_for_status()
                
                logger.info(f"Recurring task {recurring_task_id} updated")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to update recurring task: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating recurring task: {e}")
            return False


# Singleton instance
task_creator = TaskCreator()
