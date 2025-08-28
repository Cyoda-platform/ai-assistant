"""
AskAboutApiD91fMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_about_api_d91f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Would you like to improve or make adjustments to the functional requirements and the API?
    
 Please, feel free to edit this requirement directly in the 'src/main/java/com/java_template/prototype/functional_requirements.md' file.

 Once you edit the file, please push the changes to the repository. If you do not have access to the repository, please, ask for access with 'Please, give me access to the repository. My github username is {github_username}'.

 Open to feedback if you’ve got any ideas — I’m all ears👂👂

 Well... sort of😏."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
