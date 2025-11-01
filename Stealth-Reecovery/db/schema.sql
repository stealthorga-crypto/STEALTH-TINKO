-- db/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
  id             TEXT PRIMARY KEY,
  order_id       TEXT NOT NULL,
  attempt_id     TEXT,
  customer_id    TEXT,
  event_type     TEXT NOT NULL,
  status         TEXT NOT NULL,
  failure_code   TEXT,
  failure_message TEXT,
  amount         INTEGER DEFAULT 0,
  currency       TEXT DEFAULT 'INR',
  raw_json       TEXT,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attempts (
  id                 TEXT PRIMARY KEY,
  order_id           TEXT NOT NULL,
  attempt_from_event TEXT,
  method             TEXT,
  strategy           TEXT,
  status             TEXT NOT NULL,
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_order ON events(order_id);
CREATE INDEX IF NOT EXISTS idx_attempts_order ON attempts(order_id);
