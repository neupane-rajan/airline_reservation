from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.flight import Flight
from app.schemas.flight import Flight as FlightSchema, FlightCreate, FlightUpdate, FlightSearch
from app.services.auth import get_current_active_user, check_admin_access

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/", response_model=List[FlightSchema])
def get_all_flights(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    flights = db.query(Flight).filter(Flight.is_active == True).offset(skip).limit(limit).all()
    return flights

@router.post("/search", response_model=List[FlightSchema])
def search_flights(
    search: FlightSearch,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(Flight).filter(Flight.is_active == True)
    
    if search.departure_city:
        query = query.filter(Flight.departure_city == search.departure_city)
    
    if search.arrival_city:
        query = query.filter(Flight.arrival_city == search.arrival_city)
    
    if search.departure_date:
        # Extract date only for comparison
        departure_date = search.departure_date.date()
        query = query.filter(Flight.departure_time >= datetime.combine(departure_date, datetime.min.time()))
        query = query.filter(Flight.departure_time < datetime.combine(departure_date, datetime.max.time()))
    
    flights = query.all()
    return flights

@router.get("/{flight_id}", response_model=FlightSchema)
def get_flight(
    flight_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    return flight

@router.post("/", response_model=FlightSchema)
def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_admin_access)
):
    # Check if flight number already exists
    existing_flight = db.query(Flight).filter(Flight.flight_number == flight.flight_number).first()
    if existing_flight:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Flight with number {flight.flight_number} already exists"
        )
    
    db_flight = Flight(**flight.dict())
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    
    return db_flight

@router.put("/{flight_id}", response_model=FlightSchema)
def update_flight(
    flight_id: int,
    flight_data: FlightUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_admin_access)
):
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    # Update flight data
    for key, value in flight_data.dict(exclude_unset=True).items():
        setattr(flight, key, value)
    
    db.commit()
    db.refresh(flight)
    
    return flight

@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_admin_access)
):
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    # Soft delete by marking as inactive
    flight.is_active = False
    db.commit()
    
    return None