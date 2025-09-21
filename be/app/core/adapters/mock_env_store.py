"""
Mock implementation of EnvStore for testing
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from ..domain.env_var import EnvVar
from ..domain.env_var_version import EnvVarVersion
from ..domain.release import Release
from ..domain.approval import Approval
from ..domain.audit_event import AuditEvent
from ..ports.env_store import EnvStore


class MockEnvStore(EnvStore):
    """Mock implementation of EnvStore for testing"""
    
    def __init__(self):
        self.env_vars: Dict[str, EnvVar] = {}
        self.versions: Dict[str, List[EnvVarVersion]] = {}
        self.releases: Dict[str, Release] = {}
        self.approvals: Dict[str, List[Approval]] = {}
        self.audit_events: List[AuditEvent] = []
        self.rotation_schedules: Dict[str, Dict[str, Any]] = {}
    
    async def create(self, env_var: EnvVar) -> EnvVar:
        """Create a new environment variable"""
        self.env_vars[env_var.id] = env_var
        return env_var
    
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        """Get environment variable by ID"""
        return self.env_vars.get(env_var_id)
    
    async def get_by_unique_key(self, scope_level: str, scope_ref_id: str, key: str) -> Optional[EnvVar]:
        """Get environment variable by unique key"""
        for env_var in self.env_vars.values():
            if (env_var.scope.level.value == scope_level and 
                env_var.scope.ref_id == scope_ref_id and 
                env_var.key == key):
                return env_var
        return None
    
    async def update(self, env_var: EnvVar) -> EnvVar:
        """Update an environment variable"""
        self.env_vars[env_var.id] = env_var
        return env_var
    
    async def delete(self, env_var_id: str) -> bool:
        """Delete an environment variable"""
        if env_var_id in self.env_vars:
            del self.env_vars[env_var_id]
            return True
        return False
    
    async def list(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[EnvVar]:
        """List environment variables with filtering and pagination"""
        filtered_vars = []
        
        for env_var in self.env_vars.values():
            if self._matches_filters(env_var, filters):
                filtered_vars.append(env_var)
        
        # Simple pagination
        start = (page - 1) * size
        end = start + size
        return filtered_vars[start:end]
    
    async def count(self, filters: Dict[str, Any]) -> int:
        """Count environment variables matching filters"""
        count = 0
        for env_var in self.env_vars.values():
            if self._matches_filters(env_var, filters):
                count += 1
        return count
    
    def _matches_filters(self, env_var: EnvVar, filters: Dict[str, Any]) -> bool:
        """Check if environment variable matches filters"""
        if 'scope_level' in filters and env_var.scope.level.value != filters['scope_level']:
            return False
        
        if 'scope_ref_id' in filters and env_var.scope.ref_id != filters['scope_ref_id']:
            return False
        
        if 'key_filter' in filters and filters['key_filter'] not in env_var.key:
            return False
        
        if 'tag_filter' in filters:
            if not any(tag for tag in env_var.tags if filters['tag_filter'] in tag):
                return False
        
        if 'type_filter' in filters and env_var.type.value != filters['type_filter']:
            return False
        
        if 'status_filter' in filters and env_var.status.value != filters['status_filter']:
            return False
        
        return True
    
    # Version management
    async def create_version(self, version: EnvVarVersion) -> EnvVarVersion:
        """Create a new version record"""
        if version.env_var_id not in self.versions:
            self.versions[version.env_var_id] = []
        self.versions[version.env_var_id].append(version)
        return version
    
    async def get_versions(self, env_var_id: str) -> List[EnvVarVersion]:
        """Get all versions for an environment variable"""
        return self.versions.get(env_var_id, [])
    
    async def get_next_version(self, env_var_id: str) -> int:
        """Get next version number for an environment variable"""
        versions = self.versions.get(env_var_id, [])
        if not versions:
            return 1
        return max(v.version for v in versions) + 1
    
    async def rollback_to_version(self, env_var_id: str, version: int, rolled_back_by: str) -> EnvVar:
        """Rollback environment variable to a specific version"""
        versions = self.versions.get(env_var_id, [])
        target_version = next((v for v in versions if v.version == version), None)
        
        if not target_version:
            raise ValueError(f"Version {version} not found for environment variable {env_var_id}")
        
        # Get current env_var
        env_var = await self.get_by_id(env_var_id)
        if not env_var:
            raise ValueError(f"Environment variable {env_var_id} not found")
        
        # Apply version changes
        # This is a simplified implementation
        # In reality, you'd need to apply the diff_json changes
        
        return env_var
    
    # Release management
    async def create_release(self, release: Release) -> Release:
        """Create a new release"""
        self.releases[release.id] = release
        return release
    
    async def get_release_by_id(self, release_id: str) -> Optional[Release]:
        """Get release by ID"""
        return self.releases.get(release_id)
    
    async def update_release(self, release: Release) -> Release:
        """Update a release"""
        self.releases[release.id] = release
        return release
    
    async def list_releases(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[Release]:
        """List releases with filtering and pagination"""
        filtered_releases = []
        
        for release in self.releases.values():
            if self._matches_release_filters(release, filters):
                filtered_releases.append(release)
        
        # Simple pagination
        start = (page - 1) * size
        end = start + size
        return filtered_releases[start:end]
    
    def _matches_release_filters(self, release: Release, filters: Dict[str, Any]) -> bool:
        """Check if release matches filters"""
        if 'service_id' in filters and release.service_id != filters['service_id']:
            return False
        
        if 'environment' in filters and release.environment != filters['environment']:
            return False
        
        if 'status' in filters and release.status.value != filters['status']:
            return False
        
        return True
    
    # Approval management
    async def create_approval(self, approval: Approval) -> Approval:
        """Create a new approval"""
        if approval.release_id not in self.approvals:
            self.approvals[approval.release_id] = []
        self.approvals[approval.release_id].append(approval)
        return approval
    
    async def get_approvals_for_release(self, release_id: str) -> List[Approval]:
        """Get all approvals for a release"""
        return self.approvals.get(release_id, [])
    
    async def get_approval_by_id(self, approval_id: str) -> Optional[Approval]:
        """Get approval by ID"""
        for approvals in self.approvals.values():
            for approval in approvals:
                if approval.id == approval_id:
                    return approval
        return None
    
    # Audit management
    async def create_audit_event(self, event: AuditEvent) -> AuditEvent:
        """Create an audit event"""
        self.audit_events.append(event)
        return event
    
    async def get_audit_events(self, filters: Dict[str, Any], page: int = 1, size: int = 50) -> List[AuditEvent]:
        """Get audit events with filtering and pagination"""
        filtered_events = []
        
        for event in self.audit_events:
            if self._matches_audit_filters(event, filters):
                filtered_events.append(event)
        
        # Simple pagination
        start = (page - 1) * size
        end = start + size
        return filtered_events[start:end]
    
    def _matches_audit_filters(self, event: AuditEvent, filters: Dict[str, Any]) -> bool:
        """Check if audit event matches filters"""
        if 'actor' in filters and event.actor != filters['actor']:
            return False
        
        if 'action' in filters and event.action.value != filters['action']:
            return False
        
        if 'target_type' in filters and event.target_type.value != filters['target_type']:
            return False
        
        if 'target_id' in filters and event.target_id != filters['target_id']:
            return False
        
        return True
    
    # Rotation management
    async def create_rotation_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rotation schedule"""
        schedule_id = schedule['id']
        self.rotation_schedules[schedule_id] = schedule
        return schedule
    
    async def get_rotation_schedules(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get rotation schedules"""
        filtered_schedules = []
        
        for schedule in self.rotation_schedules.values():
            if self._matches_rotation_filters(schedule, filters):
                filtered_schedules.append(schedule)
        
        return filtered_schedules
    
    async def update_rotation_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a rotation schedule"""
        if schedule_id in self.rotation_schedules:
            self.rotation_schedules[schedule_id].update(updates)
            return self.rotation_schedules[schedule_id]
        return {}
    
    def _matches_rotation_filters(self, schedule: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if rotation schedule matches filters"""
        if 'env_var_id' in filters and schedule.get('env_var_id') != filters['env_var_id']:
            return False
        
        if 'status' in filters and schedule.get('status') != filters['status']:
            return False
        
        return True
