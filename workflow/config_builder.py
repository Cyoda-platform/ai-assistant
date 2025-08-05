import asyncio
import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _find_project_root() -> Path:
    """
    Find the project root directory by looking for key files.

    Returns:
        Path to the project root directory

    Raises:
        FileNotFoundError: If project root cannot be determined
    """
    # Start from current file's directory and walk up
    current_path = Path(__file__).parent

    # Look for project indicators
    project_indicators = ['app.py', 'workflow_configs', '.git', 'requirements.txt']

    for parent in [current_path] + list(current_path.parents):
        if any((parent / indicator).exists() for indicator in project_indicators):
            return parent

    # Fallback: if we can't find project root, use current working directory
    cwd = Path.cwd()
    logger.warning(f"Could not determine project root, using current working directory: {cwd}")
    return cwd


class ConfigBuilder:
    """
    Builds processor configurations from workflow_configs directory structure.

    Handles three processor types:
    - AgentProcessor: Loads agent config and resolves tool/prompt references
    - FunctionProcessor: Returns tool config directly
    - MessageProcessor: Builds config from message directory (message.md + meta.json)

    Features thread-safe caching for improved performance.
    """

    def __init__(self, workflow_configs_path: str = "workflow_configs"):
        """
        Initialize config builder.

        Args:
            workflow_configs_path: Path to workflow_configs directory (relative or absolute)
        """
        # If path is relative, resolve it relative to project root
        if not Path(workflow_configs_path).is_absolute():
            project_root = _find_project_root()
            self.workflow_configs_path = project_root / workflow_configs_path
        else:
            self.workflow_configs_path = Path(workflow_configs_path)

        self.agents_path = self.workflow_configs_path / "agents"
        self.tools_path = self.workflow_configs_path / "tools"
        self.prompts_path = self.workflow_configs_path / "prompts"
        self.messages_path = self.workflow_configs_path / "messages"

        # Thread-safe cache for configurations
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.RLock()

        # Log initialization for debugging
        logger.debug(f"ConfigBuilder initialized with workflow_configs_path: {self.workflow_configs_path}")
        logger.debug(f"Current working directory: {Path.cwd()}")
        logger.debug(f"Workflow configs directory exists: {self.workflow_configs_path.exists()}")
    
    async def build_config(self, processor_name: str) -> Dict[str, Any]:
        """
        Build configuration for the given processor name with caching.

        Args:
            processor_name: Processor name in format "ProcessorType.config_name"
                          e.g., "AgentProcessor.submit_answer_5607"

        Returns:
            Built configuration dictionary

        Raises:
            ValueError: If processor name format is invalid
            FileNotFoundError: If required config files are not found
        """
        # Check cache first
        with self._cache_lock:
            if processor_name in self._config_cache:
                logger.debug(f"Config cache hit for: {processor_name}")
                return self._config_cache[processor_name].copy()

        # Build config if not in cache
        if "." not in processor_name:
            raise ValueError(f"Invalid processor name format: {processor_name}. Expected 'ProcessorType.config_name'")

        processor_type, config_name = processor_name.split(".", 1)

        try:
            if processor_type == "AgentProcessor":
                config = await self._build_agent_config(config_name)
            elif processor_type == "FunctionProcessor":
                config = await self._build_function_config(config_name)
            elif processor_type == "MessageProcessor":
                config = await self._build_message_config(config_name)
            else:
                raise ValueError(f"Unknown processor type: {processor_type}")

            # Cache the built config
            with self._cache_lock:
                self._config_cache[processor_name] = config.copy()
                logger.debug(f"Config cached for: {processor_name}")

            return config

        except Exception as e:
            logger.error(f"Failed to build config for {processor_name}: {e}")
            raise
    
    async def _build_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Build agent configuration by loading agent.json and resolving references.
        
        Args:
            agent_name: Agent configuration name (e.g., "submit_answer_5607")
        
        Returns:
            Complete agent configuration with resolved tools and prompts
        """
        agent_config_path = self.agents_path / agent_name / "agent.json"

        if not agent_config_path.exists():
            # Enhanced error message with debugging information
            error_msg = (
                f"Agent config not found: {agent_config_path}\n"
                f"Current working directory: {Path.cwd()}\n"
                f"Workflow configs path: {self.workflow_configs_path}\n"
                f"Agents path exists: {self.agents_path.exists()}\n"
                f"Agent directory exists: {(self.agents_path / agent_name).exists()}"
            )
            raise FileNotFoundError(error_msg)

        with open(agent_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Resolve tool references
        if "tools" in config:
            config["tools"] = self._resolve_tool_references(config["tools"])
        
        # Resolve message content references
        if "messages" in config:
            config["messages"] = self._resolve_message_references(config["messages"])
        
        return config
    
    async def _build_function_config(self, function_name: str) -> Dict[str, Any]:
        """
        Build function configuration by loading tool.json.
        
        Args:
            function_name: Function/tool name (e.g., "add_new_workflow")
        
        Returns:
            Tool configuration
        """
        tool_config_path = self.tools_path / function_name / "tool.json"
        
        if not tool_config_path.exists():
            raise FileNotFoundError(f"Tool config not found: {tool_config_path}")
        
        with open(tool_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _build_message_config(self, message_name: str) -> Dict[str, Any]:
        """
        Build message configuration from message directory.
        
        Args:
            message_name: Message configuration name
        
        Returns:
            Message configuration with content from message.md and metadata from meta.json
        """
        message_dir = self.messages_path / message_name
        message_file = message_dir / "message.md"
        meta_file = message_dir / "meta.json"
        
        if not message_dir.exists():
            raise FileNotFoundError(f"Message directory not found: {message_dir}")

        if not message_file.exists():
            raise FileNotFoundError(f"Message file not found: {message_file}")

        if not meta_file.exists():
            raise FileNotFoundError(f"Meta file not found: {meta_file}")
        
        # Read message content
        with open(message_file, 'r', encoding='utf-8') as f:
            message_content = f.read().strip()
        
        # Read metadata
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Build message config
        config = {
            "type": meta.get("type", "notification"),
            meta.get("type", "notification"): message_content,
            "publish": meta.get("publish", True),
            "approve": meta.get("approve", False),
            "allow_anonymous_users": meta.get("allow_anonymous_users", True)
        }
        
        return config
    
    def _resolve_tool_references(self, tools: list) -> list:
        """
        Resolve tool references by replacing tool names with full tool configs.
        
        Args:
            tools: List of tool references (e.g., [{"name": "get_user_info"}])
        
        Returns:
            List of complete tool configurations
        """
        resolved_tools = []
        
        for tool in tools:
            if isinstance(tool, dict) and "name" in tool:
                tool_name = tool["name"]
                try:
                    full_tool_config = self._build_function_config(tool_name)
                    resolved_tools.append(full_tool_config)
                except FileNotFoundError:
                    logger.warning(f"Tool config not found for: {tool_name}, keeping original reference")
                    resolved_tools.append(tool)
            else:
                resolved_tools.append(tool)
        
        return resolved_tools
    
    def _resolve_message_references(self, messages: list) -> list:
        """
        Resolve message content references by replacing content_from_file with actual content.

        Args:
            messages: List of message objects with potential content_from_file references

        Returns:
            List of messages with resolved content
        """
        resolved_messages = []

        for message in messages:
            if isinstance(message, dict) and "content_from_file" in message:
                prompt_name = message["content_from_file"]
                try:
                    content = self._load_prompt_content(prompt_name)
                    # Replace content_from_file with content as a list for backwards compatibility
                    resolved_message = message.copy()
                    del resolved_message["content_from_file"]
                    resolved_message["content"] = [content]  # Return as list for backwards compatibility
                    resolved_messages.append(resolved_message)
                except FileNotFoundError:
                    logger.warning(f"Prompt not found for: {prompt_name}, keeping original reference")
                    resolved_messages.append(message)
            else:
                resolved_messages.append(message)

        return resolved_messages
    
    def _load_prompt_content(self, prompt_name: str) -> str:
        """
        Load prompt content from prompts directory.
        
        Args:
            prompt_name: Prompt directory name
        
        Returns:
            Prompt content as string
        """
        prompt_dir = self.prompts_path / prompt_name
        
        if not prompt_dir.exists():
            raise FileNotFoundError(f"Prompt directory not found: {prompt_dir}")

        # Look for message files (message_0.md, message_1.md, etc.)
        message_files = sorted(prompt_dir.glob("message_*.md"))
        
        if not message_files:
            raise FileNotFoundError(f"No message files found in: {prompt_dir}")
        
        # Combine all message files
        content_parts = []
        for message_file in message_files:
            with open(message_file, 'r', encoding='utf-8') as f:
                content_parts.append(f.read().strip())
        
        return "\n\n".join(content_parts)

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        with self._cache_lock:
            self._config_cache.clear()
            logger.info("Configuration cache cleared")

    def get_cache_size(self) -> int:
        """Get the current cache size."""
        with self._cache_lock:
            return len(self._config_cache)


# Convenience function for easy usage
def build_processor_config(processor_name: str, workflow_configs_path: str = "workflow_configs") -> Dict[str, Any]:
    """
    Build processor configuration for the given processor name.

    Args:
        processor_name: Processor name in format "ProcessorType.config_name"
        workflow_configs_path: Path to workflow_configs directory (relative or absolute)

    Returns:
        Built configuration dictionary
    """
    builder = ConfigBuilder(workflow_configs_path)
    return asyncio.run(builder.build_config(processor_name))
