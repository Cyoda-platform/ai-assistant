"""WorkflowEvent class for representing workflow events."""

from typing import Any
from entity.model import WorkflowEntity


class WorkflowEvent:
    """Represents a workflow event to be processed."""
    
    def __init__(self, entity: WorkflowEntity, processor_name: str, payload: Any, technical_id: str):
        self.entity = entity
        self.processor_name = processor_name
        self.payload = payload
        self.technical_id = technical_id
