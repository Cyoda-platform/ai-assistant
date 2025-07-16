import logging
from entity.workflow import Workflow

from tools.file_operations_service import FileOperationsService
from tools.web_operations_service import WebOperationsService
from tools.state_management_service import StateManagementService
from tools.deployment_service import DeploymentService
from tools.application_builder_service import ApplicationBuilderService
from tools.application_editor_service import ApplicationEditorService
from tools.workflow_management_service import WorkflowManagementService
from tools.workflow_validation_service import WorkflowValidationService
from tools.utility_service import UtilityService

logger = logging.getLogger(__name__)


class ChatWorkflow(Workflow):
    def __init__(self, dataset,
                 workflow_helper_service,
                 entity_service,
                 cyoda_auth_service,
                 workflow_converter_service,  # todo will need factory soon
                 scheduler_service,
                 data_service,
                 mock=False):
        # Store original dependencies for backward compatibility
        self.dataset = dataset
        self.workflow_helper_service = workflow_helper_service
        self.entity_service = entity_service
        self.mock = mock
        self.cyoda_auth_service = cyoda_auth_service
        self.workflow_converter_service = workflow_converter_service
        self.scheduler_service = scheduler_service
        self.data_service = data_service

        # Initialize specialized tools for AI agents
        self.file_operations_service = FileOperationsService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.web_operations_service = WebOperationsService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.state_management_service = StateManagementService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.deployment_service = DeploymentService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.application_builder_service = ApplicationBuilderService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.application_editor_service = ApplicationEditorService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.workflow_management_service = WorkflowManagementService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.workflow_validation_service = WorkflowValidationService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        self.utility_service = UtilityService(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )

        # Initialize function registry
        self._function_registry = self._build_function_registry()

    def _build_function_registry(self) -> dict:
        """
        Build the function registry mapping function names to their implementations.
        This allows for easy lookup and delegation to the appropriate AI agent tool.

        Returns:
            Dictionary mapping function names to their tool implementations
        """
        return {
            # File Operations
            'save_env_file': self.file_operations_service.save_env_file,
            'save_file': self.file_operations_service.save_file,
            'read_file': self.file_operations_service.read_file,
            'get_file_contents': self.file_operations_service.get_file_contents,
            'get_entity_pojo_contents': self.file_operations_service.get_entity_pojo_contents,
            'list_directory_files': self.file_operations_service.list_directory_files,
            'clone_repo': self.file_operations_service.clone_repo,
            'delete_files': self.file_operations_service.delete_files,
            'save_entity_templates': self.file_operations_service.save_entity_templates,
            'add_application_resource': self.file_operations_service.add_application_resource,

            # Web Operations
            'web_search': self.web_operations_service.web_search,
            'read_link': self.web_operations_service.read_link,
            'web_scrape': self.web_operations_service.web_scrape,
            'get_cyoda_guidelines': self.web_operations_service.get_cyoda_guidelines,

            # State Management
            'finish_discussion': self.state_management_service.finish_discussion,
            'is_stage_completed': self.state_management_service.is_stage_completed,
            'not_stage_completed': self.state_management_service.not_stage_completed,
            'is_chat_locked': self.state_management_service.is_chat_locked,
            'is_chat_unlocked': self.state_management_service.is_chat_unlocked,
            'lock_chat': self.state_management_service.lock_chat,
            'unlock_chat': self.state_management_service.unlock_chat,
            'reset_failed_entity': self.state_management_service.reset_failed_entity,

            # Deployment Operations
            'schedule_deploy_env': self.deployment_service.schedule_deploy_env,
            'schedule_build_user_application': self.deployment_service.schedule_build_user_application,
            'schedule_deploy_user_application': self.deployment_service.schedule_deploy_user_application,
            'deploy_cyoda_env': self.deployment_service.deploy_cyoda_env,
            'deploy_user_application': self.deployment_service.deploy_user_application,
            'get_env_deploy_status': self.deployment_service.get_env_deploy_status,

            # Application Building
            'build_general_application': self.application_builder_service.build_general_application,
            'resume_build_general_application': self.application_builder_service.resume_build_general_application,
            'init_setup_workflow': self.application_builder_service.init_setup_workflow,

            # Application Editing
            'edit_existing_app_design_additional_feature': self.application_editor_service.edit_existing_app_design_additional_feature,
            'edit_api_existing_app': self.application_editor_service.edit_api_existing_app,
            'edit_existing_workflow': self.application_editor_service.edit_existing_workflow,
            'edit_existing_processors': self.application_editor_service.edit_existing_processors,
            'add_new_entity_for_existing_app': self.application_editor_service.add_new_entity_for_existing_app,
            'add_new_workflow': self.application_editor_service.add_new_workflow,

            # Workflow Management
            'register_workflow_with_app': self.workflow_management_service.register_workflow_with_app,
            'validate_workflow_design': self.workflow_management_service.validate_workflow_design,
            'has_workflow_code_validation_succeeded': self.workflow_management_service.has_workflow_code_validation_succeeded,
            'has_workflow_code_validation_failed': self.workflow_management_service.has_workflow_code_validation_failed,
            'save_extracted_workflow_code': self.workflow_management_service.save_extracted_workflow_code,
            'convert_diagram_to_dataset': self.workflow_management_service.convert_diagram_to_dataset,
            'convert_workflow_processed_dataset_to_json': self.workflow_management_service.convert_workflow_processed_dataset_to_json,
            'convert_workflow_json_to_state_diagram': self.workflow_management_service.convert_workflow_json_to_state_diagram,
            'convert_workflow_to_dto': self.workflow_management_service.convert_workflow_to_dto,

            # Workflow Validation
            'validate_workflow_implementation': self.workflow_validation_service.validate_workflow_implementation,

            # Utility Functions
            'get_weather': self.utility_service.get_weather,
            'get_humidity': self.utility_service.get_humidity,
            'get_user_info': self.utility_service.get_user_info,
            'init_chats': self.utility_service.init_chats,
            'fail_workflow': self.utility_service.fail_workflow,
            'check_scheduled_entity_status': self.utility_service.check_scheduled_entity_status,
            'trigger_parent_entity': self.utility_service.trigger_parent_entity,

        }

    def __getattr__(self, name):
        """
        Dynamic attribute access for function registry.
        This allows the workflow to maintain backward compatibility while
        delegating to the appropriate AI agent tool.

        Args:
            name: Function name to look up

        Returns:
            Function implementation from tool registry

        Raises:
            AttributeError: If function not found in registry
        """
        if name in self._function_registry:
            return self._function_registry[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
