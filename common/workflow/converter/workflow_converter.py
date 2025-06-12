from typing import Dict, Any

from common.workflow.converter.dto_builder import DTOBuilder


class WorkflowConverter:
    def __init__(
            self,
            model_name: str,
            model_version: int,
            workflow_name: str,
            calculation_node_tags: str,
            ai: bool = False
    ):
        """
        Coordinates the transformation of input JSON into Cyoda's FullWorkflowContainerDto.
        """
        self.model_name = model_name
        self.model_version = model_version
        self.workflow_name = workflow_name
        self.calculation_node_tags = calculation_node_tags
        self.ai = ai

    def build(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms the input JSON spec into a DTO dictionary for serialization.
        """
        builder = DTOBuilder(
            model_name=self.model_name,
            model_version=self.model_version,
            workflow_name=self.workflow_name,
            calculation_node_tags=self.calculation_node_tags,
            ai=self.ai
        )
        return builder.build(input_json)
