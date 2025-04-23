import asyncio
import os

from common.ai.ai_agent import OpenAiAgent
from common.ai.clients.openai_client import AsyncOpenAIClient
from common.auth.cyoda_auth import CyodaAuthService
from common.config.config import CHAT_REPOSITORY
from common.config.conts import FSM_CYODA
from common.grpc_client.grpc_client import GrpcClient
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.repository.in_memory_db import InMemoryRepository
from common.service.service import EntityServiceImpl
from entity.chat.workflow.helper_functions import WorkflowHelperService
from entity.flow_processor import FlowProcessor
from entity.chat.workflow.workflow import ChatWorkflow
from entity.model.model_registry import model_registry
from entity.scheduler.scheduler import Scheduler
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
            self.cyoda_auth_service = CyodaAuthService()
            self.dataset = {}
            self.device_sessions = {}
            self.workflow_helper_service = WorkflowHelperService(cyoda_auth_service=self.cyoda_auth_service)
            self.workflow = Workflow()

            self.entity_repository = self._create_repository(repo_type=CHAT_REPOSITORY, cyoda_auth_service=self.cyoda_auth_service)
            self.entity_service = EntityServiceImpl(repository=self.entity_repository, model_registry=model_registry)
            self.scheduler = Scheduler(entity_service=self.entity_service, cyoda_auth_service=self.cyoda_auth_service)
            self.chat_workflow = ChatWorkflow(
                dataset=self.dataset,
                workflow_helper_service=self.workflow_helper_service,
                entity_service=self.entity_service,
                scheduler = self.scheduler,
                cyoda_auth_service=self.cyoda_auth_service
            )
            self.openai_client = AsyncOpenAIClient()
            self.ai_agent = OpenAiAgent(client=self.openai_client)

            self.workflow_dispatcher = WorkflowDispatcher(
                cls=ChatWorkflow,
                cls_instance=self.chat_workflow,
                ai_agent=self.ai_agent,
                entity_service = self.entity_service,
                cyoda_auth_service=self.cyoda_auth_service
            )
            self.flow_processor = FlowProcessor(
                workflow_dispatcher=self.workflow_dispatcher
            )
            self.grpc_client = GrpcClient(workflow_dispatcher=self.workflow_dispatcher, auth=self.cyoda_auth_service)





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

    def _create_repository(self, repo_type, cyoda_auth_service):
        """
        Create the appropriate repository based on configuration.
        """
        if repo_type.lower() == "cyoda":
            return CyodaRepository(cyoda_auth_service=cyoda_auth_service)
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
            "fsm": FSM_CYODA,
            "grpc_client": self.grpc_client,
            "chat_lock": self.chat_lock,
            "entity_repository": self.entity_repository,
            "entity_service": self.entity_service,
            "ai_agent": self.ai_agent,
            "workflow_helper_service": self.workflow_helper_service,
            "workflow": self.workflow,
            "chat_workflow": self.chat_workflow,
            "workflow_dispatcher": self.workflow_dispatcher,
            "flow_processor": self.flow_processor,
            "dataset": self.dataset,
            "device_sessions": self.device_sessions,
            "cyoda_auth_service": self.cyoda_auth_service,
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
