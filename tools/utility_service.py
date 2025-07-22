import json
from typing import Any

import common.config.const as const
from common.config.config import config
from common.exception.exceptions import InvalidTokenException
from common.utils.chat_util_functions import _launch_transition
from common.utils.utils import send_get_request
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
            if 'cyoda_env_url' not in cache:
                user_id = entity.user_id
                is_guest = user_id.startswith('guest.')
                url: str
                deployed: bool = False

                if is_guest:
                    url = "please, log in to deploy"
                else:
                    url = f"https://client-{user_id.lower()}.{config.CLIENT_HOST}"
                    try:
                        await send_get_request(api_url=url, path='api/v1', token='')
                    except InvalidTokenException:
                        deployed = True
                    except Exception as e:
                        self.logger.exception(f"Error checking Cyoda environment status: {e}")

                cache['cyoda_env_url'] = url
                cache['cyoda_environment_status'] = 'deployed' if deployed else 'is not yet deployed'

            # Prepare the final result
            cache_json = json.dumps(cache)
            return f"Please use this information for your answer: {cache_json}"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting user info: {e}")

    async def init_chats(self, technical_id: str, entity: ChatEntity, **params) -> None:
        """
        Initialize chats. Currently a placeholder that does nothing in mock mode.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters (unused)
        """
        if config.MOCK_AI == "true":
            return
        # Implementation would go here for non-mock mode

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


