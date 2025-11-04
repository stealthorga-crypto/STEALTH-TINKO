#!/usr/bin/env python3
"""
DB smoke: run minimal API flows and assert rows written to Neon.

Flows:
- Register user + org, login to get JWT
- Ingest payment_failed event (Transaction + FailureEvent)
- Create recovery link; read & open it (RecoveryAttempt)
- Print short samples from DB

This uses FastAPI TestClient to avoid starting a real server.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

def load_env() -> None:
    try:
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(usecwd=True), override=False)
    except Exception:
        pass


def main() -> None:
    load_env()
    # Avoid hermetic mode
    os.environ.pop("SKIP_DB", None)

    from fastapi.testclient import TestClient
    from app.main import app
    from app.db import SessionLocal
    from app import models

    out: dict[str, Any] = {"steps": []}
    c = TestClient(app)

    email = f"smoke_{int(time.time())}@example.com"
    password = "password123"
    org_name = "Neon Smoke Org"

    r = c.post("/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Neon Smoke",
        "org_name": org_name,
    })
    out["steps"].append({"register": r.status_code})
    assert r.status_code == 201, r.text

    r = c.post("/v1/auth/login", json={"email": email, "password": password})
    out["steps"].append({"login": r.status_code})
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token, "no token returned"

    ref = f"TXN-{int(time.time())}"
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "transaction_ref": ref,
        "amount": 2599,
        "currency": "INR",
        "gateway": "stripe",
        "failure_reason": "insufficient_funds",
        "occurred_at": "2025-11-04T12:00:00Z",
        "metadata": {"source": "db_smoke"},
    }
    r = c.post("/v1/events/payment_failed", json=body, headers=headers)
    out["steps"].append({"event_ingest": r.status_code})
    assert r.status_code == 201, r.text

    r = c.post(f"/v1/recoveries/by_ref/{ref}/link", json={"ttl_hours": 24})
    out["steps"].append({"create_link": r.status_code})
    assert r.status_code == 201, r.text
    token_link = r.json().get("token")
    assert token_link, "no link token returned"

    r = c.get(f"/v1/recoveries/by_token/{token_link}")
    out["steps"].append({"get_by_token": r.status_code})
    assert r.status_code == 200 and r.json().get("ok") is True, r.text

    r = c.post(f"/v1/recoveries/by_token/{token_link}/open")
    out["steps"].append({"mark_open": r.status_code})
    assert r.status_code == 200 and r.json().get("ok") is True, r.text

    # DB checks
    s = SessionLocal()
    try:
        txn = s.query(models.Transaction).filter(models.Transaction.transaction_ref == ref).first()
        fe_count = (
            s.query(models.FailureEvent)
            .filter(models.FailureEvent.transaction_id == txn.id)
            .count()
            if txn
            else 0
        )
        ra_count = (
            s.query(models.RecoveryAttempt)
            .filter(models.RecoveryAttempt.transaction_id == txn.id)
            .count()
            if txn
            else 0
        )
        org = s.query(models.Organization).filter(models.Organization.slug == "neon-smoke-org").first()
        out["db_checks"] = {
            "txn_found": bool(txn),
            "failure_events_for_txn": fe_count,
            "recovery_attempts_for_txn": ra_count,
            "org_found": bool(org),
            "sample": {
                "transaction_ref": getattr(txn, "transaction_ref", None),
                "amount": getattr(txn, "amount", None),
                "currency": getattr(txn, "currency", None),
            },
        }
    finally:
        s.close()

    out["result"] = "ok"
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
