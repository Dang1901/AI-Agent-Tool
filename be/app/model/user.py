# app/db/models.py
from sqlalchemy import Column, String, Integer, Boolean, Date, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)

    dob = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    phone_number = Column(String(15), nullable=True)
    avatar_url = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Additional attributes for ABAC
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    clearance_level = Column(String(50), nullable=True)  # public, internal, confidential, secret

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    user_attributes = relationship("UserAttribute", back_populates="user")
    access_logs = relationship("AccessLog", back_populates="user")
