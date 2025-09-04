#!/usr/bin/env python3
import os
import sys

# Set environment variables before importing app modules
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
os.environ['DEBUG'] = 'True'

# Now import app modules
from app.db.database import Base, engine, SessionLocal
from app.model.user import User
from app.utils.security import hash_password

def setup_database():
    """Create database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def create_test_user():
    """Create a test user"""
    print("Creating test user...")
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_user:
            print("✅ Test user already exists")
            return
        
        # Create test user
        user = User(
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            name="Admin User"
        )
        db.add(user)
        db.commit()
        print("✅ Test user created: admin@example.com / admin123")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
    create_test_user()
    print("🎉 Database setup complete!")
