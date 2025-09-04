#!/usr/bin/env python3
"""
Initialize RBAC and ABAC system with default data
Run this script after setting up the database
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services import rbac as rbac_service, abac as abac_service
from app.schemas.rbac import RoleCreate, PermissionCreate, ResourceCreate
from app.schemas.abac import AttributeCreate, PolicyCreate, PolicyAssignmentCreate

def init_database():
    """Initialize database with default RBAC and ABAC data"""
    db = SessionLocal()
    
    try:
        print("Initializing RBAC and ABAC system...")
        
        # Create default resources
        print("Creating default resources...")
        resources = [
            ResourceCreate(name="user", display_name="User Management", description="Manage users", resource_type="entity"),
            ResourceCreate(name="role", display_name="Role Management", description="Manage roles", resource_type="entity"),
            ResourceCreate(name="permission", display_name="Permission Management", description="Manage permissions", resource_type="entity"),
            ResourceCreate(name="feature", display_name="Feature Management", description="Manage features", resource_type="entity"),
            ResourceCreate(name="policy", display_name="Policy Management", description="Manage policies", resource_type="entity"),
            ResourceCreate(name="report", display_name="Reports", description="View reports", resource_type="data"),
        ]
        
        for resource_data in resources:
            existing = rbac_service.get_resource_by_name(db, resource_data.name)
            if not existing:
                rbac_service.create_resource(db, resource_data)
                print(f"  ✓ Created resource: {resource_data.name}")
        
        # Create default permissions
        print("Creating default permissions...")
        permissions = [
            # User permissions
            PermissionCreate(name="user.read", display_name="Read Users", resource="user", action="read", description="View user information"),
            PermissionCreate(name="user.write", display_name="Write Users", resource="user", action="write", description="Create and update users"),
            PermissionCreate(name="user.delete", display_name="Delete Users", resource="user", action="delete", description="Delete users"),
            
            # Role permissions
            PermissionCreate(name="role.read", display_name="Read Roles", resource="role", action="read", description="View role information"),
            PermissionCreate(name="role.write", display_name="Write Roles", resource="role", action="write", description="Create and update roles"),
            PermissionCreate(name="role.delete", display_name="Delete Roles", resource="role", action="delete", description="Delete roles"),
            
            # Permission permissions
            PermissionCreate(name="permission.read", display_name="Read Permissions", resource="permission", action="read", description="View permission information"),
            PermissionCreate(name="permission.write", display_name="Write Permissions", resource="permission", action="write", description="Create and update permissions"),
            PermissionCreate(name="permission.delete", display_name="Delete Permissions", resource="permission", action="delete", description="Delete permissions"),
            
            # Feature permissions
            PermissionCreate(name="feature.read", display_name="Read Features", resource="feature", action="read", description="View feature information"),
            PermissionCreate(name="feature.write", display_name="Write Features", resource="feature", action="write", description="Create and update features"),
            PermissionCreate(name="feature.delete", display_name="Delete Features", resource="feature", action="delete", description="Delete features"),
            
            # Policy permissions
            PermissionCreate(name="policy.read", display_name="Read Policies", resource="policy", action="read", description="View policy information"),
            PermissionCreate(name="policy.write", display_name="Write Policies", resource="policy", action="write", description="Create and update policies"),
            PermissionCreate(name="policy.delete", display_name="Delete Policies", resource="policy", action="delete", description="Delete policies"),
            
            # Report permissions
            PermissionCreate(name="report.read", display_name="Read Reports", resource="report", action="read", description="View reports"),
        ]
        
        for permission_data in permissions:
            existing = rbac_service.get_permission_by_name(db, permission_data.name)
            if not existing:
                rbac_service.create_permission(db, permission_data)
                print(f"  ✓ Created permission: {permission_data.name}")
        
        # Create default roles
        print("Creating default roles...")
        roles = [
            RoleCreate(name="super_admin", display_name="Super Administrator", description="Full system access", is_system=True),
            RoleCreate(name="admin", display_name="Administrator", description="Administrative access"),
            RoleCreate(name="manager", display_name="Manager", description="Management access"),
            RoleCreate(name="user", display_name="User", description="Basic user access"),
            RoleCreate(name="readonly", display_name="Read Only", description="Read-only access"),
        ]
        
        created_roles = {}
        for role_data in roles:
            existing = rbac_service.get_role_by_name(db, role_data.name)
            if not existing:
                role = rbac_service.create_role(db, role_data)
                created_roles[role.name] = role
                print(f"  ✓ Created role: {role_data.name}")
            else:
                created_roles[role_data.name] = existing
        
        # Assign permissions to roles
        print("Assigning permissions to roles...")
        
        # Super Admin - all permissions
        all_permissions = rbac_service.get_all_permissions(db)
        super_admin_permissions = [p.id for p in all_permissions]
        rbac_service.assign_permissions_to_role(db, created_roles["super_admin"].id, super_admin_permissions)
        print("  ✓ Assigned all permissions to super_admin")
        
        # Admin - most permissions except super admin specific
        admin_permissions = [p.id for p in all_permissions if not p.name.startswith("policy")]
        rbac_service.assign_permissions_to_role(db, created_roles["admin"].id, admin_permissions)
        print("  ✓ Assigned admin permissions to admin")
        
        # Manager - user and feature management
        manager_permissions = [p.id for p in all_permissions if p.resource in ["user", "feature", "report"]]
        rbac_service.assign_permissions_to_role(db, created_roles["manager"].id, manager_permissions)
        print("  ✓ Assigned manager permissions to manager")
        
        # User - basic permissions
        user_permissions = [p.id for p in all_permissions if p.resource == "user" and p.action == "read"]
        rbac_service.assign_permissions_to_role(db, created_roles["user"].id, user_permissions)
        print("  ✓ Assigned user permissions to user")
        
        # Read Only - read permissions
        readonly_permissions = [p.id for p in all_permissions if p.action == "read"]
        rbac_service.assign_permissions_to_role(db, created_roles["readonly"].id, readonly_permissions)
        print("  ✓ Assigned readonly permissions to readonly")
        
        # Create default attributes for ABAC
        print("Creating default attributes...")
        attributes = [
            # User attributes
            AttributeCreate(name="user.department", display_name="Department", description="User department", attribute_type="string", data_type="subject"),
            AttributeCreate(name="user.position", display_name="Position", description="User position", attribute_type="string", data_type="subject"),
            AttributeCreate(name="user.location", display_name="Location", description="User location", attribute_type="string", data_type="subject"),
            AttributeCreate(name="user.clearance_level", display_name="Clearance Level", description="Security clearance level", attribute_type="enum", data_type="subject", allowed_values=["public", "internal", "confidential", "secret"]),
            AttributeCreate(name="user.working_hours", display_name="Working Hours", description="User working hours", attribute_type="string", data_type="subject"),
            
            # Resource attributes
            AttributeCreate(name="resource.sensitivity", display_name="Resource Sensitivity", description="Resource sensitivity level", attribute_type="enum", data_type="resource", allowed_values=["public", "internal", "confidential", "secret"]),
            AttributeCreate(name="resource.owner", display_name="Resource Owner", description="Resource owner department", attribute_type="string", data_type="resource"),
            AttributeCreate(name="resource.category", display_name="Resource Category", description="Resource category", attribute_type="string", data_type="resource"),
            
            # Environment attributes
            AttributeCreate(name="env.time", display_name="Current Time", description="Current time", attribute_type="string", data_type="environment"),
            AttributeCreate(name="env.ip_address", display_name="IP Address", description="Client IP address", attribute_type="string", data_type="environment"),
            AttributeCreate(name="env.location", display_name="Access Location", description="Access location", attribute_type="string", data_type="environment"),
        ]
        
        for attribute_data in attributes:
            existing = abac_service.get_attribute_by_name(db, attribute_data.name)
            if not existing:
                abac_service.create_attribute(db, attribute_data)
                print(f"  ✓ Created attribute: {attribute_data.name}")
        
        # Create default policies
        print("Creating default policies...")
        policies = [
            # Policy 1: Department-based access
            PolicyCreate(
                name="Department Access Policy",
                description="Users can only access resources from their own department",
                policy_type="conditional",
                priority=10,
                subject_conditions={"user.department": {"operator": "eq", "value": "{{resource.owner}}"}},
                resource_conditions={"resource.owner": {"operator": "exists"}},
                effect="allow"
            ),
            
            # Policy 2: Clearance level policy
            PolicyCreate(
                name="Clearance Level Policy",
                description="Users can only access resources at or below their clearance level",
                policy_type="conditional",
                priority=20,
                subject_conditions={"user.clearance_level": {"operator": "gte", "value": "{{resource.sensitivity}}"}},
                resource_conditions={"resource.sensitivity": {"operator": "exists"}},
                effect="allow"
            ),
            
            # Policy 3: Working hours policy
            PolicyCreate(
                name="Working Hours Policy",
                description="Users can only access resources during working hours",
                policy_type="conditional",
                priority=30,
                subject_conditions={"user.working_hours": {"operator": "contains", "value": "{{env.time}}"}},
                environment_conditions={"env.time": {"operator": "regex", "value": r"^(0[8-9]|1[0-7]):\d{2}$"}},
                effect="allow"
            ),
            
            # Policy 4: Deny access to sensitive resources outside working hours
            PolicyCreate(
                name="Sensitive Resource Hours Policy",
                description="Sensitive resources can only be accessed during working hours",
                policy_type="conditional",
                priority=5,
                resource_conditions={"resource.sensitivity": {"operator": "in", "value": ["confidential", "secret"]}},
                environment_conditions={"env.time": {"operator": "regex", "value": r"^(0[8-9]|1[0-7]):\d{2}$"}},
                effect="allow"
            ),
        ]
        
        for policy_data in policies:
            policy = abac_service.create_policy(db, policy_data)
            print(f"  ✓ Created policy: {policy.name}")
            
            # Assign policy globally
            assignment = PolicyAssignmentCreate(
                policy_id=policy.id,
                assignment_type="global",
                assignment_name="Global Assignment"
            )
            abac_service.assign_policy(db, assignment)
            print(f"    ✓ Assigned policy globally")
        
        print("\n✅ RBAC and ABAC system initialized successfully!")
        print("\nDefault roles created:")
        for role_name in created_roles:
            print(f"  - {role_name}")
        
        print("\nDefault permissions created:")
        for permission in all_permissions:
            print(f"  - {permission.name}")
        
        print("\nDefault policies created:")
        for policy in policies:
            print(f"  - {policy.name}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
