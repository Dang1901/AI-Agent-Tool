from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Role Schemas
class RoleBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    is_active: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RoleResponse(RoleBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Permission Schemas
class PermissionBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    resource: str
    action: str
    is_active: bool = True

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Resource Schemas
class ResourceBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    resource_type: str
    is_active: bool = True

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    is_active: Optional[bool] = None

class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User Role Assignment Schemas
class UserRoleAssignment(BaseModel):
    user_id: int
    role_ids: List[int]

class RolePermissionAssignment(BaseModel):
    role_id: int
    permission_ids: List[int]

# User with roles
class UserWithRoles(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    is_active: bool
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True

# Role with permissions
class RoleWithPermissions(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    is_active: bool
    is_system: bool
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True
