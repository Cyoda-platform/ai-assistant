"""
ParseWorkflowConfigsB3c2PromptConfig Configuration

Configuration data for the parse workflow configs prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with parsing functional requirements and generating workflow configurations.

Based on the functional requirements provided, analyze and create workflow JSON configurations that define the business processes.

Your tasks:
1. Read and analyze the functional requirements from the input file
2. Identify the main business entities and processes
3. Design workflow states and transitions for each business process
4. Generate workflow JSON configurations following the standard format

For each workflow, create a JSON file using add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/workflow/{EntityName}.json'
- file_contents: properly formatted workflow JSON

Workflow JSON format:
{
  "version": "1.0",
  "name": "{EntityName} Workflow",
  "desc": "Description of the workflow for {EntityName}",
  "initialState": "initial_state",
  "active": true,
  "states": {
    "initial_state": {
      "transitions": [
        {
          "name": "transition_name",
          "next": "next_state",
          "manual": false,
          "processors": [
            {
              "name": "ProcessorClassName",
              "executionMode": "SYNC",
              "config": {
                "calculationNodesTags": "cyoda_application"
              }
            }
          ]
        }
      ]
    }
  }
}

Generate comprehensive workflows that cover all the business processes identified in the functional requirements.
"""
