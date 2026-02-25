"""
Delivery tracker service.

Tracks notification delivery status and metrics.
"""

import structlog
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.events import DeliveryResult, DeliveryStatus, NotificationStatus
from app.config import settings

logger = structlog.get_logger(settings.SERVICE_NAME)


class DeliveryTracker:
    """Track notification delivery metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "by_channel": {},
            "by_type": {}
        }
    
    async def track_delivery(
        self,
        notification_id: str,
        result: DeliveryResult
    ):
        """
        Track delivery result.
        
        Args:
            notification_id: Notification ID
            result: Delivery result
        """
        log = logger.bind(
            notification_id=notification_id,
            success=result.success
        )
        
        # Update metrics
        self.metrics["total_sent"] += 1
        
        if result.success:
            self.metrics["total_delivered"] += 1
            log.info("delivery_tracked_success")
        else:
            self.metrics["total_failed"] += 1
            log.warning(
                "delivery_tracked_failure",
                error=result.errorMessage,
                retryable=result.retryable
            )
        
        # Log delivery attempt
        await self._log_delivery_attempt(notification_id, result)
    
    async def _log_delivery_attempt(
        self,
        notification_id: str,
        result: DeliveryResult
    ):
        """Log delivery attempt to database."""
        try:
            # In production, save to database
            # await database.save_delivery_log(...)
            pass
        except Exception as e:
            logger.exception("delivery_log_error", error=str(e))
    
    async def track_retry(
        self,
        notification_id: str,
        attempt: int,
        max_retries: int
    ):
        """
        Track retry attempt.
        
        Args:
            notification_id: Notification ID
            attempt: Current attempt number
            max_retries: Maximum retries
        """
        log = logger.bind(
            notification_id=notification_id,
            attempt=attempt,
            max_retries=max_retries
        )
        
        if attempt <= max_retries:
            log.info("retry_scheduled")
        else:
            log.warning("max_retries_exceeded")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get delivery metrics.
        
        Returns:
            Metrics dictionary
        """
        total = self.metrics["total_sent"]
        delivery_rate = (
            self.metrics["total_delivered"] / total * 100
            if total > 0 else 0
        )
        
        return {
            **self.metrics,
            "delivery_rate_percent": round(delivery_rate, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "by_channel": {},
            "by_type": {}
        }
        logger.info("metrics_reset")


# Singleton instance
delivery_tracker = DeliveryTracker()
