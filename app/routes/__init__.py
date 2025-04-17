from fastapi import APIRouter
from app.routes import auth, passengers, flights, bookings, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(passengers.router)
api_router.include_router(flights.router)
api_router.include_router(bookings.router)
api_router.include_router(admin.router)