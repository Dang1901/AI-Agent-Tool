"""
Port interface for environment variable storage
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domain.env_var import EnvVar
from ..domain.env_var_version import EnvVarVersion
from ..domain.release import Release
from ..domain.approval import Approval
from ..domain.audit_event import AuditEvent


class EnvStore(ABC):
    """Abstract interface for environment variable storage"""
    
    @abstractmethod
    async def create(self, env_var: EnvVar) -> EnvVar:
        """Create a new environment variable"""
        pass
    
    @abstractmethod
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        """Get environment variable by ID"""
        pass
    
    @abstractmethod
    async def get_by_unique_key(self, scope_level: str, scope_ref_id: str, key: str) -> Optional[EnvVar]:
        """Get environment variable by unique key (scope + key)"""
        pass
    
    @abstractmethod
    async def update(self, env_var: EnvVar) -> EnvVar:
        """Update an environment variable"""
        pass
    
    @abstractmethod
    async def delete(self, env_var_id: str) -> bool:
        """Delete an environment variable"""
        pass
    
    @abstractmethod
    async def list(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[EnvVar]:
        """List environment variables with filtering and pagination"""
        pass
    
    @abstractmethod
    async def count(self, filters: Dict[str, Any]) -> int:
        """Count environment variables matching filters"""
        pass
    
    # Version management
    @abstractmethod
    async def create_version(self, version: EnvVarVersion) -> EnvVarVersion:
        """Create a new version record"""
        pass
    
    @abstractmethod
    async def get_versions(self, env_var_id: str) -> List[EnvVarVersion]:
        """Get all versions for an environment variable"""
        pass
    
    @abstractmethod
    async def get_next_version(self, env_var_id: str) -> int:
        """Get next version number for an environment variable"""
        pass
    
    @abstractmethod
    async def rollback_to_version(self, env_var_id: str, version: int, rolled_back_by: str) -> EnvVar:
        """Rollback environment variable to a specific version"""
        pass
    
    # Release management
    @abstractmethod
    async def create_release(self, release: Release) -> Release:
        """Create a new release"""
        pass
    
    @abstractmethod
    async def get_release_by_id(self, release_id: str) -> Optional[Release]:
        """Get release by ID"""
        pass
    
    @abstractmethod
    async def update_release(self, release: Release) -> Release:
        """Update a release"""
        pass
    
    @abstractmethod
    async def list_releases(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[Release]:
        """List releases with filtering and pagination"""
        pass
    
    # Approval management
    @abstractmethod
    async def create_approval(self, approval: Approval) -> Approval:
        """Create a new approval"""
        pass
    
    @abstractmethod
    async def get_approvals_for_release(self, release_id: str) -> List[Approval]:
        """Get all approvals for a release"""
        pass
    
    @abstractmethod
    async def get_approval_by_id(self, approval_id: str) -> Optional[Approval]:
        """Get approval by ID"""
        pass
    
    # Audit management
    @abstractmethod
    async def create_audit_event(self, event: AuditEvent) -> AuditEvent:
        """Create an audit event"""
        pass
    
    @abstractmethod
    async def get_audit_events(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[AuditEvent]:
        """Get audit events with filtering and pagination"""
        pass
    
    # Rotation management
    @abstractmethod
    async def create_rotation_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rotation schedule"""
        pass
    
    @abstractmethod
    async def get_rotation_schedules(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get rotation schedules"""
        pass
    
    @abstractmethod
    async def update_rotation_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a rotation schedule"""
        pass
