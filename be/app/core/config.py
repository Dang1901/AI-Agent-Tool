import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Database configuration with fallback to SQLite
DB_URL = os.getenv("DATABASE_URL")

def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        from app.db import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
