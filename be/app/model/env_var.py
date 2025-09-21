"""
SQLAlchemy models for environment variables
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class EnvVarModel(Base):
    """SQLAlchemy model for environment variables"""
    __tablename__ = "env_vars"
    
    id = Column(String(255), primary_key=True)
    key = Column(String(100), nullable=False)
    value_encrypted = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # STRING, NUMBER, BOOL, JSON, SECRET
    scope_level = Column(String(20), nullable=False)  # GLOBAL, PROJECT, SERVICE, ENV
    scope_ref_id = Column(String(255), nullable=False)
    tags = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    is_secret = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, PENDING, DEPRECATED
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    versions = relationship("EnvVarVersionModel", back_populates="env_var", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_env_vars_scope', 'scope_level', 'scope_ref_id'),
        Index('idx_env_vars_key', 'key'),
        Index('idx_env_vars_unique', 'scope_level', 'scope_ref_id', 'key', unique=True),
        Index('idx_env_vars_created_at', 'created_at'),
        Index('idx_env_vars_updated_at', 'updated_at'),
    )


class EnvVarVersionModel(Base):
    """SQLAlchemy model for environment variable versions"""
    __tablename__ = "env_var_versions"
    
    id = Column(String(255), primary_key=True)
    env_var_id = Column(String(255), ForeignKey("env_vars.id"), nullable=False)
    version = Column(Integer, nullable=False)
    diff_json = Column(JSON, nullable=False)
    checksum = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    env_var = relationship("EnvVarModel", back_populates="versions")
    
    # Indexes
    __table_args__ = (
        Index('idx_env_var_versions_env_var_id', 'env_var_id'),
        Index('idx_env_var_versions_version', 'env_var_id', 'version'),
        Index('idx_env_var_versions_created_at', 'created_at'),
    )


class ReleaseModel(Base):
    """SQLAlchemy model for releases"""
    __tablename__ = "releases"
    
    id = Column(String(255), primary_key=True)
    service_id = Column(String(255), nullable=False)
    environment = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="DRAFT", nullable=False)  # DRAFT, PENDING_APPROVAL, APPROVED, APPLIED, REJECTED, CANCELLED
    changes = Column(JSON, nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    applied_by = Column(String(255), nullable=True)
    applied_at = Column(DateTime, nullable=True)
    
    # Relationships
    approvals = relationship("ApprovalModel", back_populates="release", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_releases_service_id', 'service_id'),
        Index('idx_releases_environment', 'environment'),
        Index('idx_releases_status', 'status'),
        Index('idx_releases_created_at', 'created_at'),
    )


class ApprovalModel(Base):
    """SQLAlchemy model for approvals"""
    __tablename__ = "approvals"
    
    id = Column(String(255), primary_key=True)
    release_id = Column(String(255), ForeignKey("releases.id"), nullable=False)
    approver_id = Column(String(255), nullable=False)
    decision = Column(String(20), default="PENDING", nullable=False)  # APPROVED, REJECTED, PENDING
    comment = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    
    # Relationships
    release = relationship("ReleaseModel", back_populates="approvals")
    
    # Indexes
    __table_args__ = (
        Index('idx_approvals_release_id', 'release_id'),
        Index('idx_approvals_approver_id', 'approver_id'),
        Index('idx_approvals_decision', 'decision'),
        Index('idx_approvals_decided_at', 'decided_at'),
    )


class PolicyModel(Base):
    """SQLAlchemy model for policies"""
    __tablename__ = "policies"
    
    id = Column(String(255), primary_key=True)
    scope = Column(String(20), nullable=False)  # GLOBAL, PROJECT, SERVICE, ENV
    require_approval = Column(Boolean, default=False, nullable=False)
    min_approvers = Column(Integer, default=0, nullable=False)
    secret_ttl_days = Column(Integer, nullable=True)
    key_regex = Column(String(255), nullable=False)
    value_max_kb = Column(Integer, nullable=False)
    reveal_justification_required = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_policies_scope', 'scope'),
        Index('idx_policies_created_at', 'created_at'),
    )


class AuditEventModel(Base):
    """SQLAlchemy model for audit events"""
    __tablename__ = "audit_events"
    
    id = Column(String(255), primary_key=True)
    actor = Column(String(255), nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, REVEAL, APPROVE, REJECT, APPLY, ROLLBACK, EXPORT, IMPORT
    target_type = Column(String(20), nullable=False)  # ENV_VAR, RELEASE, APPROVAL, POLICY
    target_id = Column(String(255), nullable=False)
    before_json = Column(JSON, nullable=True)
    after_json = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_events_actor', 'actor'),
        Index('idx_audit_events_action', 'action'),
        Index('idx_audit_events_target_type', 'target_type'),
        Index('idx_audit_events_target_id', 'target_id'),
        Index('idx_audit_events_timestamp', 'timestamp'),
    )


class RotationScheduleModel(Base):
    """SQLAlchemy model for rotation schedules"""
    __tablename__ = "rotation_schedules"
    
    id = Column(String(255), primary_key=True)
    env_var_id = Column(String(255), ForeignKey("env_vars.id"), nullable=False)
    schedule = Column(String(100), nullable=False)  # cron expression
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, PAUSED, CANCELLED
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_rotation_schedules_env_var_id', 'env_var_id'),
        Index('idx_rotation_schedules_status', 'status'),
        Index('idx_rotation_schedules_created_at', 'created_at'),
    )
