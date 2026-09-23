import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.bookings import router as bookings_router
from .api.catalog import router as catalog_router
from .observability import snapshot

app = FastAPI(title="Ottodot Trial Booking")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(catalog_router)
app.include_router(bookings_router)


@app.get("/health", tags=["operations"])
def health():
    return {"status": "ok"}


@app.get("/metrics", tags=["operations"])
def metrics():
    return snapshot()
