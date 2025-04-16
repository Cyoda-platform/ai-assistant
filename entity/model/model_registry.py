from typing import Dict

from black import Any

from common.config.conts import CHAT_MODEL_NAME, QUESTIONS_QUEUE_MODEL_NAME, \
    MEMORY_MODEL_NAME, GEN_APP_ENTITY, GENERATING_GEN_APP_WORKFLOW, SCHEDULER_ENTITY
from entity.chat.model.chat import ChatEntity
from entity.model.model import QuestionsQueue, SchedulerEntity, ChatMemory, AgenticFlowEntity

model_registry = {
    CHAT_MODEL_NAME: ChatEntity,
    GEN_APP_ENTITY: ChatEntity,
    GENERATING_GEN_APP_WORKFLOW: AgenticFlowEntity,
    SCHEDULER_ENTITY: SchedulerEntity,
    QUESTIONS_QUEUE_MODEL_NAME: QuestionsQueue,
    MEMORY_MODEL_NAME: ChatMemory,
    # todo
    # FLOW_EDGE_MESSAGE_MODEL_NAME:
}
