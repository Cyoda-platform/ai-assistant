import json
import os
from typing import Any

import aiofiles
import common.config.const as const
from common.config.config import config
from common.exception.exceptions import InvalidTokenException
from common.utils.chat_util_functions import _launch_transition
from common.utils.utils import send_get_request, read_file_util
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity
from tools.base_service import BaseWorkflowService


class UtilityService(BaseWorkflowService):
    """
    Service responsible for utility operations including
    weather information, user info, entity resolution, and scheduler operations.
    """

    async def get_weather(self, technical_id: str, entity: ChatEntity, **params) -> dict:
        """
        Get weather information for a city.
        This is an example implementation that should be replaced with actual API integration.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including city
            
        Returns:
            Weather information dictionary
        """
        return {
            "city": params.get("city", "Unknown"),
            "temperature": "18°C",
            "condition": "Sunny"
        }

    async def get_humidity(self, technical_id: str, entity: ChatEntity, **params) -> dict:
        """
        Get humidity information for a city.
        This is an example implementation that should be replaced with actual API integration.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including city
            
        Returns:
            Humidity information dictionary
        """
        return {
            "city": params.get("city", "Unknown"),
            "humidity": "55%"
        }

    async def get_user_info(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Retrieve and cache user information including Cyoda environment URL.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters (unused)
            
        Returns:
            JSON string with user information
        """
        try:
            cache = entity.workflow_cache

            # Only construct and check the Cyoda environment URL if not already cached
            user_id = entity.user_id
            is_guest = user_id.startswith('guest.')
            url: str
            deployed: bool = False

            if is_guest:
                url = "please, log in to deploy"
            else:
                url = f"https://client-{user_id.lower()}.{config.CLIENT_HOST}"
                try:
                    await send_get_request(api_url=url, path='api/v1', token='guest_token')
                except InvalidTokenException:
                    deployed = True
                except Exception as e:
                    self.logger.exception(f"Error checking Cyoda environment status: {e}")
            cache['user_logged_in'] = not is_guest
            cache['cyoda_env_url'] = url
            cache['cyoda_environment_status'] = 'deployed' if deployed else 'is not yet deployed'

            # Prepare the final result
            cache_json = json.dumps(cache)
            return f"Please base your answer on this information: {cache_json}"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting user info: {e}")

    async def init_chats(self, technical_id: str, entity: ChatEntity, **params) -> None:
        """
        Initialize chats by saving user request and files to functional requirements directory.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
        """
        try:
            # Get user request from workflow cache
            user_request = entity.workflow_cache.get('user_request', '')

            # Get repository information
            git_branch_id = entity.workflow_cache.get('git_branch')
            repository_name = entity.workflow_cache.get('repository_name')
            programming_language = entity.workflow_cache.get(const.PROGRAMMING_LANGUAGE_PARAM)

            if not git_branch_id or not repository_name:
                self.logger.error("Missing git_branch or repository_name in workflow cache")
                return "Error: Missing repository information"

            # Save user request to functional_requirements/user_requirement.md
            from common.utils.utils import _save_file
            await _save_file(
                _data=user_request,
                item="user_requirement.md",
                git_branch_id=git_branch_id,
                repository_name=repository_name,
                folder_name=params.get(programming_language)
            )

            # Get file edge message IDs from workflow cache
            file_edge_message_ids = entity.workflow_cache.get('file_edge_message_ids', [])

            # Save each file from file_edge_message_ids
            for i, message_id in enumerate(file_edge_message_ids):
                try:
                    # Retrieve edge message content using entity service
                    edge_message = await self.entity_service.get_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=message_id,
                        meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                    )

                    if edge_message:
                        # Extract blob data from edge message
                        filename = f"uploaded_file_{i+1}.txt"
                        file_content = ""

                        # Handle FlowEdgeMessage blob format
                        if isinstance(edge_message, dict):
                            # Get base64 encoded content from message field
                            base64_content = edge_message.get('message', '')
                            metadata = edge_message.get('metadata', {})

                            # Extract filename from metadata
                            if metadata and 'filename' in metadata:
                                filename = metadata['filename']

                            # Decode base64 content if it's a file blob
                            if base64_content and metadata.get('encoding') == 'base64':
                                try:
                                    import base64
                                    # Decode base64 to get original binary data
                                    file_content = base64.b64decode(base64_content)
                                    self.logger.info(f"Decoded file blob: {filename} ({len(file_content)} bytes)")
                                except Exception as decode_error:
                                    self.logger.error(f"Error decoding base64 content: {decode_error}")
                                    file_content = f"[Error decoding file content: {decode_error}]"
                            else:
                                # Fallback to raw message content
                                file_content = str(base64_content)

                        elif hasattr(edge_message, 'message') and hasattr(edge_message, 'metadata'):
                            # Handle object format
                            base64_content = edge_message.message
                            metadata = edge_message.metadata or {}

                            if metadata.get('filename'):
                                filename = metadata['filename']

                            if base64_content and metadata.get('encoding') == 'base64':
                                try:
                                    import base64
                                    # Decode base64 to get original binary data
                                    file_content = base64.b64decode(base64_content)
                                    self.logger.info(f"Decoded file blob: {filename} ({len(file_content)} bytes)")
                                except Exception as decode_error:
                                    self.logger.error(f"Error decoding base64 content: {decode_error}")
                                    file_content = f"[Error decoding file content: {decode_error}]"
                            else:
                                file_content = str(base64_content)
                        else:
                            # Fallback for unexpected format
                            file_content = str(edge_message)

                        # Save file content to functional_requirements directory
                        await _save_file(
                            _data=file_content,
                            item=filename,
                            git_branch_id=git_branch_id,
                            repository_name=repository_name,
                            folder_name=params.get(programming_language)
                        )

                        self.logger.info(f"Saved file {filename} from edge message {message_id}")
                    else:
                        self.logger.warning(f"Could not retrieve content for edge message {message_id}")

                except Exception as e:
                    self.logger.error(f"Error processing edge message {message_id}: {e}")
                    continue

            self.logger.info(f"Successfully initialized chats with user request and {len(file_edge_message_ids)} files")
            return entity.workflow_cache['user_request']

        except Exception as e:
            return self._handle_error(entity, e, f"Error initializing chats: {e}")

    async def fail_workflow(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Mark a workflow as failed and log the failure.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters (unused)
            
        Returns:
            Failure notification message
        """
        self.logger.exception(f"failed workflow {technical_id}")
        return const.Notifications.FAILED_WORKFLOW.value.format(technical_id=technical_id)

    async def check_scheduled_entity_status(self, technical_id: str, entity: SchedulerEntity, **params) -> None:
        """
        Check the status of a scheduled entity and update its state.
        
        Args:
            technical_id: Technical identifier
            entity: Scheduler entity
            **params: Additional parameters (unused)
        """
        try:
            status, next_transition = await self.scheduler_service.run_for_entity(
                technical_id=technical_id, 
                entity=entity
            )
            
            if status:
                entity.status = status
            if next_transition:
                entity.triggered_entity_next_transition = next_transition

        except Exception as e:
            self.logger.exception(f"Error checking scheduled entity status: {e}")

    async def trigger_parent_entity(self, technical_id: str, entity: SchedulerEntity, **params) -> None:
        """
        Trigger a transition on the parent entity.
        
        Args:
            technical_id: Technical identifier
            entity: Scheduler entity
            **params: Additional parameters (unused)
        """
        try:
            await _launch_transition(
                entity_service=self.entity_service,
                technical_id=entity.triggered_entity_id,
                cyoda_auth_service=self.cyoda_auth_service,
                transition=entity.triggered_entity_next_transition
            )

        except Exception as e:
            self.logger.exception(f"Error triggering parent entity: {e}")

    async def get_entity_names_from_entities_requirement(self, technical_id: str, entity: AgenticFlowEntity, **params) -> list:
        """
        Parse entities requirement JSON file and extract entity names.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including input_file path

        Returns:
            List of entity names extracted from the JSON file
        """
        try:
            params = params.get('params', params)
            input_file = params.get('input_file', 'src/main/java/com/java_template/prototype/entities_requirement.json')

            # Get repository information from entity
            branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM)
            repository_name = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)

            # Construct full file path
            from common.config.config import config
            if branch_id and repository_name:
                full_path = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/{input_file}"
            else:
                # Fallback to just the input file path if entity doesn't have branch/repo info
                full_path = input_file

            # # Read and parse JSON file
            # if not os.path.exists(full_path):
            #     self.logger.warning(f"Entities requirement file not found: {full_path}")
            #     return []

            content = await read_file_util(
                filename=full_path,
                technical_id=branch_id,
                repository_name=repository_name
            )

            entities_data_json = json.loads(content)
            entities_data = entities_data_json.get('entities', [])


            # Extract entity names from the JSON structure
            entity_names = []
            if isinstance(entities_data, list):
                for item in entities_data:
                    if isinstance(item, dict):
                        # Each item should have one key which is the EntityName
                        for entity_name in item.keys():
                            entity_names.append(entity_name)

            self.logger.info(f"Extracted {len(entity_names)} entity names: {entity_names}")
            return entity_names

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing JSON file {params.get('input_file', 'entities_requirement.json')}: {e}"
            self.logger.error(error_msg)
            return []
        except Exception as e:
            self.logger.error(f"Error reading entities requirement file: {e}")
            return []


