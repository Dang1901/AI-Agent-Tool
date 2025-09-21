"""
Domain model for Policies
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import re


@dataclass
class Policy:
    """Policy for environment variable management"""
    id: str
    scope: str  # GLOBAL, PROJECT, SERVICE, ENV
    require_approval: bool
    min_approvers: int
    secret_ttl_days: Optional[int]
    key_regex: str
    value_max_kb: int
    reveal_justification_required: bool
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    
    def __post_init__(self):
        """Validate policy"""
        if self.min_approvers < 0:
            raise ValueError("min_approvers must be non-negative")
        
        if self.value_max_kb <= 0:
            raise ValueError("value_max_kb must be positive")
        
        if self.secret_ttl_days is not None and self.secret_ttl_days <= 0:
            raise ValueError("secret_ttl_days must be positive")
        
        # Validate regex
        try:
            re.compile(self.key_regex)
        except re.error as e:
            raise ValueError(f"Invalid key_regex: {e}")
    
    def matches_scope(self, scope_level: str, scope_ref_id: str) -> bool:
        """Check if policy matches the given scope"""
        if self.scope == "GLOBAL":
            return True
        elif self.scope == "PROJECT":
            return scope_level == "PROJECT"
        elif self.scope == "SERVICE":
            return scope_level in ["PROJECT", "SERVICE"]
        elif self.scope == "ENV":
            return scope_level in ["PROJECT", "SERVICE", "ENV"]
        else:
            return False
    
    def validate_key(self, key: str) -> bool:
        """Validate key against policy regex"""
        return bool(re.match(self.key_regex, key))
    
    def validate_value_size(self, value: str) -> bool:
        """Validate value size against policy"""
        size_kb = len(value.encode('utf-8')) / 1024
        return size_kb <= self.value_max_kb
    
    def requires_approval_for_scope(self, scope_level: str, scope_ref_id: str) -> bool:
        """Check if approval is required for the given scope"""
        return self.matches_scope(scope_level, scope_ref_id) and self.require_approval
    
    def get_min_approvers_for_scope(self, scope_level: str, scope_ref_id: str) -> int:
        """Get minimum approvers required for the given scope"""
        if self.matches_scope(scope_level, scope_ref_id):
            return self.min_approvers
        return 0
    
    def get_secret_ttl_for_scope(self, scope_level: str, scope_ref_id: str) -> Optional[int]:
        """Get secret TTL for the given scope"""
        if self.matches_scope(scope_level, scope_ref_id):
            return self.secret_ttl_days
        return None
    
    def requires_justification_for_reveal(self, scope_level: str, scope_ref_id: str) -> bool:
        """Check if justification is required for secret reveal in the given scope"""
        return self.matches_scope(scope_level, scope_ref_id) and self.reveal_justification_required
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'scope': self.scope,
            'require_approval': self.require_approval,
            'min_approvers': self.min_approvers,
            'secret_ttl_days': self.secret_ttl_days,
            'key_regex': self.key_regex,
            'value_max_kb': self.value_max_kb,
            'reveal_justification_required': self.reveal_justification_required,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat()
        }
