"""REST API endpoints for notifications."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import structlog

from app.models.events import (
    NotificationRequest,
    NotificationResponse,
    NotificationListResponse,
    Notification,
    UserPreferences,
    NotificationChannel,
    NotificationType
)
from app.services.notification import notification_service
from app.services.inapp_provider import inapp_provider
from app.repositories import database
from app.config import settings

router = APIRouter()
logger = structlog.get_logger(settings.SERVICE_NAME)


@router.post("/notifications/send", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest):
    """
    Send a notification.
    
    Args:
        request: Notification request
        
    Returns:
        Notification response
    """
    log = logger.bind(
        user_id=request.userId,
        channel=request.channel.value,
        type=request.type.value
    )
    
    log.info("send_notification_requested")
    
    try:
        response = await notification_service.send_notification(request)
        
        log.info(
            "notification_sent",
            notification_id=response.notificationId,
            status=response.status.value
        )
        
        return response
        
    except Exception as e:
        log.exception("send_notification_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/batch")
async def send_bulk_notifications(requests: List[NotificationRequest]):
    """
    Send multiple notifications in batch.
    
    Args:
        requests: List of notification requests
        
    Returns:
        List of notification responses
    """
    log = logger.bind(batch_size=len(requests))
    log.info("bulk_notification_requested")
    
    try:
        results = []
        for request in requests:
            response = await notification_service.send_notification(request)
            results.append(response)
        
        delivered = sum(1 for r in results if r.status.value == "DELIVERED")
        
        log.info(
            "bulk_notifications_complete",
            total=len(results),
            delivered=delivered
        )
        
        return {
            "total": len(results),
            "delivered": delivered,
            "failed": len(results) - delivered,
            "results": results
        }
        
    except Exception as e:
        log.exception("bulk_notification_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    unread_only: bool = Query(default=False)
):
    """
    Get user's notifications.
    
    Args:
        user_id: User ID
        limit: Max notifications to return
        unread_only: Only return unread
        
    Returns:
        List of notifications
    """
    log = logger.bind(user_id=user_id, limit=limit, unread_only=unread_only)
    log.debug("get_user_notifications_requested")
    
    try:
        notifications = await inapp_provider.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only
        )
        
        return NotificationListResponse(
            notifications=notifications,
            total=len(notifications),
            page=1,
            pageSize=limit
        )
        
    except Exception as e:
        log.exception("get_notifications_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str):
    """
    Mark notification as read.
    
    Args:
        notification_id: Notification ID
        user_id: User ID
        
    Returns:
        Success response
    """
    log = logger.bind(
        notification_id=notification_id,
        user_id=user_id
    )
    log.info("mark_notification_read_requested")
    
    try:
        success = await inapp_provider.mark_as_read(notification_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        log.info("notification_marked_read")
        return {"status": "SUCCESS", "notificationId": notification_id}
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception("mark_read_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/read-all")
async def mark_all_notifications_read(user_id: str):
    """
    Mark all user notifications as read.
    
    Args:
        user_id: User ID
        
    Returns:
        Success response with count
    """
    log = logger.bind(user_id=user_id)
    log.info("mark_all_notifications_read_requested")
    
    try:
        count = await inapp_provider.mark_all_as_read(user_id)
        
        log.info("all_notifications_marked_read", count=count)
        return {
            "status": "SUCCESS",
            "count": count,
            "userId": user_id
        }
        
    except Exception as e:
        log.exception("mark_all_read_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, user_id: str):
    """
    Delete a notification.
    
    Args:
        notification_id: Notification ID
        user_id: User ID
        
    Returns:
        Success response
    """
    log = logger.bind(notification_id=notification_id, user_id=user_id)
    log.info("delete_notification_requested")
    
    try:
        success = await inapp_provider.delete_notification(notification_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        log.info("notification_deleted")
        return {"status": "SUCCESS", "notificationId": notification_id}
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception("delete_notification_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """
    Get user notification preferences.
    
    Args:
        user_id: User ID
        
    Returns:
        User preferences
    """
    log = logger.bind(user_id=user_id)
    log.debug("get_user_preferences_requested")
    
    try:
        preferences = await database.get_user_preferences(user_id)
        
        if not preferences:
            # Return default preferences
            preferences = UserPreferences(userId=user_id)
        
        return preferences
        
    except Exception as e:
        log.exception("get_preferences_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """
    Update user notification preferences.
    
    Args:
        user_id: User ID
        preferences: New preferences
        
    Returns:
        Success response
    """
    log = logger.bind(user_id=user_id)
    log.info("update_user_preferences_requested")
    
    try:
        # Ensure user ID matches
        preferences.userId = user_id
        
        success = await database.update_user_preferences(preferences)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        log.info("user_preferences_updated")
        return {
            "status": "SUCCESS",
            "userId": user_id,
            "preferences": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception("update_preferences_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/unread-count/{user_id}")
async def get_unread_count(user_id: str):
    """
    Get unread notification count for user.
    
    Args:
        user_id: User ID
        
    Returns:
        Unread count
    """
    log = logger.bind(user_id=user_id)
    log.debug("get_unread_count_requested")
    
    try:
        count = await inapp_provider.get_unread_count(user_id)
        
        return {
            "userId": user_id,
            "unreadCount": count
        }
        
    except Exception as e:
        log.exception("get_unread_count_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
