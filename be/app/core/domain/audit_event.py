"""
Domain model for Audit Events
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json


class AuditAction(Enum):
    """Audit action types"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    REVEAL = "REVEAL"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    APPLY = "APPLY"
    ROLLBACK = "ROLLBACK"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


class AuditTargetType(Enum):
    """Audit target types"""
    ENV_VAR = "ENV_VAR"
    RELEASE = "RELEASE"
    APPROVAL = "APPROVAL"
    POLICY = "POLICY"


@dataclass
class AuditEvent:
    """Audit event for tracking all changes"""
    id: str
    actor: str
    action: AuditAction
    target_type: AuditTargetType
    target_id: str
    before_json: Optional[Dict[str, Any]]
    after_json: Optional[Dict[str, Any]]
    reason: Optional[str]
    timestamp: datetime
    
    def __post_init__(self):
        """Validate audit event"""
        if self.action in [AuditAction.UPDATE, AuditAction.APPROVE, AuditAction.REJECT]:
            if not self.before_json and not self.after_json:
                raise ValueError(f"Action {self.action.value} requires before_json or after_json")
    
    def get_action_description(self) -> str:
        """Get human-readable action description"""
        return f"{self.actor} {self.action.value.lower()}d {self.target_type.value.lower()} {self.target_id}"
    
    def get_change_summary(self) -> str:
        """Get summary of changes made"""
        if not self.before_json and not self.after_json:
            return "No changes recorded"
        
        if not self.before_json:
            return "Created new record"
        
        if not self.after_json:
            return "Deleted record"
        
        # Compare before and after
        changes = []
        all_keys = set(self.before_json.keys()) | set(self.after_json.keys())
        
        for key in all_keys:
            before_val = self.before_json.get(key)
            after_val = self.after_json.get(key)
            
            if before_val != after_val:
                if before_val is None:
                    changes.append(f"Added {key}: {after_val}")
                elif after_val is None:
                    changes.append(f"Removed {key}: {before_val}")
                else:
                    changes.append(f"Changed {key}: {before_val} → {after_val}")
        
        return "; ".join(changes) if changes else "No changes detected"
    
    def is_sensitive_action(self) -> bool:
        """Check if this is a sensitive action that should be logged with extra care"""
        return self.action in [AuditAction.REVEAL, AuditAction.DELETE, AuditAction.APPROVE, AuditAction.REJECT]
    
    def get_masked_before_json(self) -> Optional[Dict[str, Any]]:
        """Get before_json with sensitive data masked"""
        if not self.before_json:
            return None
        
        return self._mask_sensitive_data(self.before_json.copy())
    
    def get_masked_after_json(self) -> Optional[Dict[str, Any]]:
        """Get after_json with sensitive data masked"""
        if not self.after_json:
            return None
        
        return self._mask_sensitive_data(self.after_json.copy())
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in audit records"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['value', 'password', 'secret', 'token', 'key']:
                    data[key] = "***"
                elif isinstance(value, dict):
                    data[key] = self._mask_sensitive_data(value)
                elif isinstance(value, list):
                    data[key] = [self._mask_sensitive_data(item) if isinstance(item, dict) else item for item in value]
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'actor': self.actor,
            'action': self.action.value,
            'target_type': self.target_type.value,
            'target_id': self.target_id,
            'before_json': self.get_masked_before_json(),
            'after_json': self.get_masked_after_json(),
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'action_description': self.get_action_description(),
            'change_summary': self.get_change_summary(),
            'is_sensitive': self.is_sensitive_action()
        }
