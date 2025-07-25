import logging
from typing import Optional

import common.config.const as const
from common.config.config import config
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class BuildIdRetrievalService(BaseWorkflowService):
    """
    Service responsible for retrieving build IDs from deployment workflow entities.
    """

    async def get_build_id_from_context(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Get build ID from the current entity's parent deployment workflow context.

        This tool:
        1. Gets the current entity's parent ID
        2. Gets the parent entity (AgenticFlowEntity) by parent ID
        3. Gets all child entities from parent.child_entities list
        4. Filters for entities with workflow_name "deploy_cyoda_env"
        5. Gets the latest one by last_modified timestamp
        6. Returns the build_id from workflow_cache

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters (not used)

        Returns:
            Build ID string or "not found" message with warning logged
        """
        try:
            # Step 1: Get current entity parent ID
            parent_id = entity.parent_id
            if not parent_id:
                self.logger.warning("Current entity has no parent_id")
                return "Build ID not found - no parent entity"

            # Step 2: Get parent entity (AgenticFlowEntity) by parent ID
            try:
                parent_entity: AgenticFlowEntity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.AGENTIC_FLOW_ENTITY.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=parent_id
                )

                if not parent_entity:
                    self.logger.warning(f"Parent entity not found for parent_id: {parent_id}")
                    return "Build ID not found - parent entity not found"

            except Exception as e:
                self.logger.warning(f"Error retrieving parent entity {parent_id}: {e}")
                return "Build ID not found - error retrieving parent entity"

            # Step 3: Get all child entities from parent.child_entities list
            if not parent_entity.child_entities:
                self.logger.warning(f"No child entities found in parent entity {parent_id}")
                return "Build ID not found - no child entities found"

            try:
                child_entities = []
                for child_id in parent_entity.child_entities:
                    child_entity: AgenticFlowEntity = await self.entity_service.get_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.AGENTIC_FLOW_ENTITY.value,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=child_id
                    )
                    if child_entity:
                        child_entities.append(child_entity)

                if not child_entities:
                    self.logger.warning(f"No valid child entities found for parent_id: {parent_id}")
                    return "Build ID not found - no valid child entities found"

            except Exception as e:
                self.logger.warning(f"Error retrieving child entities for parent {parent_id}: {e}")
                return "Build ID not found - error retrieving child entities"

            # Step 4: Filter for entities with workflow_name "deploy_cyoda_env"
            deploy_entities: list[AgenticFlowEntity] = []
            for child_entity in child_entities:
                if child_entity.workflow_name == const.DeploymentFlow.DEPLOY_CYODA_ENV.value:
                    deploy_entities.append(child_entity)

            if not deploy_entities:
                self.logger.warning(f"No deploy_cyoda_env entities found among {len(child_entities)} child entities")
                return "Build ID not found - no deployment entities found"

            # Step 5: Get the latest one by last_modified timestamp
            latest_entity: AgenticFlowEntity = max(deploy_entities, key=lambda x: x.last_modified or 0)
            
            # Step 6: Return the build_id from workflow_cache
            if not latest_entity.workflow_cache:
                self.logger.warning(f"Latest deploy entity {latest_entity.technical_id} has no workflow_cache")
                return "Build ID not found - no workflow cache in deployment entity"

            build_id = latest_entity.workflow_cache.get('build_id')
            if not build_id:
                self.logger.warning(f"No build_id found in workflow_cache of entity {latest_entity.technical_id}")
                return "Build ID not found - no build_id in workflow cache"

            self.logger.info(f"Successfully retrieved build_id: {build_id}")
            return build_id
            
        except Exception as e:
            self.logger.exception(f"Unexpected error retrieving build ID: {e}")
            return f"Build ID not found - unexpected error: {str(e)}"
