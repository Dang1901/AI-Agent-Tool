from sqlalchemy import Column, Integer, String
from app.db.database import Base

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    service = Column(String, nullable=False)
