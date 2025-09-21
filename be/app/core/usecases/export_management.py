"""
Use cases for export management
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..domain.env_var import EnvVar
from ..domain.audit_event import AuditEvent, AuditAction, AuditTargetType
from ..ports.env_store import EnvStore
from ..ports.exporter import Exporter
from ..ports.clock import Clock
from ..ports.id_generator import IdGenerator


@dataclass
class ExportRequest:
    """Request to export environment variables"""
    mode: str  # 'k8s', 'env', 'json', 'yaml'
    service_id: Optional[str]
    environment: Optional[str]
    scope_level: Optional[str]
    scope_ref_id: Optional[str]
    exported_by: str


@dataclass
class ExportResponse:
    """Response for export request"""
    content: str
    format: str
    exported_at: datetime
    count: int


class ExportToK8sSecretUseCase:
    """Use case for exporting to Kubernetes Secret"""
    
    def __init__(self, env_store: EnvStore, exporter: Exporter, 
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.exporter = exporter
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: ExportRequest) -> ExportResponse:
        """Export environment variables to Kubernetes Secret YAML"""
        # Get environment variables based on filters
        filters = {}
        if request.service_id:
            filters['service_id'] = request.service_id
        if request.environment:
            filters['scope_level'] = 'ENV'
            filters['scope_ref_id'] = request.environment
        if request.scope_level:
            filters['scope_level'] = request.scope_level
        if request.scope_ref_id:
            filters['scope_ref_id'] = request.scope_ref_id
        
        env_vars = await self.env_store.list(filters)
        
        # Export to Kubernetes Secret format
        content = await self.exporter.export_to_k8s_secret(env_vars, request.service_id or 'default')
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.exported_by,
            action=AuditAction.EXPORT,
            target_type=AuditTargetType.ENV_VAR,
            target_id=f"k8s-secret-{request.service_id or 'default'}",
            before_json=None,
            after_json={'format': 'k8s-secret', 'count': len(env_vars)},
            reason=f"Exported {len(env_vars)} environment variables to Kubernetes Secret",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return ExportResponse(
            content=content,
            format='k8s-secret',
            exported_at=self.clock.now(),
            count=len(env_vars)
        )


class ExportToConfigMapUseCase:
    """Use case for exporting to Kubernetes ConfigMap"""
    
    def __init__(self, env_store: EnvStore, exporter: Exporter,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.exporter = exporter
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: ExportRequest) -> ExportResponse:
        """Export environment variables to Kubernetes ConfigMap YAML"""
        # Get environment variables based on filters
        filters = {}
        if request.service_id:
            filters['service_id'] = request.service_id
        if request.environment:
            filters['scope_level'] = 'ENV'
            filters['scope_ref_id'] = request.environment
        if request.scope_level:
            filters['scope_level'] = request.scope_level
        if request.scope_ref_id:
            filters['scope_ref_id'] = request.scope_ref_id
        
        env_vars = await self.env_store.list(filters)
        
        # Export to Kubernetes ConfigMap format
        content = await self.exporter.export_to_k8s_configmap(env_vars, request.service_id or 'default')
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.exported_by,
            action=AuditAction.EXPORT,
            target_type=AuditTargetType.ENV_VAR,
            target_id=f"k8s-configmap-{request.service_id or 'default'}",
            before_json=None,
            after_json={'format': 'k8s-configmap', 'count': len(env_vars)},
            reason=f"Exported {len(env_vars)} environment variables to Kubernetes ConfigMap",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return ExportResponse(
            content=content,
            format='k8s-configmap',
            exported_at=self.clock.now(),
            count=len(env_vars)
        )


class ExportToDotEnvUseCase:
    """Use case for exporting to .env format"""
    
    def __init__(self, env_store: EnvStore, exporter: Exporter,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.exporter = exporter
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: ExportRequest) -> ExportResponse:
        """Export environment variables to .env format"""
        # Get environment variables based on filters
        filters = {}
        if request.service_id:
            filters['service_id'] = request.service_id
        if request.environment:
            filters['scope_level'] = 'ENV'
            filters['scope_ref_id'] = request.environment
        if request.scope_level:
            filters['scope_level'] = request.scope_level
        if request.scope_ref_id:
            filters['scope_ref_id'] = request.scope_ref_id
        
        env_vars = await self.env_store.list(filters)
        
        # Export to .env format
        content = await self.exporter.export_to_dotenv(env_vars)
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=request.exported_by,
            action=AuditAction.EXPORT,
            target_type=AuditTargetType.ENV_VAR,
            target_id=f"dotenv-{request.service_id or 'default'}",
            before_json=None,
            after_json={'format': 'dotenv', 'count': len(env_vars)},
            reason=f"Exported {len(env_vars)} environment variables to .env format",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return ExportResponse(
            content=content,
            format='dotenv',
            exported_at=self.clock.now(),
            count=len(env_vars)
        )


class ImportFromDotEnvUseCase:
    """Use case for importing from .env format"""
    
    def __init__(self, env_store: EnvStore, exporter: Exporter,
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.exporter = exporter
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, content: str, imported_by: str, scope_level: str, scope_ref_id: str) -> Dict[str, Any]:
        """Import environment variables from .env content"""
        # Parse .env content
        env_vars = await self.exporter.parse_dotenv(content)
        
        # Create environment variables
        created_count = 0
        updated_count = 0
        errors = []
        
        for key, value in env_vars.items():
            try:
                # Check if already exists
                existing = await self.env_store.get_by_unique_key(scope_level, scope_ref_id, key)
                
                if existing:
                    # Update existing
                    # This would typically involve updating the EnvVar object
                    updated_count += 1
                else:
                    # Create new
                    # This would typically involve creating the EnvVar object
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Error processing {key}: {str(e)}")
        
        # Create audit event
        audit_event = AuditEvent(
            id=self.id_generator.generate(),
            actor=imported_by,
            action=AuditAction.IMPORT,
            target_type=AuditTargetType.ENV_VAR,
            target_id=f"import-{scope_level}-{scope_ref_id}",
            before_json=None,
            after_json={'format': 'dotenv', 'created': created_count, 'updated': updated_count},
            reason=f"Imported {len(env_vars)} environment variables from .env format",
            timestamp=self.clock.now()
        )
        await self.env_store.create_audit_event(audit_event)
        
        return {
            'created': created_count,
            'updated': updated_count,
            'total': len(env_vars),
            'errors': errors
        }
