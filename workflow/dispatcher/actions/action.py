"""Base Action class for workflow actions."""

from abc import ABC
from typing import Dict, Any


class Action(ABC):
    """Base class for all actions."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
