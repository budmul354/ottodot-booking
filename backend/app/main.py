from fastapi import FastAPI

from .api.bookings import router as bookings_router
from .api.catalog import router as catalog_router

app = FastAPI(title="Ottodot Trial Booking")
app.include_router(catalog_router)
app.include_router(bookings_router)
