from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.auth import get_current_active_user, check_staff_access

router = APIRouter(prefix="/passengers", tags=["Passengers"])

@router.get("/", response_model=List[UserSchema])
def get_all_passengers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_staff_access)
):
    passengers = db.query(User).filter(User.role == UserRole.PASSENGER).offset(skip).limit(limit).all()
    return passengers

@router.get("/{passenger_id}", response_model=UserSchema)
def get_passenger(
    passenger_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user is accessing their own data or has staff/admin access
    if current_user.id != passenger_id and current_user.role == UserRole.PASSENGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this passenger's information"
        )
    
    passenger = db.query(User).filter(User.id == passenger_id, User.role == UserRole.PASSENGER).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passenger not found"
        )
    
    return passenger

@router.put("/{passenger_id}", response_model=UserSchema)
def update_passenger(
    passenger_id: int,
    passenger_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user is updating their own data or has staff/admin access
    if current_user.id != passenger_id and current_user.role == UserRole.PASSENGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this passenger's information"
        )
    
    passenger = db.query(User).filter(User.id == passenger_id).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passenger not found"
        )
    
    # Update passenger data
    if passenger_data.email is not None:
        passenger.email = passenger_data.email
    if passenger_data.full_name is not None:
        passenger.full_name = passenger_data.full_name
    if passenger_data.phone is not None:
        passenger.phone = passenger_data.phone
    
    db.commit()
    db.refresh(passenger)
    
    return passenger

@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_passenger(
    passenger_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_staff_access)
):
    passenger = db.query(User).filter(User.id == passenger_id, User.role == UserRole.PASSENGER).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passenger not found"
        )
    
    db.delete(passenger)
    db.commit()
    
    return None