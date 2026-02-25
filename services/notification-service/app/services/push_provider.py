"""
Push notification provider service.

Sends push notifications via Firebase (FCM) or APNS.
"""

import structlog
import httpx
from typing import Optional, Dict, Any

from app.models.events import PushNotificationRequest, PushNotificationResponse, DeliveryResult, DeliveryStatus
from app.config import settings

logger = structlog.get_logger(settings.SERVICE_NAME)


class PushProvider:
    """Send push notifications via FCM or APNS."""
    
    def __init__(self):
        self.firebase_api_key = settings.FIREBASE_API_KEY
        self.fcm_endpoint = "https://fcm.googleapis.com/fcm/send"
        self.apns_key_id = settings.APNS_KEY_ID
        self.apns_team_id = settings.APNS_TEAM_ID
        self.apns_key_path = settings.APNS_KEY_PATH
    
    async def send_push(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        imageUrl: Optional[str] = None
    ) -> DeliveryResult:
        """
        Send push notification.
        
        Args:
            device_token: Device token
            title: Notification title
            body: Notification body
            data: Optional data payload
            imageUrl: Optional image URL
            
        Returns:
            Delivery result
        """
        log = logger.bind(
            channel="PUSH",
            device_token=device_token[:10] + "..."
        )
        
        try:
            # Check if Firebase is configured
            if not self.firebase_api_key:
                log.warning("firebase_not_configured_simulating")
                return self._simulate_push(device_token, title, body, data)
            
            # Build FCM payload
            payload = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {}
            }
            
            if imageUrl:
                payload["notification"]["image"] = imageUrl
            
            # Send request
            headers = {
                "Authorization": f"key={self.firebase_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.fcm_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
            
            # Check FCM response
            if result.get("success", 0) > 0:
                message_id = result.get("results", [{}])[0].get("message_id")
                log.info(
                    "push_sent_successfully",
                    message_id=message_id
                )
                return DeliveryResult(
                    success=True,
                    status=DeliveryStatus.SUCCESS,
                    messageId=message_id,
                    retryable=False
                )
            else:
                error = result.get("results", [{}])[0].get("error")
                log.warning("push_failed", error=error)
                
                # Check if retryable
                retryable = error in ["Unavailable", "InternalServerError"]
                
                return DeliveryResult(
                    success=False,
                    status=DeliveryStatus.FAILED_TEMPORARY if retryable else DeliveryStatus.FAILED_PERMANENT,
                    errorMessage=error,
                    retryable=retryable
                )
                
        except httpx.HTTPError as e:
            log.exception("http_error", error=str(e))
            
            retryable = isinstance(e, (httpx.ConnectError, httpx.TimeoutException))
            
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_TEMPORARY if retryable else DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=retryable
            )
        except Exception as e:
            log.exception("push_send_error", error=str(e))
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=False
            )
    
    def _simulate_push(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """Simulate push notification for development."""
        log = logger.bind(
            channel="PUSH_SIMULATED",
            device_token=device_token[:10] + "..."
        )
        log.info(
            "push_simulated",
            title=title,
            body=body,
            data=data
        )
        
        # In production, this would actually send the push
        # For now, we simulate success
        message_id = f"sim-{id(device_token)}"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SUCCESS,
            messageId=message_id,
            retryable=False
        )
    
    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> DeliveryResult:
        """
        Send push to a topic.
        
        Args:
            topic: Topic name
            title: Notification title
            body: Notification body
            data: Optional data payload
            
        Returns:
            Delivery result
        """
        log = logger.bind(channel="PUSH_TOPIC", topic=topic)
        
        try:
            if not self.firebase_api_key:
                return self._simulate_push(topic, title, body, data)
            
            payload = {
                "to": f"/topics/{topic}",
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {}
            }
            
            headers = {
                "Authorization": f"key={self.firebase_api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.fcm_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
            
            success_count = result.get("success", 0)
            log.info(
                "topic_push_sent",
                topic=topic,
                success_count=success_count
            )
            
            return DeliveryResult(
                success=True,
                status=DeliveryStatus.SUCCESS,
                messageId=str(success_count),
                retryable=False
            )
            
        except Exception as e:
            log.exception("topic_push_error", error=str(e))
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=False
            )
