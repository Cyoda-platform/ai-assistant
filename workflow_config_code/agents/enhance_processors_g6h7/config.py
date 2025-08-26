"""
EnhanceProcessorsG6h7AgentConfig Configuration

Configuration data for the enhance processors agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.enhance_processors_g6h7.prompt import EnhanceProcessorsG6h7PromptConfig
from workflow_config_code.prompts.enhance_processors_e5f4.prompt import EnhanceProcessorsE5f4PromptConfig
from workflow_config_code.prompts.enhance_criteria_e5f4.prompt import EnhanceCriteriaE5f4PromptConfig
from workflow_config_code.prompts.enhance_controller_d4e3.prompt import EnhanceControllerD4e3PromptConfig
from workflow_config_code.prompts.gen_processors_tests_e5f4.prompt import GenProcessorsTestsE5f4
from workflow_config_code.tools.validate_workflow_processors.tool import ValidateWorkflowProcessorsToolConfig

from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig


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
                 "EnhanceControllerD4e3PromptConfig"
             ],
             "output": "src/main/java/com/java_template/application/controller/{entityname}/version_1/{EntityName}Controller.java",
             "tool_choice": "auto",
             "max_iteration": 30,
             "approve": True,
             "input": {
                 "local_fs": [
                     "src/main/java/com/java_template/application/controller/{entityname}/version_1/{EntityName}Controller.java",
                     "src/main/java/com/java_template/application/entity/{entityname}/version_1/{EntityName}.java",
                     "src/main/java/com/java_template/prototype/project_compilation.log"
                 ]
             },
             "messages": [
                 {
                     "role": "user",
                     "content_from_file": EnhanceControllerD4e3PromptConfig.get_name()
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
                    "EnhanceProcessorsE5f4PromptConfig"
                ],
                "output": "src/main/java/com/java_template/application/processor/{ProcessorName}.java",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/java/com/java_template/prototype/user_requirement.md",
                        "src/main/java/com/java_template/application/entity",
                        "src/main/java/com/java_template/application/processor/{ProcessorName}.java",
                        "src/main/java/com/java_template/prototype/project_compilation.log"
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": EnhanceProcessorsE5f4PromptConfig.get_name()
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
                    "EnhanceCriteriaE5f4PromptConfig"
                ],
                "output": "src/main/java/com/java_template/application/criterion/{CriterionName}.java",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/java/com/java_template/prototype/user_requirement.md",
                        "src/main/java/com/java_template/application/entity",
                        "src/main/java/com/java_template/application/criterion/{CriterionName}.java",
                        "src/main/java/com/java_template/prototype/project_compilation.log"
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": EnhanceCriteriaE5f4PromptConfig.get_name()
                    }
                ]
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
                    "EnhanceProcessorsE5f4PromptConfig"
                ],
                "output": "src/test/java/com/java_template/application/processor/{ProcessorName}Test.java",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "src/main/java/com/java_template/application/processor/{ProcessorName}.java",
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": GenProcessorsTestsE5f4.get_name()
                    }
                ]
            },
        ]
    }
