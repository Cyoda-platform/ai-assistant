"""
Read Link Tool

Implements FunctionProcessor interface with get_config() method.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import FunctionProcessor, ToolConfig
from workflow_best_ux.builders import tool_config


class ReadLinkTool(FunctionProcessor):
    """Read link tool with URL content fetching implementation"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "read_link"

    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        return (tool_config("read_link")
                .with_description("Read content from a given URL")
                .add_parameter("url", "string", "URL to read content from", required=True)
                .build())

    async def execute(self, **params) -> str:
        """Execute URL content reading"""
        try:
            url = params.get("url", "")
            if not url:
                return "No URL provided"

            # Placeholder implementation
            return f"Content from URL: {url}"

        except Exception as e:
            return f"Error reading URL: {str(e)}"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process URL reading as a function processor"""
        try:
            url = context.get("url", "")
            result = await self.execute(url=url)

            return {
                "content": result,
                "url": url,
                "status": "completed"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


# Create singleton instance
read_link_tool = ReadLinkTool()
