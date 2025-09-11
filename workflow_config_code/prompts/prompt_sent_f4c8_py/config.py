"""
PromptSentF4c8PromptConfig Configuration

Generated from config: workflow_configs/prompts/prompt_sent_f4c8/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Let the user know:
    
in order to run the application they need python >3.9
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install .

Then they can either run it locally with python app.py or ask the IDE agent to read AI_TESTING_GUIDE.md and do everything for them.
Install mcp tools with:  https://pypi.org/project/mcp-cyoda-client/
pipx install mcp-cyoda-client
```json --remember to add markdown
{
  "mcpServers": {
    "cyoda": {
      "command": "mcp-cyoda-client",
      "env": {
        "CYODA_CLIENT_ID": "your-client-id-here",
        "CYODA_CLIENT_SECRET": "your-client-secret-here",
        "CYODA_HOST": "client-123.eu.cyoda.net"
      }
    }
  }
}
```
then you can import your workflows with these mcp tools - but you can fully delegate this to your AI agent
 Setting values at .env file: 
- Let the user know: a default value is used for `GRPC_PROCESSOR_TAG` (they can change it if they like).
- Let the user know: if they are using shared environment they need to make sure they specify unique ENTITY_VERSION."""
