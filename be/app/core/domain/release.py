"""
Domain model for Releases
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class ReleaseStatus(Enum):
    """Status of releases"""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass
class Release:
    """Release for applying environment variable changes"""
    id: str
    service_id: str
    environment: str
    title: str
    description: Optional[str]
    status: ReleaseStatus
    changes: List[Dict[str, Any]]  # List of env var changes
    created_by: str
    created_at: datetime
    applied_by: Optional[str]
    applied_at: Optional[datetime]
    
    def __post_init__(self):
        """Validate release"""
        if not self.title.strip():
            raise ValueError("Release title cannot be empty")
        
        if not self.changes:
            raise ValueError("Release must have at least one change")
    
    def can_be_approved(self) -> bool:
        """Check if release can be approved"""
        return self.status == ReleaseStatus.PENDING_APPROVAL
    
    def can_be_applied(self) -> bool:
        """Check if release can be applied"""
        return self.status == ReleaseStatus.APPROVED
    
    def can_be_cancelled(self) -> bool:
        """Check if release can be cancelled"""
        return self.status in [ReleaseStatus.DRAFT, ReleaseStatus.PENDING_APPROVAL]
    
    def get_change_summary(self) -> str:
        """Get human-readable summary of changes"""
        summaries = []
        for change in self.changes:
            action = change.get('action', 'unknown')
            key = change.get('key', 'unknown')
            summaries.append(f"{action}: {key}")
        return "; ".join(summaries)
    
    def get_affected_services(self) -> List[str]:
        """Get list of affected services"""
        services = set()
        for change in self.changes:
            if 'service_id' in change:
                services.add(change['service_id'])
        return list(services)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'environment': self.environment,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'changes': self.changes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'applied_by': self.applied_by,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'change_summary': self.get_change_summary(),
            'affected_services': self.get_affected_services()
        }
