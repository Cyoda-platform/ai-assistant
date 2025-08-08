"""
Generate Prototype Sketch Service

Service for generating prototype sketches by launching the functional requirements to prototype Java workflow.
"""

import common.config.const as const
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class GeneratePrototypeSketchService(BaseWorkflowService):
    """Service for generating prototype sketches"""

    async def generate_prototype_sketch_2269(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Generate a prototype sketch by launching the functional requirements to prototype Java workflow.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Additional parameters including user_request
            
        Returns:
            Success message with workflow information
        """
        try:

            # Prepare workflow cache with the user request and existing parameters
            workflow_cache = {
                **params,
                const.GIT_BRANCH_PARAM: entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
            }

            # Launch agentic workflow for functional requirements to prototype Java
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=const.ModelName.FUNCTIONAL_REQUIREMENTS_TO_PROTOTYPE_JAVA.value,
                workflow_cache=workflow_cache,
            )

            return (f"Prototype sketch generation workflow {child_technical_id} has been scheduled successfully. "
                   f"You'll be notified when the prototype is ready.")

        except Exception as e:
            return self._handle_error(entity, e, f"Error generating prototype sketch: {e}")
