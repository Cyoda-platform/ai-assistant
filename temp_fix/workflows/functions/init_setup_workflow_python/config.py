"""
InitSetupWorkflowJavaWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/init_setup_workflow_python.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.workflows.agents.process_user_input_57d2_py.agent import ProcessUserInput57d2PyAgentConfig
from workflow_config_code.workflows.agents.process_user_input_dd02_py.agent import ProcessUserInputDd02PyAgentConfig
from workflow_config_code.workflows.agents.process_user_input_e32d_py.agent import ProcessUserInputE32dPyAgentConfig
from workflow_config_code.workflows.agents.process_user_input_f107_py.agent import ProcessUserInputF107PyAgentConfig
from workflow_config_code.workflows.agents.prompt_sent_68db_py.agent import PromptSent68dbPyAgentConfig
from workflow_config_code.workflows.agents.prompt_sent_956f_py.agent import PromptSent956fPyAgentConfig
from workflow_config_code.workflows.agents.prompt_sent_a239_py.agent import PromptSentA239PyAgentConfig
from workflow_config_code.workflows.functions.not_stage_completed_d1b6.function import NotStageCompletedD1b6FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_cf58.function import IsStageCompletedCf58FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_e0d9.function import IsStageCompletedE0d9FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_68b2.function import IsStageCompleted68b2FunctionConfig
from workflow_config_code.workflows.agents.process_user_input_52da.agent import ProcessUserInput52daAgentConfig
from workflow_config_code.workflows.functions.is_stage_completed_d5ca.function import IsStageCompletedD5caFunctionConfig
from workflow_config_code.workflows.agents.prompt_sent_59d6.agent import PromptSent59d6AgentConfig
from workflow_config_code.workflows.functions.is_stage_completed_ebb9.function import IsStageCompletedEbb9FunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_6d2b.function import NotStageCompleted6d2bFunctionConfig
from workflow_config_code.workflows.agents.prompt_sent_ef07.agent import PromptSentEf07AgentConfig
from workflow_config_code.workflows.functions.not_stage_completed_812b.function import NotStageCompleted812bFunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_85df.function import NotStageCompleted85dfFunctionConfig
from workflow_config_code.workflows.messages.lock_chat_1135.message import LockChat1135MessageConfig
from workflow_config_code.workflows.functions.not_stage_completed_2f18.function import NotStageCompleted2f18FunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "init_setup_workflow_python",
        "desc": "Migrated from init_setup_workflow_python",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "init_setup_workflow_python"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_chat",
                        "next": "app_requirements_requested",
                        "manual": False
                    }
                ]
            },
            "app_requirements_requested": {
                "transitions": [
                    {
                        "name": "starting_chat",
                        "next": "prompt_app_requirements_step1",
                        "manual": False
                    }
                ]
            },
            "prompt_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step1",
                        "manual": False,
                        "processors": [
                            {
                                "name": PromptSent59d6AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step1": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step3",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "app_requirements_step1_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step1_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInputDd02PyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step1_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_1_processing",
                        "next": "app_requirements_step1",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompletedD1b6FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_app_setup_1_success",
                        "next": "prompt_app_requirements_step3",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedCf58FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "prompt_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step3",
                        "manual": False,
                        "processors": [
                            {
                                "name": PromptSentEf07AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step3": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step4",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "app_requirements_step3_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step3_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInput52daAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_3_processing",
                        "next": "app_requirements_step3",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted2f18FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_app_setup_3_success",
                        "next": "prompt_app_requirements_step4",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedD5caFunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "prompt_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step4",
                        "manual": False,
                        "processors": [
                            {
                                "name": PromptSentA239PyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step4": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step5",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "app_requirements_step4_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step4_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInput57d2PyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step4_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_4_processing",
                        "next": "app_requirements_step4",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted6d2bFunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_app_setup_4_success",
                        "next": "prompt_app_requirements_step5",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedEbb9FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "prompt_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step5",
                        "manual": False,
                        "processors": [
                            {
                                "name": PromptSent68dbPyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step5": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step6",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "app_requirements_step5_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step5_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInputE32dPyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step5_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_5_processing",
                        "next": "app_requirements_step5",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted812bFunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_app_setup_5_success",
                        "next": "prompt_app_requirements_step6",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompleted68b2FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "prompt_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step6",
                        "manual": False,
                        "processors": [
                            {
                                "name": PromptSent956fPyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step6": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "ready_to_lock_chat",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "app_requirements_step6_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step6_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInputE32dPyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "app_requirements_step6_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_6_processing",
                        "next": "app_requirements_step6",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted85dfFunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_app_setup_6_success",
                        "next": "ready_to_lock_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedE0d9FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "ready_to_lock_chat": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "processors": [
                            {
                                "name": LockChat1135MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
