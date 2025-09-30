"""
QuestionToProceedWithGeneratedAppEditing2f5fMessageConfig Configuration

Generated from config: workflow_configs/messages/question_to_proceed_with_generated_app_editing_2f5f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ Your application is ready in the {git_branch} branch!

 [Cyoda GitHub](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch}) 👀 

Let’s bring it to life — together. Setup assistant will start in a moment!"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': False, 'publish': True}
