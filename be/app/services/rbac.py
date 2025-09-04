from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.model.rbac import Role, Permission, Resource, user_roles, role_permissions
from app.model.user import User
from app.schemas.rbac import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate, ResourceCreate, ResourceUpdate

# Role Services
def create_role(db: Session, role_data: RoleCreate) -> Role:
    """Create a new role"""
    role = Role(**role_data.dict())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """Get role by ID"""
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get role by name"""
    return db.query(Role).filter(Role.name == name).first()

def get_all_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """Get all roles with pagination"""
    return db.query(Role).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
    """Update role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return None
    
    for key, value in role_data.dict(exclude_unset=True).items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    return role

def delete_role(db: Session, role_id: int) -> bool:
    """Delete role (only if not system role)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role or role.is_system:
        return False
    
    db.delete(role)
    db.commit()
    return True

# Permission Services
def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
    """Create a new permission"""
    permission = Permission(**permission_data.dict())
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission

def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
    """Get permission by ID"""
    return db.query(Permission).filter(Permission.id == permission_id).first()

def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Get permission by name"""
    return db.query(Permission).filter(Permission.name == name).first()

def get_all_permissions(db: Session, page: int = 1, page_size: int = 100) -> List[Permission]:
    """Get all permissions with pagination"""
    skip = (page - 1) * page_size
    return db.query(Permission).offset(skip).limit(page_size).all()

def get_permissions_by_resource(db: Session, resource: str) -> List[Permission]:
    """Get permissions by resource"""
    return db.query(Permission).filter(Permission.resource == resource).all()

def update_permission(db: Session, permission_id: int, permission_data: PermissionUpdate) -> Optional[Permission]:
    """Update permission"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        return None
    
    for key, value in permission_data.dict(exclude_unset=True).items():
        setattr(permission, key, value)
    
    db.commit()
    db.refresh(permission)
    return permission

def delete_permission(db: Session, permission_id: int) -> bool:
    """Delete permission"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        return False
    
    db.delete(permission)
    db.commit()
    return True

# Resource Services
def create_resource(db: Session, resource_data: ResourceCreate) -> Resource:
    """Create a new resource"""
    resource = Resource(**resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

def get_resource_by_id(db: Session, resource_id: int) -> Optional[Resource]:
    """Get resource by ID"""
    return db.query(Resource).filter(Resource.id == resource_id).first()

def get_resource_by_name(db: Session, name: str) -> Optional[Resource]:
    """Get resource by name"""
    return db.query(Resource).filter(Resource.name == name).first()

def get_all_resources(db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
    """Get all resources with pagination"""
    return db.query(Resource).offset(skip).limit(limit).all()

def update_resource(db: Session, resource_id: int, resource_data: ResourceUpdate) -> Optional[Resource]:
    """Update resource"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        return None
    
    for key, value in resource_data.dict(exclude_unset=True).items():
        setattr(resource, key, value)
    
    db.commit()
    db.refresh(resource)
    return resource

def delete_resource(db: Session, resource_id: int) -> bool:
    """Delete resource"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        return False
    
    db.delete(resource)
    db.commit()
    return True

# User-Role Assignment Services
def assign_roles_to_user(db: Session, user_id: int, role_ids: List[int]) -> bool:
    """Assign roles to user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Remove existing role assignments
    db.execute(user_roles.delete().where(user_roles.c.user_id == user_id))
    
    # Add new role assignments
    for role_id in role_ids:
        db.execute(user_roles.insert().values(user_id=user_id, role_id=role_id))
    
    db.commit()
    return True

def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Get user's roles"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return user.roles

def remove_user_roles(db: Session, user_id: int, role_ids: List[int]) -> bool:
    """Remove specific roles from user"""
    for role_id in role_ids:
        db.execute(
            user_roles.delete().where(
                and_(user_roles.c.user_id == user_id, user_roles.c.role_id == role_id)
            )
        )
    db.commit()
    return True

# Role-Permission Assignment Services
def assign_permissions_to_role(db: Session, role_id: int, permission_ids: List[int]) -> bool:
    """Assign permissions to role"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return False
    
    # Remove existing permission assignments
    db.execute(role_permissions.delete().where(role_permissions.c.role_id == role_id))
    
    # Add new permission assignments
    for permission_id in permission_ids:
        db.execute(role_permissions.insert().values(role_id=role_id, permission_id=permission_id))
    
    db.commit()
    return True

def get_role_permissions(db: Session, role_id: int) -> List[Permission]:
    """Get role's permissions"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return []
    return role.permissions

def get_user_permissions(db: Session, user_id: int) -> List[Permission]:
    """Get all permissions for a user through their roles"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    permissions = []
    for role in user.roles:
        permissions.extend(role.permissions)
    
    # Remove duplicates
    unique_permissions = list({p.id: p for p in permissions}.values())
    return unique_permissions

def check_user_permission(db: Session, user_id: int, resource: str, action: str) -> bool:
    """Check if user has specific permission"""
    user_permissions = get_user_permissions(db, user_id)
    for permission in user_permissions:
        if permission.resource == resource and permission.action == action:
            return True
    return False
