"""
Processor factory for creating and managing workflow processors.

This module provides a factory for creating processor instances and
managing the processor registry for both development and production environments.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .base_processor import BaseProcessor, ProcessorRegistry, processor_registry
from .agent_processor import AgentProcessor
from .function_processor import FunctionProcessor
from .message_processor import MessageProcessor


class ProcessorFactory:
    """
    Factory for creating and managing workflow processors.
    
    Supports:
    - Development mode (local file loading)
    - Production mode (configured directory loading)
    - Processor registration and discovery
    """
    
    def __init__(self, base_path: str = ".", production_mode: bool = False):
        """
        Initialize the processor factory.
        
        Args:
            base_path: Base directory path for loading resources
            production_mode: Whether to run in production mode
        """
        self.base_path = Path(base_path)
        self.production_mode = production_mode
        self.registry = processor_registry
        self._processors_initialized = False
    
    def initialize_processors(self) -> None:
        """
        Initialize and register all available processors.
        """
        if self._processors_initialized:
            return
        
        # Determine base path based on mode
        if self.production_mode:
            config_base_path = self._get_production_config_path()
        else:
            config_base_path = str(self.base_path)
        
        # Create and register processors
        processors = [
            AgentProcessor(config_base_path),
            FunctionProcessor(config_base_path),
            MessageProcessor(config_base_path)
        ]
        
        for processor in processors:
            self.registry.register(processor)
        
        self._processors_initialized = True
    
    def _get_production_config_path(self) -> str:
        """
        Get the production configuration path from environment or default.
        
        Returns:
            Production configuration directory path
        """
        # Check environment variable first
        config_path = os.getenv("CYODA_WORKFLOW_CONFIG_PATH")
        if config_path and Path(config_path).exists():
            return config_path
        
        # Default production paths to check
        default_paths = [
            "/etc/cyoda/workflows",
            "/opt/cyoda/config/workflows",
            str(self.base_path / "config" / "workflows")
        ]
        
        for path in default_paths:
            if Path(path).exists():
                return path
        
        # Fallback to base path
        return str(self.base_path)
    
    def get_processor(self, processor_name: str) -> Optional[BaseProcessor]:
        """
        Get a processor by name.
        
        Args:
            processor_name: Name of the processor to retrieve
            
        Returns:
            Processor instance if found, None otherwise
        """
        if not self._processors_initialized:
            self.initialize_processors()
        
        return self.registry.get_processor(processor_name)
    
    def list_processors(self) -> List[str]:
        """
        List all available processors.
        
        Returns:
            List of processor names
        """
        if not self._processors_initialized:
            self.initialize_processors()
        
        return self.registry.list_processors()
    
    def validate_configuration(self) -> Dict[str, any]:
        """
        Validate the processor configuration and resources.
        
        Returns:
            Validation result with status and any issues
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "processors": {},
            "resources": {}
        }
        
        if not self._processors_initialized:
            self.initialize_processors()
        
        # Validate each processor
        for processor_name in self.registry.list_processors():
            processor = self.registry.get_processor(processor_name)
            if processor:
                processor_result = self._validate_processor(processor)
                result["processors"][processor_name] = processor_result
                
                if not processor_result["valid"]:
                    result["valid"] = False
                    result["errors"].extend(processor_result["errors"])
                
                result["warnings"].extend(processor_result["warnings"])
        
        # Validate resource directories
        resource_result = self._validate_resources()
        result["resources"] = resource_result
        
        if not resource_result["valid"]:
            result["valid"] = False
            result["errors"].extend(resource_result["errors"])
        
        result["warnings"].extend(resource_result["warnings"])
        
        return result
    
    def _validate_processor(self, processor: BaseProcessor) -> Dict[str, any]:
        """
        Validate a specific processor.
        
        Args:
            processor: Processor to validate
            
        Returns:
            Validation result for the processor
        """
        result = {
            "processor_name": processor.processor_name,
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic processor validation
        if not hasattr(processor, 'supports') or not callable(processor.supports):
            result["errors"].append("Processor missing supports method")
            result["valid"] = False
        
        if not hasattr(processor, 'execute') or not callable(processor.execute):
            result["errors"].append("Processor missing execute method")
            result["valid"] = False
        
        # Processor-specific validation
        if isinstance(processor, AgentProcessor):
            agent_result = self._validate_agent_processor(processor)
            result["errors"].extend(agent_result["errors"])
            result["warnings"].extend(agent_result["warnings"])
            if not agent_result["valid"]:
                result["valid"] = False
        
        elif isinstance(processor, FunctionProcessor):
            function_result = self._validate_function_processor(processor)
            result["errors"].extend(function_result["errors"])
            result["warnings"].extend(function_result["warnings"])
            if not function_result["valid"]:
                result["valid"] = False
        
        elif isinstance(processor, MessageProcessor):
            message_result = self._validate_message_processor(processor)
            result["errors"].extend(message_result["errors"])
            result["warnings"].extend(message_result["warnings"])
            if not message_result["valid"]:
                result["valid"] = False
        
        return result
    
    def _validate_agent_processor(self, processor: AgentProcessor) -> Dict[str, any]:
        """Validate agent processor configuration."""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Check if agents directory exists
        agents_dir = processor.base_path / "agents"
        if not agents_dir.exists():
            result["warnings"].append("Agents directory not found")
        else:
            # List available agents
            agents = processor.agent_loader.list_agents()
            if not agents:
                result["warnings"].append("No agents found in agents directory")
        
        return result
    
    def _validate_function_processor(self, processor: FunctionProcessor) -> Dict[str, any]:
        """Validate function processor configuration."""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Check if tools directory exists
        tools_dir = processor.base_path / "tools"
        if not tools_dir.exists():
            result["warnings"].append("Tools directory not found")
        else:
            # List available tools
            tools = processor.tool_loader.list_tools()
            if not tools:
                result["warnings"].append("No tools found in tools directory")
        
        return result
    
    def _validate_message_processor(self, processor: MessageProcessor) -> Dict[str, any]:
        """Validate message processor configuration."""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Check if messages directory exists
        messages_dir = processor.base_path / "messages"
        if not messages_dir.exists():
            result["warnings"].append("Messages directory not found")
        
        return result
    
    def _validate_resources(self) -> Dict[str, any]:
        """
        Validate resource directories and files.
        
        Returns:
            Resource validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "directories": {}
        }
        
        # Check required directories
        required_dirs = ["workflows", "agents", "tools", "prompts", "messages"]
        
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            dir_result = {
                "exists": dir_path.exists(),
                "readable": False,
                "file_count": 0
            }
            
            if dir_result["exists"]:
                try:
                    dir_result["readable"] = True
                    dir_result["file_count"] = len(list(dir_path.iterdir()))
                except PermissionError:
                    result["errors"].append(f"Cannot read {dir_name} directory")
                    result["valid"] = False
            else:
                if dir_name == "workflows":
                    result["errors"].append(f"Required directory {dir_name} not found")
                    result["valid"] = False
                else:
                    result["warnings"].append(f"Optional directory {dir_name} not found")
            
            result["directories"][dir_name] = dir_result
        
        return result
    
    def create_default_structure(self) -> bool:
        """
        Create the default directory structure for workflows.
        
        Returns:
            True if structure created successfully
        """
        try:
            directories = [
                "workflows",
                "agents",
                "tools", 
                "prompts",
                "messages",
                "processors",
                "processors/loaders"
            ]
            
            for dir_name in directories:
                dir_path = self.base_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error creating directory structure: {e}")
            return False


# Global factory instance
processor_factory = ProcessorFactory()
