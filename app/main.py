from fastapi import FastAPI
from .routers.events import router as events_router
from .db import Base, engine

app = FastAPI(title="Tinko API (dev)")

@app.on_event("startup")
def _create_tables():
    # Dev convenience: ensure tables exist (Alembic still used for real migrations)
    Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

app.include_router(events_router)
from .routers.recoveries import router as recoveries_router
app.include_router(recoveries_router)

