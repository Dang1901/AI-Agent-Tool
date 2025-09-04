# ABAC Models
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    policy_type = Column(String(50), nullable=False)  # allow, deny, conditional
    priority = Column(Integer, default=100)  # Lower number = higher priority
    is_active = Column(Boolean, default=True)
    
    # Policy conditions (JSON format)
    subject_conditions = Column(JSON, nullable=True)  # User attributes
    resource_conditions = Column(JSON, nullable=True)  # Resource attributes
    action_conditions = Column(JSON, nullable=True)  # Action attributes
    environment_conditions = Column(JSON, nullable=True)  # Time, location, etc.
    
    # Policy effect
    effect = Column(String(20), nullable=False)  # allow, deny
    obligations = Column(JSON, nullable=True)  # Additional actions to take
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policy_assignments = relationship("PolicyAssignment", back_populates="policy")

class PolicyAssignment(Base):
    __tablename__ = "policy_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    assignment_type = Column(String(50), nullable=False)  # user, role, resource, global
    assignment_id = Column(Integer, nullable=True)  # ID of user/role/resource
    assignment_name = Column(String(200), nullable=True)  # Name for reference
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("Policy", back_populates="policy_assignments")

class Attribute(Base):
    __tablename__ = "attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # user.department, resource.type
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    attribute_type = Column(String(50), nullable=False)  # string, number, boolean, date, enum
    data_type = Column(String(50), nullable=False)  # subject, resource, action, environment
    is_required = Column(Boolean, default=False)
    is_multivalued = Column(Boolean, default=False)
    allowed_values = Column(JSON, nullable=True)  # For enum types
    default_value = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserAttribute(Base):
    __tablename__ = "user_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id'), nullable=False)
    value = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    attribute = relationship("Attribute")

class ResourceAttribute(Base):
    __tablename__ = "resource_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, nullable=False)  # Generic resource ID
    resource_type = Column(String(100), nullable=False)  # user, feature, etc.
    attribute_id = Column(Integer, ForeignKey('attributes.id'), nullable=False)
    value = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attribute = relationship("Attribute")

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    decision = Column(String(20), nullable=False)  # allow, deny
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=True)
    context = Column(JSON, nullable=True)  # Additional context information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    policy = relationship("Policy")
