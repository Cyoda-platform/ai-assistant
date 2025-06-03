from typing import Optional, Any

from entity.model import AgenticFlowEntity, WorkflowEntity


class ChatEntity(AgenticFlowEntity):
    pass

class ChatBusinessEntity(WorkflowEntity):
    chat_id: Optional[str] = ""
    date: Optional[Any] = None
    name: Optional[str] = ""
    description: Optional[str] = ""

