import logging
from typing import Any

from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity


class BaseWorkflowService:
    """
    Base tool class that provides common functionality and dependencies
    for all workflow tools used by AI agents.
    """
    
    def __init__(self,
                 workflow_helper_service,
                 entity_service,
                 cyoda_auth_service,
                 workflow_converter_service,
                 scheduler_service,
                 data_service,
                 dataset=None,
                 mock=False):
        """
        Initialize the base tool with common dependencies.

        Args:
            workflow_helper_service: Service for workflow operations
            entity_service: Service for entity operations
            cyoda_auth_service: Authentication service
            workflow_converter_service: Service for workflow conversion
            scheduler_service: Service for scheduling operations
            data_service: Service for data operations
            dataset: Optional dataset
            mock: Whether to run in mock mode
        """
        self.workflow_helper_service = workflow_helper_service
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.workflow_converter_service = workflow_converter_service
        self.scheduler_service = scheduler_service
        self.data_service = data_service
        self.dataset = dataset
        self.mock = mock
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _handle_error(self, entity: AgenticFlowEntity, error: Exception, message: str = None) -> str:
        """
        Common error handling for workflow operations.
        
        Args:
            entity: The chat entity to mark as failed
            error: The exception that occurred
            message: Optional custom error message
            
        Returns:
            Error message string
        """
        entity.failed = True
        entity.error = f"Error: {error}"
        error_msg = message or f"Error during operation: {error}"
        self.logger.exception(error)
        return error_msg
    
    async def _validate_required_params(self, params: dict, required_fields: list) -> tuple[bool, str]:
        """
        Validate that required parameters are present.

        Args:
            params: Parameters dictionary
            required_fields: List of required field names

        Returns:
            Tuple of (is_valid, error_message)
        """
        missing_fields = [field for field in required_fields if not params.get(field)]
        if missing_fields:
            error_msg = f"Missing required parameters: {', '.join(missing_fields)}"
            return False, error_msg
        return True, ""

    def parse_from_string(self, escaped_code: str) -> str:
        """
        Parse escaped string code.

        Args:
            escaped_code: Escaped code string

        Returns:
            Parsed code string
        """
        return escaped_code.encode("utf-8").decode("unicode_escape")

    async def get_entities_list(self, branch_id: str, repository_name: str) -> list:
        """
        Get list of entities for a given branch and repository.

        Args:
            branch_id: Git branch identifier
            repository_name: Repository name

        Returns:
            List of entity names
        """
        try:
            import os
            from common.config.config import config

            entity_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/entity"

            if repository_name.startswith("java"):
                entity_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/src/main/java/com/java_template/entity"

            # List all subdirectories (each subdirectory is an entity)
            entities = [
                name for name in os.listdir(entity_dir)
                if os.path.isdir(os.path.join(entity_dir, name))
            ]

            return entities

        except Exception as e:
            self.logger.exception(f"Error getting entities list: {e}")
            return []

    async def resolve_entity_name(self, entity_name: str, branch_id: str, repository_name: str) -> str:
        """
        Resolve entity name using similarity matching.

        Args:
            entity_name: Entity name to resolve
            branch_id: Git branch identifier
            repository_name: Repository name

        Returns:
            Resolved entity name or original if not found
        """
        try:
            from common.ai.nltk_service import get_most_similar_entity

            entity_names = await self.get_entities_list(branch_id=branch_id, repository_name=repository_name)
            resolved_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
            return resolved_name if resolved_name else entity_name

        except Exception as e:
            self.logger.exception(f"Error resolving entity name: {e}")
            return entity_name
