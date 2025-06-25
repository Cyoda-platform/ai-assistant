import logging

from common.workflow.converter.workflow_converter import convert_to_dto

logger = logging.getLogger(__name__)

class CyodaWorkflowConverterService:
    async def convert_workflow(self, workflow_contents, entity_name, entity_version, technical_id) -> dict:
        dto = convert_to_dto(
            input_workflow=workflow_contents,
            calculation_node_tags=technical_id,
            model_name=entity_name,
            model_version=int(entity_version),
            workflow_name= f"{entity_name}:{entity_version}:{technical_id}",
            ai=False)

        return dto

