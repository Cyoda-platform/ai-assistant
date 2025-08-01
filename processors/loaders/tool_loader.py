"""
Tool loader for loading reusable function/tool configurations.

This module handles loading tool configurations from JSON files
and validates their structure for use in workflows and agents.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ToolLoader:
    """
    Loader for tool/function configurations.

    Supports:
    - JSON-defined tools with parameter schemas
    - Tool configuration validation
    - Tool discovery and listing
    - Hybrid approach: registry file + individual tool files
    """

    def __init__(self, base_path: str = "."):
        """
        Initialize the tool loader.

        Args:
            base_path: Base directory path for loading tools
        """
        self.base_path = Path(base_path)
        self.tools_dir = self.base_path / "tools"
        self.registry_file = self.tools_dir / "tools_registry.json"
        self._registry_cache = None
    
    async def load_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a tool configuration by name.

        Tries multiple sources in order:
        1. tools_registry.json (production tools)
        2. Individual tool files (workflow-specific tools)

        Args:
            tool_name: Name of the tool to load

        Returns:
            Tool configuration dictionary or None if not found
        """
        # First, try loading from registry
        registry_tool = await self._load_from_registry(tool_name)
        if registry_tool:
            return registry_tool

        # Fallback to individual tool file
        return await self._load_from_file(tool_name)

    async def _load_from_registry(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load tool from tools_registry.json"""
        registry = await self._get_registry()
        if not registry:
            return None

        for tool in registry.get("tools", []):
            if tool.get("name") == tool_name:
                # Convert registry format to standard format
                return {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                }

        return None

    async def _load_from_file(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load tool from individual JSON file"""
        tool_file = self.tools_dir / f"{tool_name}.json"

        if not tool_file.exists():
            return None

        try:
            import aiofiles
            async with aiofiles.open(tool_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = json.loads(content)

            # Validate basic structure
            if not self._validate_tool_config(config):
                print(f"Invalid tool configuration in {tool_file}")
                return None

            # Ensure tool has a name
            if "name" not in config:
                config["name"] = tool_name

            return config

        except Exception as e:
            print(f"Error loading tool config {tool_file}: {e}")
            return None

    async def _get_registry(self) -> Optional[Dict[str, Any]]:
        """Load and cache the tools registry"""
        if self._registry_cache is not None:
            return self._registry_cache

        if not self.registry_file.exists():
            self._registry_cache = {}
            return self._registry_cache

        try:
            import aiofiles
            async with aiofiles.open(self.registry_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                self._registry_cache = json.loads(content)
            return self._registry_cache
        except Exception as e:
            print(f"Error loading tools registry: {e}")
            self._registry_cache = {}
            return self._registry_cache
    
    def load_tools(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """
        Load multiple tool configurations.
        
        Args:
            tool_names: List of tool names to load
            
        Returns:
            List of tool configurations (skips tools that can't be loaded)
        """
        tools = []
        for tool_name in tool_names:
            tool_config = self.load_tool(tool_name)
            if tool_config:
                tools.append(tool_config)
        
        return tools
    
    def _validate_tool_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate tool configuration structure.
        
        Args:
            config: Tool configuration to validate
            
        Returns:
            True if configuration is valid
        """
        # Check for required fields
        required_fields = ["type"]
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate type
        valid_types = ["function", "tool"]
        if config["type"] not in valid_types:
            return False
        
        # Validate function-specific fields
        if config["type"] == "function":
            if "function" not in config:
                return False
            
            function_config = config["function"]
            if not isinstance(function_config, dict):
                return False
            
            # Check function structure
            if "name" not in function_config:
                return False
            
            # Validate parameters if present
            if "parameters" in function_config:
                if not self._validate_parameters_schema(function_config["parameters"]):
                    return False
        
        return True
    
    def _validate_parameters_schema(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters schema structure.
        
        Args:
            parameters: Parameters schema to validate
            
        Returns:
            True if schema is valid
        """
        if not isinstance(parameters, dict):
            return False
        
        # Check for required schema fields
        if "type" not in parameters:
            return False
        
        if parameters["type"] != "object":
            return False
        
        # Validate properties if present
        if "properties" in parameters:
            properties = parameters["properties"]
            if not isinstance(properties, dict):
                return False
            
            # Validate each property
            for prop_name, prop_config in properties.items():
                if not isinstance(prop_config, dict):
                    return False
                if "type" not in prop_config:
                    return False
        
        # Validate required fields if present
        if "required" in parameters:
            required = parameters["required"]
            if not isinstance(required, list):
                return False
            
            # Check that all required fields exist in properties
            if "properties" in parameters:
                properties = parameters["properties"]
                for req_field in required:
                    if req_field not in properties:
                        return False
        
        return True
    
    def list_tools(self) -> List[str]:
        """
        List all available tools from both registry and individual files.

        Returns:
            List of tool names
        """
        tools = set()

        # Add tools from registry
        registry = self._get_registry()
        if registry:
            for tool in registry.get("tools", []):
                if "name" in tool:
                    tools.add(tool["name"])

        # Add tools from individual files
        if self.tools_dir.exists():
            for item in self.tools_dir.iterdir():
                if item.is_file() and item.suffix == ".json" and item.name != "tools_registry.json":
                    tools.add(item.stem)

        return sorted(list(tools))
    
    def validate_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Validate a tool configuration.
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            Validation result with status and any errors
        """
        result = {
            "tool_name": tool_name,
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        tool_config = self.load_tool(tool_name)
        if not tool_config:
            result["errors"].append("Tool configuration not found")
            return result
        
        # Validate configuration structure
        if not self._validate_tool_config(tool_config):
            result["errors"].append("Invalid tool configuration structure")
        
        # Additional validation checks
        if tool_config.get("type") == "function":
            function_config = tool_config.get("function", {})
            
            # Check for description
            if "description" not in function_config:
                result["warnings"].append("No description provided")
            
            # Check parameters
            if "parameters" in function_config:
                params = function_config["parameters"]
                if "properties" not in params:
                    result["warnings"].append("No parameter properties defined")
                elif not params["properties"]:
                    result["warnings"].append("Empty parameter properties")
        
        result["valid"] = len(result["errors"]) == 0
        return result
    
    def create_tool_template(self, tool_name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a template for a new tool configuration.
        
        Args:
            tool_name: Name of the new tool
            description: Description of the tool
            
        Returns:
            Tool configuration template
        """
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description or f"Description for {tool_name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "example_param": {
                            "type": "string",
                            "description": "Example parameter description"
                        }
                    },
                    "required": ["example_param"]
                }
            }
        }
    
    def save_tool(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """
        Save a tool configuration to file.
        
        Args:
            tool_name: Name of the tool
            config: Tool configuration to save
            
        Returns:
            True if saved successfully
        """
        try:
            # Ensure tools directory exists
            self.tools_dir.mkdir(parents=True, exist_ok=True)
            
            # Validate configuration before saving
            if not self._validate_tool_config(config):
                print(f"Cannot save invalid tool configuration for {tool_name}")
                return False
            
            tool_file = self.tools_dir / f"{tool_name}.json"
            with open(tool_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving tool {tool_name}: {e}")
            return False
