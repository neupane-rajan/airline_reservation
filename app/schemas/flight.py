from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FlightBase(BaseModel):
    flight_number: str
    airline: str
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    available_seats: int
    is_active: bool = True

class FlightCreate(FlightBase):
    pass

class FlightUpdate(BaseModel):
    airline: Optional[str] = None
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None
    available_seats: Optional[int] = None
    is_active: Optional[bool] = None

class Flight(FlightBase):
    id: int
    
    class Config:
        orm_mode = True

class FlightSearch(BaseModel):
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_date: Optional[datetime] = None