"""
Simple Chat Workflow - Builder-Based Implementation

Clean workflow using WorkflowBuilder and static get_name() methods.
All components implement proper interfaces with get_config() methods.
"""

# Import components that implement processor interfaces
from workflow_best_ux.agents.chat_assistant.agent import ChatAssistantAgent  # ✅ Ctrl+Click works
from workflow_best_ux.messages.welcome_message.message import WelcomeMessage  # ✅ Ctrl+Click works
from workflow_best_ux.tools.web_search.tool import WebSearchTool  # ✅ Ctrl+Click works

# Import workflow builder
from workflow_best_ux.builders import workflow


def simple_chat_workflow():
    """
    Build the simple chat workflow using WorkflowBuilder.

    Uses interface-based components with get_config() methods.
    """
    return (workflow("simple_chat_workflow")
            .with_description("Simple chat workflow with AI agent processing")
            .with_initial_state("none")
            .with_criterion("$.workflow_name", "EQUALS", "simple_chat_workflow")

            # State: none -> ready (initialize chat)
            .add_state("none", "Initial state")
                .add_transition("initialize_chat")
                    .to("ready")
                    .set_manual(False)
                    .with_processor(f"MessageProcessor.{WelcomeMessage.get_name()}")  # ✅ Uses static get_name()

            # State: ready -> processing (submit question)
            .add_state("ready", "Ready for user input")
                .add_transition("submit_question")
                    .to("processing")
                    .set_manual(False)
                    .with_processor(f"AgentProcessor.{ChatAssistantAgent.get_name()}")  # ✅ Uses static get_name()

            # State: processing -> ready (complete) OR processing -> error_state (error)
            .add_state("processing", "Processing user request")
                .add_transition("complete_processing")
                    .to("ready")
                    .set_manual(False)
                    .with_processor(f"FunctionProcessor.{WebSearchTool.get_name()}")  # ✅ Uses static get_name()
                .add_transition("error_occurred")
                    .to("error_state")
                    .set_manual(False)

            # State: error_state -> ready (retry)
            .add_state("error_state", "Error state for handling failures")
                .add_transition("retry")
                    .to("ready")
                    .set_manual(True)

            .build())

