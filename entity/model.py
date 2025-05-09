from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

from common.config.config import config


class WorkflowEntity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    technical_id: Optional[str] = None
    last_modified: Optional[int] = 1715182245000 #for backwards compatibility
    current_transition: Optional[str] = None
    current_state: Optional[str] = None
    user_id: str
    workflow_name: Optional[str] = None
    workflow_cache: Optional[Dict[str, Any]] = {}
    edge_messages_store: Optional[Dict[str, Any]] = {}
    failed: Optional[bool] = False
    error: Optional[str] = None
    error_code: Optional[str] = "None"


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
    model_config = ConfigDict(extra="ignore")
    current_flow: Optional[List[FlowEdgeMessage]] = []
    finished_flow: Optional[List[FlowEdgeMessage]] = []


class AgenticFlowEntity(WorkflowEntity):
    model_config = ConfigDict(extra="ignore")
    chat_id: Optional[str] = ""
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
    model_config = ConfigDict(extra="ignore")
    awaited_entity_ids: Optional[List[str]] = []
    triggered_entity_id: str = ""
    scheduled_action: Optional[str] = config.ScheduledAction.SCHEDULE_ENTITIES_FLOW.value
    triggered_entity_next_transition: Optional[str] = None

class QuestionsQueue(WorkflowEntity):
    model_config = ConfigDict(extra="ignore")
    new_questions: Optional[List[FlowEdgeMessage]] = []
    asked_questions: Optional[List[FlowEdgeMessage]] = []


# https://platform.openai.com/docs/pricing
ModelName = Literal["gpt-4o-mini",
"gpt-4.1-mini",
"gpt-4o",
"gpt-4.1-nano",
"o4-mini"]

ToolChoice = Literal["none", "auto", "required"]

class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    model_name: ModelName = Field(
        default="gpt-4.1-mini",
        description="Name of the model to use"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature: higher values = more random"
    )
    max_tokens: int = Field(
        default=10000,
        ge=1,
        description="Maximum number of tokens to generate"
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling cumulative probability"
    )
    frequency_penalty: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Penalize new tokens based on existing frequency in text"
    )
    presence_penalty: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Penalize new tokens based on whether they appear in text"
    )



