"""
GetBuildIdFromContextDeebToolConfig Configuration

Generated from config: workflow_configs/tools/get_build_id_from_context_deeb/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_build_id_from_context",
                "description": "Use this tool to get the build ID from deployment workflow context. This tool automatically finds the build ID from the parent entity's deployment workflow without requiring any parameters.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                }
        }
}
