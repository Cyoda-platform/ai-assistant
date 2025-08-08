"""
GeneratePrototypeSketch2269FunctionConfig Configuration

Configuration data for the generate_prototype_sketch_2269 tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "generate_prototype_sketch_2269",
            "description": "Generates a prototype sketch by launching the functional requirements to prototype Java workflow. This tool saves a new entity and launches the agentic workflow for prototype generation.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "The user request for prototype generation"
                    }
                },
                "required": [
                    "user_request"
                ],
                "additionalProperties": False
            }
        }
    }
