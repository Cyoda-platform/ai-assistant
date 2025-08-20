"""ProcessorSelector for selecting appropriate processors."""

from workflow.dispatcher.actions.action import Action
from workflow.dispatcher.actions.notification_action import NotificationAction
from workflow.dispatcher.actions.function_action import FunctionAction
from workflow.dispatcher.actions.agent_action import AgentAction
from workflow.dispatcher.actions.direct_method_action import DirectMethodAction
from .processor import Processor
from .config_based_agent_processor import ConfigBasedAgentProcessor
from .function_processor import FunctionProcessor
from .message_processor import MessageProcessor


class ProcessorSelector:
    """Selects appropriate processor for an action."""
    
    def __init__(self):
        self.processors = {
            NotificationAction: MessageProcessor(),
            FunctionAction: FunctionProcessor(),
            AgentAction: ConfigBasedAgentProcessor(),
            DirectMethodAction: FunctionProcessor(),
        }
    
    def select(self, action: Action) -> Processor:
        """Select appropriate processor for the action."""
        processor_class = self.processors.get(type(action))
        if not processor_class:
            raise ValueError(f"No processor found for action type: {type(action)}")
        return processor_class
