from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.bookings import router as bookings_router
from .api.catalog import router as catalog_router

app = FastAPI(title="Ottodot Trial Booking")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(catalog_router)
app.include_router(bookings_router)
