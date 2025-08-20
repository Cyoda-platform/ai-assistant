"""ActionResolver for resolving workflow events into actions."""

from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from workflow.dispatcher.actions.notification_action import NotificationAction
from workflow.dispatcher.actions.function_action import FunctionAction
from workflow.dispatcher.actions.agent_action import AgentAction
from workflow.dispatcher.actions.direct_method_action import DirectMethodAction


class ActionResolver:
    """Resolves workflow events into appropriate actions."""
    
    def resolve(self, ctx: ProcessingContext) -> Action:
        """
        Resolve a processing context into an appropriate action.
        
        Args:
            ctx: Processing context
            
        Returns:
            Resolved action
        """
        processor_name = ctx.event.processor_name
        action_name = processor_name.split(".")[1] if "Processor." in processor_name else processor_name
        
        # Direct method execution (no "Processor." prefix)
        if "Processor." not in processor_name and processor_name != "process_event":
            return DirectMethodAction(name=action_name)
        
        # Config-based actions
        if ctx.config:
            config_type = ctx.config.get("type")
            if config_type in ("notification", "question"):
                return NotificationAction(name=action_name, config=ctx.config)
            elif config_type == "function":
                return FunctionAction(name=action_name, config=ctx.config)
            elif config_type in ("prompt", "agent", "batch"):
                return AgentAction(name=action_name, config=ctx.config)
        
        # Fallback to direct method
        return DirectMethodAction(name=action_name)
