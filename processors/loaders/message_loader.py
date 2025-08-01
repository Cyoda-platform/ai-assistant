"""
Message loader for loading static message configurations.

This module handles loading message configurations from Markdown files
with YAML frontmatter for metadata.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


class MessageLoader:
    """
    Loader for static message configurations.
    
    Supports:
    - Markdown messages with YAML frontmatter
    - Message metadata validation
    - Message discovery and listing
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the message loader.
        
        Args:
            base_path: Base directory path for loading messages
        """
        self.base_path = Path(base_path)
        self.messages_dir = self.base_path / "messages"
    
    def load_message(self, message_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a message configuration by path.
        
        Args:
            message_path: Path to the message (e.g., "workflow/message_name")
            
        Returns:
            Message configuration dictionary or None if not found
        """
        file_path = self.messages_dir / f"{message_path}.md"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter and content
            metadata, message_content = self._parse_markdown_with_frontmatter(content)
            
            # Validate metadata
            if not self._validate_message_metadata(metadata):
                print(f"Invalid message metadata in {file_path}")
                return None
            
            return {
                "path": message_path,
                "content": message_content,
                "metadata": metadata,
                "publish": metadata.get("publish", False),
                "approve": metadata.get("approve", False),
                "type": metadata.get("type", "message")
            }
            
        except Exception as e:
            print(f"Error loading message {message_path}: {e}")
            return None
    
    def load_messages(self, message_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Load multiple message configurations.
        
        Args:
            message_paths: List of message paths to load
            
        Returns:
            List of message configurations (skips messages that can't be loaded)
        """
        messages = []
        for message_path in message_paths:
            message_config = self.load_message(message_path)
            if message_config:
                messages.append(message_config)
        
        return messages
    
    def _parse_markdown_with_frontmatter(self, content: str) -> tuple:
        """
        Parse Markdown content with YAML frontmatter.
        
        Args:
            content: Raw file content
            
        Returns:
            Tuple of (metadata_dict, content_string)
        """
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    message_content = parts[2].strip()
                    return metadata, message_content
                except yaml.YAMLError:
                    # If YAML parsing fails, treat as regular content
                    pass
        
        # No frontmatter or parsing failed
        return {}, content.strip()
    
    def _validate_message_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate message metadata structure.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if metadata is valid
        """
        # Check boolean fields
        boolean_fields = ["publish", "approve"]
        for field in boolean_fields:
            if field in metadata and not isinstance(metadata[field], bool):
                return False
        
        # Check string fields
        string_fields = ["type", "priority", "response_type"]
        for field in string_fields:
            if field in metadata and not isinstance(metadata[field], str):
                return False
        
        # Validate type if present
        if "type" in metadata:
            valid_types = ["message", "notification", "question", "approval"]
            if metadata["type"] not in valid_types:
                return False
        
        # Validate priority if present
        if "priority" in metadata:
            valid_priorities = ["low", "normal", "high", "urgent"]
            if metadata["priority"] not in valid_priorities:
                return False
        
        return True
    
    def list_messages(self, workflow_name: Optional[str] = None) -> List[str]:
        """
        List all available messages, optionally filtered by workflow.
        
        Args:
            workflow_name: Optional workflow name to filter by
            
        Returns:
            List of message paths
        """
        if not self.messages_dir.exists():
            return []
        
        messages = []
        
        if workflow_name:
            # List messages for specific workflow
            workflow_dir = self.messages_dir / workflow_name
            if workflow_dir.exists():
                for item in workflow_dir.iterdir():
                    if item.is_file() and item.suffix == ".md":
                        messages.append(f"{workflow_name}/{item.stem}")
        else:
            # List all messages
            for workflow_dir in self.messages_dir.iterdir():
                if workflow_dir.is_dir():
                    for item in workflow_dir.iterdir():
                        if item.is_file() and item.suffix == ".md":
                            messages.append(f"{workflow_dir.name}/{item.stem}")
        
        return sorted(messages)
    
    def list_workflows(self) -> List[str]:
        """
        List all workflow directories that contain messages.
        
        Returns:
            List of workflow names
        """
        if not self.messages_dir.exists():
            return []
        
        workflows = []
        for item in self.messages_dir.iterdir():
            if item.is_dir():
                # Check if directory contains any .md files
                if any(f.suffix == ".md" for f in item.iterdir() if f.is_file()):
                    workflows.append(item.name)
        
        return sorted(workflows)
    
    def validate_message(self, message_path: str) -> Dict[str, Any]:
        """
        Validate a message configuration.
        
        Args:
            message_path: Path to the message to validate
            
        Returns:
            Validation result with status and any errors
        """
        result = {
            "message_path": message_path,
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        message_config = self.load_message(message_path)
        if not message_config:
            result["errors"].append("Message file not found")
            return result
        
        # Validate metadata
        metadata = message_config["metadata"]
        if not self._validate_message_metadata(metadata):
            result["errors"].append("Invalid message metadata")
        
        # Check for required publish flag
        if not message_config["publish"]:
            result["warnings"].append("Message not marked for publishing")
        
        # Check content length
        content = message_config["content"]
        if not content.strip():
            result["errors"].append("Message content is empty")
        elif len(content) < 10:
            result["warnings"].append("Message content is very short")
        
        # Check for approval requirements
        if message_config["approve"] and message_config["type"] != "approval":
            result["warnings"].append("Approval flag set but type is not 'approval'")
        
        result["valid"] = len(result["errors"]) == 0
        return result
    
    def create_message_template(
        self, 
        message_path: str, 
        message_type: str = "message",
        publish: bool = True,
        approve: bool = False
    ) -> str:
        """
        Create a template for a new message.
        
        Args:
            message_path: Path for the new message
            message_type: Type of message
            publish: Whether to publish the message
            approve: Whether approval is required
            
        Returns:
            Message template content
        """
        metadata = {
            "publish": publish,
            "type": message_type
        }
        
        if approve:
            metadata["approve"] = approve
        
        # Convert metadata to YAML
        yaml_content = yaml.dump(metadata, default_flow_style=False).strip()
        
        return f"""---
{yaml_content}
---

# Message Title

Your message content goes here. You can use variables like {{variable_name}} 
that will be replaced with actual values during execution.

## Additional Information

Add any additional information or instructions here.
"""
    
    def save_message(self, message_path: str, content: str) -> bool:
        """
        Save a message to file.
        
        Args:
            message_path: Path for the message
            content: Message content (including frontmatter)
            
        Returns:
            True if saved successfully
        """
        try:
            file_path = self.messages_dir / f"{message_path}.md"
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error saving message {message_path}: {e}")
            return False
