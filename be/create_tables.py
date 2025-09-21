"""
Create database tables directly
"""
import os
from sqlalchemy import create_engine, text
from app.model.env_var import Base
from app.model.audit_event import AuditEventModel
from app.core.config import DB_URL

def create_tables():
    """Create all tables"""
    engine = create_engine(DB_URL)
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
