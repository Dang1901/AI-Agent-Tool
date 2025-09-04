from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
from app.model.user import User

def get_logged_in_users(
    db: Session, 
    page: int = 1, 
    page_size: int = 100, 
    search: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get all registered users in the system"""
    query = db.query(User)
    
    # Apply search filter
    if search:
        search_filter = or_(
            User.name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.phone_number.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply active status filter
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Order by creation time (newest first)
    query = query.order_by(desc(User.created_at))
    
    # Apply pagination
    skip = (page - 1) * page_size
    return query.offset(skip).limit(page_size).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()
