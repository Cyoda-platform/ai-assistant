import json
from typing import Any

import common.config.const as const
from common.config.config import config
from common.utils.utils import send_cyoda_request, get_repository_name
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class DeploymentService(BaseWorkflowService):
    """
    Service responsible for all deployment-related operations including
    environment deployment, application deployment, and build scheduling.
    """

    async def schedule_deploy_env(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Schedule environment deployment.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters
            
        Returns:
            Success message with deployment information
        """
        return await self._schedule_deploy(
            technical_id=technical_id,
            entity=entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
        )

    async def schedule_build_user_application(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Schedule user application build.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters
            
        Returns:
            Success message with build information
        """
        repository_name = get_repository_name(entity)
        repository_url = f"{config.REPOSITORY_URL.format(repository_name=repository_name)}.git"
        extra_payload = {
            "repository_url": repository_url,
            "branch": entity.workflow_cache.get(const.GIT_BRANCH_PARAM),
            "is_public": "true"
        }
        return await self._schedule_deploy(
            technical_id,
            entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_USER_APP_BUILD,
            extra_payload=extra_payload
        )

    async def schedule_deploy_user_application(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Schedule user application deployment.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters
            
        Returns:
            Success message with deployment information
        """
        repository_name = get_repository_name(entity)
        repository_url = f"{config.REPOSITORY_URL.format(repository_name=repository_name)}.git"
        extra_payload = {
            "repository_url": repository_url,
            "branch": entity.workflow_cache.get(const.GIT_BRANCH_PARAM),
            "is_public": "true"
        }
        return await self._schedule_deploy(
            technical_id,
            entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY,
            extra_payload=extra_payload
        )

    async def deploy_cyoda_env(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Deploy Cyoda environment.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition

        Returns:
            Success message or error for guest users
        """
        return await self._deploy_cyoda_env_common(
            technical_id=technical_id,
            entity=entity,
            workflow_name=const.DeploymentFlow.DEPLOY_CYODA_ENV.value,
            **params
        )

    async def deploy_cyoda_env_background(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Deploy Cyoda environment in background.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including transition

        Returns:
            Success message or error for guest users
        """
        return await self._deploy_cyoda_env_common(
            technical_id=technical_id,
            entity=entity,
            workflow_name=const.DeploymentFlow.DEPLOY_CYODA_ENV_BACKGROUND.value,
            **params
        )

    async def deploy_user_application(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Deploy user application.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters
            
        Returns:
            Success message or error for guest users
        """
        if entity.user_id.startswith('guest'):
            return "Sorry, deploying client application is available only to logged in users. Please sign up or login!"

        # Set user environment name
        params['user_env_name'] = f"client-{entity.user_id.lower()}.{config.CLIENT_HOST}"

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.DeploymentFlow.DEPLOY_USER_APPLICATION.value,
            params=params,
        )

    async def get_env_deploy_status(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> str:
        """
        Get the deployment status for a specific build.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including build_id
            
        Returns:
            Deployment status information
            
        Raises:
            ValueError: If build_id is missing
        """
        build_id = params.get("build_id")
        if not build_id:
            raise ValueError("Missing build_id in params")
            
        status_url = f"{config.DEPLOY_CYODA_ENV_STATUS}?build_id={build_id}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self.cyoda_auth_service,
            method="get",
            base_url=status_url,
            path=''
        )
        
        deploy_state = resp.get("json", {}).get("state")
        deploy_status = resp.get("json", {}).get("status")
        return f"Current deploy state {deploy_state}. Current deploy status {deploy_status}"

    async def _schedule_deploy(self, technical_id: str, entity: ChatEntity, 
                              scheduled_action: config.ScheduledAction, 
                              extra_payload: dict = None) -> str:
        """
        Internal method to schedule deployment operations.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            scheduled_action: Type of scheduled action
            extra_payload: Additional payload data
            
        Returns:
            Success message with deployment information
            
        Raises:
            ValueError: If unsupported action or missing build information
        """
        try:
            base_url = config.ACTION_URL_MAP[scheduled_action]
        except KeyError:
            raise ValueError(f"Unsupported scheduled action: {scheduled_action}")

        # Prepare request payload
        payload = {
            "chat_id": str(technical_id),
            "user_name": str(entity.user_id)
        }
        if extra_payload:
            payload.update(extra_payload)

        data = json.dumps(payload)
        
        # Send the deployment request
        resp = await send_cyoda_request(
            cyoda_auth_service=self.cyoda_auth_service,
            method="post",
            base_url=base_url,
            path='',
            data=data
        )

        # Validate response
        build_info = resp.get('json', {})
        build_id = build_info['build_id']
        build_namespace = build_info['build_namespace']
        entity.workflow_cache['build_namespace'] = build_namespace
        entity.workflow_cache['build_id'] = build_id
        
        if not build_id or not build_namespace:
            raise ValueError("Build information missing from the response")

        # Schedule the workflow
        scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
            awaited_entity_ids=[build_id],
            triggered_entity_id=technical_id,
            scheduled_action=scheduled_action
        )

        entity.scheduled_entities.append(scheduled_entity_id)

        return (f"Successfully scheduled {scheduled_action.value.replace('_', ' ')} with build ID {build_id}. "
                f"Your environment will be available at: https://{build_namespace}.{config.CLIENT_HOST}. "
                f"You will be notified once your environment is ready. You can check the status of the "
                f"deployment by asking 'check deploy status for build ID {build_id}'."
                f"Currently redeploying the environment will reset all the data. You'll need to re-upload "
                f"your workflows and add a new M2M user to access it (prompt: `add new machine user`). Sorry for the inconvenience. We are working on it.")

    async def _deploy_cyoda_env_common(self, technical_id: str, entity: AgenticFlowEntity,
                                      workflow_name: str, **params) -> str:
        """
        Common logic for deploying Cyoda environment.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            workflow_name: Name of the workflow to execute
            **params: Parameters including transition

        Returns:
            Success message or error for guest users
        """
        if entity.user_id.startswith('guest'):
            return "Sorry, deploying Cyoda env is available only to logged in users. Please sign up or login!"

        # Set client host parameter
        params['client_host'] = f"{config.CLIENT_HOST}"

        if params.get("transition"):
            # Note: This would need to be handled by the main workflow
            # or we need to inject the state management service
            pass

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
        )

    async def _schedule_workflow(self, technical_id: str, entity: AgenticFlowEntity,
                                entity_model: str, workflow_name: str, params: dict) -> str:
        """
        Internal method to schedule workflow operations.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            entity_model: Entity model name
            workflow_name: Workflow name
            params: Parameters for the workflow
            
        Returns:
            Success message with workflow information
        """
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=entity_model,
            workflow_name=workflow_name,
            workflow_cache=params,
            edge_messages_store={},
        )

        return (f"Successfully scheduled workflow to implement the task. I'll be right back with a new "
                f"dialogue plan. Please don't ask anything just yet i'm back.{child_technical_id}")
