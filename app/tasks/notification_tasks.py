"""
Notification tasks for sending recovery notifications via email, SMS, WhatsApp.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.worker import celery_app
from app.db import SessionLocal
from app.models import RecoveryAttempt, NotificationLog
from app.logging_config import get_logger

logger = get_logger(__name__)


def send_email_notification(
    recipient: str,
    subject: str,
    body: str,
    recovery_attempt_id: int
) -> NotificationLog:
    """
    Send email notification via SMTP.
    
    Args:
        recipient: Email address
        subject: Email subject
        body: Email body (HTML)
        recovery_attempt_id: Recovery attempt ID for logging
        
    Returns:
        NotificationLog entry
    """
    db: Session = SessionLocal()
    log = NotificationLog(
        recovery_attempt_id=recovery_attempt_id,
        channel='email',
        recipient=recipient,
        status='pending',
        provider='smtp'
    )
    db.add(log)
    db.commit()
    
    try:
        # In development, allow dry-run to avoid real SMTP dependency
        if os.getenv('SMTP_ENABLE', '0') != '1':
            log.status = 'sent'
            log.provider = 'smtp-dryrun'
            log.sent_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(
                "email_sent_dryrun",
                recipient=recipient,
                notification_log_id=log.id,
                recovery_attempt_id=recovery_attempt_id
            )
            return log

        smtp_host = os.getenv('SMTP_HOST', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', '1025'))
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        smtp_from = os.getenv('SMTP_FROM', 'noreply@stealth-recovery.dev')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_from
        msg['To'] = recipient
        
        # Add HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Send via SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        # Update log
        log.status = 'sent'
        log.sent_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(
            "email_sent",
            recipient=recipient,
            notification_log_id=log.id,
            recovery_attempt_id=recovery_attempt_id
        )
        
        return log
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)[:512]
        log.failed_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.error(
            "email_send_failed",
            recipient=recipient,
            notification_log_id=log.id,
            exc_info=e
        )
        raise
    finally:
        db.close()


def send_sms_notification(
    phone_number: str,
    message: str,
    recovery_attempt_id: int
) -> NotificationLog:
    """
    Send SMS notification via Twilio.
    
    Args:
        phone_number: Phone number with country code
        message: SMS message text
        recovery_attempt_id: Recovery attempt ID for logging
        
    Returns:
        NotificationLog entry
    """
    db: Session = SessionLocal()
    log = NotificationLog(
        recovery_attempt_id=recovery_attempt_id,
        channel='sms',
        recipient=phone_number,
        status='pending',
        provider='twilio'
    )
    db.add(log)
    db.commit()
    
    try:
        # Check if Twilio is configured
        twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_from = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_from]):
            raise ValueError("Twilio credentials not configured")
        
        # Import Twilio (optional dependency)
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("twilio package not installed. Run: pip install twilio")
        
        # Send SMS
        client = Client(twilio_account_sid, twilio_auth_token)
        message_response = client.messages.create(
            body=message,
            from_=twilio_from,
            to=phone_number
        )
        
        # Update log
        log.status = 'sent'
        log.provider_message_id = message_response.sid
        log.sent_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(
            "sms_sent",
            phone_number=phone_number,
            notification_log_id=log.id,
            twilio_sid=message_response.sid
        )
        
        return log
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)[:512]
        log.failed_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.error(
            "sms_send_failed",
            phone_number=phone_number,
            notification_log_id=log.id,
            exc_info=e
        )
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.notification_tasks.send_recovery_notification')
def send_recovery_notification(attempt_id: int):
    """
    Send recovery notification based on attempt configuration.
    
    Args:
        attempt_id: Recovery attempt ID
    """
    db: Session = SessionLocal()
    try:
        attempt = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.id == attempt_id
        ).first()
        
        if not attempt:
            logger.warning("notification_failed", reason="attempt_not_found", attempt_id=attempt_id)
            return {"status": "not_found", "attempt_id": attempt_id}
        
        # Build recovery link
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        recovery_link = f"{base_url}/pay/{attempt.token}"
        
        # PSP-001: Get payment link from transaction if available
        from app.models import Transaction
        transaction = None
        payment_link = recovery_link  # Default to recovery link
        
        if attempt.transaction_ref:
            transaction = db.query(Transaction).filter(
                Transaction.transaction_ref == attempt.transaction_ref
            ).first()
            
            # Use Stripe payment link if available
            if transaction and transaction.payment_link_url:
                payment_link = transaction.payment_link_url
                logger.info(
                    "using_stripe_payment_link",
                    attempt_id=attempt_id,
                    transaction_ref=attempt.transaction_ref,
                    payment_link=payment_link
                )
        
        # Update retry tracking
        attempt.retry_count += 1
        attempt.last_retry_at = datetime.now(timezone.utc)
        
        # Send based on channel
        if attempt.channel == 'email':
            # Get recipient email from transaction or use placeholder
            recipient = "customer@example.com"  # Default
            if transaction and transaction.customer_email:
                recipient = transaction.customer_email
            
            # Build formatted amount if available
            amount_display = ""
            if transaction and transaction.amount and transaction.currency:
                amount_formatted = f"{transaction.amount / 100:.2f}"
                currency_upper = transaction.currency.upper()
                amount_display = f"<p><strong>Amount:</strong> {currency_upper} {amount_formatted}</p>"
            
            subject = "Complete Your Payment"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Payment Recovery</h2>
                <p>We noticed your recent payment couldn't be completed.</p>
                {amount_display}
                <p>Click the button below to complete your payment securely:</p>
                <div style="margin: 30px 0;">
                    <a href="{payment_link}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Complete Payment
                    </a>
                </div>
                <p style="color: #64748b; font-size: 14px;">
                    This link expires in 7 days. If you have questions, please contact our support team.
                </p>
                <p style="color: #94a3b8; font-size: 12px; margin-top: 40px;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </body>
            </html>
            """
            
            log = send_email_notification(recipient, subject, body, attempt_id)
            attempt.status = 'sent'
            
        elif attempt.channel == 'sms':
            # Get recipient phone from transaction or use placeholder
            phone_number = "+1234567890"  # Default
            if transaction and transaction.customer_phone:
                phone_number = transaction.customer_phone
            
            # Build SMS message with payment link
            message = f"Complete your payment: {payment_link}"
            if transaction and transaction.amount and transaction.currency:
                amount_formatted = f"{transaction.amount / 100:.2f}"
                currency_upper = transaction.currency.upper()
                message = f"Complete your {currency_upper} {amount_formatted} payment: {payment_link}"
            
            log = send_sms_notification(phone_number, message, attempt_id)
            attempt.status = 'sent'
            
        elif attempt.channel == 'whatsapp':
            # TODO: Implement WhatsApp Business API
            logger.warning(
                "whatsapp_not_implemented",
                attempt_id=attempt_id
            )
            log = None
            attempt.status = 'created'  # Keep in created state
        
        db.commit()
        
        logger.info(
            "recovery_notification_sent",
            attempt_id=attempt_id,
            channel=attempt.channel,
            retry_count=attempt.retry_count
        )
        
        # Schedule next retry if needed
        from app.tasks.retry_tasks import schedule_retry
        if attempt.status != 'completed' and (attempt.retry_count < attempt.max_retries):
            schedule_retry.delay(attempt_id)
        result_status = 'sent' if attempt.status == 'sent' else ('skipped' if attempt.channel == 'whatsapp' else attempt.status)
        # Return both keys for backward-compat, but prefer 'log_id' per API contract
        log_id = getattr(log, 'id', None)
        return {"status": result_status, "attempt_id": attempt_id, "log_id": log_id, "notification_log_id": log_id}
        
    except Exception as e:
        logger.error(
            "recovery_notification_failed",
            attempt_id=attempt_id,
            exc_info=e
        )
        db.rollback()
        return {"status": "error", "attempt_id": attempt_id, "error": str(e)[:256]}
    finally:
        db.close()


@celery_app.task(name='app.tasks.notification_tasks.check_delivery_status')
def check_delivery_status(notification_log_id: int):
    """
    Check delivery status for a notification (e.g., via Twilio webhook).
    
    Args:
        notification_log_id: Notification log ID
    """
    db: Session = SessionLocal()
    try:
        log = db.query(NotificationLog).filter(
            NotificationLog.id == notification_log_id
        ).first()
        
        if not log:
            logger.warning("delivery_check_failed", reason="log_not_found", log_id=notification_log_id)
            return
        
        # Check status based on provider
        if log.provider == 'twilio' and log.provider_message_id:
            try:
                from twilio.rest import Client
                client = Client(
                    os.getenv('TWILIO_ACCOUNT_SID'),
                    os.getenv('TWILIO_AUTH_TOKEN')
                )
                message = client.messages(log.provider_message_id).fetch()
                
                if message.status == 'delivered':
                    log.status = 'delivered'
                    log.delivered_at = datetime.now(timezone.utc)
                elif message.status in ['failed', 'undelivered']:
                    log.status = 'failed'
                    log.error_message = message.error_message
                    log.failed_at = datetime.now(timezone.utc)
                
                db.commit()
                
                logger.info(
                    "delivery_status_updated",
                    log_id=notification_log_id,
                    status=log.status,
                    provider_status=message.status
                )
                
            except Exception as e:
                logger.error("twilio_status_check_failed", log_id=notification_log_id, exc_info=e)
        
    except Exception as e:
        logger.error("delivery_check_failed", log_id=notification_log_id, exc_info=e)
    finally:
        db.close()
