"""
Message processor for sending static messages within workflows.

This processor handles the delivery of notifications, questions, and other
static messages that are part of the workflow orchestration.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from .base_processor import BaseProcessor, ProcessorContext, ProcessorResult


class MessageProcessor(BaseProcessor):
    """
    Processor for sending static messages.
    
    Supports:
    - Markdown messages with YAML frontmatter
    - Message templating with context variables
    - Approval workflows for interactive messages
    - Notification delivery
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the message processor.
        
        Args:
            base_path: Base directory path for loading resources
        """
        super().__init__("MessageProcessor")
        self.base_path = Path(base_path)
    
    def supports(self, processor_name: str) -> bool:
        """
        Check if this processor supports the given processor name.

        Args:
            processor_name: Name to check (format: "MessageProcessor.workflow_name/message_name_with_underscores")

        Returns:
            True if processor name starts with "MessageProcessor."
        """
        return processor_name.startswith("MessageProcessor.") and len(processor_name.split(".", 1)) == 2
    
    async def execute(self, context: ProcessorContext) -> ProcessorResult:
        """
        Send a message based on the processor configuration.
        
        Args:
            context: Execution context containing message configuration
            
        Returns:
            ProcessorResult with message delivery outcome
        """
        if not self.validate_context(context):
            return self.create_error_result("Invalid context provided")
        
        try:
            # Extract message path from processor name (MessageProcessor.workflow/message_name)
            processor_parts = context.config.get("processor_name", "").split(".", 1)
            if len(processor_parts) != 2 or processor_parts[0] != "MessageProcessor":
                return self.create_error_result("Invalid message processor name format")
            
            message_path = processor_parts[1]
            
            # Load message configuration
            message_config = self._load_message(message_path)
            if not message_config:
                return self.create_error_result(f"Message '{message_path}' not found")
            
            # Process and send the message
            result = self._send_message(message_config, context)
            
            return self.create_success_result(data=result)
            
        except Exception as e:
            return self.create_error_result(f"Message processing failed: {str(e)}")
    
    def _load_message(self, message_path: str) -> Optional[Dict[str, Any]]:
        """
        Load message configuration from Markdown file.
        
        Args:
            message_path: Path to the message file (e.g., "workflow/message_name")
            
        Returns:
            Message configuration dictionary or None if not found
        """
        # Construct full path to message file
        file_path = self.base_path / "messages" / f"{message_path}.md"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    message_content = parts[2].strip()
                else:
                    frontmatter = {}
                    message_content = content
            else:
                frontmatter = {}
                message_content = content
            
            return {
                "path": message_path,
                "content": message_content,
                "metadata": frontmatter,
                "publish": frontmatter.get("publish", False),
                "approve": frontmatter.get("approve", False)
            }
            
        except Exception as e:
            print(f"Error loading message {message_path}: {e}")
            return None
    
    def _send_message(self, message_config: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Send the message based on its configuration.
        
        Args:
            message_config: Message configuration
            context: Execution context
            
        Returns:
            Message delivery result
        """
        # Apply context variables to message content
        content = self._apply_context_variables(
            message_config["content"], 
            context.entity_data or {}
        )
        
        # Determine message type and delivery method
        message_type = self._determine_message_type(message_config)
        
        # Send the message
        delivery_result = self._deliver_message(
            content=content,
            message_type=message_type,
            metadata=message_config["metadata"],
            context=context
        )
        
        return {
            "message_path": message_config["path"],
            "message_type": message_type,
            "content_length": len(content),
            "delivery_result": delivery_result,
            "requires_approval": message_config["approve"],
            "published": message_config["publish"]
        }
    
    def _determine_message_type(self, message_config: Dict[str, Any]) -> str:
        """
        Determine the type of message based on configuration.
        
        Args:
            message_config: Message configuration
            
        Returns:
            Message type string
        """
        metadata = message_config["metadata"]
        
        if message_config["approve"]:
            return "approval_required"
        elif metadata.get("type") == "question":
            return "question"
        elif metadata.get("type") == "notification":
            return "notification"
        else:
            return "message"
    
    def _deliver_message(
        self, 
        content: str, 
        message_type: str, 
        metadata: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Deliver the message through appropriate channels.
        
        Args:
            content: Message content
            message_type: Type of message
            metadata: Message metadata
            context: Execution context
            
        Returns:
            Delivery result
        """
        # This would integrate with your existing message delivery system
        # For now, return a placeholder result
        
        delivery_methods = {
            "approval_required": self._deliver_approval_message,
            "question": self._deliver_question_message,
            "notification": self._deliver_notification_message,
            "message": self._deliver_standard_message
        }
        
        delivery_method = delivery_methods.get(message_type, self._deliver_standard_message)
        return delivery_method(content, metadata, context)
    
    def _deliver_approval_message(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Deliver a message that requires approval.
        
        Args:
            content: Message content
            metadata: Message metadata
            context: Execution context
            
        Returns:
            Delivery result
        """
        return {
            "delivery_method": "approval_workflow",
            "status": "pending_approval",
            "approval_id": f"approval_{context.workflow_name}_{context.state_name}",
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        }
    
    def _deliver_question_message(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Deliver an interactive question message.
        
        Args:
            content: Message content
            metadata: Message metadata
            context: Execution context
            
        Returns:
            Delivery result
        """
        return {
            "delivery_method": "interactive_question",
            "status": "awaiting_response",
            "question_id": f"question_{context.workflow_name}_{context.state_name}",
            "expected_response_type": metadata.get("response_type", "text")
        }
    
    def _deliver_notification_message(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Deliver a notification message.
        
        Args:
            content: Message content
            metadata: Message metadata
            context: Execution context
            
        Returns:
            Delivery result
        """
        return {
            "delivery_method": "notification",
            "status": "delivered",
            "notification_id": f"notif_{context.workflow_name}_{context.state_name}",
            "priority": metadata.get("priority", "normal")
        }
    
    def _deliver_standard_message(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Deliver a standard message.
        
        Args:
            content: Message content
            metadata: Message metadata
            context: Execution context
            
        Returns:
            Delivery result
        """
        return {
            "delivery_method": "standard",
            "status": "delivered",
            "message_id": f"msg_{context.workflow_name}_{context.state_name}"
        }
    
    def _apply_context_variables(self, content: str, entity_data: Dict[str, Any]) -> str:
        """
        Apply context variables to message content.
        
        Args:
            content: Content string with variables
            entity_data: Entity data for variable substitution
            
        Returns:
            Content with variables replaced
        """
        # Simple variable substitution - can be enhanced
        for key, value in entity_data.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        return content
