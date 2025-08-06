"""
AskToDiscussConfigs0000MessageConfig Configuration

Generated from config: workflow_configs/messages/ask_to_discuss_configs_0000/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: \
"""✅ **Entity POJOs** and **workflow configurations** have been added to your application.

Entities can be found in the file 'src/main/java/com/java_template/application/entity/{EntityName}.java'.
Workflows can be found in the file 'src/main/java/com/java_template/application/workflow/{EntityName}.json'.

This event‑driven approach allows complex business logic to be defined declaratively and evolve through configuration instead of code changes.
 
For a detailed reference on workflow configuration, see the **[Cyoda Workflow Configuration Guide](https://docs.cyoda.net/#guides/workflow-config-guide)**. It explains:

• How to define states, transitions, and criteria  
• Manual vs automated transitions  
• Processor execution modes and best practices  
• Example workflows like "Payment Request Workflow" for real-world scenarios

You can preview workflows visually in the **“Open canvas”** view (upper-right corner of the UI).

Please review the generated entities and workflows in your `{git_branch}`.

🔗 [Cyoda GitHub](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch})

You can edit them directly in the code and we’ll assist with any changes or questions. 🚀"""



def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
