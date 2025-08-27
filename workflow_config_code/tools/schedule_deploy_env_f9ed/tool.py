"""
ScheduleDeployEnvF9edTool Implementation

Generated from config: workflow_configs/tools/schedule_deploy_env_f9ed/tool.json
Tool implementation for schedule_deploy_env function.
"""

from typing import Any, Dict
from tools.base_workflow_service import BaseWorkflowService


class ScheduleDeployEnvF9edTool(BaseWorkflowService):
    """Tool for scheduling deployment of Cyoda environment"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "schedule_deploy_env"

    def run(self, technical_id: str, entity: Dict[str, Any], **params) -> Dict[str, Any]:
        """
        Schedule deployment of Cyoda environment
        
        Args:
            technical_id: Technical identifier
            entity: Entity data
            **params: Additional parameters
            
        Returns:
            Dict containing the result of scheduling deployment
        """
        return self.call_function(
            function_name="schedule_deploy_env",
            technical_id=technical_id,
            entity=entity,
            **params
        )
