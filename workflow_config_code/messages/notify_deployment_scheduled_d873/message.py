"""
NotifyDeploymentScheduledD873Message Implementation

Generated from config: workflow_configs/messages/notify_deployment_scheduled_d873/meta.json
Message implementation for deployment scheduled notification.
"""

from typing import Any, Dict
from tools.base_workflow_service import BaseWorkflowService


class NotifyDeploymentScheduledD873Message(BaseWorkflowService):
    """Message for notifying deployment has been scheduled"""

    def run(self, technical_id: str, entity: Dict[str, Any], **params) -> Dict[str, Any]:
        """
        Send notification that deployment has been scheduled
        
        Args:
            technical_id: Technical identifier
            entity: Entity data
            **params: Additional parameters
            
        Returns:
            Dict containing the result of sending the notification
        """
        return self.send_message(
            message_type="notification",
            technical_id=technical_id,
            entity=entity,
            **params
        )
