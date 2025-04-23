from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ConfigDict


class WorkflowEntity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    technical_id: Optional[str] = None
    current_transition: Optional[str] = None
    current_state: Optional[str] = None
    user_id: str
    workflow_cache: Optional[Dict[str, Any]] = {}
    edge_messages_store: Optional[Dict[str, Any]] = {}

class AIMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    edge_message_id: str

class ChatMemory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    messages: Optional[Dict[str, List[AIMessage]]] = {}

class TransitionsMemory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    conditions: Optional[Dict[str, Any]] = {}
    current_iteration: Optional[Dict[str, Any]] = {}
    max_iteration: Optional[Dict[str, Any]] = {}

class FlowEdgeMessage(WorkflowEntity):
    model_config = ConfigDict(extra="ignore")
    type: str
    publish: Optional[bool] = False
    consumed: Optional[bool] = True
    edge_message_id: str

class ChatFlow(BaseModel):
    current_flow: Optional[List[FlowEdgeMessage]] = []
    finished_flow: Optional[List[FlowEdgeMessage]] = []

class AgenticFlowEntity(WorkflowEntity):
    model_config = ConfigDict(extra="ignore")
    chat_id: Optional[str] = ""
    workflow_name: Optional[str] = ""
    memory_id: str
    questions_queue_id: Optional[str] = None
    chat_flow: Optional[ChatFlow] = ChatFlow()
    transitions_memory: Optional[TransitionsMemory] = TransitionsMemory()
    locked: bool = False
    date: Optional[Any] = None
    name: Optional[str] = ""
    description: Optional[str] = ""
    parent_id: Optional[str] = ""
    # todo : need to implement the logic to unlock in the dialogue only chat entities. Should not unlock other types of entities
    child_entities: Optional[List[str]] = []
    scheduled_entities: Optional[List[str]] = []

class SchedulerEntity(WorkflowEntity):
    awaited_entity_ids: Optional[List[str]] = []
    triggered_entity_id: str = ""


class QuestionsQueue(WorkflowEntity):
    new_questions: Optional[List[FlowEdgeMessage]] = []
    asked_questions: Optional[List[FlowEdgeMessage]] = []