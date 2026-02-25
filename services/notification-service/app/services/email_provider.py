"""
Email provider service.

Sends emails via SMTP (or simulated for development).
"""

import structlog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from app.models.events import EmailRequest, EmailResponse, DeliveryResult, DeliveryStatus
from app.config import settings

logger = structlog.get_logger(settings.SERVICE_NAME)


class EmailProvider:
    """Send emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> DeliveryResult:
        """
        Send an email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            html: Optional HTML body
            
        Returns:
            Delivery result
        """
        log = logger.bind(
            channel="EMAIL",
            to=to,
            subject=subject
        )
        
        try:
            # Check if SMTP is configured
            if not self.smtp_user or not self.smtp_password:
                log.warning("smtp_not_configured_simulating")
                return self._simulate_email(to, subject, body)
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to
            
            # Add body
            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            message_id = f"<{datetime.utcnow().isoformat()}@{self.from_email}>"
            
            log.info(
                "email_sent_successfully",
                message_id=message_id
            )
            
            return DeliveryResult(
                success=True,
                status=DeliveryStatus.SUCCESS,
                messageId=message_id,
                retryable=False
            )
            
        except smtplib.SMTPException as e:
            log.exception("smtp_error", error=str(e))
            
            # Determine if retryable
            retryable = isinstance(e, (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError))
            
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_TEMPORARY if retryable else DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=retryable
            )
        except Exception as e:
            log.exception("email_send_error", error=str(e))
            return DeliveryResult(
                success=False,
                status=DeliveryStatus.FAILED_PERMANENT,
                errorMessage=str(e),
                retryable=False
            )
    
    def _simulate_email(
        self,
        to: str,
        subject: str,
        body: str
    ) -> DeliveryResult:
        """Simulate email sending for development."""
        log = logger.bind(channel="EMAIL_SIMULATED", to=to, subject=subject)
        log.info(
            "email_simulated",
            from_email=self.from_email,
            body_preview=body[:100]
        )
        
        # In production, this would actually send the email
        # For now, we simulate success
        message_id = f"<sim-{datetime.utcnow().isoformat()}@local>"
        
        return DeliveryResult(
            success=True,
            status=DeliveryStatus.SUCCESS,
            messageId=message_id,
            retryable=False
        )
    
    async def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> list[DeliveryResult]:
        """
        Send email to multiple recipients.
        
        Args:
            recipients: List of recipient emails
            subject: Email subject
            body: Email body
            html: Optional HTML body
            
        Returns:
            List of delivery results
        """
        log = logger.bind(channel="EMAIL_BULK", recipient_count=len(recipients))
        log.info("sending_bulk_emails")
        
        results = []
        for to in recipients:
            result = await self.send_email(to, subject, body, html)
            results.append(result)
        
        success_count = sum(1 for r in results if r.success)
        log.info(
            "bulk_emails_complete",
            total=len(recipients),
            successful=success_count
        )
        
        return results
