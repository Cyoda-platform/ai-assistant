"""
PromptSentD866PromptConfig Configuration

Generated from config: workflow_configs/prompts/prompt_sent_d866/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Let the user know: with their env configured, they should import the workflows using one of the following options:

1. Use mcp tool to import the workflows: mcp import workflow {path_to_workflow_file} 
Sometimes ai agents fail to recognise correct entity name and version - so you can instruct directly.

Alternatively you can run script scripts/import_workflows.py
There is a README.md file in the scripts directory that explains how to run the script.

Let the user know: the workflows should appear in their Cyoda UI once the import completes.
Let the user know: they can view and edit their workflow configurations here in canvas. They need to open canvas in upper right corner and choose workflow tab. There they can view the workflow and also use AI for editing if necessary.
Max tokens: 300
"""
