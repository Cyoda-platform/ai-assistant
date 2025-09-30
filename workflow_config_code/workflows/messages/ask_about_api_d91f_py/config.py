"""
AskAboutApiD91fPyMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_about_api_d91f_py/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Your requirement has been added to the `application/resources/functional_requirements` directory.

Would you like to refine or expand the functional requirements and API? If so, please feel free to edit the requirement files directly in the IDE.
Once you’ve made your edits, please push the changes to the repository and click 'Approve' to proceed.
If you don’t yet have access to the repository, you can request it by sending me a message:

```markdown
Please grant me access to the repository. My GitHub username is {github_username}.
```

You are most welcome to use your IDE’s AI agents. The prompt I recommend using to check the requirement is:

```markdown
You are provided with already generated functional requirement files under `application/resources/functional_requirements` and corresponding workflow JSONs in `application/resources/workflow`.

**Task:** Do *not* regenerate. Instead, **review and validate** correctness, completeness, and consistency against:

* `user_requirement.md`
* `user_requirement_additional_info.md`

#### Checks

1. **Entities** – Attributes, relationships, and state handling (`entity.meta.state` only).
2. **Workflows** – States, transitions (initial→first auto, loops manual), processors/criteria minimal & valid. Mermaid diagram + pseudocode present.
3. **Workflow JSON** – Matches workflow diagram exactly. Validates against `example_application/resources/workflow/workflow_schema.json`.
4. **Routes** – Endpoints align with workflows; transitions consistent; full request/response examples.
6. **Consistency** – Highlight missing, redundant, or misinterpreted elements. Suggest fixes, don’t rewrite wholesale.

**Output:** Provide a structured summary of gaps, inconsistencies, and recommended fixes.
```"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
