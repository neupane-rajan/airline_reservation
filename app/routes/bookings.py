from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models.booking import Booking, BookingStatus, PaymentStatus
from app.models.flight import Flight
from app.models.user import User, UserRole
from app.schemas.booking import (
    Booking as BookingSchema,
    BookingCreate,
    BookingUpdate,
    PaymentCreate,
    ETicket
)
from app.services.auth import get_current_active_user
from app.services.payment import process_payment, refund_payment

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/", response_model=List[BookingSchema])
def get_user_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # For regular passengers, show only their bookings
    if current_user.role == UserRole.PASSENGER:
        bookings = db.query(Booking).filter(Booking.passenger_id == current_user.id).all()
    # For admin/staff, show all bookings
    else:
        bookings = db.query(Booking).all()
    
    return bookings

@router.get("/{booking_id}", response_model=BookingSchema)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user is authorized to view this booking
    if current_user.role == UserRole.PASSENGER and booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this booking"
        )
    
    return booking

@router.post("/", response_model=BookingSchema)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if flight exists and has available seats
    flight = db.query(Flight).filter(Flight.id == booking.flight_id, Flight.is_active == True).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found or inactive"
        )
    
    if flight.available_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available seats on this flight"
        )
    
    # Generate a unique booking reference
    booking_reference = f"BK-{uuid.uuid4().hex[:8].upper()}"
    
    # Create booking record
    new_booking = Booking(
        booking_reference=booking_reference,
        passenger_id=current_user.id,
        flight_id=booking.flight_id,
        seat_number=booking.seat_number,
        status=BookingStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        payment_amount=flight.price
    )
    
    # Reduce available seats
    flight.available_seats -= 1
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking

@router.post("/{booking_id}/payment", response_model=BookingSchema)
async def make_payment(
    booking_id: int,
    payment_details: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user is authorized to pay for this booking
    if current_user.role == UserRole.PASSENGER and booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this booking"
        )
    
    # Check if booking is already paid
    if booking.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment has already been processed for this booking"
        )
    
    # Process payment via payment gateway
    payment_result = await process_payment(
        amount=payment_details.amount,
        card_number=payment_details.card_number,
        expiry_date=payment_details.expiry_date,
        cvv=payment_details.cvv
    )
    
    # Update booking based on payment result
    booking.payment_status = payment_result["status"]
    booking.payment_id = payment_result["payment_id"]
    
    if payment_result["status"] == PaymentStatus.COMPLETED:
        booking.status = BookingStatus.CONFIRMED
    
    db.commit()
    db.refresh(booking)
    
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingSchema)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user is authorized to cancel this booking
    if current_user.role == UserRole.PASSENGER and booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    # Check if booking is already cancelled
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    # Process refund if payment was completed
    if booking.payment_status == PaymentStatus.COMPLETED:
        refund_result = await refund_payment(booking.payment_id)
        booking.payment_status = refund_result["status"]
    
    # Update booking status
    booking.status = BookingStatus.CANCELLED
    
    # Return seat to available inventory
    flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
    if flight:
        flight.available_seats += 1
    
    db.commit()
    db.refresh(booking)
    
    return booking

@router.get("/{booking_id}/e-ticket", response_model=ETicket)
def generate_e_ticket(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get booking with related data
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user is authorized to view this e-ticket
    if current_user.role == UserRole.PASSENGER and booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this e-ticket"
        )
    
    # Check if booking is confirmed (payment completed)
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-ticket is only available for confirmed bookings"
        )
    
    # Get related passenger and flight info
    passenger = db.query(User).filter(User.id == booking.passenger_id).first()
    flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
    
    # Generate e-ticket
    e_ticket = ETicket(
        booking_reference=booking.booking_reference,
        passenger_name=passenger.full_name,
        flight_number=flight.flight_number,
        airline=flight.airline,
        departure_city=flight.departure_city,
        arrival_city=flight.arrival_city,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        seat_number=booking.seat_number,
        booking_date=booking.booking_date,
        payment_amount=booking.payment_amount
    )
    
    return e_ticket