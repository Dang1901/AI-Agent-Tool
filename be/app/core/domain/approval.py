"""
Domain model for Approvals
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class ApprovalDecision(Enum):
    """Approval decisions"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


@dataclass
class Approval:
    """Approval for releases"""
    id: str
    release_id: str
    approver_id: str
    decision: ApprovalDecision
    comment: Optional[str]
    decided_at: Optional[datetime]
    
    def __post_init__(self):
        """Validate approval"""
        if self.decision == ApprovalDecision.PENDING and self.decided_at is not None:
            raise ValueError("Pending approvals cannot have decided_at timestamp")
        
        if self.decision != ApprovalDecision.PENDING and self.decided_at is None:
            raise ValueError("Decided approvals must have decided_at timestamp")
    
    def is_pending(self) -> bool:
        """Check if approval is pending"""
        return self.decision == ApprovalDecision.PENDING
    
    def is_approved(self) -> bool:
        """Check if approval is approved"""
        return self.decision == ApprovalDecision.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if approval is rejected"""
        return self.decision == ApprovalDecision.REJECTED
    
    def can_be_updated(self) -> bool:
        """Check if approval can be updated (only pending ones)"""
        return self.is_pending()
    
    def get_decision_summary(self) -> str:
        """Get human-readable decision summary"""
        if self.is_pending():
            return f"Pending approval from {self.approver_id}"
        elif self.is_approved():
            return f"Approved by {self.approver_id}"
        else:
            return f"Rejected by {self.approver_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'release_id': self.release_id,
            'approver_id': self.approver_id,
            'decision': self.decision.value,
            'comment': self.comment,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'is_pending': self.is_pending(),
            'is_approved': self.is_approved(),
            'is_rejected': self.is_rejected(),
            'decision_summary': self.get_decision_summary()
        }
