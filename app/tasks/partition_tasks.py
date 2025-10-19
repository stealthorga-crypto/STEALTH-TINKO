"""
Celery tasks for database partition management.
"""
from celery import shared_task
from datetime import datetime, timedelta
from app.db import get_db
import structlog

logger = structlog.get_logger(__name__)

@shared_task(name="create_monthly_partitions")
def create_monthly_partitions():
    """
    Create monthly partitions for high-volume tables.
    Runs on the 1st of each month to create next 3 months.
    """
    db = next(get_db())
    tables = ['failure_events', 'recovery_attempts', 'notification_logs']
    
    today = datetime.utcnow()
    months_ahead = 3
    
    for table in tables:
        for i in range(1, months_ahead + 1):
            target_date = today + timedelta(days=30 * i)
            partition_name = f"{table}_{target_date.strftime('%Y%m')}"
            
            # Check if partition exists
            result = db.execute(f"""
                SELECT 1 FROM pg_tables 
                WHERE tablename = '{partition_name}'
            """).fetchone()
            
            if not result:
                # Create partition
                start_date = target_date.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1)
                
                db.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name}
                    PARTITION OF {table}
                    FOR VALUES FROM ('{start_date}') TO ('{end_date}')
                """)
                
                logger.info("partition_created", 
                           table=table, 
                           partition=partition_name,
                           start=start_date,
                           end=end_date)
    
    db.close()
    return {"status": "completed", "tables": tables}

@shared_task(name="reconcile_transactions_daily")
def reconcile_transactions_daily():
    """
    Daily reconciliation task to verify transaction data integrity.
    """
    db = next(get_db())
    
    # Find transactions with recovery_attempts but no updates in 24h
    result = db.execute("""
        SELECT t.id, t.external_ref, t.status, COUNT(ra.id) as attempts
        FROM transactions t
        LEFT JOIN recovery_attempts ra ON ra.transaction_id = t.id
        WHERE t.status = 'failed'
        AND t.updated_at < NOW() - INTERVAL '24 hours'
        GROUP BY t.id
        HAVING COUNT(ra.id) > 0
    """).fetchall()
    
    logger.info("reconciliation_complete", 
               stale_transactions=len(result))
    
    db.close()
    return {"stale_transactions": len(result)}
