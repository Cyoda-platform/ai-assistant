import json
from pathlib import Path
from typing import Dict, Any

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "workflow_configs" / "agents" / "configs" / "canvas_assistant" / "schemas"

_SCHEMA_CACHE = {}


def load_schema(schema_name: str) -> Dict[str, Any]:
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]

    schema_path = SCHEMAS_DIR / f"{schema_name}.json"
    with open(schema_path, "r") as f:
        schema = json.load(f)
        _SCHEMA_CACHE[schema_name] = schema
        return schema


def get_response_format(response_type: str) -> Dict[str, Any]:
    schema_map = {
        "entity_json": ("entity_schema", "entity_config_schema", "Entity configuration schema"),
        "workflow_json": ("workflow_schema", "workflow_config_schema", "Workflow configuration schema"),
        "app_config_json": ("app_config_schema", "app_config_schema", "Application configuration schema"),
        "environment_json": ("environment_schema", "environment_config_schema", "Environment configuration schema"),
        "requirement_json": ("requirement_schema", "requirement_config_schema", "Requirement configuration schema")
    }

    if response_type not in schema_map:
        raise ValueError(f"Invalid response_type: {response_type}. Must be one of: {list(schema_map.keys())}")

    schema_file, schema_name, description = schema_map[response_type]
    schema = load_schema(schema_file)

    return {
        "name": schema_name,
        "description": description,
        "schema": schema
    }

