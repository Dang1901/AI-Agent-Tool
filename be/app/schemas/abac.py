from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Policy Schemas
class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    policy_type: str  # allow, deny, conditional
    priority: int = 100
    is_active: bool = True
    subject_conditions: Optional[Dict[str, Any]] = None
    resource_conditions: Optional[Dict[str, Any]] = None
    action_conditions: Optional[Dict[str, Any]] = None
    environment_conditions: Optional[Dict[str, Any]] = None
    effect: str  # allow, deny
    obligations: Optional[Dict[str, Any]] = None

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    policy_type: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    subject_conditions: Optional[Dict[str, Any]] = None
    resource_conditions: Optional[Dict[str, Any]] = None
    action_conditions: Optional[Dict[str, Any]] = None
    environment_conditions: Optional[Dict[str, Any]] = None
    effect: Optional[str] = None
    obligations: Optional[Dict[str, Any]] = None

class PolicyResponse(PolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Policy Assignment Schemas
class PolicyAssignmentBase(BaseModel):
    policy_id: int
    assignment_type: str  # user, role, resource, global
    assignment_id: Optional[int] = None
    assignment_name: Optional[str] = None
    is_active: bool = True

class PolicyAssignmentCreate(PolicyAssignmentBase):
    pass

class PolicyAssignmentUpdate(BaseModel):
    is_active: Optional[bool] = None

class PolicyAssignmentResponse(PolicyAssignmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Attribute Schemas
class AttributeBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    attribute_type: str  # string, number, boolean, date, enum
    data_type: str  # subject, resource, action, environment
    is_required: bool = False
    is_multivalued: bool = False
    allowed_values: Optional[List[str]] = None
    default_value: Optional[str] = None

class AttributeCreate(AttributeBase):
    pass

class AttributeUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    attribute_type: Optional[str] = None
    data_type: Optional[str] = None
    is_required: Optional[bool] = None
    is_multivalued: Optional[bool] = None
    allowed_values: Optional[List[str]] = None
    default_value: Optional[str] = None

class AttributeResponse(AttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User Attribute Schemas
class UserAttributeBase(BaseModel):
    user_id: int
    attribute_id: int
    value: str

class UserAttributeCreate(UserAttributeBase):
    pass

class UserAttributeUpdate(BaseModel):
    value: str

class UserAttributeResponse(UserAttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attribute: AttributeResponse
    
    class Config:
        from_attributes = True

# Resource Attribute Schemas
class ResourceAttributeBase(BaseModel):
    resource_id: int
    resource_type: str
    attribute_id: int
    value: str

class ResourceAttributeCreate(ResourceAttributeBase):
    pass

class ResourceAttributeUpdate(BaseModel):
    value: str

class ResourceAttributeResponse(ResourceAttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attribute: AttributeResponse
    
    class Config:
        from_attributes = True

# Access Log Schemas
class AccessLogBase(BaseModel):
    user_id: Optional[int] = None
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    decision: str  # allow, deny
    policy_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AccessLogCreate(AccessLogBase):
    pass

class AccessLogResponse(AccessLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authorization Request Schemas
class AuthorizationRequest(BaseModel):
    user_id: int
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    context: Optional[Dict[str, Any]] = None

class AuthorizationResponse(BaseModel):
    decision: str  # allow, deny
    policy_id: Optional[int] = None
    reason: Optional[str] = None
    obligations: Optional[Dict[str, Any]] = None
