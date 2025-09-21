"""
Use cases for environment variable management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..domain.env_var import EnvVar, EnvVarType, ScopeRef, ScopeLevel, EnvVarStatus
from ..domain.env_var_version import EnvVarVersion
from ..domain.audit_event import AuditEvent, AuditAction, AuditTargetType
from ..ports.env_store import EnvStore
from ..ports.secret_cipher import SecretCipher
from ..ports.clock import Clock
from ..ports.id_generator import IdGenerator


@dataclass
class CreateEnvVarRequest:
    """Request to create environment variable"""
    key: str
    value: str
    type: EnvVarType
    scope: ScopeRef
    tags: List[str]
    description: Optional[str]
    is_secret: bool
    created_by: str


@dataclass
class UpdateEnvVarRequest:
    """Request to update environment variable"""
    env_var_id: str
    value: Optional[str]
    type: Optional[EnvVarType]
    tags: Optional[List[str]]
    description: Optional[str]
    updated_by: str


@dataclass
class ListEnvVarsRequest:
    """Request to list environment variables"""
    scope_level: Optional[ScopeLevel]
    scope_ref_id: Optional[str]
    key_filter: Optional[str]
    tag_filter: Optional[str]
    type_filter: Optional[EnvVarType]
    status_filter: Optional[EnvVarStatus]
    page: int = 1
    size: int = 50


@dataclass
class ListEnvVarsResponse:
    """Response for listing environment variables"""
    env_vars: List[EnvVar]
    total: int
    page: int
    size: int


class CreateEnvVarUseCase:
    """Use case for creating environment variables"""
    
    def __init__(self, env_store: EnvStore, secret_cipher: SecretCipher, 
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.secret_cipher = secret_cipher
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: CreateEnvVarRequest) -> EnvVar:
        """Create a new environment variable"""
        # Check if key already exists in scope
        existing = await self.env_store.get_by_unique_key(
            request.scope.level.value, 
            request.scope.ref_id, 
            request.key
        )
        if existing:
            raise ValueError(f"Environment variable {request.key} already exists in scope {request.scope}")
        
        # Encrypt value if it's a secret
        encrypted_value = request.value
        if request.is_secret:
            encrypted_value = await self.secret_cipher.encrypt(request.value)
        
        # Create environment variable
        now = self.clock.now()
        env_var = EnvVar(
            id=self.id_generator.generate(),
            key=request.key,
            value=encrypted_value,
            type=request.type,
            scope=request.scope,
            tags=request.tags,
            description=request.description,
            is_secret=request.is_secret,
            status=EnvVarStatus.ACTIVE,
            created_by=request.created_by,
            created_at=now,
            updated_by=request.created_by,
            updated_at=now
        )
        
        # Save to store
        await self.env_store.create(env_var)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.created_by,
            action=AuditAction.CREATE,
            target_type=AuditTargetType.ENV_VAR,
            target_id=env_var.id,
            before_json=None,
            after_json=env_var.to_dict(),
            reason=f"Created environment variable {request.key}",
            timestamp=now
        )
        await self.env_store.create_audit_event(audit_event)
        
        return env_var


class UpdateEnvVarUseCase:
    """Use case for updating environment variables"""
    
    def __init__(self, env_store: EnvStore, secret_cipher: SecretCipher,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.secret_cipher = secret_cipher
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: UpdateEnvVarRequest) -> EnvVar:
        """Update an environment variable"""
        # Get existing environment variable
        existing = await self.env_store.get_by_id(request.env_var_id)
        if not existing:
            raise ValueError(f"Environment variable {request.env_var_id} not found")
        
        # Create version before update
        before_dict = existing.to_dict()
        
        # Update fields
        updated_env_var = EnvVar(
            id=existing.id,
            key=existing.key,
            value=request.value if request.value is not None else existing.value,
            type=request.type if request.type is not None else existing.type,
            scope=existing.scope,
            tags=request.tags if request.tags is not None else existing.tags,
            description=request.description if request.description is not None else existing.description,
            is_secret=existing.is_secret,
            status=existing.status,
            created_by=existing.created_by,
            created_at=existing.created_at,
            updated_by=request.updated_by,
            updated_at=self.clock.now()
        )
        
        # Encrypt value if it's a secret and value changed
        if updated_env_var.is_secret and request.value is not None:
            updated_env_var.value = await self.secret_cipher.encrypt(request.value)
        
        # Save updated environment variable
        await self.env_store.update(updated_env_var)
        
        # Create version record
        version = EnvVarVersion(
            id=self.id_generator.generate(),
            env_var_id=updated_env_var.id,
            version=await self.env_store.get_next_version(updated_env_var.id),
            diff_json={
                'value': {'old': existing.value, 'new': updated_env_var.value},
                'type': {'old': existing.type.value, 'new': updated_env_var.type.value},
                'tags': {'old': existing.tags, 'new': updated_env_var.tags},
                'description': {'old': existing.description, 'new': updated_env_var.description}
            },
            checksum="",  # Will be computed in __post_init__
            author=request.updated_by,
            created_at=self.clock.now()
        )
        await self.env_store.create_version(version)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.updated_by,
            action=AuditAction.UPDATE,
            target_type=AuditTargetType.ENV_VAR,
            target_id=updated_env_var.id,
            before_json=before_dict,
            after_json=updated_env_var.to_dict(),
            reason=f"Updated environment variable {updated_env_var.key}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return updated_env_var


class DeleteEnvVarUseCase:
    """Use case for deleting environment variables"""
    
    def __init__(self, env_store: EnvStore, clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, env_var_id: str, deleted_by: str) -> bool:
        """Delete an environment variable"""
        # Get existing environment variable
        existing = await self.env_store.get_by_id(env_var_id)
        if not existing:
            raise ValueError(f"Environment variable {env_var_id} not found")
        
        # Check if it's a restricted environment that requires approval
        if existing.is_restricted_environment():
            raise ValueError(f"Cannot delete environment variable in restricted environment {existing.scope}")
        
        # Create audit event before deletion
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=deleted_by,
            action=AuditAction.DELETE,
            target_type=AuditTargetType.ENV_VAR,
            target_id=env_var_id,
            before_json=existing.to_dict(),
            after_json=None,
            reason=f"Deleted environment variable {existing.key}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        # Delete from store
        await self.env_store.delete(env_var_id)
        
        return True


class ListEnvVarsUseCase:
    """Use case for listing environment variables"""
    
    def __init__(self, env_store: EnvStore):
        self.env_store = env_store
    
    async def execute(self, request: ListEnvVarsRequest) -> ListEnvVarsResponse:
        """List environment variables with filtering and pagination"""
        # Build filter criteria
        filters = {}
        if request.scope_level:
            filters['scope_level'] = request.scope_level.value
        if request.scope_ref_id:
            filters['scope_ref_id'] = request.scope_ref_id
        if request.key_filter:
            filters['key_filter'] = request.key_filter
        if request.tag_filter:
            filters['tag_filter'] = request.tag_filter
        if request.type_filter:
            filters['type_filter'] = request.type_filter.value
        if request.status_filter:
            filters['status_filter'] = request.status_filter.value
        
        # Get total count
        total = await self.env_store.count(filters)
        
        # Get paginated results
        env_vars = await self.env_store.list(
            filters=filters,
            page=request.page,
            size=request.size
        )
        
        return ListEnvVarsResponse(
            env_vars=env_vars,
            total=total,
            page=request.page,
            size=request.size
        )


class DiffEnvironmentsUseCase:
    """Use case for comparing environments"""
    
    def __init__(self, env_store: EnvStore):
        self.env_store = env_store
    
    async def execute(self, env1: str, env2: str) -> Dict[str, Any]:
        """Compare two environments and return differences"""
        # Get all environment variables for both environments
        env1_vars = await self.env_store.list({'scope_level': 'ENV', 'scope_ref_id': env1})
        env2_vars = await self.env_store.list({'scope_level': 'ENV', 'scope_ref_id': env2})
        
        # Create key-value maps
        env1_map = {var.key: var for var in env1_vars}
        env2_map = {var.key: var for var in env2_vars}
        
        # Find differences
        all_keys = set(env1_map.keys()) | set(env2_map.keys())
        
        missing_in_env2 = []
        missing_in_env1 = []
        different_values = []
        
        for key in all_keys:
            var1 = env1_map.get(key)
            var2 = env2_map.get(key)
            
            if var1 and not var2:
                missing_in_env2.append(var1)
            elif var2 and not var1:
                missing_in_env1.append(var2)
            elif var1 and var2 and var1.value != var2.value:
                different_values.append({
                    'key': key,
                    'env1_value': var1.get_masked_value(),
                    'env2_value': var2.get_masked_value(),
                    'env1_var': var1,
                    'env2_var': var2
                })
        
        return {
            'env1': env1,
            'env2': env2,
            'missing_in_env2': [var.to_dict() for var in missing_in_env2],
            'missing_in_env1': [var.to_dict() for var in missing_in_env1],
            'different_values': different_values,
            'summary': {
                'total_keys': len(all_keys),
                'missing_in_env2_count': len(missing_in_env2),
                'missing_in_env1_count': len(missing_in_env1),
                'different_count': len(different_values)
            }
        }
