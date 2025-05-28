import json
import logging
import os
from pathlib import Path

from common.workflow.converter_v1.util.workflow_enricher import enrich_workflow
from common.workflow.converter_v1.util.workflow_to_dto_converter import parse_ai_workflow_to_dto

logger = logging.getLogger(__name__)

entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'

API_V_WORKFLOWS_ = "api/v1/workflows"

class CyodaWorkflowConverterService:
    def convert_workflow(self, workflow_contents, entity_name, entity_version, technical_id):
        workflow_contents = enrich_workflow(workflow_contents)
        workflow_contents['name'] = f"{workflow_contents['name']}:ENTITY_MODEL_VAR:ENTITY_VERSION_VAR:CHAT_ID_VAR"
        workflow_contents = json.dumps(workflow_contents)
        workflow_contents = workflow_contents.replace("ENTITY_VERSION_VAR", entity_version)
        workflow_contents = workflow_contents.replace("ENTITY_MODEL_VAR", entity_name)
        workflow_contents = workflow_contents.replace("CHAT_ID_VAR", technical_id)
        dto = parse_ai_workflow_to_dto(input_workflow=json.loads(workflow_contents), class_name="com.cyoda.tdb.model.treenode.TreeNodeEntity")
        return dto

