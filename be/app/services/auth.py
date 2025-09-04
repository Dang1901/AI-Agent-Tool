from sqlalchemy.orm import Session
from app.utils.security import hash_password, verify_password
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.token import verify_token
from app.db.database import get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_by_email(db: Session, email: str):
    from app.model.user import User
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    from app.model.user import User
    from datetime import datetime
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    
    # Update last login time
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


# app/services/auth.py
def create_user(db: Session, email: str, password: str, name: str, dob=None, gender=None, phone_number=None, avatar_url=None):
    from app.model.user import User
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        dob=dob,
        gender=gender,
        phone_number=phone_number,
        avatar_url=avatar_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = verify_token(token, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

