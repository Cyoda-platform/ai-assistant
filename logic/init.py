import asyncio
import os

from common.ai.ai_assistant_service import AiAssistantService
from common.ai.editing_agent import EditingAgent
from common.ai.requirement_agent import RequirementAgent
from common.config.config import CHAT_REPOSITORY
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.repository.in_memory_db import InMemoryRepository
from common.service.service import EntityServiceImpl
from entity.chat.workflow.helper_functions import WorkflowHelperService
from entity.chat.workflow.flow_processor import FlowProcessor
from entity.chat.workflow.workflow import ChatWorkflow
from entity.workflow import Workflow
from entity.workflow_dispatcher import WorkflowDispatcher


class BeanFactory:
    def __init__(self, config=None):
        """
        Initialize the dependency container. You can pass a configuration dictionary,
        or rely on environment variables/default values.
        """
        # Load configuration, allowing overrides via environment or parameter.
        # Initialize asynchronous lock (e.g., for handling concurrent chat operations)
        self.chat_lock = asyncio.Lock()

        try:
            # Create the repository based on configuration.
            self.entity_repository = self._create_repository(CHAT_REPOSITORY)
            self.entity_service = EntityServiceImpl(self.entity_repository)
            self.editing_agent = EditingAgent(self.entity_service)
            self.requirement_agent = RequirementAgent()

            # Externalize dataset creation; can later be replaced with a loader if needed.
            self.dataset = {}
            self.device_sessions = {}
            # Set up the AI assistant service with its dependencies.
            self.ai_service = AiAssistantService(
                requirement_agent=self.requirement_agent,
                editing_agent=self.editing_agent,
                dataset=self.dataset
            )
            self.workflow_helper_service = WorkflowHelperService(ai_service=self.ai_service)
            self.workflow = Workflow()
            self.chat_workflow = ChatWorkflow(
                ai_service=self.ai_service,
                dataset=self.dataset,
                workflow_helper_service=self.workflow_helper_service,
                entity_service=self.entity_service
            )
            self.workflow_dispatcher = WorkflowDispatcher(
                cls=ChatWorkflow,
                cls_instance=self.chat_workflow
            )
            self.flow_processor = FlowProcessor(
                entity_service=self.entity_service,
                helper_functions=self.workflow_helper_service,
                workflow_dispatcher=self.workflow_dispatcher
            )
        except Exception as e:
            # Replace print with a proper logging framework in production.
            print("Error during BeanFactory initialization:", e)
            raise

    def _load_default_config(self):
        """
        Load default configuration values, optionally from environment variables.
        """
        return {
            "CHAT_REPOSITORY": os.getenv("CHAT_REPOSITORY", "inmemory")
        }

    def _create_repository(self, repo_type):
        """
        Create the appropriate repository based on configuration.
        """
        if repo_type.lower() == "cyoda":
            return CyodaRepository()
        else:
            return InMemoryRepository()

    def get_flow_processor(self):
        """
        Retrieve the FlowProcessor instance.
        """
        return self.flow_processor

    def get_services(self):
        """
        Retrieve a dictionary of all managed services for further use.
        """
        return {
            "chat_lock": self.chat_lock,
            "entity_repository": self.entity_repository,
            "entity_service": self.entity_service,
            "editing_agent": self.editing_agent,
            "requirement_agent": self.requirement_agent,
            "ai_service": self.ai_service,
            "workflow_helper_service": self.workflow_helper_service,
            "workflow": self.workflow,
            "chat_workflow": self.chat_workflow,
            "workflow_dispatcher": self.workflow_dispatcher,
            "flow_processor": self.flow_processor,
            "dataset": self.dataset,
            "device_sessions": self.device_sessions,
        }


# Example usage:
if __name__ == "__main__":
    # Optional: Define a custom configuration (this can also be managed externally)
    config = {
        "CHAT_REPOSITORY": "cyoda"  # Change to "inmemory" if desired
    }
    factory = BeanFactory(config=config)
    flow_processor = factory.get_flow_processor()

    # Now you can use flow_processor and other services as needed in your application.
    print("BeanFactory initialized successfully. FlowProcessor is ready to use.")
