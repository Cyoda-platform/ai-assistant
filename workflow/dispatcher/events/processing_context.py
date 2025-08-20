"""ProcessingContext class for workflow event processing."""

from typing import Dict, Any
from .workflow_event import WorkflowEvent
from .services import Services


class ProcessingContext:
    """Context for processing workflow events."""
    
    def __init__(self, event: WorkflowEvent, services: Services):
        self.event = event
        self.services = services
        self.config = None
        self.response = "returned empty response"
