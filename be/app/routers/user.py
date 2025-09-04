from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.user import UserResponse
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List all users who have logged in to the system"""
    return user_service.get_logged_in_users(
        db, 
        page=page, 
        page_size=page_size, 
        search=search, 
        is_active=is_active
    )
