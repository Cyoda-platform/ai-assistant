"""
GetCyodaGuidelines4c97ToolConfig Configuration

Generated from config: workflow_configs/agents/tools/get_cyoda_guidelines_4c97/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_cyoda_guidelines",
                "description": "Use this tool to generate configurations (workflows, entities, Cyoda settings) for informational purposes only, without modifying the application or saving data. If your goal is to change the application, this tool is not suitable. If it's unclear whether you need to modify the application or just need information, please clarify. The retrieved information can then be used to generate the required data without altering the application.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "workflow_name": {
                                        "type": "string",
                                        "enum": [
                                                "#guides/cyoda-design-principles",
                                                "#guides/provision-environment",
                                                "#guides/workflow-config-guide",
                                                "#guides/authentication-authorization",
                                                "#guides/api-saving-and-getting-data",
                                                "#guides/sql-and-trino",
                                                "#concepts/edbms",
                                                "#concepts/event-driven-architecture",
                                                "#concepts/cpl-overview",
                                                "#architecture/cyoda-cloud-architecture",
                                                "#platform/cyoda-cloud-status",
                                                "#platform/entitlements"
                                        ]
                                }
                        },
                        "required": [
                                "workflow_name"
                        ],
                        "additionalProperties": False
                }
        }
}
