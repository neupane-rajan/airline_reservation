from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    PASSENGER = "passenger"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.PASSENGER)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    bookings = relationship("Booking", back_populates="passenger")