"""
Notification service.

Orchestrates notification delivery across multiple channels.
"""

import structlog
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.events import (
    Notification,
    NotificationRequest,
    NotificationResponse,
    NotificationChannel,
    NotificationType,
    NotificationStatus,
    DeliveryResult,
    DeliveryStatus
)
from app.services.email_provider import EmailProvider
from app.services.push_provider import PushProvider
from app.services.inapp_provider import InAppProvider
from app.services.delivery_tracker import DeliveryTracker
from app.repositories import database
from app.config import settings

logger = structlog.get_logger(settings.SERVICE_NAME)


class NotificationService:
    """Orchestrate notification delivery."""
    
    def __init__(self):
        self.email_provider = EmailProvider()
        self.push_provider = PushProvider()
        self.inapp_provider = InAppProvider()
        self.delivery_tracker = DeliveryTracker()
    
    async def send_notification(
        self,
        request: NotificationRequest
    ) -> NotificationResponse:
        """
        Send a notification via specified channel.
        
        Args:
            request: Notification request
            
        Returns:
            Notification response
        """
        log = logger.bind(
            user_id=request.userId,
            channel=request.channel.value,
            notification_type=request.type.value
        )
        
        log.info("sending_notification")
        
        # Create notification record
        notification = Notification(
            userId=request.userId,
            taskId=request.taskId,
            reminderId=request.reminderId,
            channel=request.channel,
            type=request.type,
            title=request.title,
            message=request.message,
            status=NotificationStatus.PENDING,
            metadata=request.metadata
        )
        
        # Save to database
        await database.save_notification(notification)
        log = log.bind(notification_id=notification.notificationId)
        
        # Send via appropriate channel
        try:
            if request.channel == NotificationChannel.EMAIL:
                result = await self._send_email(notification, request)
            elif request.channel == NotificationChannel.PUSH:
                result = await self._send_push(notification, request)
            elif request.channel == NotificationChannel.IN_APP:
                result = await self._send_inapp(notification, request)
            else:
                raise ValueError(f"Unknown channel: {request.channel}")
            
            # Track delivery
            await self.delivery_tracker.track_delivery(
                notification_id=notification.notificationId,
                result=result
            )
            
            # Update status
            if result.success:
                notification.status = NotificationStatus.DELIVERED
                notification.deliveredAt = datetime.utcnow()
                log.info(
                    "notification_delivered",
                    message_id=result.messageId,
                    channel=request.channel.value
                )
            else:
                notification.status = NotificationStatus.FAILED
                log.warning(
                    "notification_failed",
                    error=result.errorMessage,
                    retryable=result.retryable
                )
            
            await database.update_notification(notification)
            
            return NotificationResponse(
                notificationId=notification.notificationId,
                status=notification.status,
                sentAt=notification.sentAt,
                messageId=result.messageId
            )
            
        except Exception as e:
            log.exception("notification_error", error=str(e))
            
            notification.status = NotificationStatus.FAILED
            await database.update_notification(notification)
            
            return NotificationResponse(
                notificationId=notification.notificationId,
                status=NotificationStatus.FAILED,
                sentAt=None
            )
    
    async def _send_email(
        self,
        notification: Notification,
        request: NotificationRequest
    ) -> DeliveryResult:
        """Send email notification."""
        log = logger.bind(
            notification_id=notification.notificationId,
            channel="EMAIL"
        )
        
        # Get user email (from database or service)
        user_email = await database.get_user_email(notification.userId)
        
        if not user_email:
            log.warning("user_email_not_found")
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage="User email not found",
                retryable=False
            )
        
        # Send email
        result = await self.email_provider.send_email(
            to=user_email,
            subject=notification.title,
            body=notification.message
        )
        
        log.info(
            "email_sent" if result.success else "email_failed",
            to=user_email,
            message_id=result.messageId
        )
        
        return result
    
    async def _send_push(
        self,
        notification: Notification,
        request: NotificationRequest
    ) -> DeliveryResult:
        """Send push notification."""
        log = logger.bind(
            notification_id=notification.notificationId,
            channel="PUSH"
        )
        
        # Get user device tokens
        device_tokens = await database.get_user_device_tokens(notification.userId)
        
        if not device_tokens:
            log.warning("no_device_tokens_found")
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage="No device tokens found",
                retryable=False
            )
        
        # Send push to all devices
        results = []
        for token in device_tokens:
            result = await self.push_provider.send_push(
                device_token=token,
                title=notification.title,
                body=notification.message,
                data={
                    "notificationId": notification.notificationId,
                    "taskId": notification.taskId,
                    "type": notification.type.value
                }
            )
            results.append(result)
        
        # Consider success if at least one device received
        success = any(r.success for r in results)
        message_id = next((r.messageId for r in results if r.success), None)
        
        log.info(
            "push_sent" if success else "push_failed",
            devices=len(device_tokens),
            successful=sum(1 for r in results if r.success)
        )
        
        return DeliveryResult(
            success=success,
            status=DeliveryStatus.SUCCESS if success else DeliveryStatus.FAILED_PERMANENT,
            messageId=message_id,
            retryable=False
        )
    
    async def _send_inapp(
        self,
        notification: Notification,
        request: NotificationRequest
    ) -> DeliveryResult:
        """Send in-app notification."""
        log = logger.bind(
            notification_id=notification.notificationId,
            channel="IN_APP"
        )
        
        # Store in-app notification
        result = await self.inapp_provider.store_notification(
            user_id=notification.userId,
            notification=notification
        )
        
        log.info(
            "inapp_notification_stored" if result.success else "inapp_storage_failed",
            user_id=notification.userId
        )
        
        return result
    
    async def send_bulk_notifications(
        self,
        requests: list[NotificationRequest]
    ) -> list[NotificationResponse]:
        """
        Send multiple notifications in batch.
        
        Args:
            requests: List of notification requests
            
        Returns:
            List of notification responses
        """
        log = logger.bind(batch_size=len(requests))
        log.info("sending_bulk_notifications")
        
        results = []
        for request in requests:
            response = await self.send_notification(request)
            results.append(response)
        
        log.info(
            "bulk_notifications_complete",
            total=len(results),
            delivered=sum(1 for r in results if r.status == NotificationStatus.DELIVERED)
        )
        
        return results


# Singleton instance
notification_service = NotificationService()
