"""Event and notification data models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


# ============== Enums ==============

class EventType(str, Enum):
    """Event types."""
    REMINDER_SCHEDULED = "REMINDER_SCHEDULED"
    REMINDER_TRIGGERED = "REMINDER_TRIGGERED"
    REMINDER_DISMISSED = "REMINDER_DISMISSED"
    TASK_CREATED = "TASK_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"


class NotificationChannel(str, Enum):
    """Notification channels."""
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class NotificationType(str, Enum):
    """Notification types."""
    REMINDER = "REMINDER"
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    WELCOME = "WELCOME"
    SYSTEM = "SYSTEM"


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class DeliveryStatus(str, Enum):
    """Detailed delivery status."""
    SUCCESS = "SUCCESS"
    FAILED_TEMPORARY = "FAILED_TEMPORARY"
    FAILED_PERMANENT = "FAILED_PERMANENT"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"


# ============== Event Models ==============

class EventMetadata(BaseModel):
    """Event metadata."""
    correlationId: Optional[str] = None
    causationId: Optional[str] = None
    tenantId: Optional[str] = None


class ReminderTriggeredData(BaseModel):
    """Reminder triggered event data."""
    reminderId: str
    taskId: str
    userId: str
    channel: NotificationChannel
    message: str
    triggeredAt: datetime
    title: Optional[str] = "Task Reminder"
    taskTitle: Optional[str] = None
    dueDate: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ReminderScheduledData(BaseModel):
    """Reminder scheduled event data."""
    reminderId: str
    taskId: str
    userId: str
    triggerTime: datetime
    channel: NotificationChannel
    message: str
    title: Optional[str] = None


class TaskCreatedData(BaseModel):
    """Task created event data."""
    taskId: str
    userId: str
    title: str
    description: Optional[str] = None
    dueDate: Optional[datetime] = None
    isRecurring: bool = False
    createdAt: datetime


class TaskCompletedData(BaseModel):
    """Task completed event data."""
    taskId: str
    userId: str
    completedAt: datetime
    isRecurring: bool = False


# ============== Base Event Structure ==============

class BaseEvent(BaseModel):
    """Base event structure."""
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventType: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source: str = "notification-service"
    data: Dict[str, Any]
    metadata: Optional[EventMetadata] = None


# ============== Notification Models ==============

class Notification(BaseModel):
    """Notification model."""
    notificationId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    taskId: Optional[str] = None
    reminderId: Optional[str] = None
    channel: NotificationChannel
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.PENDING
    sentAt: Optional[datetime] = None
    deliveredAt: Optional[datetime] = None
    readAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class NotificationRequest(BaseModel):
    """Notification send request."""
    userId: str
    channel: NotificationChannel
    type: NotificationType
    title: str
    message: str
    taskId: Optional[str] = None
    reminderId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification send response."""
    notificationId: str
    status: NotificationStatus
    channel: NotificationChannel
    sentAt: Optional[datetime] = None
    messageId: Optional[str] = None


class DeliveryResult(BaseModel):
    """Delivery result."""
    success: bool
    status: DeliveryStatus
    messageId: Optional[str] = None
    errorMessage: Optional[str] = None
    retryable: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== Email Models ==============

class EmailRequest(BaseModel):
    """Email send request."""
    to: str
    subject: str
    body: str
    html: Optional[str] = None
    fromEmail: Optional[str] = None
    fromName: Optional[str] = None


class EmailResponse(BaseModel):
    """Email send response."""
    success: bool
    messageId: Optional[str] = None
    errorMessage: Optional[str] = None


# ============== Push Notification Models ==============

class PushNotificationRequest(BaseModel):
    """Push notification send request."""
    userId: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    imageUrl: Optional[str] = None
    action: Optional[str] = None


class PushNotificationResponse(BaseModel):
    """Push notification send response."""
    success: bool
    messageId: Optional[str] = None
    errorMessage: Optional[str] = None


# ============== API Models ==============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationListResponse(BaseModel):
    """Notification list response."""
    notifications: List[Notification]
    total: int
    page: int
    pageSize: int


class UserPreferences(BaseModel):
    """User notification preferences."""
    userId: str
    emailEnabled: bool = True
    pushEnabled: bool = True
    inAppEnabled: bool = True
    quietHoursStart: Optional[str] = None  # HH:MM format
    quietHoursEnd: Optional[str] = None
    timezone: str = "UTC"
