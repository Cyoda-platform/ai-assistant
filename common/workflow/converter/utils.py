import json
import uuid
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from common.workflow.converter.constants import (
    OPERATION_MAPPING,
    VALID_VALUE_TYPES,
    FIELD_NAME_PREFIX,
    META_FIELD_TYPES,
    RAW_TYPES,
    VALUE_TYPE_TO_JAVA_TYPE,
)


def generate_id():
    return str(uuid.uuid1())


def current_timestamp():
    now = datetime.now(ZoneInfo("UTC"))
    return now.isoformat(timespec="milliseconds").replace("+0000", "+00:00")


def get_mapping(operator_type: str):
    normalized = operator_type.lower().strip()
    return OPERATION_MAPPING.get(normalized) or OPERATION_MAPPING.get(operator_type)


def resolve_field_if_needed(json_path: str, value_type: str) -> str:
    if json_path.startswith("$."):
        if value_type not in VALID_VALUE_TYPES:
            raise ValueError(f"Invalid value_type '{value_type}'. Must be one of: {', '.join(sorted(VALID_VALUE_TYPES))}")
        return f"{FIELD_NAME_PREFIX}{value_type}.[{json_path}]"
    return json_path


def map_value_type_to_java_type(value_type):
    return VALUE_TYPE_TO_JAVA_TYPE.get(value_type)


def build_between_value(field_name: str, value: Any, value_type: str):
    if value_type in RAW_TYPES:
        return value
    explicit_java_type = META_FIELD_TYPES.get(field_name)
    java_type = explicit_java_type or map_value_type_to_java_type(value_type)
    return {"@type": java_type, "value": value} if java_type else value


def convert_condition(condition: dict) -> dict:
    condition_type = condition.get("type")

    if condition_type == "group":
        return {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": condition.get("operator"),
            "conditions": [convert_condition(sub) for sub in condition.get("conditions", [])],
        }

    elif condition_type == "simple":
        operator_type = condition.get("operatorType", "")
        mapping = get_mapping(operator_type)

        if not mapping:
            raise ValueError(f"Unsupported operatorType: {operator_type}")

        json_path = resolve_field_if_needed(condition["jsonPath"], condition.get("value_type"))
        field_name = json_path
        value_type = condition.get("value_type")

        result = {
            "@bean": mapping["@bean"],
            "fieldName": field_name,
            "operation": mapping["operation"],
            "rangeField": "false",
        }

        if mapping["operation"] in {"BETWEEN", "BETWEEN_INCLUSIVE"}:
            if "value_from" not in condition or "value_to" not in condition:
                raise ValueError(f"'value_from' and 'value_to' must be present for operatorType '{operator_type}'")
            result["from"] = build_between_value(field_name, condition["value_from"], value_type)
            result["to"] = build_between_value(field_name, condition["value_to"], value_type)
        else:
            result["value"] = condition["value"]

        return result

    else:
        raise ValueError(f"Unknown condition type: {condition_type}")


def build_param(name, value_type, value, owner):
    return {
        "persisted": True,
        "owner": owner,
        "id": generate_id(),
        "name": name,
        "creationDate": current_timestamp(),
        "valueType": value_type,
        "value": {
            "@type": VALUE_TYPE_TO_JAVA_TYPE.get(value_type, "String"),
            "value": value,
        },
    }


def generate_ext_criteria_params(criteria: dict):
    return [
        build_param(
            "Tags for filtering calculation nodes (separated by ',' or ';')",
            "STRING",
            criteria["calculation_nodes_tags"],
            criteria["owner"],
        ),
        build_param(
            "Attach entity",
            "STRING",
            str(criteria["attach_entity"]).lower(),
            criteria["owner"],
        ),
        build_param(
            "Calculation response timeout (ms)",
            "INTEGER",
            criteria["calculation_response_timeout_ms"],
            criteria["owner"],
        ),
        build_param(
            "Retry policy",
            "STRING",
            criteria["retry_policy"],
            criteria["owner"],
        ),
        build_param(
            "Parameter 'context'",
            "STRING",
            json.dumps(criteria["config"]),
            criteria["owner"],
        ),
    ]


def generate_ext_criteria(criteria, criteria_id, criteria_params, class_name):
    return {
        "persisted": True,
        "owner": criteria["owner"],
        "id": criteria_id,
        "name": criteria["name"],
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": criteria["description"],
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [],
        },
        "aliasDefs": [],
        "parameters": criteria_params,
        "criteriaChecker": "ExternalizedCriteriaChecker",
        "user": "CYODA",
    }


def build_state(state_name, default_param_values, class_name, description=""):
    return {
        "persisted": True,
        "owner": default_param_values["owner"],
        "id": "noneState" if state_name.lower() == "none" else generate_id(),
        "name": state_name,
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": description,
    }


def save_new_state(state_name, state_map, default_param_values, class_name, state_data):
    if state_name not in state_map:
        state_map[state_name] = build_state(
            state_name,
            default_param_values,
            class_name,
            state_data.get("description", ""),
        )
    return state_map[state_name]


def add_none_state_if_not_exists(dto, default_param_values, class_name):
    if any(str(state["name"]).lower() == "none" for state in dto["states"]):
        return

    none_state = build_state("None", default_param_values, class_name, "Initial state of the workflow.")
    dto["states"].append(none_state)

    end_state_ids = {transition["endStateId"] for transition in dto["transitions"]}
    first_state_id = next(
        (t["startStateId"] for t in dto["transitions"] if t["startStateId"] not in end_state_ids), None
    )

    if first_state_id:
        new_transition = {
            "persisted": True,
            "owner": default_param_values["owner"],
            "id": generate_id(),
            "name": "initial_transition",
            "entityClassName": class_name,
            "creationDate": current_timestamp(),
            "description": "Initial transition from None state.",
            "startStateId": "noneState",
            "endStateId": first_state_id,
            "workflowId": dto["workflow"][0]["id"],
            "criteriaIds": [],
            "endProcessesIds": [],
            "active": True,
            "automated": True,
            "logActivity": False,
        }
        dto["transitions"].append(new_transition)
        dto["workflow"][0]["transitionIds"].append(new_transition["id"])
