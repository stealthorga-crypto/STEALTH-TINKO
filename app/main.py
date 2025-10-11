# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1) Load .env early (optional but recommended)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 2) DB base/engine so we can auto-create tables in dev
from .db import Base, engine

# 3) Routers (import-guarded so app still boots even if one has an error)
events_router = recoveries_router = pay_router = razorpay_webhook_router = dev_router = None

try:
    from .routers.events import router as events_router
except Exception:
    pass

try:
    from .routers.recoveries import router as recoveries_router
except Exception:
    pass

try:
    from .routers.pay import router as pay_router  # optional if you have it
except Exception:
    pass

try:
    from .routers.webhooks_razorpay import router as razorpay_webhook_router  # optional
except Exception:
    pass

try:
    from .routers.dev import router as dev_router  # our debug/schema/bootstraps
except Exception:
    pass

app = FastAPI(title="Tinko API (dev)", version="0.1.0")

# (Dev) CORS — handy if you’ll hit endpoints from a local frontend
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
    except Exception:
        # Don’t block app start in dev
        pass

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

# Mount routers if present
if events_router:
    app.include_router(events_router)
if recoveries_router:
    app.include_router(recoveries_router)
if pay_router:
    app.include_router(pay_router)
if razorpay_webhook_router:
    app.include_router(razorpay_webhook_router)
if dev_router:
    app.include_router(dev_router)   # exposes /_dev/...
