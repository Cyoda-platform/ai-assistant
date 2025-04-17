from common.config.conts import CHAT_MODEL_NAME, QUESTIONS_QUEUE_MODEL_NAME, \
    MEMORY_MODEL_NAME, GEN_APP_ENTITY, GENERATING_GEN_APP_WORKFLOW, SCHEDULER_ENTITY, ADD_NEW_FEATURE, ADD_NEW_ENTITY, \
    ADD_NEW_WORKFLOW, EDIT_API_EXISTING_APP, EDIT_EXISTING_PROCESSORS, EDIT_EXISTING_WORKFLOW
from entity.chat.model.chat import ChatEntity
from entity.model.model import QuestionsQueue, SchedulerEntity, ChatMemory, AgenticFlowEntity

model_registry = {
    CHAT_MODEL_NAME: ChatEntity,
    GEN_APP_ENTITY: ChatEntity,
    GENERATING_GEN_APP_WORKFLOW: AgenticFlowEntity,
    SCHEDULER_ENTITY: SchedulerEntity,
    QUESTIONS_QUEUE_MODEL_NAME: QuestionsQueue,
    MEMORY_MODEL_NAME: ChatMemory,
    ADD_NEW_FEATURE: ChatEntity,
    ADD_NEW_ENTITY: ChatEntity,
    ADD_NEW_WORKFLOW: ChatEntity,
    EDIT_API_EXISTING_APP: ChatEntity,
    EDIT_EXISTING_WORKFLOW: ChatEntity,
    EDIT_EXISTING_PROCESSORS: ChatEntity
    # todo
    # FLOW_EDGE_MESSAGE_MODEL_NAME:
}
