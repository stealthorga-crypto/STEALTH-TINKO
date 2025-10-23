from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy import text

from app.db import engine


def _month_bounds(dt: datetime):
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


essential_notice = "Partition attach skipped (parent may not be partitioned)."


def ensure_current_month_partitions() -> List[str]:
    """Ensure current and next month partitions exist for transactions.

    - Postgres: create child tables and attempt ATTACH PARTITION (if parent is partitioned).
    - Other dialects (e.g., SQLite): no-op.

    Returns a list of partition table names touched/ensured.
    """
    created: List[str] = []
    dialect = engine.dialect.name
    if dialect != "postgresql":
        return created

    now = datetime.now(timezone.utc)
    months = [now, (now.replace(day=28) + timedelta(days=4))]

    with engine.begin() as conn:
        for m in months:
            start, end = _month_bounds(m)
            suffix = f"y{start.year}m{start.month:02d}"
            part_table = f"transactions_{suffix}"
            sql = f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = '{part_table}' AND n.nspname = 'public'
                ) THEN
                    EXECUTE 'CREATE TABLE public.{part_table} (LIKE public.transactions INCLUDING ALL)';
                END IF;
                BEGIN
                    EXECUTE 'ALTER TABLE public.transactions ATTACH PARTITION public.{part_table} FOR VALUES FROM (\"{start.isoformat()}\") TO (\"{end.isoformat()}\")';
                EXCEPTION WHEN others THEN
                    RAISE NOTICE '{essential_notice}';
                END;
            END $$;
            """
            conn.execute(text(sql))
            created.append(part_table)

    return created
