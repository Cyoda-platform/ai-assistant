from common.config.conts import CHAT_MODEL_NAME, QUESTIONS_QUEUE_MODEL_NAME, SCHEDULER_ENTITY, AGENTIC_FLOW_ENTITY
from entity.chat.model.chat import ChatEntity
from entity.model.model import QuestionsQueue, SchedulerEntity, AgenticFlowEntity

model_registry = {
    AGENTIC_FLOW_ENTITY: AgenticFlowEntity,
    CHAT_MODEL_NAME: ChatEntity,
    SCHEDULER_ENTITY: SchedulerEntity,
    QUESTIONS_QUEUE_MODEL_NAME: QuestionsQueue,

    # todo
    # FLOW_EDGE_MESSAGE_MODEL_NAME:
}
