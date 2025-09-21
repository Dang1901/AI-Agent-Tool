"""
SQLAlchemy implementation of EnvStore
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.core.domain.env_var import EnvVar, EnvVarType, ScopeRef, ScopeLevel, EnvVarStatus
from app.core.domain.env_var_version import EnvVarVersion
from app.core.domain.release import Release, ReleaseStatus
from app.core.domain.approval import Approval, ApprovalDecision
from app.core.domain.audit_event import AuditEvent, AuditAction, AuditTargetType
from app.core.ports.env_store import EnvStore
from app.model.env_var import (
    EnvVarModel, EnvVarVersionModel, ReleaseModel, ApprovalModel, 
    AuditEventModel, RotationScheduleModel
)


class SqlAlchemyEnvStore(EnvStore):
    """SQLAlchemy implementation of EnvStore"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def create(self, env_var: EnvVar) -> EnvVar:
        """Create a new environment variable"""
        model = EnvVarModel(
            id=env_var.id,
            key=env_var.key,
            value_encrypted=env_var.value,
            type=env_var.type.value,
            scope_level=env_var.scope.level.value,
            scope_ref_id=env_var.scope.ref_id,
            tags=env_var.tags,
            description=env_var.description,
            is_secret=env_var.is_secret,
            status=env_var.status.value,
            created_by=env_var.created_by,
            created_at=env_var.created_at,
            updated_by=env_var.updated_by,
            updated_at=env_var.updated_at
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return env_var
    
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        """Get environment variable by ID"""
        model = self.db_session.query(EnvVarModel).filter(EnvVarModel.id == env_var_id).first()
        if not model:
            return None
        
        return self._model_to_domain(model)
    
    async def get_by_unique_key(self, scope_level: str, scope_ref_id: str, key: str) -> Optional[EnvVar]:
        """Get environment variable by unique key"""
        model = self.db_session.query(EnvVarModel).filter(
            and_(
                EnvVarModel.scope_level == scope_level,
                EnvVarModel.scope_ref_id == scope_ref_id,
                EnvVarModel.key == key
            )
        ).first()
        
        if not model:
            return None
        
        return self._model_to_domain(model)
    
    async def update(self, env_var: EnvVar) -> EnvVar:
        """Update an environment variable"""
        model = self.db_session.query(EnvVarModel).filter(EnvVarModel.id == env_var.id).first()
        if not model:
            raise ValueError(f"Environment variable {env_var.id} not found")
        
        model.value_encrypted = env_var.value
        model.type = env_var.type.value
        model.tags = env_var.tags
        model.description = env_var.description
        model.status = env_var.status.value
        model.updated_by = env_var.updated_by
        model.updated_at = env_var.updated_at
        
        self.db_session.commit()
        return env_var
    
    async def delete(self, env_var_id: str) -> bool:
        """Delete an environment variable"""
        model = self.db_session.query(EnvVarModel).filter(EnvVarModel.id == env_var_id).first()
        if not model:
            return False
        
        self.db_session.delete(model)
        self.db_session.commit()
        return True
    
    async def list(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[EnvVar]:
        """List environment variables with filtering and pagination"""
        query = self.db_session.query(EnvVarModel)
        
        # Apply filters
        if 'scope_level' in filters:
            query = query.filter(EnvVarModel.scope_level == filters['scope_level'])
        
        if 'scope_ref_id' in filters:
            query = query.filter(EnvVarModel.scope_ref_id == filters['scope_ref_id'])
        
        if 'key_filter' in filters:
            query = query.filter(EnvVarModel.key.ilike(f"%{filters['key_filter']}%"))
        
        if 'tag_filter' in filters:
            query = query.filter(EnvVarModel.tags.contains([filters['tag_filter']]))
        
        if 'type_filter' in filters:
            query = query.filter(EnvVarModel.type == filters['type_filter'])
        
        if 'status_filter' in filters:
            query = query.filter(EnvVarModel.status == filters['status_filter'])
        
        # Apply pagination
        offset = (page - 1) * size
        models = query.offset(offset).limit(size).all()
        
        return [self._model_to_domain(model) for model in models]
    
    async def count(self, filters: Dict[str, Any]) -> int:
        """Count environment variables matching filters"""
        query = self.db_session.query(EnvVarModel)
        
        # Apply same filters as list method
        if 'scope_level' in filters:
            query = query.filter(EnvVarModel.scope_level == filters['scope_level'])
        
        if 'scope_ref_id' in filters:
            query = query.filter(EnvVarModel.scope_ref_id == filters['scope_ref_id'])
        
        if 'key_filter' in filters:
            query = query.filter(EnvVarModel.key.ilike(f"%{filters['key_filter']}%"))
        
        if 'tag_filter' in filters:
            query = query.filter(EnvVarModel.tags.contains([filters['tag_filter']]))
        
        if 'type_filter' in filters:
            query = query.filter(EnvVarModel.type == filters['type_filter'])
        
        if 'status_filter' in filters:
            query = query.filter(EnvVarModel.status == filters['status_filter'])
        
        return query.count()
    
    # Version management
    async def create_version(self, version: EnvVarVersion) -> EnvVarVersion:
        """Create a new version record"""
        model = EnvVarVersionModel(
            id=version.id,
            env_var_id=version.env_var_id,
            version=version.version,
            diff_json=version.diff_json,
            checksum=version.checksum,
            author=version.author,
            created_at=version.created_at
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return version
    
    async def get_versions(self, env_var_id: str) -> List[EnvVarVersion]:
        """Get all versions for an environment variable"""
        models = self.db_session.query(EnvVarVersionModel).filter(
            EnvVarVersionModel.env_var_id == env_var_id
        ).order_by(desc(EnvVarVersionModel.version)).all()
        
        return [self._version_model_to_domain(model) for model in models]
    
    async def get_next_version(self, env_var_id: str) -> int:
        """Get next version number for an environment variable"""
        max_version = self.db_session.query(EnvVarVersionModel.version).filter(
            EnvVarVersionModel.env_var_id == env_var_id
        ).order_by(desc(EnvVarVersionModel.version)).first()
        
        if max_version:
            return max_version[0] + 1
        return 1
    
    async def rollback_to_version(self, env_var_id: str, version: int, rolled_back_by: str) -> EnvVar:
        """Rollback environment variable to a specific version"""
        # Get the version to rollback to
        version_model = self.db_session.query(EnvVarVersionModel).filter(
            and_(
                EnvVarVersionModel.env_var_id == env_var_id,
                EnvVarVersionModel.version == version
            )
        ).first()
        
        if not version_model:
            raise ValueError(f"Version {version} not found for environment variable {env_var_id}")
        
        # Get current env_var
        env_var = await self.get_by_id(env_var_id)
        if not env_var:
            raise ValueError(f"Environment variable {env_var_id} not found")
        
        # Apply version changes (simplified implementation)
        # In reality, you'd need to apply the diff_json changes
        
        return env_var
    
    # Release management
    async def create_release(self, release: Release) -> Release:
        """Create a new release"""
        model = ReleaseModel(
            id=release.id,
            service_id=release.service_id,
            environment=release.environment,
            title=release.title,
            description=release.description,
            status=release.status.value,
            changes=release.changes,
            created_by=release.created_by,
            created_at=release.created_at,
            applied_by=release.applied_by,
            applied_at=release.applied_at
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return release
    
    async def get_release_by_id(self, release_id: str) -> Optional[Release]:
        """Get release by ID"""
        model = self.db_session.query(ReleaseModel).filter(ReleaseModel.id == release_id).first()
        if not model:
            return None
        
        return self._release_model_to_domain(model)
    
    async def update_release(self, release: Release) -> Release:
        """Update a release"""
        model = self.db_session.query(ReleaseModel).filter(ReleaseModel.id == release.id).first()
        if not model:
            raise ValueError(f"Release {release.id} not found")
        
        model.status = release.status.value
        model.applied_by = release.applied_by
        model.applied_at = release.applied_at
        
        self.db_session.commit()
        return release
    
    async def list_releases(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[Release]:
        """List releases with filtering and pagination"""
        query = self.db_session.query(ReleaseModel)
        
        # Apply filters
        if 'service_id' in filters:
            query = query.filter(ReleaseModel.service_id == filters['service_id'])
        
        if 'environment' in filters:
            query = query.filter(ReleaseModel.environment == filters['environment'])
        
        if 'status' in filters:
            query = query.filter(ReleaseModel.status == filters['status'])
        
        # Apply pagination
        offset = (page - 1) * size
        models = query.order_by(desc(ReleaseModel.created_at)).offset(offset).limit(size).all()
        
        return [self._release_model_to_domain(model) for model in models]
    
    # Approval management
    async def create_approval(self, approval: Approval) -> Approval:
        """Create a new approval"""
        model = ApprovalModel(
            id=approval.id,
            release_id=approval.release_id,
            approver_id=approval.approver_id,
            decision=approval.decision.value,
            comment=approval.comment,
            decided_at=approval.decided_at
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return approval
    
    async def get_approvals_for_release(self, release_id: str) -> List[Approval]:
        """Get all approvals for a release"""
        models = self.db_session.query(ApprovalModel).filter(
            ApprovalModel.release_id == release_id
        ).order_by(desc(ApprovalModel.decided_at)).all()
        
        return [self._approval_model_to_domain(model) for model in models]
    
    async def get_approval_by_id(self, approval_id: str) -> Optional[Approval]:
        """Get approval by ID"""
        model = self.db_session.query(ApprovalModel).filter(ApprovalModel.id == approval_id).first()
        if not model:
            return None
        
        return self._approval_model_to_domain(model)
    
    # Audit management
    async def create_audit_event(self, event: AuditEvent) -> AuditEvent:
        """Create an audit event"""
        model = AuditEventModel(
            id=event.id,
            actor=event.actor,
            action=event.action.value,
            target_type=event.target_type.value,
            target_id=event.target_id,
            before_json=event.before_json,
            after_json=event.after_json,
            reason=event.reason,
            timestamp=event.timestamp
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return event
    
    async def get_audit_events(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[AuditEvent]:
        """Get audit events with filtering and pagination"""
        query = self.db_session.query(AuditEventModel)
        
        # Apply filters
        if 'actor' in filters:
            query = query.filter(AuditEventModel.actor == filters['actor'])
        
        if 'action' in filters:
            query = query.filter(AuditEventModel.action == filters['action'])
        
        if 'target_type' in filters:
            query = query.filter(AuditEventModel.target_type == filters['target_type'])
        
        if 'target_id' in filters:
            query = query.filter(AuditEventModel.target_id == filters['target_id'])
        
        # Apply pagination
        offset = (page - 1) * size
        models = query.order_by(desc(AuditEventModel.timestamp)).offset(offset).limit(size).all()
        
        return [self._audit_event_model_to_domain(model) for model in models]
    
    # Rotation management
    async def create_rotation_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rotation schedule"""
        model = RotationScheduleModel(
            id=schedule['id'],
            env_var_id=schedule['env_var_id'],
            schedule=schedule['schedule'],
            status=schedule['status'],
            created_by=schedule['created_by'],
            created_at=schedule['created_at'],
            updated_by=schedule['updated_by'],
            updated_at=schedule['updated_at']
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        return schedule
    
    async def get_rotation_schedules(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get rotation schedules"""
        query = self.db_session.query(RotationScheduleModel)
        
        # Apply filters
        if 'env_var_id' in filters:
            query = query.filter(RotationScheduleModel.env_var_id == filters['env_var_id'])
        
        if 'status' in filters:
            query = query.filter(RotationScheduleModel.status == filters['status'])
        
        models = query.all()
        return [self._rotation_schedule_model_to_dict(model) for model in models]
    
    async def update_rotation_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a rotation schedule"""
        model = self.db_session.query(RotationScheduleModel).filter(
            RotationScheduleModel.id == schedule_id
        ).first()
        
        if not model:
            return {}
        
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        self.db_session.commit()
        return self._rotation_schedule_model_to_dict(model)
    
    # Helper methods
    def _model_to_domain(self, model: EnvVarModel) -> EnvVar:
        """Convert SQLAlchemy model to domain object"""
        return EnvVar(
            id=model.id,
            key=model.key,
            value=model.value_encrypted,
            type=EnvVarType(model.type),
            scope=ScopeRef(ScopeLevel(model.scope_level), model.scope_ref_id),
            tags=model.tags or [],
            description=model.description,
            is_secret=model.is_secret,
            status=EnvVarStatus(model.status),
            created_by=model.created_by,
            created_at=model.created_at,
            updated_by=model.updated_by,
            updated_at=model.updated_at
        )
    
    def _version_model_to_domain(self, model: EnvVarVersionModel) -> EnvVarVersion:
        """Convert version model to domain object"""
        return EnvVarVersion(
            id=model.id,
            env_var_id=model.env_var_id,
            version=model.version,
            diff_json=model.diff_json,
            checksum=model.checksum,
            author=model.author,
            created_at=model.created_at
        )
    
    def _release_model_to_domain(self, model: ReleaseModel) -> Release:
        """Convert release model to domain object"""
        return Release(
            id=model.id,
            service_id=model.service_id,
            environment=model.environment,
            title=model.title,
            description=model.description,
            status=ReleaseStatus(model.status),
            changes=model.changes,
            created_by=model.created_by,
            created_at=model.created_at,
            applied_by=model.applied_by,
            applied_at=model.applied_at
        )
    
    def _approval_model_to_domain(self, model: ApprovalModel) -> Approval:
        """Convert approval model to domain object"""
        return Approval(
            id=model.id,
            release_id=model.release_id,
            approver_id=model.approver_id,
            decision=ApprovalDecision(model.decision),
            comment=model.comment,
            decided_at=model.decided_at
        )
    
    def _audit_event_model_to_domain(self, model: AuditEventModel) -> AuditEvent:
        """Convert audit event model to domain object"""
        return AuditEvent(
            id=model.id,
            actor=model.actor,
            action=AuditAction(model.action),
            target_type=AuditTargetType(model.target_type),
            target_id=model.target_id,
            before_json=model.before_json,
            after_json=model.after_json,
            reason=model.reason,
            timestamp=model.timestamp
        )
    
    def _rotation_schedule_model_to_dict(self, model: RotationScheduleModel) -> Dict[str, Any]:
        """Convert rotation schedule model to dictionary"""
        return {
            'id': model.id,
            'env_var_id': model.env_var_id,
            'schedule': model.schedule,
            'status': model.status,
            'created_by': model.created_by,
            'created_at': model.created_at.isoformat(),
            'updated_by': model.updated_by,
            'updated_at': model.updated_at.isoformat()
        }
