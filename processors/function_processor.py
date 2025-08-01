"""
Function processor for executing reusable tools/functions within workflows.

This processor handles the execution of standalone functions and tools
that can be shared across multiple workflows and agents.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .base_processor import BaseProcessor, ProcessorContext, ProcessorResult
from .loaders.tool_loader import ToolLoader
logger = logging.getLogger(__name__)

class FunctionProcessor(BaseProcessor):
    """
    Processor for executing reusable functions and tools.
    
    Supports:
    - JSON-defined tools with parameters
    - Function parameter validation
    - Tool result processing
    - Integration with existing tool ecosystem
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the function processor.
        
        Args:
            base_path: Base directory path for loading resources
        """
        super().__init__("FunctionProcessor")
        self.base_path = Path(base_path)
        self.tool_loader = ToolLoader(base_path)
        self._services = None
        self._function_map = None
    
    def supports(self, processor_name: str) -> bool:
        """
        Check if this processor supports the given processor name.

        Args:
            processor_name: Name to check (format: "FunctionProcessor.function_name_with_underscores")

        Returns:
            True if processor name starts with "FunctionProcessor."
        """
        return processor_name.startswith("FunctionProcessor.") and len(processor_name.split(".", 1)) == 2

    def _initialize_services(self):
        """Initialize the tool services with mock dependencies."""
        if self._services is not None:
            return

        from unittest.mock import Mock

        # Create mock dependencies
        mock_dataset = Mock()
        mock_workflow_helper = Mock()
        mock_entity_service = Mock()
        mock_cyoda_auth = Mock()
        mock_workflow_converter = Mock()
        mock_scheduler = Mock()
        mock_data_service = Mock()

        # Import and initialize all services
        from tools.file_operations_service import FileOperationsService
        from tools.web_operations_service import WebOperationsService
        from tools.state_management_service import StateManagementService
        from tools.deployment_service import DeploymentService
        from tools.application_builder_service import ApplicationBuilderService
        from tools.application_editor_service import ApplicationEditorService
        from tools.workflow_management_service import WorkflowManagementService
        from tools.workflow_validation_service import WorkflowValidationService
        from tools.utility_service import UtilityService
        from tools.build_id_retrieval_service import BuildIdRetrievalService
        from tools.github_operations_service import GitHubOperationsService
        from tools.workflow_orchestration_service import WorkflowOrchestrationService

        # Initialize services
        self._services = {
            'file_operations': FileOperationsService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'web_operations': WebOperationsService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'state_management': StateManagementService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'deployment': DeploymentService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'application_builder': ApplicationBuilderService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'application_editor': ApplicationEditorService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'workflow_management': WorkflowManagementService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'workflow_validation': WorkflowValidationService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'utility': UtilityService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'build_id_retrieval': BuildIdRetrievalService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'github_operations': GitHubOperationsService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            ),
            'workflow_orchestration': WorkflowOrchestrationService(
                workflow_helper_service=mock_workflow_helper,
                entity_service=mock_entity_service,
                cyoda_auth_service=mock_cyoda_auth,
                workflow_converter_service=mock_workflow_converter,
                scheduler_service=mock_scheduler,
                data_service=mock_data_service,
                dataset=mock_dataset,
                mock=True
            )
        }

        # Build function mapping (same as ChatWorkflow._build_function_registry)
        self._function_map = {
            # File Operations
            'save_env_file': self._services['file_operations'].save_env_file,
            'save_file': self._services['file_operations'].save_file,
            'read_file': self._services['file_operations'].read_file,
            'get_file_contents': self._services['file_operations'].get_file_contents,
            'get_entity_pojo_contents': self._services['file_operations'].get_entity_pojo_contents,
            'list_directory_files': self._services['file_operations'].list_directory_files,
            'clone_repo': self._services['file_operations'].clone_repo,
            'delete_files': self._services['file_operations'].delete_files,
            'save_entity_templates': self._services['file_operations'].save_entity_templates,
            'add_application_resource': self._services['file_operations'].add_application_resource,

            # Web Operations
            'web_search': self._services['web_operations'].web_search,
            'read_link': self._services['web_operations'].read_link,
            'web_scrape': self._services['web_operations'].web_scrape,
            'get_cyoda_guidelines': self._services['web_operations'].get_cyoda_guidelines,

            # State Management
            'finish_discussion': self._services['state_management'].finish_discussion,
            'is_stage_completed': self._services['state_management'].is_stage_completed,
            'not_stage_completed': self._services['state_management'].not_stage_completed,
            'is_chat_locked': self._services['state_management'].is_chat_locked,
            'is_chat_unlocked': self._services['state_management'].is_chat_unlocked,
            'lock_chat': self._services['state_management'].lock_chat,
            'unlock_chat': self._services['state_management'].unlock_chat,
            'reset_failed_entity': self._services['state_management'].reset_failed_entity,

            # Deployment Operations
            'schedule_deploy_env': self._services['deployment'].schedule_deploy_env,
            'schedule_build_user_application': self._services['deployment'].schedule_build_user_application,
            'schedule_deploy_user_application': self._services['deployment'].schedule_deploy_user_application,
            'deploy_cyoda_env': self._services['deployment'].deploy_cyoda_env,
            'deploy_cyoda_env_background': self._services['deployment'].deploy_cyoda_env_background,
            'deploy_user_application': self._services['deployment'].deploy_user_application,
            'get_env_deploy_status': self._services['deployment'].get_env_deploy_status,

            # Application Building
            'build_general_application': self._services['application_builder'].build_general_application,
            'resume_build_general_application': self._services['application_builder'].resume_build_general_application,
            'init_setup_workflow': self._services['application_builder'].init_setup_workflow,

            # Application Editing
            'edit_existing_app_design_additional_feature': self._services['application_editor'].edit_existing_app_design_additional_feature,
            'edit_api_existing_app': self._services['application_editor'].edit_api_existing_app,
            'edit_existing_workflow': self._services['application_editor'].edit_existing_workflow,
            'edit_existing_processors': self._services['application_editor'].edit_existing_processors,
            'add_new_entity_for_existing_app': self._services['application_editor'].add_new_entity_for_existing_app,
            'add_new_workflow': self._services['application_editor'].add_new_workflow,

            # Workflow Management
            'launch_gen_app_workflows': self._services['workflow_management'].launch_gen_app_workflows,
            'launch_deployment_chat_workflow': self._services['workflow_management'].launch_deployment_chat_workflow,
            'register_workflow_with_app': self._services['workflow_management'].register_workflow_with_app,
            'validate_workflow_design': self._services['workflow_management'].validate_workflow_design,
            'has_workflow_code_validation_succeeded': self._services['workflow_management'].has_workflow_code_validation_succeeded,
            'has_workflow_code_validation_failed': self._services['workflow_management'].has_workflow_code_validation_failed,
            'save_extracted_workflow_code': self._services['workflow_management'].save_extracted_workflow_code,
            'convert_diagram_to_dataset': self._services['workflow_management'].convert_diagram_to_dataset,
            'convert_workflow_processed_dataset_to_json': self._services['workflow_management'].convert_workflow_processed_dataset_to_json,
            'convert_workflow_json_to_state_diagram': self._services['workflow_management'].convert_workflow_json_to_state_diagram,
            'convert_workflow_to_dto': self._services['workflow_management'].convert_workflow_to_dto,

            # Workflow Validation
            'validate_workflow_implementation': self._services['workflow_validation'].validate_workflow_implementation,

            # Utility Functions
            'get_weather': self._services['utility'].get_weather,
            'get_humidity': self._services['utility'].get_humidity,
            'get_user_info': self._services['utility'].get_user_info,
            'init_chats': self._services['utility'].init_chats,
            'fail_workflow': self._services['utility'].fail_workflow,
            'check_scheduled_entity_status': self._services['utility'].check_scheduled_entity_status,
            'trigger_parent_entity': self._services['utility'].trigger_parent_entity,

            # Build ID Retrieval
            'get_build_id_from_context': self._services['build_id_retrieval'].get_build_id_from_context,

            # GitHub Operations
            'add_collaborator': self._services['github_operations'].add_collaborator,

            # Workflow Orchestration
            'launch_agentic_workflow': self._services['workflow_orchestration'].launch_agentic_workflow,
            'launch_scheduled_workflow': self._services['workflow_orchestration'].launch_scheduled_workflow,
            'order_states_in_fsm': self._services['workflow_orchestration'].order_states_in_fsm,
            'read_json': self._services['workflow_orchestration'].read_json,
            'persist_json': self._services['workflow_orchestration'].persist_json
        }
    
    async def execute(self, context: ProcessorContext) -> ProcessorResult:
        """
        Execute a function/tool based on the processor configuration.

        Args:
            context: Execution context containing function configuration

        Returns:
            ProcessorResult with function execution outcome
        """
        if not self.validate_context(context):
            return self.create_error_result("Invalid context provided")

        try:
            # Extract function name from processor name (FunctionProcessor.function_name)
            processor_parts = context.config.get("processor_name", "").split(".", 1)
            if len(processor_parts) != 2 or processor_parts[0] != "FunctionProcessor":
                return self.create_error_result("Invalid function processor name format")

            function_name = processor_parts[1]

            # Initialize services if not already done
            self._initialize_services()

            # Get the function from mapping
            if function_name not in self._function_map:
                available_functions = list(self._function_map.keys())[:10]
                return self.create_error_result(f"Function '{function_name}' not found. Available functions: {available_functions}")

            try:
                # Get the function
                function = self._function_map[function_name]

                # Prepare arguments
                technical_id = context.entity_id
                entity = context.entity_data  # Now receives the entity object directly

                # Extract kwargs from workflow_cache if entity has it
                kwargs = {}
                if hasattr(entity, 'workflow_cache'):
                    kwargs = entity.workflow_cache or {}
                elif isinstance(entity, dict):
                    # Backward compatibility for dict-based entity_data
                    kwargs = entity.get('workflow_cache', {})

                # Execute the function directly (async or sync)
                import inspect
                if inspect.iscoroutinefunction(function):
                    result = await function(technical_id, entity, **kwargs)
                else:
                    result = function(technical_id, entity, **kwargs)

                return self.create_success_result(data={
                    "function_name": function_name,
                    "result": result,
                    "execution_type": "function"
                })

            except Exception as e:
                logger.exception(f"Error executing function '{function_name}': {e}")
                return self.create_error_result(f"Function execution failed: {str(e)}")

        except Exception as e:
            logger.exception(f"Error in function processor execution: {e}")
            return self.create_error_result(f"Function processor failed: {str(e)}")


    
    def _prepare_parameters(self, function_config: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Prepare function parameters from context and configuration.
        
        Args:
            function_config: Function configuration
            context: Execution context
            
        Returns:
            Prepared parameters dictionary
        """
        parameters = {}
        
        # Get parameter definitions from function config
        param_definitions = function_config.get("parameters", {}).get("properties", {})
        required_params = function_config.get("parameters", {}).get("required", [])
        
        # Extract parameters from context config
        context_params = context.config.get("parameters", {})
        
        # Apply context variables to parameters
        for param_name, param_def in param_definitions.items():
            if param_name in context_params:
                param_value = context_params[param_name]
                
                # Apply entity data substitution if needed
                if isinstance(param_value, str) and context.entity_data:
                    param_value = self._apply_context_variables(param_value, context.entity_data)
                
                parameters[param_name] = param_value
            elif param_name in required_params:
                # Check if we can derive from entity data
                if context.entity_data and param_name in context.entity_data:
                    parameters[param_name] = context.entity_data[param_name]
                else:
                    raise ValueError(f"Required parameter '{param_name}' not provided")
        
        return parameters
    
    async def _execute_function(
        self,
        function_config: Dict[str, Any],
        parameters: Dict[str, Any],
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Execute the function with the given parameters.

        Args:
            function_config: Function configuration
            parameters: Function parameters
            context: Execution context

        Returns:
            Function execution result
        """
        function_name = function_config.get("name")
        function_type = function_config.get("type", "function")

        if function_type == "function":
            return await self._execute_standard_function(function_name, parameters, context)
        elif function_type == "tool":
            return self._execute_tool_function(function_config, parameters, context)
        else:
            raise ValueError(f"Unsupported function type: {function_type}")
    
    async def _execute_standard_function(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Execute a standard function by name using direct service calls.

        Args:
            function_name: Name of the function to execute
            parameters: Function parameters
            context: Execution context

        Returns:
            Function result
        """
        # Initialize services if not already done
        self._initialize_services()

        # Check if function exists in our mapping
        if function_name in self._function_map:
            try:
                # Get the function
                function = self._function_map[function_name]

                # Prepare arguments
                technical_id = context.entity_id
                entity = context.entity_data  # Now receives the entity object directly

                # Extract kwargs from workflow_cache and parameters
                kwargs = {}
                if hasattr(entity, 'workflow_cache'):
                    kwargs = entity.workflow_cache or {}
                elif isinstance(entity, dict):
                    # Backward compatibility for dict-based entity_data
                    kwargs = entity.get('workflow_cache', {})
                kwargs.update(parameters)

                # Execute the function directly (async or sync)
                import inspect
                if inspect.iscoroutinefunction(function):
                    result = await function(technical_id, entity, **kwargs)
                else:
                    result = function(technical_id, entity, **kwargs)

                return {
                    "function_name": function_name,
                    "result": result,
                    "execution_type": "function"
                }

            except Exception as e:
                raise ValueError(f"Function execution failed: {str(e)}")
        else:
            # Fallback to hardcoded functions for backward compatibility
            function_map = {
                "convert_workflow_to_dto": self._convert_workflow_to_dto,
                "add_application_resource": self._add_application_resource,
                "validate_entity": self._validate_entity,
            }

            if function_name in function_map:
                return function_map[function_name](parameters, context)
            else:
                available_functions = list(self._function_map.keys())[:10]
                raise ValueError(f"Unknown function: {function_name}. Available functions: {available_functions}")
    
    def _execute_tool_function(
        self, 
        function_config: Dict[str, Any], 
        parameters: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Execute a tool-based function.
        
        Args:
            function_config: Tool configuration
            parameters: Function parameters
            context: Execution context
            
        Returns:
            Tool execution result
        """
        # This would integrate with your existing tool execution framework
        return {
            "type": "tool_result",
            "tool_name": function_config.get("name"),
            "parameters": parameters,
            "status": "executed"
        }
    
    def _convert_workflow_to_dto(self, parameters: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Convert workflow to DTO format.
        
        Args:
            parameters: Function parameters
            context: Execution context
            
        Returns:
            Conversion result
        """
        workflow_file = parameters.get("workflow_file_name")
        output_file = parameters.get("output_file_name")
        
        # Placeholder implementation
        return {
            "function": "convert_workflow_to_dto",
            "input_file": workflow_file,
            "output_file": output_file,
            "status": "converted"
        }
    
    def _add_application_resource(self, parameters: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Add application resource file.
        
        Args:
            parameters: Function parameters
            context: Execution context
            
        Returns:
            Resource addition result
        """
        resource_path = parameters.get("resource_path")
        file_contents = parameters.get("file_contents")
        
        # Placeholder implementation
        return {
            "function": "add_application_resource",
            "resource_path": resource_path,
            "content_length": len(file_contents) if file_contents else 0,
            "status": "added"
        }
    
    def _validate_entity(self, parameters: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Validate entity data.
        
        Args:
            parameters: Function parameters
            context: Execution context
            
        Returns:
            Validation result
        """
        entity_data = parameters.get("entity_data", context.entity_data)
        
        # Placeholder implementation
        return {
            "function": "validate_entity",
            "entity_valid": entity_data is not None,
            "validation_errors": [],
            "status": "validated"
        }
    
    def _apply_context_variables(self, content: str, entity_data: Dict[str, Any]) -> str:
        """
        Apply context variables to content string.
        
        Args:
            content: Content string with variables
            entity_data: Entity data for variable substitution
            
        Returns:
            Content with variables replaced
        """
        # Simple variable substitution - can be enhanced
        for key, value in entity_data.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        return content
