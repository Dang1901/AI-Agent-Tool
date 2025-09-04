# RBAC Models
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime

# Many-to-many relationship tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # admin, manager, user
    display_name = Column(String(200), nullable=False)  # Administrator, Manager, User
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # user.read, feature.create
    display_name = Column(String(200), nullable=False)  # Read Users, Create Features
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False)  # user, feature, report
    action = Column(String(50), nullable=False)  # read, write, delete, execute
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # user, feature, report
    display_name = Column(String(200), nullable=False)  # User Management, Feature Management
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=False)  # entity, action, data
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
