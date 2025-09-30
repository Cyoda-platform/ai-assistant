# Workflow Configuration Code Structure

This directory contains the Python code representation of workflow configurations, organized in a clean domain-driven architecture.

## 🏗️ Directory Structure

```
workflows/
├── agents/                      # Agent Components
│   ├── configs/     (50)       # Agent configurations (workflow orchestration agents)
│   ├── tools/       (60)       # AI agent tools
│   └── prompts/     (49)       # AI agent prompts
├── functions/       (36)       # Workflow functions (workflow-specific operations)
├── messages/        (30)       # Workflow user communication messages
└── configs/         (16)       # Workflow configurations
```

## 📋 Component Types

### Agent Configurations (`agents/configs/`)
- **Purpose**: Workflow orchestration agents that process workflow states and transitions
- **Structure**: Each agent has its own directory with `agent.py`, `config.py`, and `__init__.py`
- **Examples**: `process_user_input_f107/`, `generate_app_python/`, `submit_answer_4a45/`
- **Interface**: Implements `AgentProcessor` with `get_name()` and `get_config()` methods

### AI Agent Tools (`agents/tools/`)
- **Purpose**: Tools that AI agents can call to perform specific actions
- **Structure**: Each tool has its own directory with `tool.py`, `config.py`, and `__init__.py`
- **Examples**: `build_general_application_f281/`, `web_search_53be/`, `deploy_cyoda_env_76b1/`
- **Interface**: Implements `FunctionProcessor` with `get_name()` and `get_config()` methods

### AI Agent Prompts (`agents/prompts/`)
- **Purpose**: AI instruction prompts used by agents
- **Structure**: Each prompt has its own directory with `prompt.py`, `config.py`, and `__init__.py`
- **Examples**: `generate_app_python/`, `process_user_input_a094/`, `compile_project_f6g5/`
- **Interface**: Implements `PromptConfig` with `get_name()` and `get_config()` methods

### Workflow Functions (`functions/`)
- **Purpose**: Workflow-specific functions for state management and orchestration
- **Structure**: Each function has its own directory with `function.py`, `config.py`, and `__init__.py`
- **Examples**: `is_stage_completed_e7bf/`, `clone_repo_b60a/`, `init_chats_d512/`
- **Interface**: Implements `FunctionProcessor` with `get_name()` and `get_config()` methods

### Workflow Messages (`messages/`)
- **Purpose**: User communication messages sent during workflow execution
- **Structure**: Each message has its own directory with `message.py`, `config.py`, and `__init__.py`
- **Examples**: `welcome_user_25fc/`, `notify_deployment_success_7458/`, `ask_about_api_063f/`
- **Interface**: Implements `MessageProcessor` with `get_name()` and `get_config()` methods

### Workflow Configurations (`configs/`)
- **Purpose**: Complete workflow definitions with states, transitions, and processors
- **Structure**: Each workflow has its own directory with `workflow.py`, `config.py`, and `__init__.py`
- **Examples**: `build_general_application_python/`, `deploy_cyoda_env/`, `chat_entity/`
- **Interface**: Implements workflow configuration with `get_name()` and `get_config()` methods

## 🔄 Converting Between Code and JSON

### Convert Code to JSON Configs
Use the `convert_code_to_configs.py` script to convert this Python code structure back to JSON configurations:

```bash
python convert_code_to_configs.py
```

This will:
- Read all Python configurations from `workflow_config_code/workflows/`
- Generate JSON configurations in `workflow_configs/`
- Maintain the proper structure for each component type

### Convert JSON Configs to Code
Use the `convert_configs_to_code.py` script to convert JSON configurations to Python code:

```bash
python convert_configs_to_code.py
```

This will:
- Read JSON configurations from `workflow_configs/`
- Generate Python code in `workflow_config_code/workflows/`
- Create proper class interfaces and imports

## 🎯 Import Paths

All components use the new domain-based import structure:

```python
# Agent configurations
from workflow_config_code.workflows.agents.configs.process_user_input_f107.agent import ProcessUserInputF107AgentConfig

# AI agent tools
from workflow_config_code.workflows.agents.tools.web_search_53be.tool import WebSearch53beToolConfig

# AI agent prompts
from workflow_config_code.workflows.agents.prompts.generate_app_python.prompt import GenerateAppPythonPromptConfig

# Workflow functions
from workflow_config_code.workflows.functions.is_stage_completed_e7bf.function import IsStageCompletedE7bfFunctionConfig

# Workflow messages
from workflow_config_code.workflows.messages.welcome_user_25fc.message import WelcomeUser25fcMessageConfig

# Workflow configurations
from workflow_config_code.workflows.configs.build_general_application_python.workflow import BuildGeneralApplicationPythonWorkflowConfig
```

## 🔧 Key Features

1. **Domain Separation**: Clear separation between workflow orchestration and AI agent processing
2. **Consistent Interfaces**: All components implement standard processor interfaces
3. **Type Safety**: Full type hints and proper Python class structure
4. **Modular Design**: Each component is self-contained with its own configuration
5. **Easy Conversion**: Seamless conversion between Python code and JSON configurations

## 📝 Notes

- All components are automatically generated from JSON configurations
- Each component directory contains `__init__.py` to make it a proper Python package
- Configuration logic is separated into `config.py` files for better organization
- Import paths reflect the new domain-driven architecture structure
- The structure mirrors the organization of `workflow_configs/` but in Python code form
