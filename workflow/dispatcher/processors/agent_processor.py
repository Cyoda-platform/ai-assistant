"""AgentProcessor for AI agent actions."""

from entity.chat.chat import AgenticFlowEntity
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from .processor import Processor


class AgentProcessor(Processor):
    """Processor for AI agent actions."""
    
    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Execute AI agent processing."""
        if not isinstance(ctx.event.entity, AgenticFlowEntity):
            return "Error: AgentProcessor requires AgenticFlowEntity"
        
        # Get chat memory
        chat_memory = await ctx.services.memory_manager.get_chat_memory(
            memory_id=ctx.event.entity.memory_id
        )

        # Run AI agent
        response = await ctx.services.ai_agent_handler.run_ai_agent(
            config=action.config, 
            entity=ctx.event.entity, 
            memory=chat_memory, 
            technical_id=ctx.event.technical_id
        )

        # Update chat memory
        await ctx.services.memory_manager.update_chat_memory(
            memory_id=ctx.event.entity.memory_id, 
            chat_memory=chat_memory
        )
        
        return response
