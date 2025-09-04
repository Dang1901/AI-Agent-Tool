from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from app.model.abac import Policy, PolicyAssignment, Attribute, UserAttribute, ResourceAttribute, AccessLog
from app.model.user import User
from app.schemas.abac import (
    PolicyCreate, PolicyUpdate, PolicyAssignmentCreate, AttributeCreate, 
    UserAttributeCreate, ResourceAttributeCreate, AuthorizationRequest, AuthorizationResponse
)

# Policy Services
def create_policy(db: Session, policy_data: PolicyCreate) -> Policy:
    """Create a new policy"""
    policy = Policy(**policy_data.dict())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

def get_policy_by_id(db: Session, policy_id: int) -> Optional[Policy]:
    """Get policy by ID"""
    return db.query(Policy).filter(Policy.id == policy_id).first()

def get_all_policies(db: Session, page: int = 1, page_size: int = 100) -> List[Policy]:
    """Get all policies with pagination"""
    skip = (page - 1) * page_size
    return db.query(Policy).order_by(Policy.priority.asc()).offset(skip).limit(page_size).all()

def get_active_policies(db: Session) -> List[Policy]:
    """Get all active policies ordered by priority"""
    return db.query(Policy).filter(Policy.is_active == True).order_by(Policy.priority.asc()).all()

def update_policy(db: Session, policy_id: int, policy_data: PolicyUpdate) -> Optional[Policy]:
    """Update policy"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        return None
    
    for key, value in policy_data.dict(exclude_unset=True).items():
        setattr(policy, key, value)
    
    db.commit()
    db.refresh(policy)
    return policy

def delete_policy(db: Session, policy_id: int) -> bool:
    """Delete policy"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        return False
    
    db.delete(policy)
    db.commit()
    return True

# Policy Assignment Services
def assign_policy(db: Session, assignment_data: PolicyAssignmentCreate) -> PolicyAssignment:
    """Assign policy to user/role/resource"""
    assignment = PolicyAssignment(**assignment_data.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def get_policy_assignments(db: Session, policy_id: int) -> List[PolicyAssignment]:
    """Get all assignments for a policy"""
    return db.query(PolicyAssignment).filter(PolicyAssignment.policy_id == policy_id).all()

def get_user_policies(db: Session, user_id: int) -> List[Policy]:
    """Get all policies assigned to a user"""
    assignments = db.query(PolicyAssignment).filter(
        and_(
            PolicyAssignment.assignment_type == "user",
            PolicyAssignment.assignment_id == user_id,
            PolicyAssignment.is_active == True
        )
    ).all()
    
    policies = []
    for assignment in assignments:
        policy = db.query(Policy).filter(Policy.id == assignment.policy_id).first()
        if policy and policy.is_active:
            policies.append(policy)
    
    return policies

def remove_policy_assignment(db: Session, assignment_id: int) -> bool:
    """Remove policy assignment"""
    assignment = db.query(PolicyAssignment).filter(PolicyAssignment.id == assignment_id).first()
    if not assignment:
        return False
    
    db.delete(assignment)
    db.commit()
    return True

# Attribute Services
def create_attribute(db: Session, attribute_data: AttributeCreate) -> Attribute:
    """Create a new attribute"""
    attribute = Attribute(**attribute_data.dict())
    db.add(attribute)
    db.commit()
    db.refresh(attribute)
    return attribute

def get_attribute_by_id(db: Session, attribute_id: int) -> Optional[Attribute]:
    """Get attribute by ID"""
    return db.query(Attribute).filter(Attribute.id == attribute_id).first()

def get_attribute_by_name(db: Session, name: str) -> Optional[Attribute]:
    """Get attribute by name"""
    return db.query(Attribute).filter(Attribute.name == name).first()

def get_all_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[Attribute]:
    """Get all attributes with pagination"""
    return db.query(Attribute).offset(skip).limit(limit).all()

def get_attributes_by_type(db: Session, data_type: str) -> List[Attribute]:
    """Get attributes by data type"""
    return db.query(Attribute).filter(Attribute.data_type == data_type).all()

# User Attribute Services
def set_user_attribute(db: Session, user_id: int, attribute_name: str, value: str) -> UserAttribute:
    """Set user attribute value"""
    attribute = get_attribute_by_name(db, attribute_name)
    if not attribute:
        raise ValueError(f"Attribute {attribute_name} not found")
    
    # Check if attribute already exists
    existing = db.query(UserAttribute).filter(
        and_(UserAttribute.user_id == user_id, UserAttribute.attribute_id == attribute.id)
    ).first()
    
    if existing:
        existing.value = value
        db.commit()
        db.refresh(existing)
        return existing
    else:
        user_attribute = UserAttribute(
            user_id=user_id,
            attribute_id=attribute.id,
            value=value
        )
        db.add(user_attribute)
        db.commit()
        db.refresh(user_attribute)
        return user_attribute

def get_user_attributes(db: Session, user_id: int) -> List[UserAttribute]:
    """Get all attributes for a user"""
    return db.query(UserAttribute).filter(UserAttribute.user_id == user_id).all()

def get_user_attribute_value(db: Session, user_id: int, attribute_name: str) -> Optional[str]:
    """Get specific user attribute value"""
    attribute = get_attribute_by_name(db, attribute_name)
    if not attribute:
        return None
    
    user_attribute = db.query(UserAttribute).filter(
        and_(UserAttribute.user_id == user_id, UserAttribute.attribute_id == attribute.id)
    ).first()
    
    return user_attribute.value if user_attribute else None

# Resource Attribute Services
def set_resource_attribute(db: Session, resource_id: int, resource_type: str, attribute_name: str, value: str) -> ResourceAttribute:
    """Set resource attribute value"""
    attribute = get_attribute_by_name(db, attribute_name)
    if not attribute:
        raise ValueError(f"Attribute {attribute_name} not found")
    
    # Check if attribute already exists
    existing = db.query(ResourceAttribute).filter(
        and_(
            ResourceAttribute.resource_id == resource_id,
            ResourceAttribute.resource_type == resource_type,
            ResourceAttribute.attribute_id == attribute.id
        )
    ).first()
    
    if existing:
        existing.value = value
        db.commit()
        db.refresh(existing)
        return existing
    else:
        resource_attribute = ResourceAttribute(
            resource_id=resource_id,
            resource_type=resource_type,
            attribute_id=attribute.id,
            value=value
        )
        db.add(resource_attribute)
        db.commit()
        db.refresh(resource_attribute)
        return resource_attribute

def get_resource_attributes(db: Session, resource_id: int, resource_type: str) -> List[ResourceAttribute]:
    """Get all attributes for a resource"""
    return db.query(ResourceAttribute).filter(
        and_(ResourceAttribute.resource_id == resource_id, ResourceAttribute.resource_type == resource_type)
    ).all()

# Policy Engine
def evaluate_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Evaluate a policy condition against context"""
    if not condition:
        return True
    
    for key, expected_value in condition.items():
        if key not in context:
            return False
        
        actual_value = context[key]
        
        # Handle different comparison operators
        if isinstance(expected_value, dict):
            operator = expected_value.get('operator', 'eq')
            value = expected_value.get('value')
            
            if operator == 'eq':
                if actual_value != value:
                    return False
            elif operator == 'ne':
                if actual_value == value:
                    return False
            elif operator == 'gt':
                if actual_value <= value:
                    return False
            elif operator == 'lt':
                if actual_value >= value:
                    return False
            elif operator == 'in':
                if actual_value not in value:
                    return False
            elif operator == 'not_in':
                if actual_value in value:
                    return False
            elif operator == 'regex':
                if not re.match(value, str(actual_value)):
                    return False
        else:
            if actual_value != expected_value:
                return False
    
    return True

def authorize_request(db: Session, request: AuthorizationRequest) -> AuthorizationResponse:
    """Authorize a request using ABAC policies"""
    # Get user attributes
    user_attributes = get_user_attributes(db, request.user_id)
    user_context = {attr.attribute.name: attr.value for attr in user_attributes}
    
    # Add user basic info
    user = db.query(User).filter(User.id == request.user_id).first()
    if user:
        user_context.update({
            'user.id': user.id,
            'user.email': user.email,
            'user.department': user.department,
            'user.position': user.position,
            'user.location': user.location,
            'user.clearance_level': user.clearance_level
        })
    
    # Add request context
    context = {
        **user_context,
        'resource.type': request.resource_type,
        'resource.id': request.resource_id,
        'action': request.action,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if request.context:
        context.update(request.context)
    
    # Get applicable policies
    policies = get_user_policies(db, request.user_id)
    
    # Also get global policies
    global_policies = db.query(Policy).filter(
        and_(
            Policy.is_active == True,
            Policy.id.in_(
                db.query(PolicyAssignment.policy_id).filter(
                    PolicyAssignment.assignment_type == "global"
                )
            )
        )
    ).order_by(Policy.priority.asc()).all()
    
    policies.extend(global_policies)
    
    # Evaluate policies in priority order
    for policy in policies:
        # Check subject conditions
        if policy.subject_conditions and not evaluate_condition(policy.subject_conditions, context):
            continue
        
        # Check resource conditions
        if policy.resource_conditions and not evaluate_condition(policy.resource_conditions, context):
            continue
        
        # Check action conditions
        if policy.action_conditions and not evaluate_condition(policy.action_conditions, context):
            continue
        
        # Check environment conditions
        if policy.environment_conditions and not evaluate_condition(policy.environment_conditions, context):
            continue
        
        # Policy matches, apply effect
        decision = policy.effect
        reason = f"Policy '{policy.name}' matched"
        obligations = policy.obligations
        
        # Log the access decision
        log_access(db, request, decision, policy.id, context)
        
        return AuthorizationResponse(
            decision=decision,
            policy_id=policy.id,
            reason=reason,
            obligations=obligations
        )
    
    # No policy matched, default deny
    log_access(db, request, "deny", None, context)
    return AuthorizationResponse(
        decision="deny",
        reason="No matching policy found"
    )

def log_access(db: Session, request: AuthorizationRequest, decision: str, policy_id: Optional[int], context: Dict[str, Any]) -> AccessLog:
    """Log access decision"""
    access_log = AccessLog(
        user_id=request.user_id,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        action=request.action,
        decision=decision,
        policy_id=policy_id,
        context=context
    )
    db.add(access_log)
    db.commit()
    db.refresh(access_log)
    return access_log

def get_access_logs(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[AccessLog]:
    """Get access logs with optional user filter"""
    query = db.query(AccessLog)
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    
    return query.order_by(AccessLog.created_at.desc()).offset(skip).limit(limit).all()
