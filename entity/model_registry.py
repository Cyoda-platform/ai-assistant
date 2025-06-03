import common.config.const as const
from entity.chat.chat import ChatEntity, ChatBusinessEntity
from entity.model import QuestionsQueue, SchedulerEntity, AgenticFlowEntity, ChatMemory, FlowEdgeMessage, AIMessage

model_registry = {
    const.ModelName.AGENTIC_FLOW_ENTITY.value: AgenticFlowEntity,
    const.ModelName.FLOW_EDGE_MESSAGE.value: FlowEdgeMessage,
    const.ModelName.AI_MEMORY_EDGE_MESSAGE.value: AIMessage,
    const.ModelName.CHAT_ENTITY.value: ChatEntity,
    const.ModelName.SCHEDULER_ENTITY.value: SchedulerEntity,
    const.ModelName.QUESTIONS_QUEUE.value: QuestionsQueue,
    const.ModelName.CHAT_MEMORY.value: ChatMemory,
    const.ModelName.CHAT_BUSINESS_ENTITY.value: ChatBusinessEntity

}
