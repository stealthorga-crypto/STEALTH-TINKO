"""
Retry logic tasks for processing failed payment recoveries.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.worker import celery_app
from app.db import SessionLocal
from app.models import RecoveryAttempt, RetryPolicy, Organization
from app.logging_config import get_logger

logger = get_logger(__name__)


def calculate_next_retry(
    attempt: RecoveryAttempt,
    policy: RetryPolicy
) -> Optional[datetime]:
    """
    Calculate next retry time using exponential backoff.
    
    Args:
        attempt: Recovery attempt to calculate retry for
        policy: Retry policy configuration
        
    Returns:
        Next retry datetime or None if max retries exceeded
    """
    if attempt.retry_count >= policy.max_retries:
        return None
    
    # Exponential backoff: initial_delay * (multiplier ^ retry_count)
    delay_minutes = min(
        policy.initial_delay_minutes * (policy.backoff_multiplier ** attempt.retry_count),
        policy.max_delay_minutes
    )
    
    return datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)


@celery_app.task(name='app.tasks.retry_tasks.process_retry_queue')
def process_retry_queue():
    """
    Process all recovery attempts that are due for retry.
    Runs every minute via Celery Beat.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Find all attempts due for retry
        attempts_to_retry = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.status.in_(['created', 'sent']),
            RecoveryAttempt.next_retry_at <= now,
            RecoveryAttempt.retry_count < RecoveryAttempt.max_retries,
            RecoveryAttempt.expires_at > now
        ).all()
        
        logger.info(
            "retry_queue_processing",
            attempts_found=len(attempts_to_retry),
            current_time=now.isoformat()
        )
        
        for attempt in attempts_to_retry:
            # Dispatch notification task for each channel
            from app.tasks.notification_tasks import send_recovery_notification
            send_recovery_notification.delay(attempt.id)
            
            logger.info(
                "retry_scheduled",
                attempt_id=attempt.id,
                retry_count=attempt.retry_count + 1,
                channel=attempt.channel
            )
        
        return {
            'processed': len(attempts_to_retry),
            'timestamp': now.isoformat()
        }
        
    except Exception as e:
        logger.error("retry_queue_processing_failed", exc_info=e)
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.retry_tasks.schedule_retry')
def schedule_retry(attempt_id: int, org_id: Optional[int] = None):
    """
    Schedule next retry for a recovery attempt.
    
    Args:
        attempt_id: Recovery attempt ID
        org_id: Organization ID (for policy lookup)
    """
    db: Session = SessionLocal()
    try:
        attempt = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.id == attempt_id
        ).first()
        
        if not attempt:
            logger.warning("retry_schedule_failed", reason="attempt_not_found", attempt_id=attempt_id)
            return
        
        # Get retry policy (default if none configured)
        policy = None
        if org_id:
            policy = db.query(RetryPolicy).filter(
                RetryPolicy.org_id == org_id,
                RetryPolicy.is_active == True
            ).first()
        
        if not policy:
            # Create default policy
            policy = RetryPolicy(
                org_id=org_id or 0,
                name="Default Policy",
                max_retries=3,
                initial_delay_minutes=60,
                backoff_multiplier=2,
                max_delay_minutes=1440,
                enabled_channels=["email"],
                is_active=True
            )
        
        # Calculate next retry time
        next_retry = calculate_next_retry(attempt, policy)
        
        if next_retry:
            attempt.next_retry_at = next_retry
            attempt.max_retries = policy.max_retries
            db.commit()
            
            logger.info(
                "retry_scheduled",
                attempt_id=attempt_id,
                next_retry_at=next_retry.isoformat(),
                retry_count=attempt.retry_count,
                max_retries=policy.max_retries
            )
        else:
            # Max retries exceeded, mark as cancelled
            attempt.status = 'cancelled'
            db.commit()
            
            logger.info(
                "retry_cancelled",
                attempt_id=attempt_id,
                reason="max_retries_exceeded",
                retry_count=attempt.retry_count
            )
        
    except Exception as e:
        logger.error("retry_schedule_failed", attempt_id=attempt_id, exc_info=e)
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.retry_tasks.cleanup_expired_attempts')
def cleanup_expired_attempts():
    """
    Clean up expired recovery attempts.
    Runs daily at 2 AM via Celery Beat.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Find expired attempts that aren't already cancelled
        expired_attempts = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.expires_at < now,
            RecoveryAttempt.status.in_(['created', 'sent', 'opened'])
        ).all()
        
        count = 0
        for attempt in expired_attempts:
            attempt.status = 'expired'
            count += 1
        
        db.commit()
        
        logger.info(
            "cleanup_completed",
            expired_count=count,
            timestamp=now.isoformat()
        )
        
        return {'expired_count': count, 'timestamp': now.isoformat()}
        
    except Exception as e:
        logger.error("cleanup_failed", exc_info=e)
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.retry_tasks.update_retry_policy')
def update_retry_policy(org_id: int, policy_config: dict):
    """
    Update or create retry policy for an organization.
    
    Args:
        org_id: Organization ID
        policy_config: Policy configuration dict
    """
    db: Session = SessionLocal()
    try:
        policy = db.query(RetryPolicy).filter(
            RetryPolicy.org_id == org_id,
            RetryPolicy.is_active == True
        ).first()
        
        if policy:
            # Update existing policy
            for key, value in policy_config.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
        else:
            # Create new policy
            policy = RetryPolicy(org_id=org_id, **policy_config)
            db.add(policy)
        
        db.commit()
        
        logger.info(
            "retry_policy_updated",
            org_id=org_id,
            policy_id=policy.id,
            max_retries=policy.max_retries
        )
        
        return {'policy_id': policy.id, 'org_id': org_id}
        
    except Exception as e:
        logger.error("retry_policy_update_failed", org_id=org_id, exc_info=e)
        db.rollback()
        raise
    finally:
        db.close()
