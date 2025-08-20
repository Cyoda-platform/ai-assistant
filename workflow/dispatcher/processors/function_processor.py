"""FunctionProcessor for function actions."""

from entity.chat.chat import AgenticFlowEntity
from entity.model import WorkflowEntity
from common.config.config import config as env_config
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from workflow.dispatcher.actions.direct_method_action import DirectMethodAction
from workflow.dispatcher.actions.function_action import FunctionAction
from .processor import Processor


class FunctionProcessor(Processor):
    """Processor for function actions."""
    
    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Execute function processing."""
        if isinstance(action, DirectMethodAction):
            # Handle direct method execution
            method_name = action.name
            
            return await ctx.services.method_registry.dispatch_method(
                method_name=method_name,
                technical_id=ctx.event.technical_id,
                entity=ctx.event.entity
            )
        
        elif isinstance(action, FunctionAction):
            # Handle function call from config
            if isinstance(ctx.event.entity, AgenticFlowEntity):
                function_config = action.config.get("function", {})
                function_name = function_config.get("name")
                parameters = function_config.get("parameters", {})
                
                if not function_name:
                    return "Error: Function name not specified"
                
                response = await ctx.services.ai_agent_handler.handle_function_calling(
                    function_name=function_name, 
                    parameters=parameters, 
                    entity=ctx.event.entity, 
                    technical_id=ctx.event.technical_id
                )
                
                # Store response in memory if needed
                if response and isinstance(response, str):
                    memory_tags = action.config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
                    if memory_tags:
                        await ctx.services.memory_manager.append_to_ai_memory(
                            entity=ctx.event.entity, content=response, memory_tags=memory_tags
                        )
                
                return str(response)
            
            elif isinstance(ctx.event.entity, WorkflowEntity):
                params = action.config["function"].get("parameters", {})
                return await ctx.services.method_registry.dispatch_method(
                    action.config["function"]["name"],
                    technical_id=ctx.event.technical_id,
                    entity=ctx.event.entity,
                    **params
                )
        
        return "Error: Unsupported action type for FunctionProcessor"
