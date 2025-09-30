"""
PromptSentF501PromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/prompt_sent_f501/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Let the user know: they should test their API by visiting `http://localhost:8080` and ensure everything works.
- Let the user know: when they save `{entity_name}`, an event will be sent and processed by their workflow code in `application/processor/* and application/criterion/*`
- Let the user know: alternatively they can prompt their IDE AI agent to run and test the application for them with the following prompt:
Please help me run and test the application against Cyoda, do end to end testing. Make sure all processors and criteria are invoked and you see logs for them. Use AI_TESTING_GUIDE.md as a reference.
Prerequisites:
Have MCP tools configured in the IDE with:
Install mcp tools with:  https://pypi.org/project/mcp-cyoda/
pipx install mcp-cyoda
```json --remember to add markdown
{
  "mcpServers": {
    "cyoda": {
      "command": "mcp-cyoda",
      "env": {
        "CYODA_CLIENT_ID": "your-client-id-here",
        "CYODA_CLIENT_SECRET": "your-client-secret-here",
        "CYODA_HOST": "client-123.eu.cyoda.net"
      }
    }
  }
}
```
Do not forget the markdown"""
