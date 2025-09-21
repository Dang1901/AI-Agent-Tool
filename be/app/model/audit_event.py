"""
Audit Event SQLAlchemy model
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    action_description = Column(Text)
    target_type = Column(String(100), nullable=False, index=True)
    target_id = Column(String(255), nullable=False, index=True)
    change_summary = Column(Text)
    before_json = Column(JSON)
    after_json = Column(JSON)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    is_sensitive = Column(Boolean, default=False, index=True)
    reason = Column(Text)
    
    # Additional metadata
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    session_id = Column(String(255))
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "actor": self.actor,
            "action": self.action,
            "action_description": self.action_description,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "change_summary": self.change_summary,
            "before_json": self.before_json,
            "after_json": self.after_json,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_sensitive": self.is_sensitive,
            "reason": self.reason,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id
        }

