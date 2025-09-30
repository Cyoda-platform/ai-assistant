#!/usr/bin/env python3
"""
Create workflow functions from existing tools

This script creates workflow function wrappers in the functions/ directory
for tools that are referenced as FunctionProcessor in workflows.
"""

import json
from pathlib import Path
from typing import Dict, Any


def create_workflow_function(function_name: str, tool_config: Dict[str, Any]):
    """Create a workflow function wrapper for a tool"""
    
    # Create function directory
    function_dir = Path(f"workflow_config_code/workflows/functions/{function_name}")
    function_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    with open(function_dir / "__init__.py", 'w') as f:
        f.write('"""Generated Python package for workflow function"""\n')
    
    # Create config.py
    # Convert tool config to Python format
    config_str = json.dumps(tool_config, indent=8)
    config_str = config_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')

    config_code = f'''"""
{function_name.replace('_', ' ').title().replace(' ', '')}FunctionConfig Configuration

Generated from tool: {function_name}
Configuration data for the workflow function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {config_str}
'''
    
    with open(function_dir / "config.py", 'w') as f:
        f.write(config_code)
    
    # Create function.py
    # Convert function name to proper class name (e.g., is_stage_completed_8a02 -> IsStageCompleted8a02FunctionConfig)
    class_name = ''.join(word.capitalize() for word in function_name.split('_')) + "FunctionConfig"
    
    function_code = f'''"""
{class_name} Function

Generated from tool: {function_name}
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class {class_name}(FunctionProcessor):
    """Function configuration for {function_name}"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{{{class_name}.get_type()}}.{function_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "{function_name}"


# Create singleton instance
{function_name}_function = {class_name}()
'''
    
    with open(function_dir / "function.py", 'w') as f:
        f.write(function_code)
    
    print(f"  ✅ Created workflow function: {function_name}")


def main():
    """Create all workflow functions from tools"""
    print("🔄 CREATING WORKFLOW FUNCTIONS FROM TOOLS")
    print("=" * 50)
    
    # List of functions needed by workflows
    workflow_functions = [
        "check_scheduled_entity_status_4d37",
        "clone_repo_b60a", 
        "convert_workflow_to_dto_d870",
        "delete_files_6818",
        "generate_prototype_sketch_2269",
        "init_chats_d512",
        "init_chats_d512_py",
        "init_setup_workflow_5f06",
        "is_chat_locked_5b22",
        "is_chat_unlocked_f77c",
        "is_stage_completed_68b2",
        "is_stage_completed_8a02",
        "is_stage_completed_b809",
        "is_stage_completed_cf58",
        "is_stage_completed_d5ca",
        "is_stage_completed_discuss_prototype_0000",
        "is_stage_completed_e0d9",
        "is_stage_completed_e7bf",
        "is_stage_completed_ebb9",
        "lock_chat_670c",
        "not_stage_completed_2f18",
        "not_stage_completed_5e0e",
        "not_stage_completed_6d2b",
        "not_stage_completed_812b",
        "not_stage_completed_85df",
        "not_stage_completed_d1b6",
        "not_stage_completed_discuss_prototype_0000",
        "not_stage_completed_f259",
        "not_stage_completed_f57d",
        "save_env_file_d2aa",
        "schedule_deploy_env_f9ed",
        "trigger_parent_entity_b4c4"
    ]
    
    tools_dir = Path("workflow_configs/tools")
    
    for function_name in workflow_functions:
        tool_json_path = tools_dir / function_name / "tool.json"
        
        if tool_json_path.exists():
            # Load tool configuration
            with open(tool_json_path, 'r') as f:
                tool_config = json.load(f)
            
            # Create workflow function
            create_workflow_function(function_name, tool_config)
        else:
            print(f"  ❌ Tool not found: {function_name}")
    
    print(f"\n✅ Workflow functions creation complete!")


if __name__ == "__main__":
    main()
