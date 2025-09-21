"""
Port interface for notifications
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class Notifier(ABC):
    """Abstract interface for notifications"""
    
    @abstractmethod
    async def send_notification(self, 
                              recipients: List[str], 
                              subject: str, 
                              message: str, 
                              notification_type: str = "info") -> bool:
        """Send notification to recipients"""
        pass
    
    @abstractmethod
    async def send_approval_request(self, 
                                 approvers: List[str], 
                                 release_id: str, 
                                 release_title: str, 
                                 release_url: str) -> bool:
        """Send approval request notification"""
        pass
    
    @abstractmethod
    async def send_approval_decision(self, 
                                  release_id: str, 
                                  decision: str, 
                                  approver: str, 
                                  comment: Optional[str]) -> bool:
        """Send approval decision notification"""
        pass
    
    @abstractmethod
    async def send_release_applied(self, 
                                 release_id: str, 
                                 release_title: str, 
                                 applied_by: str) -> bool:
        """Send release applied notification"""
        pass
    
    @abstractmethod
    async def send_secret_revealed(self, 
                                 env_var_key: str, 
                                 revealed_by: str, 
                                 justification: str) -> bool:
        """Send secret revealed notification"""
        pass
    
    @abstractmethod
    async def send_rotation_alert(self, 
                                env_var_key: str, 
                                rotation_schedule: str, 
                                next_rotation: datetime) -> bool:
        """Send rotation alert notification"""
        pass
    
    @abstractmethod
    async def send_drift_alert(self, 
                             service_id: str, 
                             environment: str, 
                             drift_details: Dict[str, Any]) -> bool:
        """Send drift alert notification"""
        pass
