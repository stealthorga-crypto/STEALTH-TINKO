# app/routers/dev.py  (append)
from app.db import engine
from sqlalchemy import text
from fastapi import APIRouter

router = APIRouter(prefix="/_dev", tags=["_dev"])

@router.post("/bootstrap/recoveries")
def bootstrap_recoveries():
    sql = """
    CREATE TABLE IF NOT EXISTS recoveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        url TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        opened_at TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id)
    );
    """
    with engine.connect() as conn:
        conn.exec_driver_sql(sql)
    return {"ok": True, "created_or_exists": "recoveries"}

@router.get("/schema/recoveries")
def schema_recoveries():
    with engine.connect() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(recoveries)").all()
    return [{"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "dflt": r[4]} for r in rows]
