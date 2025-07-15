import json
import aiofiles
from typing import Any

import common.config.const as const
from common.config.config import config
from common.utils.batch_converter import convert_state_diagram_to_jsonl_dataset
from common.utils.batch_parallel_code import build_workflow_from_jsonl
from common.utils.function_extractor import extract_function
from common.utils.result_validator import validate_ai_result
from common.utils.utils import get_project_file_name, _save_file, get_repository_name
from common.workflow.workflow_to_state_diagram_converter import convert_to_mermaid
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class WorkflowManagementService(BaseWorkflowService):
    """
    Service responsible for workflow management operations including
    workflow registration, validation, conversion, and diagram generation.
    """

    async def register_workflow_with_app(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Register workflow with application by processing entity models and launching workflows.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including filename and routes_file
            
        Returns:
            Success message or error
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["filename", "routes_file"]
            )
            if not is_valid:
                return error_msg

            filename = params.get("filename")
            routes_file = params.get("routes_file")

            # Get project file path
            file_path = await get_project_file_name(
                file_name=filename,
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=get_repository_name(entity)
            )

            # Read and parse input JSON
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                input_json = json.loads(content)

            # Save routes file
            await _save_file(
                _data=input_json.get("file_without_workflow").get("code"),
                item=routes_file,
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=get_repository_name(entity)
            )

            # Process entity models
            awaited_entity_ids = []
            for item in input_json.get("entity_models", []):
                if not isinstance(item, dict):
                    continue

                entity_model_name = item.get("entity_model_name")
                if not entity_model_name or not isinstance(entity_model_name, str):
                    continue

                workflow_function = item.get("workflow_function")
                if not workflow_function or not isinstance(workflow_function, dict):
                    continue

                # Prepare workflow cache
                workflow_cache = {
                    'workflow_function': workflow_function.get('name'),
                    'entity_name': entity_model_name,
                    const.GIT_BRANCH_PARAM: entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
                }

                # Store workflow function in edge messages
                edge_message_id = await self.entity_service.add_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                    entity_version=config.ENTITY_VERSION,
                    entity=json.dumps(workflow_function),
                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )

                edge_messages_store = {'code': edge_message_id}

                # Launch agentic workflow
                child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                    technical_id=technical_id,
                    entity=entity,
                    entity_model=const.ModelName.AGENTIC_FLOW_ENTITY.value,
                    workflow_name=(
                        const.ModelName.GENERATING_GEN_APP_WORKFLOW_JAVA.value 
                        if entity.workflow_name.endswith("java") 
                        else const.ModelName.GENERATING_GEN_APP_WORKFLOW_PYTHON.value
                    ),
                    workflow_cache=workflow_cache,
                    edge_messages_store=edge_messages_store
                )
                awaited_entity_ids.append(child_technical_id)

            if awaited_entity_ids:
                # Schedule workflow completion
                scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
                    awaited_entity_ids=awaited_entity_ids,
                    triggered_entity_id=technical_id,
                    triggered_entity_next_transition="update_routes_file"
                )
                entity.scheduled_entities.append(scheduled_entity_id)
                return "Workflow registration completed successfully"
            else:
                raise Exception(f"No workflows generated for {technical_id}")

        except Exception as e:
            return self._handle_error(entity, e, f"Error registering workflow: {e}")

    async def validate_workflow_design(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Validate workflow design by checking edge message store.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition
            
        Returns:
            Formatted validation result or None if invalid
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(params, ["transition"])
            if not is_valid:
                return error_msg

            edge_message_id = entity.edge_messages_store.get(params.get("transition"))
            if not edge_message_id:
                return "No edge message found for transition"

            # Get validation result from edge message store
            result = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=edge_message_id,
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            # Validate the result
            is_valid, formatted_result = validate_ai_result(result, "result.py")
            return formatted_result if is_valid else None

        except Exception as e:
            self.logger.exception(f"Error validating workflow design: {e}")
            return None

    async def has_workflow_code_validation_succeeded(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> bool:
        """
        Check if workflow code validation succeeded.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition
            
        Returns:
            True if validation succeeded, False otherwise
        """
        try:
            edge_message_id = entity.edge_messages_store.get(params.get("transition"))
            if not edge_message_id:
                return False

            result = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=edge_message_id,
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            return result is not None

        except Exception as e:
            self.logger.exception(f"Error checking workflow validation: {e}")
            return False

    async def has_workflow_code_validation_failed(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> bool:
        """
        Check if workflow code validation failed.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition
            
        Returns:
            True if validation failed, False otherwise
        """
        return not await self.has_workflow_code_validation_succeeded(technical_id, entity, **params)

    async def save_extracted_workflow_code(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Save extracted workflow code from edge message store.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition
            
        Returns:
            Extracted function code
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(params, ["transition"])
            if not is_valid:
                return error_msg

            edge_message_id = entity.edge_messages_store.get(params.get("transition"))
            if not edge_message_id:
                return "No edge message found for transition"

            # Get source code from edge message store
            source = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=edge_message_id,
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            # Extract function from source
            code_without_function, extracted_function = extract_function(
                source=source,
                function_name=entity.workflow_cache.get("workflow_function")
            )

            self.logger.info(extracted_function)

            # Save the code without function
            await _save_file(
                _data=code_without_function,
                item=f"entity/{entity.workflow_cache.get('entity_name')}/workflow.py",
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=get_repository_name(entity)
            )

            return extracted_function

        except Exception as e:
            return self._handle_error(entity, e, f"Error saving extracted workflow code: {e}")

    async def convert_diagram_to_dataset(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Convert state diagram to JSONL dataset.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including input_file_path and output_file_path
            
        Returns:
            Success message or error
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["input_file_path", "output_file_path"]
            )
            if not is_valid:
                return error_msg

            input_file_path = params.get("input_file_path")
            output_file_path = params.get("output_file_path")

            convert_state_diagram_to_jsonl_dataset(
                input_file_path=input_file_path,
                output_file_path=output_file_path
            )
            return "Diagram converted to dataset successfully"

        except Exception as e:
            return self._handle_error(entity, e, f"Error converting diagram to dataset: {e}")

    async def convert_workflow_processed_dataset_to_json(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Convert workflow processed dataset to JSON.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including input_file_path and output_file_path
            
        Returns:
            Success message or error
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["input_file_path", "output_file_path"]
            )
            if not is_valid:
                return error_msg

            input_file_path = params.get("input_file_path")
            output_file_path = params.get("output_file_path")

            # Build workflow from JSONL
            result = await build_workflow_from_jsonl(input_file_path=input_file_path)

            # Save the result
            await _save_file(
                _data=result,
                item=output_file_path,
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=get_repository_name(entity)
            )
            return "Workflow dataset converted to JSON successfully"

        except Exception as e:
            return self._handle_error(entity, e, f"Error converting workflow dataset: {e}")

    async def convert_workflow_json_to_state_diagram(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Convert workflow JSON to state diagram.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including input_file_path
            
        Returns:
            Mermaid diagram string or error
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(params, ["input_file_path"])
            if not is_valid:
                return error_msg

            input_file_path = params.get("input_file_path")

            # Read and parse JSON file
            with open(input_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert to mermaid diagram
            mermaid_diagram = convert_to_mermaid(data)
            return mermaid_diagram

        except Exception as e:
            return self._handle_error(entity, e, f"Error converting workflow to diagram: {e}")

    async def convert_workflow_to_dto(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> str:
        """
        Convert workflow configuration to Cyoda DTO format.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_file_name, output_file_name, entity_version

        Returns:
            Success or error message
        """
        success_msg = "Successfully converted workflow config to cyoda dto"
        error_msg = "Error while converting workflow"

        try:
            # Extract & validate parameters
            entity_name = entity.workflow_cache.get("entity_name", params.get("entity_name"))
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, params.get(const.GIT_BRANCH_PARAM))

            if not (entity_name or git_branch_id):
                raise ValueError("Missing entity_name in workflow_cache")

            workflow_file_tmpl = params.get("workflow_file_name")
            output_file_tmpl = params.get("output_file_name")
            if not (workflow_file_tmpl and output_file_tmpl):
                raise ValueError("Both workflow_file_name and output_file_name are required")

            entity_version = params.get("entity_version", config.CLIENT_ENTITY_VERSION)
            repo_name = get_repository_name(entity)

            # Compute file names
            workflow_filename = workflow_file_tmpl.format(entity_name=entity_name)
            output_filename = output_file_tmpl.format(entity_name=entity_name)

            # Load, transform, persist original workflow
            project_path = await get_project_file_name(
                git_branch_id=git_branch_id,
                file_name=workflow_filename,
                repository_name=repo_name,
            )
            workflow = await self.workflow_helper_service.read_json(project_path)

            ordered_fsm = await self.workflow_helper_service.order_states_in_fsm(workflow)

            # Convert to DTO
            dto = await self.workflow_converter_service.convert_workflow(
                workflow_contents=workflow,
                entity_name=entity_name,
                entity_version=entity_version,
                technical_id=git_branch_id,
            )

            # Persist both JSON blobs
            to_save = [
                (workflow_filename, ordered_fsm),
                (output_filename, dto),
            ]
            for path_or_item, data in to_save:
                await self.workflow_helper_service.persist_json(
                    path_or_item=path_or_item,
                    data=data,
                    git_branch_id=git_branch_id,
                    repository_name=repo_name,
                )

            return success_msg

        except Exception as e:
            self.logger.exception(f"Failed to convert workflow for {technical_id}: {e}")
            return error_msg
