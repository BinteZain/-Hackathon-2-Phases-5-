"""
In-app notification provider service.

Stores notifications for in-app display.
"""

import structlog
from datetime import datetime
from typing import Optional, List

from app.models.events import Notification, DeliveryResult, DeliveryStatus
from app.repositories import database
from app.config import settings

logger = structlog.get_logger(settings.SERVICE_NAME)


class InAppProvider:
    """Store and manage in-app notifications."""
    
    async def store_notification(
        self,
        user_id: str,
        notification: Notification
    ) -> DeliveryResult:
        """
        Store in-app notification.
        
        Args:
            user_id: User ID
            notification: Notification to store
            
        Returns:
            Delivery result
        """
        log = logger.bind(
            channel="IN_APP",
            user_id=user_id,
            notification_id=notification.notificationId
        )
        
        try:
            # Save to database
            await database.save_notification(notification)
            
            log.info(
                "inapp_notification_stored",
                type=notification.type.value,
                title=notification.title
            )
            
            return DeliveryResult(
                success=True,
                status=DeliveryStatus.SUCCESS,
                messageId=notification.notificationId,
                retryable=False
            )
            
        except Exception as e:
            log.exception("inapp_storage_error", error=str(e))
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=True
            )
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get user's notifications.
        
        Args:
            user_id: User ID
            limit: Max notifications to return
            unread_only: Only return unread notifications
            
        Returns:
            List of notifications
        """
        log = logger.bind(
            channel="IN_APP",
            user_id=user_id
        )
        
        try:
            notifications = await database.get_user_notifications(
                user_id=user_id,
                limit=limit,
                unread_only=unread_only
            )
            
            log.debug(
                "retrieved_user_notifications",
                count=len(notifications)
            )
            
            return notifications
            
        except Exception as e:
            log.exception("get_notifications_error", error=str(e))
            return []
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        log = logger.bind(
            channel="IN_APP",
            notification_id=notification_id,
            user_id=user_id
        )
        
        try:
            await database.mark_notification_read(notification_id, user_id)
            
            log.info("notification_marked_read")
            return True
            
        except Exception as e:
            log.exception("mark_read_error", error=str(e))
            return False
    
    async def mark_all_as_read(
        self,
        user_id: str
    ) -> int:
        """
        Mark all user notifications as read.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        log = logger.bind(channel="IN_APP", user_id=user_id)
        
        try:
            count = await database.mark_all_notifications_read(user_id)
            
            log.info("all_notifications_marked_read", count=count)
            return count
            
        except Exception as e:
            log.exception("mark_all_read_error", error=str(e))
            return 0
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        log = logger.bind(
            channel="IN_APP",
            notification_id=notification_id
        )
        
        try:
            await database.delete_notification(notification_id, user_id)
            
            log.info("notification_deleted")
            return True
            
        except Exception as e:
            log.exception("delete_notification_error", error=str(e))
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """
        Get unread notification count for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Unread count
        """
        try:
            count = await database.get_unread_count(user_id)
            return count
        except Exception as e:
            logger.exception("get_unread_count_error", error=str(e))
            return 0
