from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_URL

# Tạo engine (pool_pre_ping để check connection khỏe)
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,  # giúp tránh lỗi connection drop
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
)

# SessionLocal cho mỗi request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model cho ORM
Base = declarative_base()

# Dependency để inject DB session vào route
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()