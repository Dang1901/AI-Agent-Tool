"""
Drop and recreate audit_events table
"""
from sqlalchemy import create_engine, text
from app.core.config import DB_URL

def drop_and_recreate():
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # Drop table if exists
        conn.execute(text('DROP TABLE IF EXISTS audit_events CASCADE'))
        conn.commit()
        print("✅ Dropped audit_events table")
        
        # Recreate table
        from app.model.audit_event import AuditEventModel
        from app.db.database import Base
        Base.metadata.create_all(engine)
        print("✅ Recreated audit_events table")

if __name__ == "__main__":
    drop_and_recreate()

