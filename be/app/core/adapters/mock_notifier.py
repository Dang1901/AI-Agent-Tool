"""
Mock implementation of Notifier for testing
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..ports.notifier import Notifier


class MockNotifier(Notifier):
    """Mock implementation of Notifier for testing"""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
    
    async def send_notification(self, 
                              recipients: List[str], 
                              subject: str, 
                              message: str, 
                              notification_type: str = "info") -> bool:
        """Send notification to recipients"""
        notification = {
            'type': 'notification',
            'recipients': recipients,
            'subject': subject,
            'message': message,
            'notification_type': notification_type,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_approval_request(self, 
                                 approvers: List[str], 
                                 release_id: str, 
                                 release_title: str, 
                                 release_url: str) -> bool:
        """Send approval request notification"""
        notification = {
            'type': 'approval_request',
            'approvers': approvers,
            'release_id': release_id,
            'release_title': release_title,
            'release_url': release_url,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_approval_decision(self, 
                                  release_id: str, 
                                  decision: str, 
                                  approver: str, 
                                  comment: Optional[str]) -> bool:
        """Send approval decision notification"""
        notification = {
            'type': 'approval_decision',
            'release_id': release_id,
            'decision': decision,
            'approver': approver,
            'comment': comment,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_release_applied(self, 
                                 release_id: str, 
                                 release_title: str, 
                                 applied_by: str) -> bool:
        """Send release applied notification"""
        notification = {
            'type': 'release_applied',
            'release_id': release_id,
            'release_title': release_title,
            'applied_by': applied_by,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_secret_revealed(self, 
                                 env_var_key: str, 
                                 revealed_by: str, 
                                 justification: str) -> bool:
        """Send secret revealed notification"""
        notification = {
            'type': 'secret_revealed',
            'env_var_key': env_var_key,
            'revealed_by': revealed_by,
            'justification': justification,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_rotation_alert(self, 
                                env_var_key: str, 
                                rotation_schedule: str, 
                                next_rotation: datetime) -> bool:
        """Send rotation alert notification"""
        notification = {
            'type': 'rotation_alert',
            'env_var_key': env_var_key,
            'rotation_schedule': rotation_schedule,
            'next_rotation': next_rotation.isoformat(),
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    async def send_drift_alert(self, 
                             service_id: str, 
                             environment: str, 
                             drift_details: Dict[str, Any]) -> bool:
        """Send drift alert notification"""
        notification = {
            'type': 'drift_alert',
            'service_id': service_id,
            'environment': environment,
            'drift_details': drift_details,
            'sent_at': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return True
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all sent notifications (for testing)"""
        return self.notifications.copy()
    
    def clear_notifications(self):
        """Clear all notifications (for testing)"""
        self.notifications.clear()
