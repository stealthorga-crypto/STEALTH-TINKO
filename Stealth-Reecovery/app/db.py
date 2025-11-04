import os
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

try:
    # Load .env if present for local runs
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SKIP_DB = os.getenv("SKIP_DB", "").lower() in ("1", "true", "yes")

if SKIP_DB:
    # Hermetic mode for CI/local runs: use in-memory SQLite to avoid network
    SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        future=True,
        echo=False,
        pool_pre_ping=True,
    )
else:
    # Require Neon/PostgreSQL
    if not SQLALCHEMY_DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Please set a Neon Postgres URL in your .env, e.g. "
            "postgresql+psycopg2://<USER>:<PASSWORD>@<HOST>:5432/<DB>?sslmode=require"
        )

    parsed = urlparse(SQLALCHEMY_DATABASE_URL)
    if not parsed.scheme.startswith("postgresql"):
        raise RuntimeError(
            f"Unsupported DATABASE_URL scheme '{parsed.scheme}'. This application only supports Postgres/Neon."
        )

    if "sslmode=" not in SQLALCHEMY_DATABASE_URL and parsed.scheme.startswith("postgresql"):
        sep = "&" if "?" in SQLALCHEMY_DATABASE_URL else "?"
        SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL}{sep}sslmode=require"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        future=True,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
