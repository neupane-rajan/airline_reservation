from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.booking import Booking, BookingStatus, PaymentStatus
from app.models.flight import Flight
from app.models.user import User, UserRole
from app.services.auth import check_admin_access

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard/stats", response_model=Dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)
):
    # Get total users count
    total_users = db.query(func.count(User.id)).scalar()
    passengers_count = db.query(func.count(User.id)).filter(User.role == UserRole.PASSENGER).scalar()
    staff_count = db.query(func.count(User.id)).filter(User.role == UserRole.STAFF).scalar()
    
    # Get flights stats
    total_flights = db.query(func.count(Flight.id)).scalar()
    active_flights = db.query(func.count(Flight.id)).filter(Flight.is_active == True).scalar()
    
    # Get bookings stats
    total_bookings = db.query(func.count(Booking.id)).scalar()
    confirmed_bookings = db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.CONFIRMED).scalar()
    pending_bookings = db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.PENDING).scalar()
    cancelled_bookings = db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.CANCELLED).scalar()
    
    # Get revenue stats
    total_revenue = db.query(func.sum(Booking.payment_amount)).filter(
        Booking.payment_status == PaymentStatus.COMPLETED
    ).scalar() or 0.0
    
    # Get recent booking stats (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_bookings = db.query(func.count(Booking.id)).filter(
        Booking.booking_date >= seven_days_ago
    ).scalar()
    
    # Compile stats
    stats = {
        "user_stats": {
            "total_users": total_users,
            "passengers_count": passengers_count,
            "staff_count": staff_count,
        },
        "flight_stats": {
            "total_flights": total_flights,
            "active_flights": active_flights,
        },
        "booking_stats": {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "pending_bookings": pending_bookings,
            "cancelled_bookings": cancelled_bookings,
            "recent_bookings": recent_bookings,
        },
        "financial_stats": {
            "total_revenue": total_revenue,
        }
    }
    
    return stats

@router.get("/revenue/monthly", response_model=List[Dict])
def get_monthly_revenue(
    year: int = datetime.now().year,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)
):
    monthly_revenue = []
    
    for month in range(1, 13):
        # Calculate start and end dates for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query revenue for the month
        revenue = db.query(func.sum(Booking.payment_amount)).filter(
            Booking.payment_status == PaymentStatus.COMPLETED,
            Booking.booking_date >= start_date,
            Booking.booking_date < end_date
        ).scalar() or 0.0
        
        monthly_revenue.append({
            "month": month,
            "month_name": start_date.strftime("%B"),
            "revenue": revenue
        })
    
    return monthly_revenue

@router.get("/popular-routes", response_model=List[Dict])
def get_popular_routes(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)
):
    # This query gets the top routes based on confirmed bookings
    popular_routes = db.query(
        Flight.departure_city,
        Flight.arrival_city,
        func.count(Booking.id).label("booking_count")
    ).join(
        Booking, Booking.flight_id == Flight.id
    ).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).group_by(
        Flight.departure_city,
        Flight.arrival_city
    ).order_by(
        func.count(Booking.id).desc()
    ).limit(limit).all()
    
    result = []
    for route in popular_routes:
        result.append({
            "departure_city": route.departure_city,
            "arrival_city": route.arrival_city,
            "booking_count": route.booking_count
        })
    
    return result