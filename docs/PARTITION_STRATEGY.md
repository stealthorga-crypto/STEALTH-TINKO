# Database Partition Strategy

## High-Volume Tables

### 1. failure_events
- **Partition By**: created_at (monthly)
- **Retention**: 24 months
- **Strategy**: Range partitioning on timestamp
- **Auto-creation**: Celery Beat task creates next 3 months

### 2. recovery_attempts
- **Partition By**: created_at (monthly)
- **Retention**: 12 months
- **Strategy**: Range partitioning on timestamp
- **Auto-creation**: Celery Beat task creates next 3 months

### 3. notification_logs
- **Partition By**: sent_at (monthly)
- **Retention**: 6 months
- **Strategy**: Range partitioning on timestamp
- **Auto-creation**: Celery Beat task creates next 3 months

## Implementation Plan

1. Create base partition tables
2. Migrate existing data to first partition
3. Set up Celery Beat task for auto-partition creation
4. Configure partition pruning for old data

## Reconciliation Tasks

### Daily Reconciliation
- Verify transaction status with PSPs
- Match recovery_attempts to transactions
- Flag orphaned records

### Weekly Reconciliation
- Aggregate success rates by org
- Compare expected vs actual recovery amounts
- Generate reconciliation reports
