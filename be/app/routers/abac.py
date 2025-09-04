from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services import abac as abac_service
from app.schemas.abac import (
    PolicyCreate, PolicyUpdate, PolicyResponse,
    PolicyAssignmentCreate, PolicyAssignmentResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    UserAttributeCreate, UserAttributeResponse,
    ResourceAttributeCreate, ResourceAttributeResponse,
    AuthorizationRequest, AuthorizationResponse,
    AccessLogResponse
)

router = APIRouter(prefix="/abac", tags=["ABAC"])

# Policy endpoints
@router.post("/policies", response_model=PolicyResponse)
def create_policy(policy_data: PolicyCreate, db: Session = Depends(get_db)):
    """Create a new policy"""
    return abac_service.create_policy(db, policy_data)

@router.get("/policies", response_model=List[PolicyResponse])
def list_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List all policies"""
    if active_only:
        return abac_service.get_active_policies(db)
    return abac_service.get_all_policies(db, page=page, page_size=page_size)

@router.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    """Get policy by ID"""
    policy = abac_service.get_policy_by_id(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/policies/{policy_id}", response_model=PolicyResponse)
def update_policy(policy_id: int, policy_data: PolicyUpdate, db: Session = Depends(get_db)):
    """Update policy"""
    policy = abac_service.update_policy(db, policy_id, policy_data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete policy"""
    success = abac_service.delete_policy(db, policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}

# Policy Assignment endpoints
@router.post("/policy-assignments", response_model=PolicyAssignmentResponse)
def assign_policy(assignment_data: PolicyAssignmentCreate, db: Session = Depends(get_db)):
    """Assign policy to user/role/resource"""
    return abac_service.assign_policy(db, assignment_data)

@router.get("/policies/{policy_id}/assignments", response_model=List[PolicyAssignmentResponse])
def get_policy_assignments(policy_id: int, db: Session = Depends(get_db)):
    """Get all assignments for a policy"""
    assignments = abac_service.get_policy_assignments(db, policy_id)
    return assignments

@router.get("/users/{user_id}/policies", response_model=List[PolicyResponse])
def get_user_policies(user_id: int, db: Session = Depends(get_db)):
    """Get all policies assigned to a user"""
    policies = abac_service.get_user_policies(db, user_id)
    return policies

@router.delete("/policy-assignments/{assignment_id}")
def remove_policy_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Remove policy assignment"""
    success = abac_service.remove_policy_assignment(db, assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy assignment not found")
    return {"message": "Policy assignment removed successfully"}

# Attribute endpoints
@router.post("/attributes", response_model=AttributeResponse)
def create_attribute(attribute_data: AttributeCreate, db: Session = Depends(get_db)):
    """Create a new attribute"""
    existing_attribute = abac_service.get_attribute_by_name(db, attribute_data.name)
    if existing_attribute:
        raise HTTPException(status_code=400, detail="Attribute with this name already exists")
    
    return abac_service.create_attribute(db, attribute_data)

@router.get("/attributes", response_model=List[AttributeResponse])
def list_attributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    data_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all attributes"""
    if data_type:
        return abac_service.get_attributes_by_type(db, data_type)
    return abac_service.get_all_attributes(db, skip=skip, limit=limit)

@router.get("/attributes/{attribute_id}", response_model=AttributeResponse)
def get_attribute(attribute_id: int, db: Session = Depends(get_db)):
    """Get attribute by ID"""
    attribute = abac_service.get_attribute_by_id(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute

# User Attribute endpoints
@router.post("/users/{user_id}/attributes")
def set_user_attribute(
    user_id: int,
    attribute_name: str = Query(...),
    value: str = Query(...),
    db: Session = Depends(get_db)
):
    """Set user attribute value"""
    try:
        user_attribute = abac_service.set_user_attribute(db, user_id, attribute_name, value)
        return {"message": "User attribute set successfully", "attribute": user_attribute}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}/attributes", response_model=List[UserAttributeResponse])
def get_user_attributes(user_id: int, db: Session = Depends(get_db)):
    """Get all attributes for a user"""
    attributes = abac_service.get_user_attributes(db, user_id)
    return attributes

@router.get("/users/{user_id}/attributes/{attribute_name}")
def get_user_attribute_value(
    user_id: int,
    attribute_name: str,
    db: Session = Depends(get_db)
):
    """Get specific user attribute value"""
    value = abac_service.get_user_attribute_value(db, user_id, attribute_name)
    if value is None:
        raise HTTPException(status_code=404, detail="User attribute not found")
    return {"attribute_name": attribute_name, "value": value}

# Resource Attribute endpoints
@router.post("/resources/{resource_id}/attributes")
def set_resource_attribute(
    resource_id: int,
    resource_type: str = Query(...),
    attribute_name: str = Query(...),
    value: str = Query(...),
    db: Session = Depends(get_db)
):
    """Set resource attribute value"""
    try:
        resource_attribute = abac_service.set_resource_attribute(
            db, resource_id, resource_type, attribute_name, value
        )
        return {"message": "Resource attribute set successfully", "attribute": resource_attribute}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/resources/{resource_id}/attributes", response_model=List[ResourceAttributeResponse])
def get_resource_attributes(
    resource_id: int,
    resource_type: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get all attributes for a resource"""
    attributes = abac_service.get_resource_attributes(db, resource_id, resource_type)
    return attributes

# Authorization endpoint
@router.post("/authorize", response_model=AuthorizationResponse)
def authorize_request(request: AuthorizationRequest, db: Session = Depends(get_db)):
    """Authorize a request using ABAC policies"""
    return abac_service.authorize_request(db, request)

# Access Log endpoints
@router.get("/access-logs", response_model=List[AccessLogResponse])
def get_access_logs(
    user_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get access logs"""
    logs = abac_service.get_access_logs(db, user_id=user_id, skip=skip, limit=limit)
    return logs
