"""
REST endpoints for releases
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.domain.release import Release, ReleaseStatus
from app.core.usecases.release_management import (
    CreateReleaseUseCase, CreateReleaseRequest,
    ApproveReleaseUseCase, ApproveReleaseRequest,
    ApplyReleaseUseCase, ApplyReleaseRequest
)
from app.adapters.sqlalchemy_env_store import SqlAlchemyEnvStore
from app.core.adapters.mock_clock import MockClock
from app.core.adapters.mock_id_generator import MockIdGenerator

router = APIRouter(prefix="/releases", tags=["Releases"])


def get_env_store(db: Session = Depends(get_db)) -> SqlAlchemyEnvStore:
    """Get environment variable store"""
    return SqlAlchemyEnvStore(db)


def get_clock() -> MockClock:
    """Get clock"""
    return MockClock()


def get_id_generator() -> MockIdGenerator:
    """Get ID generator"""
    return MockIdGenerator()


@router.post("/", response_model=Dict[str, Any])
async def create_release(
    service_id: str = Body(..., description="Service ID"),
    environment: str = Body(..., description="Environment"),
    title: str = Body(..., description="Release title"),
    description: Optional[str] = Body(None, description="Release description"),
    changes: List[Dict[str, Any]] = Body(..., description="List of changes"),
    created_by: str = Body(..., description="Created by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Create a new release"""
    try:
        # Create request
        request = CreateReleaseRequest(
            service_id=service_id,
            environment=environment,
            title=title,
            description=description,
            changes=changes,
            created_by=created_by
        )
        
        # Execute use case
        use_case = CreateReleaseUseCase(env_store, clock, id_generator)
        result = await use_case.execute(request)
        
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_releases(
    service_id: Optional[str] = Query(None, description="Filter by service ID"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """List releases with filtering and pagination"""
    try:
        # Build filters
        filters = {}
        if service_id:
            filters['service_id'] = service_id
        if environment:
            filters['environment'] = environment
        if status:
            filters['status'] = status
        
        # Get releases
        releases = await env_store.list_releases(filters, page, size)
        return [release.to_dict() for release in releases]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{release_id}", response_model=Dict[str, Any])
async def get_release(
    release_id: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Get release by ID"""
    try:
        release = await env_store.get_release_by_id(release_id)
        if not release:
            raise HTTPException(status_code=404, detail="Release not found")
        
        return release.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{release_id}/approve")
async def approve_release(
    release_id: str,
    approver_id: str = Body(..., description="Approver ID"),
    comment: Optional[str] = Body(None, description="Approval comment"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Approve a release"""
    try:
        # Create request
        request = ApproveReleaseRequest(
            release_id=release_id,
            approver_id=approver_id,
            comment=comment
        )
        
        # Execute use case
        use_case = ApproveReleaseUseCase(env_store, clock, id_generator)
        result = await use_case.execute(request)
        
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{release_id}/apply")
async def apply_release(
    release_id: str,
    applied_by: str = Body(..., description="Applied by user"),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    """Apply a release"""
    try:
        # Create request
        request = ApplyReleaseRequest(
            release_id=release_id,
            applied_by=applied_by
        )
        
        # Execute use case
        use_case = ApplyReleaseUseCase(env_store, clock, id_generator)
        result = await use_case.execute(request)
        
        return result.to_dict()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{release_id}/approvals")
async def get_release_approvals(
    release_id: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Get approvals for a release"""
    try:
        approvals = await env_store.get_approvals_for_release(release_id)
        return [approval.to_dict() for approval in approvals]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{release_id}/status")
async def get_release_status(
    release_id: str,
    env_store: SqlAlchemyEnvStore = Depends(get_env_store)
):
    """Get release status and approval information"""
    try:
        release = await env_store.get_release_by_id(release_id)
        if not release:
            raise HTTPException(status_code=404, detail="Release not found")
        
        approvals = await env_store.get_approvals_for_release(release_id)
        
        return {
            "release": release.to_dict(),
            "approvals": [approval.to_dict() for approval in approvals],
            "can_be_approved": release.can_be_approved(),
            "can_be_applied": release.can_be_applied(),
            "can_be_cancelled": release.can_be_cancelled()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
