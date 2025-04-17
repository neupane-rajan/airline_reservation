from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_active_user

# Common dependencies can be defined here
def get_current_user_with_db(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    A dependency that provides both the current user and the database session.
    Can be used in routes that need both dependencies.
    """
    return {"current_user": current_user, "db": db}