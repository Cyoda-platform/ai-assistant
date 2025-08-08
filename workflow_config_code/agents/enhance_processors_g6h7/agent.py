"""
EnhanceProcessorsG6h7AgentConfig Configuration

Agent configuration for reviewing and enhancing processors to ensure they satisfy functional requirements.
"""

from typing import Any, Dict
from workflow_config_code.prompts.enhance_processors_g6h7.prompt import EnhanceProcessorsG6h7PromptConfig


class EnhanceProcessorsG6h7AgentConfig:
    """Configuration for the enhance processors agent"""
    
    @staticmethod
    def get_name() -> str:
        """Get the agent name"""
        return "enhance_processors_g6h7"
    
    @staticmethod
    def get_type() -> str:
        """Get the agent type"""
        return "AgentProcessor"
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get the agent configuration"""
        return {
            "name": "enhance_processors_g6h7",
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 4000,
            "system_prompt": EnhanceProcessorsG6h7PromptConfig.get_config(),
            "tools": [
                "list_directory_files_1161",
                "read_file_2766",
                "get_file_contents_2480",
                "get_entity_pojo_contents_04a3",
                "web_search_53be",
                "web_scrape_9740"
            ]
        }
