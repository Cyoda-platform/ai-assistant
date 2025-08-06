"""
SaveWorkflowCode959fPromptConfig Configuration

Generated from config: workflow_configs/prompts/save_workflow_code_959f/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Which workflow would you recommend for this code?
 How would you split this code into functions and condition functions (return boolean) so that you can use them in the workflow transitions"""
