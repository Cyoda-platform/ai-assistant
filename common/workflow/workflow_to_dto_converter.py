import json
import uuid
import common.config.const as const
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from common.config.config import config


def generate_id():
    return str(uuid.uuid1())


def convert(input_file_path, output_file_path, calculation_node_tags, model_name, model_version, workflow_name):
    """Reads JSON from a file, converts it to workflow_dto, and writes it to another file."""
    with open(input_file_path, "r", encoding="utf-8") as infile:
        input_json = json.load(infile)

    # Call the conversion method
    workflow_dto = convert_json_to_workflow_dto(input_json=input_json,
                                                class_name="com.cyoda.tdb.model.treenode.TreeNodeEntity",
                                                calculation_nodes_tags=calculation_node_tags,
                                                model_name=model_name,
                                                model_version=model_version,
                                                workflow_name=workflow_name)

    with open(output_file_path, "w", encoding="utf-8") as outfile:
        json.dump(workflow_dto, outfile, indent=4, ensure_ascii=False)


def convert_json_to_workflow_dto(input_json, class_name, calculation_nodes_tags, model_name, model_version,
                                 workflow_name):
    default_param_values = {
        "owner": "CYODA",
        "user": "CYODA",
        "attach_entity": "true",
        "calculation_response_timeout_ms": "900000",
        "retry_policy": "FIXED",  # NONE
        "sync_process": "false",
        "new_transaction_for_async": "true",
        "none_transactional_for_async": "false",
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
                dto["processes"].append({
                    "persisted": True,
                    "owner": default_param_values["owner"],
                    "id": {
                        "@bean": "com.cyoda.core.model.stateMachine.dto.ProcessIdDto",
                        "persisted": True,
                        "persistedId": process_id,
                        "runtimeId": 0
                    },
                    "name": transition_data["action"]["name"],
                    "entityClassName": class_name,
                    "creationDate": current_timestamp(),
                    "description": transition_data["action"]["config"].get("description", ""),
                    # "config": transition_data["action"]["config"],
                    "processorClassName": "net.cyoda.saas.externalize.processor.ExternalizedProcessor",
                    "parameters": process_params,
                    "fields": [],
                    "syncProcess": transition_data["action"]["config"].get("sync_process",
                                                                           default_param_values["sync_process"]),
                    "newTransactionForAsync": transition_data["action"]["config"].get("new_transaction_for_async",
                                                                                      default_param_values[
                                                                                          "new_transaction_for_async"]),
                    "noneTransactionalForAsync": transition_data["action"]["config"].get(
                        "none_transactional_for_async",
                        default_param_values[
                            "none_transactional_for_async"]),
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
                            "value": transition_data["action"]["config"].get("calculation_nodes_tags",
                                                                             calculation_nodes_tags)
                            # todo what source for tags?
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
                                transition_data["action"]["config"].get("attach_entity", default_param_values[
                                    "attach_entity"])).lower()
                        }
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Calculation response timeout (ms)",
                        "creationDate": current_timestamp(),
                        "valueType": "INTEGER",
                        "value": {"@type": "String", "value": str(
                            transition_data["action"]["config"].get("calculation_response_timeout_ms",
                                                                    default_param_values[
                                                                        "calculation_response_timeout_ms"]))}
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Retry policy",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value": {"@type": "String",
                                  "value": transition_data["action"]["config"].get("retry_policy",
                                                                                   default_param_values[
                                                                                       "retry_policy"])}
                    },
                    {
                        "persisted": True,
                        "owner": default_param_values["owner"],
                        "id": generate_id(),
                        "name": "Parameter 'context'",
                        "creationDate": current_timestamp(),
                        "valueType": "STRING",
                        "value": {"@type": "String", "value": json.dumps(transition_data["action"]["config"])}
                    }
                ])

                dto["processParams"].extend(process_params)

                # Process externalized_processor's externalized_criteria - skip

            # Process transition's externalized_criteria
            if "condition" in transition_data:
                criteria = {
                    "owner": default_param_values["owner"],
                    "calculation_nodes_tags": transition_data["condition"]["config"].get("calculation_nodes_tags",
                                                                                         calculation_nodes_tags),
                    "attach_entity": str(transition_data["condition"]["config"].get("attach_entity",
                                                                                    default_param_values[
                                                                                        "attach_entity"])).lower(),
                    "calculation_response_timeout_ms": str(
                        transition_data["condition"]["config"].get("calculation_response_timeout_ms",
                                                                   default_param_values[
                                                                       "calculation_response_timeout_ms"])),
                    "retry_policy": transition_data["condition"]["config"].get("retry_policy",
                                                                               default_param_values[
                                                                                   "retry_policy"]),
                    "name": transition_data["condition"]["config"]["function"]["name"],
                    "description": transition_data["condition"]["config"]["function"].get("description", ""),
                    "config": transition_data["condition"]["config"],
                    "user": default_param_values["user"]
                }

                criteria_id = generate_id()
                criteria_ids.append(criteria_id)
                criteria_params = generate_ext_criteria_params(criteria)
                dto["processParams"].extend(criteria_params)
                criteria_dto = generate_ext_criteria(criteria, criteria_id, criteria_params, class_name)
                dto["criterias"].append(criteria_dto)

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
        # Call your conversion
        convert(
            input_file_path=input_file,
            output_file_path=str(output_file),
            calculation_node_tags=config.GRPC_PROCESSOR_TAG,
            model_name=model_name,
            model_version=int(config.ENTITY_VERSION),
            workflow_name=workflow_name
        )

        print(f"Conversion completed. Result saved to {output_file}")
