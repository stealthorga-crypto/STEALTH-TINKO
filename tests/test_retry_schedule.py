from datetime import datetime, timezone

from app.services.retry_schedule import compute_retry_schedule


class DummyPolicy:
    def __init__(self, initial_delay_minutes=60, backoff_multiplier=2, max_delay_minutes=1440):
        self.initial_delay_minutes = initial_delay_minutes
        self.backoff_multiplier = backoff_multiplier
        self.max_delay_minutes = max_delay_minutes


def test_compute_retry_schedule_exponential():
    now = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    p = DummyPolicy(initial_delay_minutes=10, backoff_multiplier=2, max_delay_minutes=1000)
    t0 = compute_retry_schedule(p, now, 0)
    t1 = compute_retry_schedule(p, now, 1)
    t2 = compute_retry_schedule(p, now, 2)
    assert (t0 - now).total_seconds() == 10 * 60
    assert (t1 - now).total_seconds() == 20 * 60
    assert (t2 - now).total_seconds() == 40 * 60


def test_compute_retry_schedule_caps_at_max():
    now = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    p = DummyPolicy(initial_delay_minutes=100, backoff_multiplier=10, max_delay_minutes=250)
    # attempt_index 1 would be 1000 minutes, but cap is 250
    t = compute_retry_schedule(p, now, 1)
    assert (t - now).total_seconds() == 250 * 60


def test_compute_retry_schedule_naive_now_assumes_utc():
    now = datetime(2025, 1, 1, 0, 0)  # naive
    p = DummyPolicy(initial_delay_minutes=5, backoff_multiplier=1, max_delay_minutes=10)
    t = compute_retry_schedule(p, now, 0)
    assert t.tzinfo is not None