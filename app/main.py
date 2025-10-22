# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Initialize Sentry (if DSN is provided)
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            SqlalchemyIntegration(),
        ],
        environment=os.getenv('ENVIRONMENT', 'development'),
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
    )

# 1) Load .env early (optional but recommended)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 2) Initialize logging
from .logging_config import configure_logging, get_logger
configure_logging()
logger = get_logger(__name__)

# 3) DB base/engine so we can auto-create tables in dev
from .db import Base, engine

# 4) Routers (import-guarded so app still boots even if one has an error)
events_router = recoveries_router = dev_router = recovery_links_router = classifier_router = payments_router = stripe_webhook_router = auth_router = retry_router = stripe_payments_router = maintenance_router = None

try:
    from .routers.auth import router as auth_router
except Exception:
    pass

try:
    from .routers.retry_policies import router as retry_router
except Exception:
    pass

try:
    from .routers.stripe_payments import router as stripe_payments_router
except Exception:
    pass

try:
    from .routers.events import router as events_router
except Exception:
    pass

try:
    from .routers.recoveries import router as recoveries_router
except Exception:
    pass

# Removed optional routers that don't exist in this repo to avoid unresolved import warnings

try:
    from .routers.dev import router as dev_router  # our debug/schema/bootstraps
except Exception:
    pass

try:
    from .routers.recovery_links import router as recovery_links_router
except Exception:
    pass

try:
    from .routers.classifier import router as classifier_router
except Exception:
    pass

try:
    from .routers.payments import router as payments_router
except Exception:
    pass

try:
    from .routers.webhooks_stripe import router as stripe_webhook_router
except Exception:
    pass

try:
    from .routers.analytics import router as analytics_router
except Exception:
    pass

try:
    from .routers.maintenance import router as maintenance_router
except Exception:
    pass

app = FastAPI(title="Tinko API (dev)", version="0.1.0")

# Add request tracing middleware
from .middleware import request_id_middleware
app.middleware("http")(request_id_middleware)

# (Dev) CORS — handy if you'll hit endpoints from a local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _create_tables():
    # Dev convenience: ensure tables exist (use Alembic for real migrations later)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("database_tables_created", stage="startup")
    except Exception as e:
        # Don't block app start in dev
        logger.error("database_tables_creation_failed", stage="startup", exc_info=e)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

# Mount routers if present
if auth_router:
    app.include_router(auth_router)
if retry_router:
    app.include_router(retry_router)
if stripe_payments_router:
    app.include_router(stripe_payments_router)
if events_router:
    app.include_router(events_router)
if recoveries_router:
    app.include_router(recoveries_router)
if dev_router:
    app.include_router(dev_router)   # exposes /_dev/...
if recovery_links_router:
    app.include_router(recovery_links_router)
if classifier_router:
    app.include_router(classifier_router)
if payments_router:
    app.include_router(payments_router)
if stripe_webhook_router:
    app.include_router(stripe_webhook_router)
if analytics_router:
    app.include_router(analytics_router)
if maintenance_router:
    app.include_router(maintenance_router)
