"""
REST endpoints for environment variables
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.domain.env_var import EnvVar, EnvVarType, ScopeRef, ScopeLevel, EnvVarStatus
from app.core.usecases.env_var_management import (
    CreateEnvVarUseCase, CreateEnvVarRequest,
    UpdateEnvVarUseCase, UpdateEnvVarRequest,
    DeleteEnvVarUseCase,
    ListEnvVarsUseCase, ListEnvVarsRequest, ListEnvVarsResponse,
    DiffEnvironmentsUseCase
)
from app.core.usecases.secret_management import (
    RevealSecretUseCase, RevealSecretRequest, RevealSecretResponse
)
from app.core.usecases.export_management import (
    ExportToK8sSecretUseCase, ExportToConfigMapUseCase, ExportToDotEnvUseCase,
    ExportRequest, ExportResponse
)
from app.adapters.sqlalchemy_env_store import SqlAlchemyEnvStore
from app.adapters.crypto_cipher import CryptoCipher
from app.adapters.k8s_yaml_exporter import K8sYamlExporter
from app.adapters.slack_notifier import SlackNotifier
from app.core.adapters.mock_clock import MockClock
from app.core.adapters.mock_id_generator import MockIdGenerator

router = APIRouter(prefix="/envvars", tags=["Environment Variables"])


def get_env_store(db: Session = Depends(get_db)) -> SqlAlchemyEnvStore:
    """Get environment variable store"""
    return SqlAlchemyEnvStore(db)


def get_secret_cipher() -> CryptoCipher:
    """Get secret cipher"""
    return CryptoCipher()


def get_exporter() -> K8sYamlExporter:
    """Get exporter"""
    return K8sYamlExporter()


def get_notifier() -> SlackNotifier:
    """Get notifier"""
    return SlackNotifier()


def get_clock() -> MockClock:
    """Get clock"""
    return MockClock()


def get_id_generator() -> MockIdGenerator:
    """Get ID generator"""
    # TODO: Replace with real ID generator in production
    # For now, use MockIdGenerator with UUID v4 to avoid conflicts
    generator = MockIdGenerator()
    # Use UUID v4 method for reliable UUID generation
    generator.generate = generator.generate_uuid
    return generator


@router.post("/", response_model=Dict[str, Any])
async def create_env_var(
    key: str = Body(..., description="Environment variable key"),
    value: str = Body(..., description="Environment variable value"),
    type: str = Body(..., description="Environment variable type"),
    scope_level: str = Body(..., description="Scope level"),
    scope_ref_id: str = Body(..., description="Scope reference ID"),
    tags: List[str] = Body(default=[], description="Tags"),
    description: Optional[str] = Body(None, description="Description"),
    is_secret: bool = Body(False, description="Is secret"),
    created_by: str = Body(..., description="Created by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    secret_cipher: CryptoCipher = Depends(get_secret_cipher),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Create a new environment variable"""
    try:
        # Validate input
        env_var_type = EnvVarType(type)
        scope = ScopeRef(ScopeLevel(scope_level), scope_ref_id)
        
        # Create request
        request = CreateEnvVarRequest(
            key=key,
            value=value,
            type=env_var_type,
            scope=scope,
            tags=tags,
            description=description,
            is_secret=is_secret,
            created_by=created_by
        )
        
        # Execute use case
        use_case = CreateEnvVarUseCase(env_store, secret_cipher, clock, id_generator)
        result = await use_case.execute(request)
        
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ListEnvVarsResponse)
async def list_env_vars(
    scope_level: Optional[str] = Query(None, description="Filter by scope level"),
    scope_ref_id: Optional[str] = Query(None, description="Filter by scope reference ID"),
    key_filter: Optional[str] = Query(None, description="Filter by key"),
    tag_filter: Optional[str] = Query(None, description="Filter by tag"),
    type_filter: Optional[str] = Query(None, description="Filter by type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """List environment variables with filtering and pagination"""
    try:
        # Build request
        request = ListEnvVarsRequest(
            scope_level=ScopeLevel(scope_level) if scope_level else None,
            scope_ref_id=scope_ref_id,
            key_filter=key_filter,
            tag_filter=tag_filter,
            type_filter=EnvVarType(type_filter) if type_filter else None,
            status_filter=EnvVarStatus(status_filter) if status_filter else None,
            page=page,
            size=size
        )
        
        # Execute use case
        use_case = ListEnvVarsUseCase(env_store)
        result = await use_case.execute(request)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{env_var_id}", response_model=Dict[str, Any])
async def get_env_var(
    env_var_id: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Get environment variable by ID"""
    try:
        env_var = await env_store.get_by_id(env_var_id)
        if not env_var:
            raise HTTPException(status_code=404, detail="Environment variable not found")
        
        return env_var.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{env_var_id}", response_model=Dict[str, Any])
async def update_env_var(
    env_var_id: str,
    value: Optional[str] = Body(None, description="New value"),
    type: Optional[str] = Body(None, description="New type"),
    tags: Optional[List[str]] = Body(None, description="New tags"),
    description: Optional[str] = Body(None, description="New description"),
    updated_by: str = Body(..., description="Updated by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    secret_cipher: CryptoCipher = Depends(get_secret_cipher),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Update an environment variable"""
    try:
        # Validate input
        env_var_type = EnvVarType(type) if type else None
        
        # Create request
        request = UpdateEnvVarRequest(
            env_var_id=env_var_id,
            value=value,
            type=env_var_type,
            tags=tags,
            description=description,
            updated_by=updated_by
        )
        
        # Execute use case
        use_case = UpdateEnvVarUseCase(env_store, secret_cipher, clock, id_generator)
        result = await use_case.execute(request)
        
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{env_var_id}")
async def delete_env_var(
    env_var_id: str,
    deleted_by: str = Body(..., description="Deleted by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Delete an environment variable"""
    try:
        # Execute use case
        use_case = DeleteEnvVarUseCase(env_store, clock, id_generator)
        result = await use_case.execute(env_var_id, deleted_by)
        
        return {"success": result}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{env_var_id}/versions")
async def get_env_var_versions(
    env_var_id: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Get versions for an environment variable"""
    try:
        versions = await env_store.get_versions(env_var_id)
        return [version.to_dict() for version in versions]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{env_var_id}/rollback")
async def rollback_env_var(
    env_var_id: str,
    version: int = Body(..., description="Version to rollback to"),
    rolled_back_by: str = Body(..., description="Rolled back by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Rollback environment variable to a specific version"""
    try:
        result = await env_store.rollback_to_version(env_var_id, version, rolled_back_by)
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{env_var_id}/reveal", response_model=RevealSecretResponse)
async def reveal_secret(
    env_var_id: str,
    justification: str = Body(..., description="Justification for revealing secret"),
    ttl_seconds: int = Body(30, ge=1, le=300, description="TTL in seconds"),
    requested_by: str = Body(..., description="Requested by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    secret_cipher: CryptoCipher = Depends(get_secret_cipher),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Reveal a secret with TTL"""
    try:
        # Create request
        request = RevealSecretRequest(
            env_var_id=env_var_id,
            justification=justification,
            ttl_seconds=ttl_seconds,
            requested_by=requested_by
        )
        
        # Execute use case
        use_case = RevealSecretUseCase(env_store, secret_cipher, clock, id_generator)
        result = await use_case.execute(request)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/diff/{env1}/{env2}")
async def diff_environments(
    env1: str,
    env2: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Compare two environments"""
    try:
        use_case = DiffEnvironmentsUseCase(env_store)
        result = await use_case.execute(env1, env2)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/export/k8s-secret")
async def export_to_k8s_secret(
    service_id: str = Body(..., description="Service ID"),
    environment: Optional[str] = Body(None, description="Environment"),
    scope_level: Optional[str] = Body(None, description="Scope level"),
    scope_ref_id: Optional[str] = Body(None, description="Scope reference ID"),
    exported_by: str = Body(..., description="Exported by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    exporter: K8sYamlExporter = Depends(get_exporter),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Export environment variables to Kubernetes Secret YAML"""
    try:
        # Create request
        request = ExportRequest(
            mode="k8s-secret",
            service_id=service_id,
            environment=environment,
            scope_level=scope_level,
            scope_ref_id=scope_ref_id,
            exported_by=exported_by
        )
        
        # Execute use case
        use_case = ExportToK8sSecretUseCase(env_store, exporter, clock, id_generator)
        result = await use_case.execute(request)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/export/k8s-configmap")
async def export_to_k8s_configmap(
    service_id: str = Body(..., description="Service ID"),
    environment: Optional[str] = Body(None, description="Environment"),
    scope_level: Optional[str] = Body(None, description="Scope level"),
    scope_ref_id: Optional[str] = Body(None, description="Scope reference ID"),
    exported_by: str = Body(..., description="Exported by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    exporter: K8sYamlExporter = Depends(get_exporter),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Export environment variables to Kubernetes ConfigMap YAML"""
    try:
        # Create request
        request = ExportRequest(
            mode="k8s-configmap",
            service_id=service_id,
            environment=environment,
            scope_level=scope_level,
            scope_ref_id=scope_ref_id,
            exported_by=exported_by
        )
        
        # Execute use case
        use_case = ExportToConfigMapUseCase(env_store, exporter, clock, id_generator)
        result = await use_case.execute(request)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/export/dotenv")
async def export_to_dotenv(
    service_id: Optional[str] = Body(None, description="Service ID"),
    environment: Optional[str] = Body(None, description="Environment"),
    scope_level: Optional[str] = Body(None, description="Scope level"),
    scope_ref_id: Optional[str] = Body(None, description="Scope reference ID"),
    exported_by: str = Body(..., description="Exported by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    exporter: K8sYamlExporter = Depends(get_exporter),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Export environment variables to .env format"""
    try:
        # Create request
        request = ExportRequest(
            mode="dotenv",
            service_id=service_id,
            environment=environment,
            scope_level=scope_level,
            scope_ref_id=scope_ref_id,
            exported_by=exported_by
        )
        
        # Execute use case
        use_case = ExportToDotEnvUseCase(env_store, exporter, clock, id_generator)
        result = await use_case.execute(request)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
