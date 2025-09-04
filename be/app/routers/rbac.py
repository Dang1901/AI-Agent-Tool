from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services import rbac as rbac_service
from app.schemas.rbac import (
    RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    ResourceCreate, ResourceUpdate, ResourceResponse,
    UserRoleAssignment, RolePermissionAssignment, UserWithRoles
)

router = APIRouter(prefix="/rbac", tags=["RBAC"])

# Role endpoints
@router.post("/roles", response_model=RoleResponse)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    existing_role = rbac_service.get_role_by_name(db, role_data.name)
    if existing_role:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    return rbac_service.create_role(db, role_data)

@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all roles"""
    return rbac_service.get_all_roles(db, skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=RoleWithPermissions)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get role by ID with permissions"""
    role = rbac_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = rbac_service.get_role_permissions(db, role_id)
    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        display_name=role.display_name,
        description=role.description,
        is_active=role.is_active,
        is_system=role.is_system,
        permissions=permissions
    )

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """Update role"""
    role = rbac_service.update_role(db, role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete role"""
    success = rbac_service.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found or cannot be deleted")
    return {"message": "Role deleted successfully"}

# Permission endpoints
@router.post("/permissions", response_model=PermissionResponse)
def create_permission(permission_data: PermissionCreate, db: Session = Depends(get_db)):
    """Create a new permission"""
    existing_permission = rbac_service.get_permission_by_name(db, permission_data.name)
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission with this name already exists")
    
    return rbac_service.create_permission(db, permission_data)

@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    resource: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all permissions"""
    if resource:
        return rbac_service.get_permissions_by_resource(db, resource)
    return rbac_service.get_all_permissions(db, page=page, page_size=page_size)

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """Get permission by ID"""
    permission = rbac_service.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(permission_id: int, permission_data: PermissionUpdate, db: Session = Depends(get_db)):
    """Update permission"""
    permission = rbac_service.update_permission(db, permission_id, permission_data)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.delete("/permissions/{permission_id}")
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """Delete permission"""
    success = rbac_service.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted successfully"}

# Resource endpoints
@router.post("/resources", response_model=ResourceResponse)
def create_resource(resource_data: ResourceCreate, db: Session = Depends(get_db)):
    """Create a new resource"""
    existing_resource = rbac_service.get_resource_by_name(db, resource_data.name)
    if existing_resource:
        raise HTTPException(status_code=400, detail="Resource with this name already exists")
    
    return rbac_service.create_resource(db, resource_data)

@router.get("/resources", response_model=List[ResourceResponse])
def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all resources"""
    return rbac_service.get_all_resources(db, skip=skip, limit=limit)

@router.get("/resources/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get resource by ID"""
    resource = rbac_service.get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, resource_data: ResourceUpdate, db: Session = Depends(get_db)):
    """Update resource"""
    resource = rbac_service.update_resource(db, resource_id, resource_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete resource"""
    success = rbac_service.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}

# Assignment endpoints
@router.post("/users/{user_id}/roles")
def assign_roles_to_user(user_id: int, assignment: UserRoleAssignment, db: Session = Depends(get_db)):
    """Assign roles to user"""
    success = rbac_service.assign_roles_to_user(db, user_id, assignment.role_ids)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Roles assigned successfully"}

@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    """Get user's roles"""
    roles = rbac_service.get_user_roles(db, user_id)
    return roles

@router.get("/users/{user_id}/permissions", response_model=List[PermissionResponse])
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    """Get user's permissions through roles"""
    permissions = rbac_service.get_user_permissions(db, user_id)
    return permissions

@router.post("/roles/{role_id}/permissions")
def assign_permissions_to_role(role_id: int, assignment: RolePermissionAssignment, db: Session = Depends(get_db)):
    """Assign permissions to role"""
    success = rbac_service.assign_permissions_to_role(db, role_id, assignment.permission_ids)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Permissions assigned successfully"}

@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    """Get role's permissions"""
    permissions = rbac_service.get_role_permissions(db, role_id)
    return permissions

# Authorization check endpoint
@router.get("/users/{user_id}/check-permission")
def check_user_permission(
    user_id: int,
    resource: str = Query(...),
    action: str = Query(...),
    db: Session = Depends(get_db)
):
    """Check if user has specific permission"""
    has_permission = rbac_service.check_user_permission(db, user_id, resource, action)
    return {
        "user_id": user_id,
        "resource": resource,
        "action": action,
        "has_permission": has_permission
    }
