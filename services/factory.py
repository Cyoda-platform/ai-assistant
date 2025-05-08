import asyncio
import os

from common.config.config import config as env_config
import common.config.const as const
from common.ai.ai_agent import OpenAiAgent
from common.ai.clients.openai_client import AsyncOpenAIClient
from common.auth.cyoda_auth import CyodaAuthService
from common.grpc_client.grpc_client import GrpcClient
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.repository.in_memory_db import InMemoryRepository
from common.service.service import EntityServiceImpl
from entity.model_registry import model_registry
from entity.chat.workflow.helper_functions import WorkflowHelperService
from entity.chat.workflow.workflow import ChatWorkflow
from services.scheduler import Scheduler
from entity.workflow import Workflow
from entity.workflow_dispatcher import WorkflowDispatcher


class BeanFactory:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only run the initialization logic a single time
        if self.__class__._initialized:
            return
        self.__class__._initialized = True

        # === your existing init logic ===
        self.chat_lock = asyncio.Lock()

        try:
            # Create the repository based on configuration.
            self.cyoda_auth_service = CyodaAuthService()
            self.dataset = {}
            self.device_sessions = {}
            self.workflow_helper_service = WorkflowHelperService(cyoda_auth_service=self.cyoda_auth_service)
            self.workflow = Workflow()

            self.entity_repository = self._create_repository(repo_type=env_config.CHAT_REPOSITORY,
                                                             cyoda_auth_service=self.cyoda_auth_service)
            self.entity_service = EntityServiceImpl(repository=self.entity_repository, model_registry=model_registry)
            self.scheduler = Scheduler(entity_service=self.entity_service, cyoda_auth_service=self.cyoda_auth_service)
            self.chat_workflow = ChatWorkflow(
                dataset=self.dataset,
                workflow_helper_service=self.workflow_helper_service,
                entity_service=self.entity_service,
                scheduler=self.scheduler,
                cyoda_auth_service=self.cyoda_auth_service
            )
            self.openai_client = AsyncOpenAIClient()
            self.ai_agent = OpenAiAgent(client=self.openai_client)

            self.workflow_dispatcher = WorkflowDispatcher(
                cls=ChatWorkflow,
                cls_instance=self.chat_workflow,
                ai_agent=self.ai_agent,
                entity_service=self.entity_service,
                cyoda_auth_service=self.cyoda_auth_service
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

    def get_services(self):
        """
        Retrieve a dictionary of all managed services for further use.
        """
        return {
            "fsm": const.FsmTarget.CYODA.value,
            "grpc_client": self.grpc_client,
            "chat_lock": self.chat_lock,
            "entity_repository": self.entity_repository,
            "entity_service": self.entity_service,
            "ai_agent": self.ai_agent,
            "workflow_helper_service": self.workflow_helper_service,
            "workflow": self.workflow,
            "chat_workflow": self.chat_workflow,
            "workflow_dispatcher": self.workflow_dispatcher,
            "dataset": self.dataset,
            "device_sessions": self.device_sessions,
            "cyoda_auth_service": self.cyoda_auth_service,
        } # or directly paste the BeanFactory class here, then drop logic.init

# one single factory for the whole app
_factory = BeanFactory()
_services = _factory.get_services()

ai_agent           = _services['ai_agent']
entity_service     = _services['entity_service']
chat_lock          = _services['chat_lock']
fsm_implementation = _services['fsm']
grpc_client        = _services['grpc_client']
cyoda_auth_service = _services['cyoda_auth_service']