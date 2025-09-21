"""
Real implementation of Notifier for Slack
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

from app.core.ports.notifier import Notifier


class SlackNotifier(Notifier):
    """Real implementation of Notifier for Slack"""
    
    def __init__(self, webhook_url: str = None, token: str = None):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url: Slack webhook URL for sending messages
            token: Slack bot token for API calls
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        
        if not self.webhook_url and not self.token:
            raise ValueError("Either SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN must be provided")
    
    async def send_notification(self, 
                              recipients: List[str], 
                              subject: str, 
                              message: str, 
                              notification_type: str = "info") -> bool:
        """Send notification to recipients"""
        try:
            # Format message for Slack
            slack_message = self._format_slack_message(subject, message, notification_type)
            
            # Send to Slack
            if self.webhook_url:
                return await self._send_webhook_message(slack_message)
            elif self.token:
                return await self._send_api_message(recipients, slack_message)
            else:
                return False
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False
    
    async def send_approval_request(self, 
                                 approvers: List[str], 
                                 release_id: str, 
                                 release_title: str, 
                                 release_url: str) -> bool:
        """Send approval request notification"""
        message = f"""
🚀 *Release Approval Request*

*Release:* {release_title}
*ID:* {release_id}
*Approvers:* {', '.join(approvers)}

Please review and approve this release:
{release_url}
        """.strip()
        
        return await self.send_notification(
            recipients=approvers,
            subject="Release Approval Request",
            message=message,
            notification_type="warning"
        )
    
    async def send_approval_decision(self, 
                                  release_id: str, 
                                  decision: str, 
                                  approver: str, 
                                  comment: Optional[str]) -> bool:
        """Send approval decision notification"""
        emoji = "✅" if decision == "APPROVED" else "❌"
        message = f"""
{emoji} *Release {decision}*

*Release ID:* {release_id}
*Approver:* {approver}
*Decision:* {decision}
*Comment:* {comment or "No comment provided"}
        """.strip()
        
        return await self.send_notification(
            recipients=[approver],
            subject=f"Release {decision}",
            message=message,
            notification_type="success" if decision == "APPROVED" else "error"
        )
    
    async def send_release_applied(self, 
                                 release_id: str, 
                                 release_title: str, 
                                 applied_by: str) -> bool:
        """Send release applied notification"""
        message = f"""
🎉 *Release Applied Successfully*

*Release:* {release_title}
*ID:* {release_id}
*Applied by:* {applied_by}
*Applied at:* {datetime.now().isoformat()}
        """.strip()
        
        return await self.send_notification(
            recipients=[applied_by],
            subject="Release Applied",
            message=message,
            notification_type="success"
        )
    
    async def send_secret_revealed(self, 
                                 env_var_key: str, 
                                 revealed_by: str, 
                                 justification: str) -> bool:
        """Send secret revealed notification"""
        message = f"""
🔓 *Secret Revealed*

*Environment Variable:* {env_var_key}
*Revealed by:* {revealed_by}
*Justification:* {justification}
*Timestamp:* {datetime.now().isoformat()}

⚠️ *Security Alert:* A secret has been revealed. Please ensure this is authorized.
        """.strip()
        
        return await self.send_notification(
            recipients=[revealed_by],
            subject="Secret Revealed - Security Alert",
            message=message,
            notification_type="warning"
        )
    
    async def send_rotation_alert(self, 
                                env_var_key: str, 
                                rotation_schedule: str, 
                                next_rotation: datetime) -> bool:
        """Send rotation alert notification"""
        message = f"""
🔄 *Secret Rotation Alert*

*Environment Variable:* {env_var_key}
*Schedule:* {rotation_schedule}
*Next Rotation:* {next_rotation.isoformat()}

The secret will be automatically rotated according to the schedule.
        """.strip()
        
        return await self.send_notification(
            recipients=[],  # Send to configured recipients
            subject="Secret Rotation Alert",
            message=message,
            notification_type="info"
        )
    
    async def send_drift_alert(self, 
                             service_id: str, 
                             environment: str, 
                             drift_details: Dict[str, Any]) -> bool:
        """Send drift alert notification"""
        message = f"""
⚠️ *Configuration Drift Detected*

*Service:* {service_id}
*Environment:* {environment}
*Drift Details:* {json.dumps(drift_details, indent=2)}

Please review and resolve the configuration drift.
        """.strip()
        
        return await self.send_notification(
            recipients=[],  # Send to configured recipients
            subject="Configuration Drift Alert",
            message=message,
            notification_type="warning"
        )
    
    async def _send_webhook_message(self, message: Dict[str, Any]) -> bool:
        """Send message via Slack webhook"""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook send failed: {e}")
            return False
    
    async def _send_api_message(self, recipients: List[str], message: Dict[str, Any]) -> bool:
        """Send message via Slack API"""
        try:
            # This is a simplified implementation
            # In real implementation, you'd use Slack SDK
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            for recipient in recipients:
                # Get user ID from username/email
                user_id = await self._get_user_id(recipient)
                if user_id:
                    # Send direct message
                    dm_data = {
                        'channel': user_id,
                        'text': message.get('text', ''),
                        'blocks': message.get('blocks', [])
                    }
                    
                    response = requests.post(
                        'https://slack.com/api/chat.postMessage',
                        headers=headers,
                        json=dm_data,
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        print(f"Failed to send message to {recipient}: {response.text}")
                        return False
            
            return True
        except Exception as e:
            print(f"API send failed: {e}")
            return False
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Get Slack user ID from username/email"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            # This is a simplified implementation
            # In real implementation, you'd use Slack SDK
            response = requests.get(
                'https://slack.com/api/users.lookupByEmail',
                headers=headers,
                params={'email': username},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data['user']['id']
            
            return None
        except Exception as e:
            print(f"Failed to get user ID for {username}: {e}")
            return None
    
    def _format_slack_message(self, subject: str, message: str, notification_type: str) -> Dict[str, Any]:
        """Format message for Slack"""
        # Choose color based on notification type
        color_map = {
            'info': '#36a64f',
            'warning': '#ff9500',
            'error': '#ff0000',
            'success': '#36a64f'
        }
        
        color = color_map.get(notification_type, '#36a64f')
        
        return {
            'text': subject,
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*{subject}*\n\n{message}"
                    }
                }
            ],
            'attachments': [
                {
                    'color': color,
                    'footer': 'EnvVar Manager',
                    'ts': int(datetime.now().timestamp())
                }
            ]
        }
