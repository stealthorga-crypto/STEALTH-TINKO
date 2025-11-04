#!/usr/bin/env python3
"""
Schema ensure/planner for Neon Postgres.

- Loads .env and uses DATABASE_URL.
- Verifies Postgres and sslmode=require.
- Reflects current DB and compares with SQLAlchemy models (app.models via app.db.Base).
  - Missing tables: plan create via Base.metadata.create_all(tables=[...]).
  - Missing columns: plan Alembic autogenerate to add columns safely.
  - Indexes/constraints: recommend autogenerate (we rely on Alembic for these).
- Emits a JSON plan with actions. With --apply, performs actions idempotently and runs Alembic
  autogenerate + upgrade when column/constraint diffs are detected.

Usage:
  python scripts/db_ensure.py --plan
  python scripts/db_ensure.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import Engine


def load_env() -> None:
    try:
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(usecwd=True), override=False)
    except Exception:
        pass


def build_engine_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        print("ERROR: DATABASE_URL is not set in environment/.env", file=sys.stderr)
        sys.exit(2)
    parsed = urlparse(url)
    if not parsed.scheme.startswith("postgresql"):
        print(f"ERROR: Unsupported scheme '{parsed.scheme}'. Postgres/Neon required.", file=sys.stderr)
        sys.exit(2)
    if "sslmode=" not in url and parsed.scheme.startswith("postgresql"):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


def get_model_metadata() -> Any:
    # Import model Base and register tables by importing models
    from app.db import Base  # type: ignore
    import app.models  # noqa: F401
    return Base.metadata


@dataclass
class Plan:
    created_tables: List[str]
    missing_columns: Dict[str, List[Dict[str, Any]]]
    notes: List[str]
    will_generate_migration: bool


def diff_schema(engine: Engine, model_md: Any) -> Plan:
    inspector = inspect(engine)
    # Prefer explicit public schema for Neon
    existing_tables = set(inspector.get_table_names(schema="public"))
    if not existing_tables:
        existing_tables = set(inspector.get_table_names())

    model_tables = set(model_md.tables.keys())

    missing_tables = sorted(list(model_tables - existing_tables))

    missing_columns: Dict[str, List[Dict[str, Any]]] = {}
    for tname in sorted(list(model_tables & existing_tables)):
        # columns in DB (names)
        db_cols = {c["name"] for c in inspector.get_columns(tname, schema="public")}
        # model columns
        mt = model_md.tables[tname]
        mcols = {c.name: c for c in mt.columns}
        for cname, col in mcols.items():
            if cname not in db_cols:
                # Basic type name string for reporting
                coltype = type(col.type).__name__
                missing_columns.setdefault(tname, []).append(
                    {
                        "column": cname,
                        "type": coltype,
                        "nullable": bool(getattr(col, "nullable", True)),
                        "default": str(getattr(getattr(col, "default", None), "arg", None)),
                    }
                )

    notes: List[str] = []
    if missing_columns:
        notes.append("Columns missing will be handled via Alembic autogenerate (add-only).")
    notes.append("Indexes/constraints differences are best handled by Alembic autogenerate.")

    will_generate_migration = bool(missing_columns)
    return Plan(
        created_tables=missing_tables,
        missing_columns=missing_columns,
        notes=notes,
        will_generate_migration=will_generate_migration,
    )


def create_missing_tables(engine: Engine, model_md: Any, table_names: List[str]) -> None:
    if not table_names:
        return
    # Map names to Table objects from model metadata
    tables = [model_md.tables[name] for name in table_names if name in model_md.tables]
    if tables:
        model_md.create_all(bind=engine, tables=tables)


def maybe_generate_and_upgrade_migration(plan: Plan) -> str | None:
    """If diffs exist (e.g., missing columns), autogenerate a migration and upgrade head.
    Returns the revision id or path when created, else None.
    """
    if not plan.will_generate_migration:
        return None
    try:
        from alembic.config import Config
        from alembic import command
        cfg = Config("alembic.ini")
        # Create revision with autogenerate
        command.revision(cfg, autogenerate=True, message="ensure schema")
        # Upgrade to head
        command.upgrade(cfg, "head")
        # We don't have the revision id handy without parsing alembic output; return a marker
        return "created-and-upgraded"
    except Exception as e:
        print(f"WARNING: Alembic autogenerate failed: {e}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensure Neon DB schema matches models (additive only)")
    parser.add_argument("--plan", action="store_true", help="Show plan only (default)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (create tables, then alembic autogenerate+upgrade)")
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    args = parser.parse_args()

    load_env()
    url = build_engine_url()
    engine = create_engine(url, pool_pre_ping=True, future=True)

    model_md = get_model_metadata()
    plan = diff_schema(engine, model_md)

    output = {
        "database": url.split("?")[0],
        "plan": asdict(plan),
        "applied": False,
        "alembic": None,
    }

    if args.apply:
        # 1) Create missing tables directly (idempotent)
        create_missing_tables(engine, model_md, plan.created_tables)
        # 2) Use Alembic autogenerate to add missing columns / constraints
        rev = maybe_generate_and_upgrade_migration(plan)
        output["applied"] = True
        output["alembic"] = rev

    if args.json or True:
        print(json.dumps(output, indent=2, default=str))
    else:
        # Human readable fallback
        print("Created tables:", ", ".join(plan.created_tables) or "none")
        print("Missing columns:")
        for t, cols in plan.missing_columns.items():
            print(f"  {t}: {[c['column'] for c in cols]}")


if __name__ == "__main__":
    main()
