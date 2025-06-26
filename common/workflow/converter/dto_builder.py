import json

from common.config import const
from common.workflow.converter.constants import DEFAULT_PARAM_VALUES
from common.workflow.converter.utils import (
    generate_id, current_timestamp, add_none_state_if_not_exists,
    generate_ext_criteria, generate_ext_criteria_params,
    convert_condition, save_new_state
)


def _build_simple_condition_criteria(criterion_id, name, class_name, field_name, value, bean, queryable=True):
    return {
        "persisted": True,
        "owner": "CYODA",
        "id": criterion_id,
        "name": name,
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": "",
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [
                {
                    "@bean": bean,
                    "fieldName": field_name,
                    "operation": "EQUALS" if bean.endswith("Equals") else "IEQUALS",
                    "rangeField": "false",
                    "value": value,
                    **({"queryable": True} if queryable else {})
                }
            ]
        },
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": "CYODA"
    }


def convert_json_to_workflow_dto(input_json, class_name, calculation_nodes_tags, model_name, model_version,
                                 workflow_name, ai):
    # Create common criteria
    fail_crit_id = generate_id()
    succeed_crit_id = generate_id()
    wrong_gen_crit_id = generate_id()

    fail_crit = _build_simple_condition_criteria(fail_crit_id, "has_failed", class_name, "failed", True,
                                                 "com.cyoda.core.conditions.queryable.Equals")
    succeed_crit = _build_simple_condition_criteria(succeed_crit_id, "has_succeeded", class_name, "failed", False,
                                                    "com.cyoda.core.conditions.queryable.Equals")
    wrong_gen_crit = _build_simple_condition_criteria(wrong_gen_crit_id, "wrong_generated_content", class_name,
                                                      "error_code", "wrong_generated_content",
                                                      "com.cyoda.core.conditions.nonqueryable.IEquals", queryable=False)

    dto = {
        "@bean": "com.cyoda.core.model.stateMachine.dto.FullWorkflowContainerDto",
        "workflow": [],
        "transitions": [],
        "criterias": [fail_crit, succeed_crit, wrong_gen_crit] if ai else [],
        "processes": [],
        "states": [],
        "processParams": []
    }

    workflow_id = generate_id()
    dto["workflow"].append({
        "persisted": True,
        "owner": DEFAULT_PARAM_VALUES["owner"],
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

    workflow_criteria_id = generate_id()
    dto["criterias"].append({
        "persisted": True,
        "owner": DEFAULT_PARAM_VALUES["owner"],
        "id": workflow_criteria_id,
        "name": f"{model_name}:{model_version}:{workflow_name}",
        "entityClassName": class_name,
        "creationDate": current_timestamp(),
        "description": "Workflow criteria",
        "condition": {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [
                {
                    "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                    "fieldName": "workflow_name",
                    "operation": "IEQUALS",
                    "rangeField": "false",
                    "value": workflow_name
                }
            ] if ai else []
        },
        "aliasDefs": [],
        "parameters": [],
        "criteriaChecker": "ConditionCriteriaChecker",
        "user": DEFAULT_PARAM_VALUES["user"]
    })
    dto["workflow"][0]["criteriaIds"].append(workflow_criteria_id)

    error_codes_name_to_id = {
        const.AiErrorCodes.WRONG_GENERATED_CONTENT.value: wrong_gen_crit_id
    }

    state_map = {}
    state_name_to_id = {}
    transitions = []

    def _extract_processor(process_ids, transition_data):
        action = transition_data.get("action", {})
        process_id = generate_id()
        process_params = []
        process_criteria_ids = []
        process_ids.append({"persisted": True, "persistedId": process_id, "runtimeId": 0})

        if action.get("type") == "scheduled":
            dto["processes"].append({
                "persisted": True,
                "owner": DEFAULT_PARAM_VALUES["owner"],
                "id": {"@bean": "com.cyoda.core.model.stateMachine.dto.ProcessIdDto",
                       "persisted": True, "persistedId": process_id, "runtimeId": 0},
                "name": action.get("name"),
                "entityClassName": class_name,
                "creationDate": current_timestamp(),
                "description":  "",
                "processorClassName": "com.cyoda.plugins.statemachine.scheduler.ScheduleTransitionProcessor",
                "parameters": process_params,
                "fields": [],
                "syncProcess": DEFAULT_PARAM_VALUES["sync_process"],
                "newTransactionForAsync": DEFAULT_PARAM_VALUES["new_transaction_for_async"],
                "noneTransactionalForAsync": DEFAULT_PARAM_VALUES["none_transactional_for_async"],
                "isTemplate": False,
                "criteriaIds": process_criteria_ids,
                "user": DEFAULT_PARAM_VALUES["user"]
            })
            for key, name, vtype in [
                ("delay", "Delay (ms)", "INTEGER"),
                ("timeout", "Timeout (ms)", "INTEGER"),
                ("next_transition", "Transition name", "STRING")
            ]:
                process_params.append({
                    "persisted": True,
                    "owner": DEFAULT_PARAM_VALUES["owner"],
                    "id": generate_id(),
                    "name": name,
                    "creationDate": current_timestamp(),
                    "valueType": vtype,
                    "value": {"@type": "String", "value": action["parameters"].get(key)}
                })
            dto["processParams"].extend(process_params)
        else:
            _extract_processor_condition(action, process_criteria_ids, process_id, process_params)


    def _extract_processor_condition(action, process_criteria_ids, process_id, process_params):
        config_data = action.get("config", {})
        if calculation_nodes_tags:
            config_data["calculation_nodes_tags"] = calculation_nodes_tags
        dto["processes"].append({
            "persisted": True,
            "owner": DEFAULT_PARAM_VALUES["owner"],
            "id": {"@bean": "com.cyoda.core.model.stateMachine.dto.ProcessIdDto",
                   "persisted": True, "persistedId": process_id, "runtimeId": 0},
            "name": action.get("name"),
            "entityClassName": class_name,
            "creationDate": current_timestamp(),
            "description": action.get("description", ""),
            "processorClassName": "net.cyoda.saas.externalize.processor.ExternalizedProcessor",
            "parameters": process_params,
            "fields": [],
            "syncProcess": action.get("sync_process", DEFAULT_PARAM_VALUES["sync_process"]),
            "newTransactionForAsync": action.get("new_transaction_for_async",
                                                      DEFAULT_PARAM_VALUES["new_transaction_for_async"]),
            "noneTransactionalForAsync": action.get("none_transactional_for_async",
                                                         DEFAULT_PARAM_VALUES["none_transactional_for_async"]),
            "isTemplate": False,
            "criteriaIds": process_criteria_ids,
            "user": DEFAULT_PARAM_VALUES["user"]
        })
        # Add externalized params
        for name, key, vtype in [
            ("Tags for filtering calculation nodes (separated by ',' or ';')", "calculation_nodes_tags", "STRING"),
            ("Attach entity", "attach_entity", "STRING"),
            ("Calculation response timeout (ms)", "calculation_response_timeout_ms", "INTEGER"),
            ("Retry policy", "retry_policy", "STRING")
        ]:
            process_params.append({
                "persisted": True,
                "owner": DEFAULT_PARAM_VALUES["owner"],
                "id": generate_id(),
                "name": name,
                "creationDate": current_timestamp(),
                "valueType": vtype,
                "value": {"@type": "String", "value": str(config_data.get(key, DEFAULT_PARAM_VALUES.get(key, '')))}
            })
        if config_data:
            process_params.append({
                "persisted": True,
                "owner": DEFAULT_PARAM_VALUES["owner"],
                "id": generate_id(),
                "name": "Parameter 'context'",
                "creationDate": current_timestamp(),
                "valueType": "STRING",
                "value": {"@type": "String", "value": json.dumps(config_data)}
            })
        dto["processParams"].extend(process_params)

    def _add_transition(transition_name, transition_data, start_state, transition_start_state=None,
                        transition_criteria_id=None):
        transition_id = generate_id()
        criteria_ids = [transition_criteria_id] if transition_criteria_id else []
        if not criteria_ids and ai:
            if transition_name == const.TransitionKey.FAIL.value:
                criteria_ids.append(fail_crit_id)
            elif not transition_data.get("manual", False):
                criteria_ids.append(succeed_crit_id)

        end_state_name = transition_data["next"]
        end_state = save_new_state(end_state_name, state_map, DEFAULT_PARAM_VALUES, class_name, state_data)
        state_name_to_id[end_state_name] = end_state
        process_ids = []
        transitions.append({
            "persisted": True,
            "owner": DEFAULT_PARAM_VALUES["owner"],
            "id": transition_id,
            "name": transition_name,
            "entityClassName": class_name,
            "creationDate": current_timestamp(),
            "description": transition_data.get("description", ""),
            "startStateId": (transition_start_state or start_state)["id"],
            "endStateId": end_state["id"],
            "workflowId": workflow_id,
            "criteriaIds": criteria_ids,
            "endProcessesIds": process_ids,
            "active": True,
            "automated": not transition_data.get("manual", False),
            "logActivity": False
        })
        dto["workflow"][0]["transitionIds"].append(transition_id)

        if "action" in transition_data:
            _extract_processor(process_ids, transition_data)

        if "condition" in transition_data:
            condition_data = transition_data["condition"]
            config_obj = condition_data.get("config", condition_data if condition_data.get("type") and condition_data.get("type") == "function" else {})
            if config_obj:
                function = config_obj.get("function", {})
                criteria = {
                    "owner": DEFAULT_PARAM_VALUES["owner"],
                    "calculation_nodes_tags": function.get("calculation_nodes_tags", calculation_nodes_tags),
                    "attach_entity": str(function.get("attach_entity", DEFAULT_PARAM_VALUES["attach_entity"])).lower(),
                    "calculation_response_timeout_ms": str(function.get("calculation_response_timeout_ms",
                                                                          DEFAULT_PARAM_VALUES["calculation_response_timeout_ms"])),
                    "retry_policy": config_obj.get("retry_policy", DEFAULT_PARAM_VALUES["retry_policy"]),
                    "name": function.get("name") or condition_data.get("name", DEFAULT_PARAM_VALUES["default_condition_name"]),
                    "description": function.get("description") or condition_data.get("description", ""),
                    "config": config_obj,
                    "user": DEFAULT_PARAM_VALUES["user"]
                }
                crit_id = generate_id()
                criteria_ids.append(crit_id)
                crit_params = generate_ext_criteria_params(criteria)
                dto["processParams"].extend(crit_params)
                crit_dto = generate_ext_criteria(criteria, crit_id, crit_params, class_name)
                dto["criterias"].append(crit_dto)
            else:
                cond_crit_id = generate_id()
                criteria_ids.append(cond_crit_id)
                converted = convert_condition(condition_data)
                dto["criterias"].append({
                    "persisted": True,
                    "owner": DEFAULT_PARAM_VALUES["owner"],
                    "id": cond_crit_id,
                    "name": condition_data["name"],
                    "entityClassName": class_name,
                    "creationDate": current_timestamp(),
                    "description": condition_data.get("description", ""),
                    "condition": converted,
                    "aliasDefs": [],
                    "parameters": [],
                    "criteriaChecker": "ConditionCriteriaChecker",
                    "user": DEFAULT_PARAM_VALUES["user"]
                })

    for state_name, state_data in input_json["states"].items():
        start_state = save_new_state(state_name, state_map, DEFAULT_PARAM_VALUES, class_name, state_data)
        state_name_to_id[state_name] = start_state

        if ai:
            state_data["transitions"][const.TransitionKey.MANUAL_RETRY.value] = {"next": state_name, "manual": True}
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

        for transition_name, transition_data in state_data["transitions"].items():
            _add_transition(transition_name, transition_data, start_state)

        for ec in state_data.get("error_codes", []):
            _add_transition(
                const.TransitionKey.ROLLBACK.value,
                {
                    "next": ec["next_state"],
                    "manual": True,
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
                },
                start_state=state_name_to_id.get(f"{const.TransitionKey.LOCKED_CHAT.value}_{state_name}"),
                transition_criteria_id=error_codes_name_to_id.get(ec["error_code"])
            )

    dto["states"].extend(state_map.values())
    dto["transitions"].extend(transitions)
    add_none_state_if_not_exists(dto, DEFAULT_PARAM_VALUES, class_name)
    return dto
