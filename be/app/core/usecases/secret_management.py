"""
Use cases for secret management
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..domain.env_var import EnvVar
from ..domain.audit_event import AuditEvent, AuditAction, AuditTargetType
from ..ports.env_store import EnvStore
from ..ports.secret_cipher import SecretCipher
from ..ports.clock import Clock
from ..ports.id_generator import IdGenerator


@dataclass
class RevealSecretRequest:
    """Request to reveal a secret"""
    env_var_id: str
    justification: str
    requested_by: str
    ttl_seconds: int = 30


@dataclass
class RevealSecretResponse:
    """Response for revealing a secret"""
    value: str
    expires_at: datetime
    ttl_seconds: int


class RevealSecretUseCase:
    """Use case for revealing secrets with TTL"""
    
    def __init__(self, env_store: EnvStore, secret_cipher: SecretCipher,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.secret_cipher = secret_cipher
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: RevealSecretRequest) -> RevealSecretResponse:
        """Reveal a secret with TTL"""
        # Get environment variable
        env_var = await self.env_store.get_by_id(request.env_var_id)
        if not env_var:
            raise ValueError(f"Environment variable {request.env_var_id} not found")
        
        if not env_var.is_secret:
            raise ValueError(f"Environment variable {env_var.key} is not a secret")
        
        # Decrypt the value
        decrypted_value = await self.secret_cipher.decrypt(env_var.value)
        
        # Calculate expiration time
        expires_at = self.clock.now() + timedelta(seconds=request.ttl_seconds)
        
        # Create audit event for secret reveal
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.requested_by,
            action=AuditAction.REVEAL,
            target_type=AuditTargetType.ENV_VAR,
            target_id=env_var.id,
            before_json=None,
            after_json={'justification': request.justification, 'ttl_seconds': request.ttl_seconds},
            reason=f"Revealed secret {env_var.key}: {request.justification}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return RevealSecretResponse(
            value=decrypted_value,
            expires_at=expires_at,
            ttl_seconds=request.ttl_seconds
        )


class RotateSecretUseCase:
    """Use case for rotating secrets"""
    
    def __init__(self, env_store: EnvStore, secret_cipher: SecretCipher,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.secret_cipher = secret_cipher
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, env_var_id: str, new_value: str, rotated_by: str) -> EnvVar:
        """Rotate a secret value"""
        # Get existing environment variable
        existing = await self.env_store.get_by_id(env_var_id)
        if not existing:
            raise ValueError(f"Environment variable {env_var_id} not found")
        
        if not existing.is_secret:
            raise ValueError(f"Environment variable {existing.key} is not a secret")
        
        # Create version before rotation
        before_dict = existing.to_dict()
        
        # Encrypt new value
        encrypted_new_value = await self.secret_cipher.encrypt(new_value)
        
        # Update environment variable
        updated_env_var = EnvVar(
            id=existing.id,
            key=existing.key,
            value=encrypted_new_value,
            type=existing.type,
            scope=existing.scope,
            tags=existing.tags,
            description=existing.description,
            is_secret=existing.is_secret,
            status=existing.status,
            created_by=existing.created_by,
            created_at=existing.created_at,
            updated_by=rotated_by,
            updated_at=self.clock.now()
        )
        
        # Save updated environment variable
        await self.env_store.update(updated_env_var)
        
        # Create version record
        from ..domain.env_var_version import EnvVarVersion
        version = EnvVarVersion(
            id=self.id_generator.generate(),
            env_var_id=updated_env_var.id,
            version=await self.env_store.get_next_version(updated_env_var.id),
            diff_json={
                'value': {'old': '***', 'new': '***'},  # Don't expose actual values
                'rotation': True
            },
            checksum="",  # Will be computed in __post_init__
            author=rotated_by,
            created_at=self.clock.now()
        )
        await self.env_store.create_version(version)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=rotated_by,
            action=AuditAction.UPDATE,
            target_type=AuditTargetType.ENV_VAR,
            target_id=updated_env_var.id,
            before_json=before_dict,
            after_json=updated_env_var.to_dict(),
            reason=f"Rotated secret {updated_env_var.key}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return updated_env_var


class ScheduleRotationUseCase:
    """Use case for scheduling secret rotations"""
    
    def __init__(self, env_store: EnvStore, clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, env_var_id: str, rotation_schedule: str, scheduled_by: str) -> Dict[str, Any]:
        """Schedule automatic rotation for a secret"""
        # Get environment variable
        env_var = await self.env_store.get_by_id(env_var_id)
        if not env_var:
            raise ValueError(f"Environment variable {env_var_id} not found")
        
        if not env_var.is_secret:
            raise ValueError(f"Environment variable {env_var.key} is not a secret")
        
        # Create rotation schedule record
        rotation_record = {
            'id': self.id_generator.generate(),
            'env_var_id': env_var_id,
            'schedule': rotation_schedule,
            'created_by': scheduled_by,
            'created_at': self.clock.now(),
            'status': 'ACTIVE'
        }
        
        # Save rotation schedule
        await self.env_store.create_rotation_schedule(rotation_record)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=scheduled_by,
            action=AuditAction.UPDATE,
            target_type=AuditTargetType.ENV_VAR,
            target_id=env_var_id,
            before_json=None,
            after_json={'rotation_schedule': rotation_schedule},
            reason=f"Scheduled rotation for secret {env_var.key}",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return rotation_record
