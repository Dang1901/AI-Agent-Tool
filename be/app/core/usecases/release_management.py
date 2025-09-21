"""
Use cases for release management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..domain.release import Release, ReleaseStatus
from ..domain.approval import Approval, ApprovalDecision
from ..domain.env_var import EnvVar
from ..domain.audit_event import AuditEvent, AuditAction, AuditTargetType
from ..ports.env_store import EnvStore
from ..ports.clock import Clock
from ..ports.id_generator import IdGenerator


@dataclass
class CreateReleaseRequest:
    """Request to create a release"""
    service_id: str
    environment: str
    title: str
    description: Optional[str]
    changes: List[Dict[str, Any]]
    created_by: str


@dataclass
class ApproveReleaseRequest:
    """Request to approve a release"""
    release_id: str
    approver_id: str
    comment: Optional[str]


@dataclass
class ApplyReleaseRequest:
    """Request to apply a release"""
    release_id: str
    applied_by: str


class CreateReleaseUseCase:
    """Use case for creating releases"""
    
    def __init__(self, env_store: EnvStore, clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: CreateReleaseRequest) -> Release:
        """Create a new release"""
        # Validate changes
        if not request.changes:
            raise ValueError("Release must have at least one change")
        
        # Check if environment requires approval
        requires_approval = await self._requires_approval(request.environment)
        
        # Create release
        release = Release(
            id=self.id_generator.generate(),
            service_id=request.service_id,
            environment=request.environment,
            title=request.title,
            description=request.description,
            status=ReleaseStatus.PENDING_APPROVAL if requires_approval else ReleaseStatus.APPROVED,
            changes=request.changes,
            created_by=request.created_by,
            created_at=self.clock.now(),
            applied_by=None,
            applied_at=None
        )
        
        # Save release
        await self.env_store.create_release(release)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.created_by,
            action=AuditAction.CREATE,
            target_type=AuditTargetType.RELEASE,
            target_id=release.id,
            before_json=None,
            after_json=release.to_dict(),
            reason=f"Created release {request.title}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return release
    
    async def _requires_approval(self, environment: str) -> bool:
        """Check if environment requires approval"""
        # This would typically check against policies
        # For now, assume prod environments require approval
        return environment.lower() in ['prod', 'production']


class ApproveReleaseUseCase:
    """Use case for approving releases"""
    
    def __init__(self, env_store: EnvStore, clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: ApproveReleaseRequest) -> Approval:
        """Approve a release"""
        # Get release
        release = await self.env_store.get_release_by_id(request.release_id)
        if not release:
            raise ValueError(f"Release {request.release_id} not found")
        
        if not release.can_be_approved():
            raise ValueError(f"Release {request.release_id} cannot be approved in current status {release.status}")
        
        # Create approval
        approval = Approval(
            id=self.id_generator.generate(),
            release_id=request.release_id,
            approver_id=request.approver_id,
            decision=ApprovalDecision.APPROVED,
            comment=request.comment,
            decided_at=self.clock.now()
        )
        
        # Save approval
        await self.env_store.create_approval(approval)
        
        # Update release status
        release.status = ReleaseStatus.APPROVED
        await self.env_store.update_release(release)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.approver_id,
            action=AuditAction.APPROVE,
            target_type=AuditTargetType.RELEASE,
            target_id=request.release_id,
            before_json={'status': ReleaseStatus.PENDING_APPROVAL.value},
            after_json={'status': ReleaseStatus.APPROVED.value},
            reason=f"Approved release {release.title}: {request.comment or 'No comment'}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return approval


class ApplyReleaseUseCase:
    """Use case for applying releases"""
    
    def __init__(self, env_store: EnvStore, clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: ApplyReleaseRequest) -> Release:
        """Apply a release"""
        # Get release
        release = await self.env_store.get_release_by_id(request.release_id)
        if not release:
            raise ValueError(f"Release {request.release_id} not found")
        
        if not release.can_be_applied():
            raise ValueError(f"Release {request.release_id} cannot be applied in current status {release.status}")
        
        # Apply changes
        for change in release.changes:
            await self._apply_change(change, request.applied_by)
        
        # Update release status
        release.status = ReleaseStatus.APPLIED
        release.applied_by = request.applied_by
        release.applied_at = self.clock.now()
        await self.env_store.update_release(release)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.applied_by,
            action=AuditAction.APPLY,
            target_type=AuditTargetType.RELEASE,
            target_id=request.release_id,
            before_json={'status': ReleaseStatus.APPROVED.value},
            after_json={'status': ReleaseStatus.APPLIED.value},
            reason=f"Applied release {release.title}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return release
    
    async def _apply_change(self, change: Dict[str, Any], applied_by: str):
        """Apply a single change from the release"""
        action = change.get('action')
        env_var_id = change.get('env_var_id')
        
        if action == 'CREATE':
            # Create new environment variable
            # This would typically involve creating the EnvVar object
            pass
        elif action == 'UPDATE':
            # Update existing environment variable
            # This would typically involve updating the EnvVar object
            pass
        elif action == 'DELETE':
            # Delete environment variable
            # This would typically involve deleting the EnvVar object
            pass
