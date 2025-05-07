import common.config.const as const
from entity.chat.model.chat import ChatEntity
from entity.model import QuestionsQueue, SchedulerEntity, AgenticFlowEntity, ChatMemory

model_registry = {
    const.AGENTIC_FLOW_ENTITY: AgenticFlowEntity,
    const.CHAT_MODEL_NAME: ChatEntity,
    const.SCHEDULER_ENTITY: SchedulerEntity,
    const.QUESTIONS_QUEUE_MODEL_NAME: QuestionsQueue,
    const.MEMORY_MODEL_NAME: ChatMemory,

}
