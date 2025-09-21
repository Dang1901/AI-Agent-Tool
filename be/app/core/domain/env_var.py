"""
Domain model for Environment Variables
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import re


class ScopeLevel(Enum):
    """Scope levels for environment variables"""
    GLOBAL = "GLOBAL"
    PROJECT = "PROJECT" 
    SERVICE = "SERVICE"
    ENV = "ENV"


class EnvVarType(Enum):
    """Types of environment variables"""
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOL = "BOOL"
    JSON = "JSON"
    SECRET = "SECRET"


class EnvVarStatus(Enum):
    """Status of environment variables"""
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DEPRECATED = "DEPRECATED"


@dataclass
class ScopeRef:
    """Scope reference for environment variables"""
    level: ScopeLevel
    ref_id: str
    
    def __str__(self) -> str:
        return f"{self.level.value}:{self.ref_id}"


@dataclass
class EnvVar:
    """Core domain model for environment variables"""
    id: str
    key: str
    value: str
    type: EnvVarType
    scope: ScopeRef
    tags: List[str]
    description: Optional[str]
    is_secret: bool
    status: EnvVarStatus
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    
    # Validation rules
    KEY_REGEX = re.compile(r'^[A-Z0-9_]{1,100}$')
    MAX_VALUE_SIZE = 1024 * 1024  # 1MB
    
    def __post_init__(self):
        """Validate the environment variable"""
        self._validate()
    
    def _validate(self):
        """Validate environment variable according to business rules"""
        # Validate key format
        if not self.KEY_REGEX.match(self.key):
            raise ValueError(f"Key must match pattern ^[A-Z0-9_]{{1,100}}$: {self.key}")
        
        # Validate value size
        if len(self.value.encode('utf-8')) > self.MAX_VALUE_SIZE:
            raise ValueError(f"Value too large: {len(self.value.encode('utf-8'))} bytes")
        
        # Validate type-specific constraints
        if self.type == EnvVarType.NUMBER:
            try:
                float(self.value)
            except ValueError:
                raise ValueError(f"Value must be numeric for type NUMBER: {self.value}")
        
        elif self.type == EnvVarType.BOOL:
            if self.value.lower() not in ['true', 'false', '1', '0']:
                raise ValueError(f"Value must be boolean for type BOOL: {self.value}")
        
        elif self.type == EnvVarType.JSON:
            try:
                import json
                json.loads(self.value)
            except json.JSONDecodeError:
                raise ValueError(f"Value must be valid JSON for type JSON: {self.value}")
    
    def get_unique_key(self) -> str:
        """Get unique key for this environment variable"""
        return f"{self.scope.level.value}:{self.scope.ref_id}:{self.key}"
    
    def is_restricted_environment(self) -> bool:
        """Check if this is a restricted environment (prod) that requires approval"""
        return self.scope.level == ScopeLevel.ENV and self.scope.ref_id.lower() in ['prod', 'production']
    
    def get_masked_value(self) -> str:
        """Get masked value for display (secrets are masked)"""
        if self.is_secret:
            return "***"
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.get_masked_value(),
            'type': self.type.value,
            'scope': {
                'level': self.scope.level.value,
                'ref_id': self.scope.ref_id
            },
            'tags': self.tags,
            'description': self.description,
            'is_secret': self.is_secret,
            'status': self.status.value,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat()
        }
