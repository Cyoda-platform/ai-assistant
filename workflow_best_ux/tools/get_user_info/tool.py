"""
Get User Info Tool

Implements Processor and AIConfig interfaces.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import FunctionProcessor, ToolConfig
from workflow_best_ux.builders import tool_config


class GetUserInfoTool(FunctionProcessor):
    """User info tool with implementation"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "get_user_info"

    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        return (tool_config("get_user_info")
                .with_description("Retrieve information about the current user including permissions and preferences")
                .add_parameter("user_id", "string", "User identifier (optional, uses current user if not provided)", required=False)
                .add_parameter("include_permissions", "boolean", "Whether to include user permissions in the response", required=False, default=True)
                .build())

    async def execute(self, **params) -> str:
        """Execute user info retrieval"""
        try:
            user_id = params.get("user_id", "current_user")
            include_permissions = params.get("include_permissions", True)

            result = f"User info for: {user_id}"
            if include_permissions:
                result += "\nPermissions: read, write, execute"

            return result

        except Exception as e:
            return f"Error getting user info: {str(e)}"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user info retrieval as a function processor"""
        try:
            user_id = context.get("user_id", "current_user")
            include_permissions = context.get("include_permissions", True)

            result = await self.execute(user_id=user_id, include_permissions=include_permissions)

            return {
                "user_info": result,
                "user_id": user_id,
                "status": "completed"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


# Create singleton instance
get_user_info_tool = GetUserInfoTool()
