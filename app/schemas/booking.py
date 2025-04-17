from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.booking import BookingStatus, PaymentStatus
from app.schemas.flight import Flight
from app.schemas.user import User

class BookingBase(BaseModel):
    flight_id: int
    seat_number: str

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None

class BookingInDB(BookingBase):
    id: int
    booking_reference: str
    passenger_id: int
    booking_date: datetime
    status: BookingStatus
    payment_status: PaymentStatus
    payment_id: Optional[str] = None
    payment_amount: float
    
    class Config:
        orm_mode = True

class Booking(BookingInDB):
    flight: Optional[Flight] = None
    passenger: Optional[User] = None

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    card_number: str
    expiry_date: str
    cvv: str

class ETicket(BaseModel):
    booking_reference: str
    passenger_name: str
    flight_number: str
    airline: str
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    seat_number: str
    booking_date: datetime
    payment_amount: float