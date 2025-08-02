"""
Shared interfaces for AI Agent components.

This module defines the abstract interfaces that all AI agent implementations
(OpenAI SDK, Google ADK, etc.) must implement, ensuring consistent behavior
and easy testing across different agent backends.
"""

from .message_adapter import MessageAdapterInterface
from .tool_adapter import ToolAdapterInterface
from .ui_function_handler import UiFunctionHandlerInterface
from .schema_adapter import SchemaAdapterInterface

__all__ = [
    'MessageAdapterInterface',
    'ToolAdapterInterface',
    'UiFunctionHandlerInterface', 
    'SchemaAdapterInterface'
]
