import json

from common.workflow.converter_v2.dto_builder import convert_json_to_workflow_dto


def convert(input_file_path, output_file_path, calculation_node_tags, model_name, model_version, workflow_name, ai):
    """Reads JSON from a file, converts it to workflow_dto, and writes it to another file."""
    with open(input_file_path, "r", encoding="utf-8") as infile:
        input_workflow = json.load(infile)

    # Call the conversion method
    workflow_dto = _convert_workflow(ai=ai,
                                     calculation_node_tags=calculation_node_tags,
                                     input_workflow=input_workflow,
                                     model_name=model_name,
                                     model_version=model_version,
                                     workflow_name=workflow_name)
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        json.dump(workflow_dto, outfile, indent=4, ensure_ascii=False)


def convert_to_dto(input_workflow, calculation_node_tags, model_name, model_version, workflow_name, ai):
    workflow_dto = _convert_workflow(ai=ai,
                                     calculation_node_tags=calculation_node_tags,
                                     input_workflow=input_workflow,
                                     model_name=model_name,
                                     model_version=model_version,
                                     workflow_name=workflow_name)
    return workflow_dto


def _convert_workflow(ai, calculation_node_tags, input_workflow, model_name, model_version, workflow_name):
    class_name = f"{model_name}.{model_version}"
    workflow_dto = convert_json_to_workflow_dto(input_json=input_workflow,
                                                class_name=class_name,
                                                calculation_nodes_tags=calculation_node_tags,
                                                model_name=model_name,
                                                model_version=model_version,
                                                workflow_name=workflow_name,
                                                ai=ai)
    return workflow_dto
