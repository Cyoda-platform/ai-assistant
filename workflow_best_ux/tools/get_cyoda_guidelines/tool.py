"""
Get Cyoda Guidelines Tool

Implements Processor and AIConfig interfaces.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import FunctionProcessor, ToolConfig
from workflow_best_ux.builders import tool_config


class GetCyodaGuidelinesTool(FunctionProcessor):
    """Cyoda guidelines tool with implementation"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "get_cyoda_guidelines"

    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        return (tool_config("get_cyoda_guidelines")
                .with_description("Retrieve Cyoda platform guidelines for workflows")
                .add_parameter("workflow_name", "string", "Name of the workflow", required=True)
                .build())

    async def execute(self, **params) -> str:
        """Execute Cyoda guidelines retrieval"""
        try:
            workflow_name = params.get("workflow_name", "")
            if not workflow_name:
                return "No workflow name provided"

            # Placeholder implementation
            return f"Cyoda Guidelines for '{workflow_name}'"

        except Exception as e:
            return f"Error getting guidelines: {str(e)}"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process guidelines retrieval as a function processor"""
        try:
            workflow_name = context.get("workflow_name", "")
            result = await self.execute(workflow_name=workflow_name)

            return {
                "guidelines": result,
                "workflow_name": workflow_name,
                "status": "completed"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


# Create singleton instance
get_cyoda_guidelines_tool = GetCyodaGuidelinesTool()
