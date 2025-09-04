from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import user
from app.services import auth as auth_service
from app.schemas.user import UserCreate
from app.schemas.user import UserLogin, TokenResponse
from app.services.auth import get_current_user 
from app.utils.security import create_access_token, create_refresh_token, decode_token
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if auth_service.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return auth_service.create_user(
        db,
        email=user.email,
        password=user.password,
        name=user.name,
        dob=user.dob,
        gender=user.gender,
        phone_number=user.phone_number,
        avatar_url=user.avatar_url
    )

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    # Validate user credentials
    user = auth_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    data = {"sub": str(user.id)}
    access_token = create_access_token(data, timedelta(minutes=15))
    refresh_token = create_refresh_token(data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.get("/me", response_model=user.UserResponse)
def get_me(current_user: user.UserResponse = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: user.UserResponse = Depends(get_current_user)):
    """Logout user"""
    return {"message": "Logged out successfully"}

@router.post("/refresh")
def refresh_token(token: str):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401)
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": username})
    return {"access_token": new_access_token}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
