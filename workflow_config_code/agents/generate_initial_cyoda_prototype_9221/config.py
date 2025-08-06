"""
GenerateInitialCyodaPrototype9221AgentConfig Configuration

Generated from config: workflow_configs/agents/generate_initial_cyoda_prototype_9221/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.generate_initial_cyoda_prototype_9ff0.prompt import \
    GenerateInitialCyodaPrototype9ff0PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "model": {},
        "memory_tags": [
            "controller_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateInitialCyodaPrototype9ff0PromptConfig.get_name()
            }
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/EntityControllerPrototype.java"
            ]
        },
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/application/controller/Controller.java"
            ]
        }
    }
