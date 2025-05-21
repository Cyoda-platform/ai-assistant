import json
import uuid
from typing import Any

import common.config.const as const
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from common.config.config import config


OPERATION_MAPPING = {
    "equals (disregard case)": {"operation": "IEQUALS", "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals"},
    "not equal (disregard case)": {"operation": "INOT_EQUAL", "@bean": "com.cyoda.core.conditions.nonqueryable.INotEquals"},
    "between (inclusive)": {"operation": "BETWEEN", "@bean": "com.cyoda.core.conditions.queryable.Between"},
    "contains": {"operation": "CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.IContains"},
    "starts with": {"operation": "ISTARTS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IStartsWith"},
    "ends with": {"operation": "IENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IEndsWith"},
    "does not contain": {"operation": "INOT_CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.INotContains"},
    "does not start with": {"operation": "INOT_STARTS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.INotStartsWith"},
    "does not end with": {"operation": "NOT_ENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEndsWith"},
    "matches other field (case insensitive)": {"operation": "INOT_ENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.INotEndsWith"},
    "equals": {"operation": "EQUALS", "@bean": "com.cyoda.core.conditions.queryable.Equals"},
    "not equal": {"operation": "NOT_EQUAL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEquals"},
    "less than": {"operation": "LESS_THAN", "@bean": "com.cyoda.core.conditions.queryable.LessThan"},
    "greater than": {"operation": "GREATER_THAN", "@bean": "com.cyoda.core.conditions.queryable.GreaterThan"},
    "less than or equal to": {"operation": "LESS_OR_EQUAL", "@bean": "com.cyoda.core.conditions.queryable.LessThanEquals"},
    "greater than or equal to": {"operation": "GREATER_OR_EQUAL", "@bean": "com.cyoda.core.conditions.queryable.GreaterThanEquals"},
    "between (inclusive, match case)": {"operation": "BETWEEN_INCLUSIVE", "@bean": "com.cyoda.core.conditions.queryable.BetweenInclusive"},
    "is null": {"operation": "IS_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.IsNull"},
    "is not null": {"operation": "NOT_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotNull"}
}

VALID_VALUE_TYPES = {
    "classes", "nulls", "localTimes", "timeuuids", "years", "longs", "yearMonths", "strings",
    "ints", "byteArrays", "booleans", "bigIntegers", "shorts", "typeReferences", "zonedDateTimes",
    "floats", "bigDecimals", "dates", "localDates", "locales", "doubles", "bytes", "localDateTimes",
    "chars", "uuids"
}

VALUE_TYPE_TO_JAVA_TYPE = {
    "strings": "String",
    "uuids": "java.util.UUID",
    "timeuuids": "com.datastax.oss.driver.api.core.uuid.Uuids",
    "dates": "java.util.Date",
    "localDates": "java.time.LocalDate",
    "localTimes": "java.time.LocalTime",
    "localDateTimes": "java.time.LocalDateTime",
    "zonedDateTimes": "java.time.ZonedDateTime",
    "yearMonths": "java.time.YearMonth",
    "years": "java.time.Year",
    "locales": "java.util.Locale",
    "chars": "char",
    "byteArrays": "byte[]",
    "classes": "java.lang.Class",
    "typeReferences": "java.lang.reflect.Type"
}

META_FIELD_TYPES = {
    "id": "UUID",
    "entityModelClassId": "UUID",
    "owner": "String",
    "state": "String",
    "entityModelName": "String",
    "previousTransition": "String",
    "creationDate": "java.util.Date",
    "lastUpdateTime": "java.util.Date",
    "entityModelVersion": None
}

RAW_TYPES = {
    "ints", "longs", "doubles", "floats", "booleans", "shorts", "bytes", "bigDecimals", "bigIntegers"
}

FIELD_NAME_PREFIX = (
    "members.[*]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps."
)

def generate_id():
    return str(uuid.uuid1())


def convert(input_file_path, output_file_path, calculation_node_tags, model_name, model_version, workflow_name, ai):
    """Reads JSON from a file, converts it to workflow_dto, and writes it to another file."""
    with open(input_file_path, "r", encoding="utf-8") as infile:
        input_json = json.load(infile)

    # Call the conversion method
    workflow_dto = convert_json_to_workflow_dto(input_json=input_json,
                                                class_name="com.cyoda.tdb.model.treenode.TreeNodeEntity",
                                                calculation_nodes_tags=calculation_node_tags,
                                                model_name=model_name,
                                                model_version=model_version,
                                                workflow_name=workflow_name,
                                                ai=ai)

    with open(output_file_path, "w", encoding="utf-8") as outfile:
        json.dump(workflow_dto, outfile, indent=4, ensure_ascii=False)


def convert_json_to_workflow_dto(input_json, class_name, calculation_nodes_tags, model_name, model_version,
                                 workflow_name, ai):
    default_param_values = {
        "owner": "CYODA",
        "user": "CYODA",
        "attach_entity": "true",
        "calculation_response_timeout_ms": "300000",
        "retry_policy": "FIXED",  # NONE
        "sync_process": "false",
        "new_transaction_for_async": "true",
        "none_transactional_for_async": "false",
        "default_condition_name": "default_condition_name"
    }
    fail_chat_criteria_id = generate_id()
    fail_chat_criteria = {
        "persisted": True,
        "owner": "CYODA",
        "id": fail_chat_criteria_id,
        "name": "has_failed",
        "entityClassName": "com.cyoda.tdb.model.treenode.TreeNodeEntity",
        "creationDate": "2025-05-02T15:17:30.992+02:00",
        "description": "",
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [
                {
                    "@bean": "com.cyoda.core.conditions.queryable.Equals",
                    "fieldName": "members.[0]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps.booleans.[$.failed]",
                    "operation": "EQUALS",
                    "rangeField": "false",
                    "value": True,
                    "queryable": True
                }
            ]
        },
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": "CYODA"
    }
    proceed_chat_criteria_id = generate_id()
    proceed_chat_criteria = {
        "persisted": True,
        "owner": "CYODA",
        "id": proceed_chat_criteria_id,
        "name": "has_succeeded",
        "entityClassName": "com.cyoda.tdb.model.treenode.TreeNodeEntity",
        "creationDate": "2025-05-02T15:17:30.992+02:00",
        "description": "",
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [
                {
                    "@bean": "com.cyoda.core.conditions.queryable.Equals",
                    "fieldName": "members.[0]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps.booleans.[$.failed]",
                    "operation": "EQUALS",
                    "rangeField": "false",
                    "value": False,
                    "queryable": True
                }
            ]
        },
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": "CYODA"
    }
    wrong_generated_content_criteria_id = generate_id()
    wrong_generated_content_criteria = {
        "persisted": True,
        "owner": "CYODA",
        "id": wrong_generated_content_criteria_id,
        "name": "wrong_generated_content",
        "entityClassName": "com.cyoda.tdb.model.treenode.TreeNodeEntity",
        "creationDate": "2025-05-02T15:17:30.992+02:00",
        "description": "",
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [
                {
                    "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                    "fieldName": "members.[0]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps.booleans.[$.error_code]",
                    "operation": "IEQUALS",
                    "rangeField": "false",
                    "value": "wrong_generated_content"
                }
            ]
        },
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": "CYODA"
    }
    error_codes_name_to_id = {const.AiErrorCodes.WRONG_GENERATED_CONTENT.value: wrong_generated_content_criteria_id}
    dto = {
        "@bean": "com.cyoda.core.model.stateMachine.dto.FullWorkflowContainerDto",
        "workflow": [],
        "transitions": [],
        "criterias": [fail_chat_criteria, proceed_chat_criteria, wrong_generated_content_criteria],
        "processes": [],
        "states": [],
        "processParams": []
    }

    # Map workflow
    workflow_id = generate_id()
    dto["workflow"].append({
        "persisted": True,
        "owner": default_param_values["owner"],
        "id": workflow_id,
        "name": f"{model_name}:{model_version}:{workflow_name}",
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": input_json.get("description", ""),
        "entityShortClassName": "TreeNodeEntity",
        "transitionIds": [],
        "criteriaIds": [],
        "stateIds": ["noneState"],
        "active": True,
        "useDecisionTree": False,
        "decisionTrees": [],
        "metaData": {"documentLink": ""}
    })

    # Process workflow's externalized_criteria - skip

    # Add workflow's condition_criteria based on model_name and model_version
    workflow_criteria_ids = []
    condition = {
        "@bean": "com.cyoda.core.conditions.GroupCondition",
        "operator": "AND",
        "conditions": [
            {
                "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                "fieldName": "entityModelName",
                "operation": "IEQUALS",
                "rangeField": "false",
                "value": model_name
            },
            {
                "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                "fieldName": "members.[0]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps.strings.[$.workflow_name]",
                "operation": "IEQUALS",
                "rangeField": "false",
                "value": workflow_name
            },
            {
                "@bean": "com.cyoda.core.conditions.queryable.Equals",
                "fieldName": "entityModelVersion",
                "operation": "EQUALS",
                "rangeField": "false",
                "value": model_version,
                "queryable": True
            }
        ]}

    criteria_id = generate_id()
    workflow_criteria_ids.append(criteria_id)
    dto["criterias"].append({
        "persisted": True,
        "owner": default_param_values["owner"],
        "id": criteria_id,
        "name": f"{model_name}:{model_version}:{workflow_name}",
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": "Workflow criteria",
        "condition": condition,
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": default_param_values["user"]
    })

    dto["workflow"][0]["criteriaIds"].extend(workflow_criteria_ids)

    # Process states
    state_map = {}
    state_name_to_id = {}
    transitions = []

    for state_name, state_data in input_json["states"].items():
        start_state = save_new_state(state_name, state_map, default_param_values, class_name, state_data)
        state_name_to_id[state_name] = start_state
        if ai:
            state_data["transitions"][const.TransitionKey.MANUAL_RETRY.value] = {
                "next": state_name,
                "manual": True
            }
            state_data["transitions"][const.TransitionKey.FAIL.value] = {
                "next": f"{const.TransitionKey.LOCKED_CHAT.value}_{state_name}",
                "action": {
                    "name": "process_event",
                    "config": {
                        "type": "function",
                        "function": {
                            "name": "fail_workflow",
                            "description": "Clones template repository"
                        },
                        "publish": True
                    }
                }
            }

        # Process transitions
        def add_transition(transition_name, transition_data, transition_start_state=None, transition_criteria_id=None):
            transition_id = generate_id()
            dto["workflow"][0]["transitionIds"].append(transition_id)
            if transition_criteria_id:
                criteria_ids = [transition_criteria_id]
            else:
                if transition_name != const.TransitionKey.FAIL.value:
                    # if active
                    if not transition_data.get("manual", False):
                        criteria_ids = [proceed_chat_criteria_id]
                    else:
                        criteria_ids = []
                else:
                    criteria_ids = [fail_chat_criteria_id]
            process_ids = []
            end_state_name = transition_data["next"]
            end_state = save_new_state(end_state_name, state_map, default_param_values, class_name, state_data)
            state_name_to_id[end_state_name] = end_state
            transitions.append({
                "persisted": True,
                "owner": default_param_values["owner"],
                "id": transition_id,
                "name": transition_name,
                "entityClassName": class_name,
                "creationDate": current_timestamp(),
                "description": transition_data.get("description", ""),
                "startStateId": transition_start_state["id"] if transition_start_state else start_state["id"],
                "endStateId": end_state["id"],
                "workflowId": workflow_id,
                "criteriaIds": criteria_ids,
                "endProcessesIds": process_ids,
                "active": True,
                "automated": not transition_data.get("manual", False),
                "logActivity": False
            })

            # Process externalized processor
            if "action" in transition_data:
                process_id = generate_id()
                process_params = []
                process_criteria_ids = []
                process_ids.append(
                    {
                        "persisted": True,
                        "persistedId": process_id,
                        "runtimeId": 0
                    }
                )

                # Process externalized_processor's dto
                action = transition_data.get("action", {})
                config = action.get("config", {}) or {}

                dto["processes"].append({
                    "persisted": True,
                    "owner": default_param_values["owner"],
                    "id": {
                        "@bean": "com.cyoda.core.model.stateMachine.dto.ProcessIdDto",
                        "persisted": True,
                        "persistedId": process_id,
                        "runtimeId": 0
                    },
                    "name": action.get("name"),
                    "entityClassName": class_name,
                    "creationDate": current_timestamp(),
                    "description": config.get("description", ""),
                    "processorClassName": "net.cyoda.saas.externalize.processor.ExternalizedProcessor",
                    "parameters": process_params,
                    "fields": [],
                    "syncProcess": config.get("sync_process", default_param_values["sync_process"]),
                    "newTransactionForAsync": config.get(
                        "new_transaction_for_async",
                        default_param_values["new_transaction_for_async"]),
                    "noneTransactionalForAsync": config.get(
                        "none_transactional_for_async",
                        default_param_values["none_transactional_for_async"]),
                    "isTemplate": False,
                    "criteriaIds": process_criteria_ids,
                    "user": default_param_values["user"]
                })

                process_params.extend([
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Tags for filtering calculation nodes (separated by ',' or ';')",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value": {
                            "@type": "String",
                            "value": config.get(
                                "calculation_nodes_tags",
                                calculation_nodes_tags)
                        }
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Attach entity",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value": {
                            "@type": "String",
                            "value": str(
                                config.get("attach_entity",
                                default_param_values["attach_entity"])).lower()
                        }
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Calculation response timeout (ms)",
                        "creationDate": current_timestamp(),
                        "valueType": "INTEGER",
                        "value": {
                            "@type": "String", "value": str(
                                config.get("calculation_response_timeout_ms",
                                default_param_values["calculation_response_timeout_ms"]))}
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Retry policy",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value": {
                            "@type": "String",
                            "value": config.get(
                                "retry_policy",
                                default_param_values["retry_policy"])}
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Parameter 'context'",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value":
                            {"@type": "String", "value": json.dumps(config)}
                    }
                ])

                dto["processParams"].extend(process_params)

                # Process externalized_processor's externalized_criteria - skip

            # Process transition's externalized_criteria
            if "condition" in transition_data:
                condition = transition_data.get("condition", {})
                config = condition.get("config", {}) or {}
                function = config.get("function", {}) or {}
                criteria = {
                    "owner": default_param_values["owner"],
                    "calculation_nodes_tags": config.get(
                        "calculation_nodes_tags",
                        calculation_nodes_tags),
                    "attach_entity": str(config.get(
                        "attach_entity",
                        default_param_values["attach_entity"])).lower(),
                    "calculation_response_timeout_ms": str(config.get(
                            "calculation_response_timeout_ms",
                            default_param_values["calculation_response_timeout_ms"])),
                    "retry_policy": config.get(
                        "retry_policy",
                        default_param_values["retry_policy"]),
                    "name": function.get("name") or condition.get("name", default_param_values["default_condition_name"]),
                    "description": function.get("description") or condition.get("description", ""),
                    "config": config,
                    "user": default_param_values["user"]
                }

                criteria_id = generate_id()
                criteria_ids.append(criteria_id)
                criteria_params = generate_ext_criteria_params(criteria)
                dto["processParams"].extend(criteria_params)
                criteria_dto = generate_ext_criteria(criteria, criteria_id, criteria_params, class_name)
                dto["criterias"].append(criteria_dto)

            # Process transition's condition_criteria
            if "condition_criteria" in transition_data:
                condition_criteria = transition_data.get("condition_criteria", {})
                params = condition_criteria.get("params", {}) or {}

                cond_crit_id = generate_id()
                criteria_ids.append(cond_crit_id)

                converted_condition = convert_condition(params)

                condition_criteria_dto = {
                    "persisted": True,
                    "owner": default_param_values["owner"],
                    "id": cond_crit_id,
                    "name": condition_criteria["name"],
                    "entityClassName": class_name,
                    "creationDate": current_timestamp(),
                    "description": condition_criteria.get("description", ""),
                    "condition": converted_condition,
                    "aliasDefs": [],
                    "parameters": [],
                    "criteriaChecker": "ConditionCriteriaChecker",
                    "user": default_param_values["user"]
                }

                dto["criterias"].append(condition_criteria_dto)

        for transition_name, transition_data in state_data["transitions"].items():
            add_transition(transition_name=transition_name, transition_data=transition_data)
        if state_data.get("error_codes", []):
            for state in state_data["error_codes"]:
                transition_name = const.TransitionKey.ROLLBACK.value
                transition_data = {
                    "next": state["next_state"],  # f"{LOCKED_CHAT}_{state_name}",
                    "manual": True, #always manual to prevent loops
                    "action": {
                        "name": "process_event",
                        "config": {
                            "type": "function",
                            "function": {
                                "name": "reset_failed_entity",
                                "description": "reset failed entity state"
                            },
                            "publish": True
                        }
                    }
                }
                add_transition(transition_name=transition_name, transition_data=transition_data,
                               transition_start_state=state_name_to_id.get(f"{const.TransitionKey.LOCKED_CHAT.value}_{state_name}"),
                               transition_criteria_id=error_codes_name_to_id.get(state["error_code"]))

    dto["states"].extend(state_map.values())
    dto["transitions"].extend(transitions)

    add_none_state_if_not_exists(dto, default_param_values, class_name)
    return dto

def convert_condition(condition):
    if condition.get("type") == "group":
        return {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": condition.get("operator"),
            "conditions": [convert_condition(sub) for sub in condition.get("conditions", [])]
        }

    elif condition.get("type") == "simple":
        operator_type = condition.get("operatorType", "").strip()
        mapping = OPERATION_MAPPING.get(operator_type.lower()) or OPERATION_MAPPING.get(operator_type)

        if not mapping:
            raise ValueError(f"Unsupported operatorType: {operator_type}")

        json_path = condition["jsonPath"]
        value_type = condition.get("value_type")

        if json_path.startswith("$."):
            json_path = resolve_field_name(json_path, value_type)

        field_name = json_path  # after resolve, use this for META_FIELD_TYPES and final output

        result = {
            "@bean": mapping["@bean"],
            "fieldName": field_name,
            "operation": mapping["operation"],
            "rangeField": "false"
        }

        if mapping["operation"] in {"BETWEEN", "BETWEEN_INCLUSIVE"}:
            if "value_from" not in condition or "value_to" not in condition:
                raise ValueError(f"'value_from' and 'value_to' must be present for operatorType '{operator_type}'")

            result["from"] = build_between_value(field_name, condition["value_from"], value_type)
            result["to"] = build_between_value(field_name, condition["value_to"], value_type)
        else:
            result["value"] = condition["value"]

        # if ".queryable." in mapping["@bean"]:
        #     result["queryable"] = True

        return result

    else:
        raise ValueError(f"Unknown condition type: {condition.get('type')}")

def map_value_type_to_java_type(value_type):
    VALUE_TYPE_TO_JAVA_TYPE = {
        "uuids": "UUID",
        "strings": "String",
        "dates": "java.util.Date"
    }
    return VALUE_TYPE_TO_JAVA_TYPE.get(value_type)

def build_between_value(field_name: str, value: Any, value_type: str):
    if value_type in RAW_TYPES:
        return value

    explicit_java_type = META_FIELD_TYPES.get(field_name)
    java_type = explicit_java_type or map_value_type_to_java_type(value_type)

    if java_type:
        return {
            "@type": java_type,
            "value": value
        }

    return value  # fallback if no mapping

def resolve_field_name(json_path: str, value_type: str) -> str:
    """
    - if jsonPath starts with '$.', adds prefix + value_type (value_type must be present and valid);
    """
    if value_type not in VALID_VALUE_TYPES:
        raise ValueError(f"Invalid value_type '{value_type}'. Must be one of: {', '.join(sorted(VALID_VALUE_TYPES))}")
    return f"{FIELD_NAME_PREFIX}{value_type}.[{json_path}]"

def build_between_value(field_name: str, value: Any, which: str):
    java_type = META_FIELD_TYPES.get(field_name)
    if java_type:
        return {"@type": java_type, "value": value}
    return value

def save_new_state(state_name, state_map, default_param_values, class_name, state_data):
    if state_name in state_map:
        return state_map[state_name]
    else:
        new_state = {
            "persisted": True,
            "owner": default_param_values["owner"],
            "id": "noneState" if state_name == "none" else generate_id(),
            "name": state_name,
            "entityClassName": class_name,
            "creationDate": current_timestamp(),
            "description": state_data.get("description", "")
        }
        state_map[state_name] = new_state
    return new_state


def add_none_state_if_not_exists(dto, default_param_values, class_name):
    # State "None" is mandatory for the workflow. It is added, if missing in the DTO.
    none_state_exists = any(str(state["name"]).lower() == "none" for state in dto["states"])

    if not none_state_exists:
        none_state = {
            "persisted": True,
            "owner": default_param_values["owner"],
            "id": "noneState",
            "name": "None",
            "entityClassName": class_name,
            "creationDate": current_timestamp(),
            "description": "Initial state of the workflow."
        }
        dto["states"].append(none_state)

        # Find the current first state
        end_state_ids = {transition["endStateId"] for transition in dto["transitions"]}
        first_state_id = None
        for transition in dto["transitions"]:
            if transition["startStateId"] not in end_state_ids:
                first_state_id = transition["startStateId"]
                break
        if first_state_id:
            # Add new transition connecting noneState with current first state
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
                "logActivity": False
            }
            dto["transitions"].append(new_transition)
            dto["workflow"][0]["transitionIds"].append(new_transition["id"])


def current_timestamp():
    now = datetime.now(ZoneInfo("UTC"))
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]


def generate_ext_criteria_params(criteria):
    criteria_params = [
        {
            "persisted": True,
            "owner": criteria["owner"],
            "id": generate_id(),
            "name": "Tags for filtering calculation nodes (separated by ',' or ';')",
            "creationDate": current_timestamp(),
            "valueType": "STRING",
            "value": {
                "@type": "String",
                "value": criteria["calculation_nodes_tags"]
            }
        },
        {
            "persisted": True,
            "owner": criteria["owner"],
            "id": generate_id(),
            "name": "Attach entity",
            "creationDate": current_timestamp(),
            "valueType": "STRING",
            "value": {
                "@type": "String",
                "value": str(criteria["attach_entity"]).lower()
            }
        },
        {
            "persisted": True,
            "owner": criteria["owner"],
            "id": generate_id(),
            "name": "Calculation response timeout (ms)",
            "creationDate": current_timestamp(),
            "valueType": "INTEGER",
            "value": {"@type": "String", "value": criteria["calculation_response_timeout_ms"]}
        },
        {
            "persisted": True,
            "owner": criteria["owner"],
            "id": generate_id(),
            "name": "Retry policy",
            "creationDate": current_timestamp(),
            "valueType": "STRING",
            "value": {"@type": "String", "value": criteria["retry_policy"]}
        },
        {
            "persisted": True,
            "owner": criteria["owner"],
            "id": generate_id(),
            "name": "Parameter 'context'",
            "creationDate": "2025-04-07T20:57:40.935+00:00",
            "valueType": "STRING",
            "value": {
                "@type": "String",
                "value": json.dumps(criteria["config"])
            }
        }
    ]
    return criteria_params


def generate_ext_criteria(criteria, criteria_id, criteria_params, class_name):
    criteria_dto = {
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
            "conditions": []
        },
        "aliasDefs": [],
        "parameters": criteria_params,
        "criteriaChecker": "ExternalizedCriteriaChecker",
        "user": "CYODA"
    }
    return criteria_dto


if __name__ == "__main__":

    CONFIG_DIR = Path("config")
    OUTPUT_ROOT = Path("outputs")
    CALCULATION_NODE_TAGS = "ai_assistant"

    for file_path in CONFIG_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        # model_name is the name of the folder directly under config/
        # e.g. config/scheduler/foo.json -> scheduler
        try:
            # file_path.relative_to(CONFIG_DIR) == scheduler/foo.json
            model_name = file_path.relative_to(CONFIG_DIR).parts[-2]
        except IndexError:
            # fallback, though .rglob under CONFIG_DIR always has at least one part
            model_name = file_path.parent.name

        input_file = str(file_path)

        # Build the output path under outputs/ preserving subdirs
        output_file = OUTPUT_ROOT / file_path
        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        workflow_name = file_path.relative_to(CONFIG_DIR).parts[-1].split(".")[0]
        # Set the AI flag
        ai = True
        # Call your conversion
        convert(input_file_path=input_file, output_file_path=str(output_file),
                calculation_node_tags=config.GRPC_PROCESSOR_TAG, model_name=model_name,
                model_version=int(config.ENTITY_VERSION), workflow_name=workflow_name, ai=ai)

        print(f"Conversion completed. Result saved to {output_file}")
