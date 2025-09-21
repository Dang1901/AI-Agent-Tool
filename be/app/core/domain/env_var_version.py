"""
Domain model for Environment Variable Versions
"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
import hashlib
import json


@dataclass
class EnvVarVersion:
    """Version of an environment variable for tracking changes"""
    id: str
    env_var_id: str
    version: int
    diff_json: Dict[str, Any]
    checksum: str
    author: str
    created_at: datetime
    
    def __post_init__(self):
        """Validate and compute checksum if not provided"""
        if not self.checksum:
            self.checksum = self._compute_checksum()
    
    def _compute_checksum(self) -> str:
        """Compute checksum for this version"""
        content = json.dumps(self.diff_json, sort_keys=True)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def verify_checksum(self) -> bool:
        """Verify the checksum is correct"""
        expected = self._compute_checksum()
        return self.checksum == expected
    
    def get_diff_summary(self) -> str:
        """Get human-readable summary of changes"""
        changes = []
        for field, change in self.diff_json.items():
            if isinstance(change, dict) and 'old' in change and 'new' in change:
                changes.append(f"{field}: {change['old']} → {change['new']}")
            else:
                changes.append(f"{field}: {change}")
        return "; ".join(changes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'env_var_id': self.env_var_id,
            'version': self.version,
            'diff_json': self.diff_json,
            'checksum': self.checksum,
            'author': self.author,
            'created_at': self.created_at.isoformat(),
            'diff_summary': self.get_diff_summary()
        }
