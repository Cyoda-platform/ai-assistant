"""
GenerateEntitiesRequirements1641PromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/generate_entities_requirements_1641/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Please return a json with the list of entities and their data model example based on the functional requirement.
        Example:
        { "entities": [
        {"EntityName": {
            "entity_data_example": {
                "field1": "value1",
                "field2": "value2"
            }
        }}
        ]}
        
        You must return the json with the list of entities and their data model example. 
        You should keep the entities and their data model exactly as they are in the functional requirement. 
        Do not add any additional entities or fields. 
        Do not remove any entities or fields.
        Response format: Return only json without any extra text."""
