"""
LockChat670cTool Implementation

Generated from config: workflow_configs/tools/lock_chat_670c/tool.json
Tool implementation for lock_chat function.
"""

from typing import Any, Dict
from tools.base_workflow_service import BaseWorkflowService


class LockChat670cTool(BaseWorkflowService):
    """Tool for locking chat during deployment"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "lock_chat"

    def run(self, technical_id: str, entity: Dict[str, Any], **params) -> Dict[str, Any]:
        """
        Lock the chat to prevent user interaction
        
        Args:
            technical_id: Technical identifier
            entity: Entity data
            **params: Additional parameters
            
        Returns:
            Dict containing the result of locking the chat
        """
        return self.call_function(
            function_name="lock_chat",
            technical_id=technical_id,
            entity=entity,
            **params
        )
