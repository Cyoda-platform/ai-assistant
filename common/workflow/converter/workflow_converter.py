import json

from common.workflow.converter.dto_builder import convert_json_to_workflow_dto


def convert(input_file_path, output_file_path, calculation_node_tags, model_name, model_version, workflow_name, ai):
    """Reads JSON from a file, converts it to workflow_dto, and writes it to another file."""
    with open(input_file_path, "r", encoding="utf-8") as infile:
        input_json = json.load(infile)

    # Call the conversion method
    class_name = f"{model_name}.{model_version}"
    workflow_dto = convert_json_to_workflow_dto(input_json=input_json,
                                                class_name=class_name,
                                                calculation_nodes_tags=calculation_node_tags,
                                                model_name=model_name,
                                                model_version=model_version,
                                                workflow_name=workflow_name,
                                                ai=ai)

    with open(output_file_path, "w", encoding="utf-8") as outfile:
        json.dump(workflow_dto, outfile, indent=4, ensure_ascii=False)