"""
GetCyodaGuidelinesF3bbToolConfig Configuration

Generated from config: workflow_configs/tools/get_cyoda_guidelines_f3bb/tool.json
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
                                                "generate_workflow",
                                                "generate_processors",
                                                "configure_trino",
                                                "generate_entity",
                                                "cyoda_best_practice"
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
