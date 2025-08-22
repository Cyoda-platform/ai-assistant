"""
GenerateControllerD4e3AgentConfig Configuration

Configuration data for the generate controller agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.generate_criteria_e5f4.prompt import GenerateCriteriaE5f4PromptConfig
from workflow_config_code.prompts.generate_processors_and_criteria_e5f4.prompt import \
    GenerateProcessorsAndCriteriaE5f4PromptConfig
from workflow_config_code.prompts.generate_controller_d4e3.prompt import GenerateControllerD4e3PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "jobs": [
            {"type": "agent",
             "publish": False,
             "model": {},
             "tools": [
             ],
             "split_function": {"name": "get_entity_names_from_entities_requirement",
                                "split_parameter": "EntityName",
                                "input_file": "src/main/java/com/java_template/prototype/entities_requirement.json"},

             "memory_tags": [
                 "GenerateControllerD4e3PromptConfig"
             ],
             "output": "src/main/java/com/java_template/application/controller/{entityname}/version_1/{EntityName}Controller.java",
             "tool_choice": "auto",
             "max_iteration": 30,
             "approve": True,
             "input": {
                 "local_fs": [
                     "src/main/java/com/java_template/prototype/functional_requirement.md",
                     "src/main/java/com/java_template/application/entity/{entityname}/version_1/{EntityName}.java"
                 ]
             },
             "messages": [
                 {
                     "role": "user",
                     "content_from_file": GenerateControllerD4e3PromptConfig.get_name()
                 }
             ],

             },
            {
                "type": "agent",
                "publish": False,
                "model": {},
                "tools": [
                ],
                "split_function": {"name": "validate_workflow_processors",
                                   "split_parameter": "ProcessorName",
                                   "input_file": "src/main/java/com/java_template/prototype/workflow_processors.json"},
                # todo unnecessary

                "memory_tags": [
                    "GenerateProcessorsAndCriteriaE5f4PromptConfig"
                ],
                "output": "src/main/java/com/java_template/application/processor/{ProcessorName}.java",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/java/com/java_template/prototype/user_requirement.md",
                        "src/main/java/com/java_template/application/entity"
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": GenerateProcessorsAndCriteriaE5f4PromptConfig.get_name()
                    }
                ]
            },
            {
                "type": "agent",
                "publish": False,
                "model": {},
                "tools": [
                ],
                "split_function": {"name": "validate_workflow_criteria",
                                   "split_parameter": "CriterionName",
                                   "input_file": "src/main/java/com/java_template/prototype/workflow_processors.json"},
                # todo unnecessary

                "memory_tags": [
                    "GenerateCriteriaE5f4PromptConfig"
                ],
                "output": "src/main/java/com/java_template/application/criterion/{CriterionName}.java",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/java/com/java_template/prototype/user_requirement.md",
                        "src/main/java/com/java_template/application/entity"
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": GenerateCriteriaE5f4PromptConfig.get_name()
                    }
                ]
            }
        ]
    }
