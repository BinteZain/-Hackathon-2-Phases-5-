"""Task and Event data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============== Enums ==============

class EventType(str, Enum):
    """Task event types."""
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_DELETED = "TASK_DELETED"
    TASK_CONFLICT_DETECTED = "TASK_CONFLICT_DETECTED"


class Priority(str, Enum):
    """Task priority levels."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskStatus(str, Enum):
    """Task status."""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


# ============== Event Models ==============

class EventMetadata(BaseModel):
    """Event metadata for correlation and tracing."""
    correlationId: Optional[str] = None
    causationId: Optional[str] = None
    tenantId: Optional[str] = None


class TaskEventData(BaseModel):
    """Task event payload data."""
    taskId: str
    userId: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = Priority.NONE
    status: Optional[TaskStatus] = TaskStatus.ACTIVE
    dueDate: Optional[datetime] = None
    tags: Optional[List[str]] = None
    isRecurring: Optional[bool] = False
    recurringTaskId: Optional[str] = None
    completedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class TaskUpdatedData(BaseModel):
    """Task updated event payload."""
    taskId: str
    userId: str
    changedFields: Optional[List[Dict[str, Any]]] = None
    updatedAt: Optional[datetime] = None


class TaskCompletedData(BaseModel):
    """Task completed event payload."""
    taskId: str
    userId: str
    completedAt: datetime
    isRecurring: bool
    recurringTaskId: Optional[str] = None
    recurrenceRule: Optional[str] = None
    recurrenceStartDate: Optional[datetime] = None
    timezone: Optional[str] = "UTC"


class RecurringTaskEventData(BaseModel):
    """Recurring task specific event data."""
    taskId: str
    userId: str
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.NONE
    dueDate: datetime
    isRecurring: bool = True
    recurringTaskId: str
    occurrenceNumber: int
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class ConflictData(BaseModel):
    """Conflict detection data."""
    taskId: str
    userId: str
    conflictType: str  # DUPLICATE, OVERLAP, INVALID_STATE
    resolution: str  # AUTO_MERGE, MANUAL_REQUIRED
    details: Dict[str, Any]


# ============== Base Event Structure ==============

class BaseEvent(BaseModel):
    """Base event structure for all events."""
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventType: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source: str = "recurring-service"
    data: Dict[str, Any]
    metadata: Optional[EventMetadata] = None


class TaskEvent(BaseEvent):
    """Task event wrapper."""
    data: TaskEventData | TaskUpdatedData | TaskCompletedData | RecurringTaskEventData


class TaskUpdateEvent(BaseEvent):
    """Task update event wrapper."""
    data: Dict[str, Any]


# ============== Recurring Task Models ==============

class RecurringTask(BaseModel):
    """Recurring task model."""
    recurringTaskId: str
    taskId: str
    userId: str
    recurrenceRule: str  # iCal RRule format
    startDate: datetime
    endDate: Optional[datetime] = None
    maxOccurrences: Optional[int] = None
    currentOccurrence: int = 0
    timezone: str = "UTC"
    isActive: bool = True
    lastGeneratedAt: Optional[datetime] = None
    nextOccurrenceAt: Optional[datetime] = None


class RecurrencePattern(BaseModel):
    """Recurrence pattern for calculation."""
    frequency: str  # DAILY, WEEKLY, MONTHLY, YEARLY
    interval: int = 1
    byWeekday: Optional[List[str]] = None  # MO, TU, WE, TH, FR, SA, SU
    byMonthday: Optional[List[int]] = None
    byYearday: Optional[List[int]] = None
    count: Optional[int] = None
    until: Optional[datetime] = None


# ============== API Request/Response Models ==============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DaprSubscriptionResponse(BaseModel):
    """Dapr subscription endpoint response."""
    status: str = "SUCCESS"
