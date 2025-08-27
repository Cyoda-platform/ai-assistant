"""
NotifyChatLockedDd3eMessage Implementation

Generated from config: workflow_configs/messages/notify_chat_locked_dd3e/meta.json
Message implementation for chat locked notification.
"""

from typing import Any, Dict
from tools.base_workflow_service import BaseWorkflowService


class NotifyChatLockedDd3eMessage(BaseWorkflowService):
    """Message for notifying chat has been locked"""

    def run(self, technical_id: str, entity: Dict[str, Any], **params) -> Dict[str, Any]:
        """
        Send notification that chat has been locked
        
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
