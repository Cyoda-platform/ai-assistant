import common.config.const as const
from entity.chat.model.chat import ChatEntity
from entity.model import QuestionsQueue, SchedulerEntity, AgenticFlowEntity, ChatMemory

model_registry = {
    const.ModelName.AGENTIC_FLOW_ENTITY.value: AgenticFlowEntity,
    const.ModelName.CHAT_ENTITY.value: ChatEntity,
    const.ModelName.SCHEDULER_ENTITY.value: SchedulerEntity,
    const.ModelName.QUESTIONS_QUEUE.value: QuestionsQueue,
    const.ModelName.CHAT_MEMORY.value: ChatMemory,

}
