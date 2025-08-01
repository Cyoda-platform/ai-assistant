"""
Agent loader for loading AI agent configurations.

This module handles loading agent configurations from JSON files
and optionally SDK-based agent classes.
"""

import json
import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional


class AgentLoader:
    """
    Loader for AI agent configurations.
    
    Supports:
    - JSON-defined agents with model and tool configurations
    - SDK-based agents with custom Python implementations
    - Agent configuration validation
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the agent loader.
        
        Args:
            base_path: Base directory path for loading agents
        """
        self.base_path = Path(base_path)
        self.agents_dir = self.base_path / "agent_configs"
    
    async def load_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Load an agent configuration by name.
        
        Args:
            agent_name: Name of the agent to load
            
        Returns:
            Agent configuration dictionary or None if not found
        """
        agent_dir = self.agents_dir / agent_name
        
        if not agent_dir.exists():
            return None
        
        # Try to load JSON configuration first
        json_config = await self._load_json_config(agent_dir)
        if json_config:
            # Check if there's also an SDK implementation
            sdk_config = await self._load_sdk_config(agent_dir)
            if sdk_config:
                json_config.update(sdk_config)

            return json_config

        # If no JSON config, try SDK-only
        return await self._load_sdk_config(agent_dir)
    
    async def _load_json_config(self, agent_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Load JSON agent configuration.

        Args:
            agent_dir: Agent directory path

        Returns:
            JSON configuration or None if not found
        """
        config_file = agent_dir / "agent.json"

        if not config_file.exists():
            return None

        try:
            import aiofiles
            async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = json.loads(content)

            # Validate basic structure
            if not self._validate_json_config(config):
                print(f"Invalid agent configuration in {config_file}")
                return None

            return config

        except Exception as e:
            print(f"Error loading agent config {config_file}: {e}")
            return None
    
    async def _load_sdk_config(self, agent_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Load SDK-based agent configuration.
        
        Args:
            agent_dir: Agent directory path
            
        Returns:
            SDK configuration or None if not found
        """
        sdk_file = agent_dir / "agent.py"
        
        if not sdk_file.exists():
            return None
        
        try:
            # Load the Python module
            spec = importlib.util.spec_from_file_location("agent", sdk_file)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for agent configuration or class
            if hasattr(module, 'AGENT_CONFIG'):
                config = module.AGENT_CONFIG
                config["type"] = "sdk"
                config["sdk_module"] = str(sdk_file)
                return config
            elif hasattr(module, 'Agent'):
                # SDK agent class found
                return {
                    "type": "sdk",
                    "sdk_module": str(sdk_file),
                    "agent_class": "Agent"
                }
            
            return None
            
        except Exception as e:
            print(f"Error loading SDK agent {sdk_file}: {e}")
            return None
    
    def _validate_json_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate JSON agent configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid
        """
        # Check required fields
        if "type" not in config:
            config["type"] = "agent"  # Default type
        
        # Validate model configuration if present
        if "model" in config:
            model_config = config["model"]
            if not isinstance(model_config, dict):
                return False

        
        # Validate messages if present
        if "messages" in config:
            if not isinstance(config["messages"], list):
                return False
            
            for message in config["messages"]:
                if not isinstance(message, dict):
                    return False
                if "role" not in message:
                    return False
                if "content" not in message and "content_from_file" not in message:
                    return False
        
        # Validate tools if present
        if "tools" in config:
            if not isinstance(config["tools"], list):
                return False
            
            for tool in config["tools"]:
                if not isinstance(tool, dict):
                    return False
                # Tools can be either inline or references
                if "type" not in tool and "name" not in tool:
                    return False
        
        return True
    
    def list_agents(self) -> list:
        """
        List all available agents.
        
        Returns:
            List of agent names
        """
        if not self.agents_dir.exists():
            return []
        
        agents = []
        for item in self.agents_dir.iterdir():
            if item.is_dir():
                # Check if it has either agent.json or agent.py
                if (item / "agent.json").exists() or (item / "agent.py").exists():
                    agents.append(item.name)
        
        return sorted(agents)
    
    def validate_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Validate an agent configuration.
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            Validation result with status and any errors
        """
        result = {
            "agent_name": agent_name,
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        agent_config = self.load_agent(agent_name)
        if not agent_config:
            result["errors"].append("Agent configuration not found")
            return result
        
        # Validate configuration structure
        if agent_config.get("type") == "agent":
            # Validate JSON agent
            if "model" not in agent_config:
                result["warnings"].append("No model configuration specified")
            
            if "messages" not in agent_config:
                result["warnings"].append("No messages specified")
            
            # Validate message file references
            if "messages" in agent_config:
                for message in agent_config["messages"]:
                    if "content_from_file" in message:
                        file_path = self.base_path / message["content_from_file"]
                        if not file_path.exists():
                            result["errors"].append(f"Message file not found: {message['content_from_file']}")
        
        elif agent_config.get("type") == "sdk":
            # Validate SDK agent
            sdk_module = agent_config.get("sdk_module")
            if not sdk_module or not Path(sdk_module).exists():
                result["errors"].append("SDK module file not found")
        
        result["valid"] = len(result["errors"]) == 0
        return result
