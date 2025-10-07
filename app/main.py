from fastapi import FastAPI

app = FastAPI(title="Tinko API (dev)")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}
