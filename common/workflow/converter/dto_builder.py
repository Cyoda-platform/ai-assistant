import json
from typing import Any, Dict

from common.config import const
from common.workflow.workflow_to_dto_converter import (
    current_timestamp,
    generate_id,
    resolve_field_name,
    OPERATION_MAPPING,
    convert_condition,
    generate_ext_criteria_params,
    generate_ext_criteria,
)
from common.workflow.converter.utils import (
    extract_processor,
    extract_processor_condition,
)


class DTOBuilder:
    def __init__(
            self,
            model_name: str,
            model_version: int,
            workflow_name: str,
            calculation_node_tags: str,
            ai: bool = False,
            default_owner: str = "CYODA",
            default_user: str = "CYODA"
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.workflow_name = workflow_name
        self.calculation_node_tags = calculation_node_tags
        self.class_name = f"{model_name}.{model_version}"
        self.ai = ai
        self.default_owner = default_owner
        self.default_user = default_user

        self.workflow_id = generate_id()
        self.criteria_id_map: Dict[str, str] = {}
        self.dto: Dict[str, Any] = {
            "@bean": "com.cyoda.core.model.stateMachine.dto.FullWorkflowContainerDto",
            "workflow": [],
            "transitions": [],
            "criterias": [],
            "processes": [],
            "states": [],
            "processParams": []
        }

    def build(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        # 1) workflow metadata
        self._add_workflow_metadata(input_json.get("description", ""))
        # 2) workflow-level criteria
        self._add_workflow_condition_criteria()
        # 3) base criteria: has_failed, has_succeeded, wrong_generated_content
        self._add_base_criterias()
        # 4) states + transitions
        self._add_states_and_transitions(input_json["states"])
        # 5) final “None”‐state & initial_transition
        self._add_none_state_if_missing()
        return self.dto

    def _add_workflow_metadata(self, description: str):
        self.dto["workflow"].append({
            "persisted": True,
            "owner": self.default_owner,
            "id": self.workflow_id,
            "name": f"{self.model_name}:{self.model_version}:{self.workflow_name}",
            "entityClassName": self.class_name,
            "creationDate": current_timestamp(),
            "description": description,
            "entityShortClassName": "TreeNodeEntity",
            "transitionIds": [],
            "criteriaIds": [],
            "stateIds": ["noneState"],    # we'll extend this later
            "active": True,
            "useDecisionTree": False,
            "decisionTrees": [],
            "metaData": {"documentLink": ""}
        })

    def _add_workflow_condition_criteria(self):
        crit_id = generate_id()
        self.dto["workflow"][0]["criteriaIds"].append(crit_id)

        cond = {
            "@bean": "com.cyoda.core.conditions.GroupCondition",
            "operator": "AND",
            "conditions": [{
                "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                "fieldName": "workflow_name",
                "operation": "IEQUALS",
                "rangeField": "false",
                "value": self.workflow_name
            }]
        }

        self.dto["criterias"].append({
            "persisted": True,
            "owner": self.default_owner,
            "id": crit_id,
            "name": f"{self.model_name}:{self.model_version}:{self.workflow_name}",
            "entityClassName": self.class_name,
            "creationDate": current_timestamp(),
            "description": "Workflow criteria",
            "condition": cond,
            "aliasDefs": [],
            "parameters": [],
            "criteriaChecker": "ConditionCriteriaChecker",
            "user": self.default_user
        })

    def _add_base_criterias(self):
        # has_failed / has_succeeded
        for name, failed_value in [("has_failed", True), ("has_succeeded", False)]:
            crit_id = generate_id()
            self.criteria_id_map[name] = crit_id
            self.dto["criterias"].append({
                "persisted": True,
                "owner": self.default_owner,
                "id": crit_id,
                "name": name,
                "entityClassName": self.class_name,
                "creationDate": current_timestamp(),
                "description": "",
                "condition": {
                    "@bean": "com.cyoda.core.conditions.GroupCondition",
                    "operator": "AND",
                    "conditions": [{
                        "@bean": "com.cyoda.core.conditions.queryable.Equals",
                        "fieldName": "failed",
                        "operation": "EQUALS",
                        "rangeField": "false",
                        "value": failed_value,
                        "queryable": True
                    }]
                },
                "aliasDefs": [],
                "parameters": [],
                "criteriaChecker": "ConditionCriteriaChecker",
                "user": self.default_user
            })

        # wrong_generated_content
        wgc_id = generate_id()
        self.criteria_id_map[const.AiErrorCodes.WRONG_GENERATED_CONTENT.value] = wgc_id
        self.dto["criterias"].append({
            "persisted": True,
            "owner": self.default_owner,
            "id": wgc_id,
            "name": "wrong_generated_content",
            "entityClassName": self.class_name,
            "creationDate": current_timestamp(),
            "description": "",
            "condition": {
                "@bean": "com.cyoda.core.conditions.GroupCondition",
                "operator": "AND",
                "conditions": [{
                    "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals",
                    "fieldName": "error_code",
                    "operation": "IEQUALS",
                    "rangeField": "false",
                    "value": "wrong_generated_content"
                }]
            },
            "aliasDefs": [],
            "parameters": [],
            "criteriaChecker": "ConditionCriteriaChecker",
            "user": self.default_user
        })

    def _add_states_and_transitions(self, states: Dict[str, Any]):
        state_map: Dict[str, Dict[str, Any]] = {}
        transitions = []

        def save_state(name: str, data: Dict[str, Any]) -> Dict[str, Any]:
            if name in state_map:
                return state_map[name]
            sid = "noneState" if name.lower() == "none" else generate_id()
            obj = {
                "persisted": True,
                "owner": self.default_owner,
                "id": sid,
                "name": name,
                "entityClassName": self.class_name,
                "creationDate": current_timestamp(),
                "description": data.get("description", "")
            }
            state_map[name] = obj
            return obj

        def build_transition(name, start, end_name, manual, desc, criteria_ids):
            end = save_state(end_name, states.get(end_name, {}))
            tid = generate_id()
            tr = {
                "persisted": True,
                "owner": self.default_owner,
                "id": tid,
                "name": name,
                "entityClassName": self.class_name,
                "creationDate": current_timestamp(),
                "description": desc,
                "startStateId": start["id"],
                "endStateId": end["id"],
                "workflowId": self.workflow_id,
                "criteriaIds": criteria_ids,
                "endProcessesIds": [],
                "active": True,
                "automated": not manual,
                "logActivity": False
            }
            # action → processes
            if "action" in states[start["name"]]["transitions"].get(name, {}):
                proc_info = states[start["name"]]["transitions"][name]["action"]
                extract_processor(tr["endProcessesIds"], states[start["name"]]["transitions"][name])
            self.dto["workflow"][0]["transitionIds"].append(tid)
            transitions.append(tr)

        # iterate states
        for sname, sdata in states.items():
            curr = save_state(sname, sdata)
            # inject AI defaults
            if self.ai:
                sdata.setdefault("transitions", {})
                sdata["transitions"].update({
                    const.TransitionKey.MANUAL_RETRY.value: {"next": sname, "manual": True},
                    const.TransitionKey.FAIL.value: {
                        "next": f"{const.TransitionKey.LOCKED_CHAT.value}_{sname}",
                        "action": {
                            "name": "process_event",
                            "config": {"type": "function", "function": {"name": "fail_workflow"}, "publish": True}
                        }
                    }
                })

            for tname, tdata in sdata.get("transitions", {}).items():
                manual = tdata.get("manual", False)
                crits: list = []
                # inline condition?
                if "condition" in tdata:
                    cid = generate_id()
                    conv = convert_condition(tdata["condition"])
                    self.dto["criterias"].append({
                        "persisted": True,
                        "owner": self.default_owner,
                        "id": cid,
                        "name": tdata["condition"].get("name", ""),
                        "entityClassName": self.class_name,
                        "creationDate": current_timestamp(),
                        "description": tdata["condition"].get("description", ""),
                        "condition": conv,
                        "aliasDefs": [],
                        "parameters": [],
                        "criteriaChecker": "ConditionCriteriaChecker",
                        "user": self.default_user
                    })
                    crits.append(cid)
                else:
                    # ROUTE on fail / success
                    if tname == const.TransitionKey.FAIL.value:
                        crits.append(self.criteria_id_map["has_failed"])
                    elif not manual:
                        crits.append(self.criteria_id_map["has_succeeded"])

                build_transition(
                    name=tname,
                    start=curr,
                    end_name=tdata["next"],
                    manual=manual,
                    desc=tdata.get("description", ""),
                    criteria_ids=crits
                )

            # error_codes → rollback
            for err in sdata.get("error_codes", []):
                elog = const.TransitionKey.ROLLBACK.value
                src = save_state(f"{const.TransitionKey.LOCKED_CHAT.value}_{sname}", {})
                cid = self.criteria_id_map.get(err["error_code"])
                build_transition(
                    name=elog,
                    start=src,
                    end_name=err["next_state"],
                    manual=True,
                    desc="Error rollback",
                    criteria_ids=[cid] if cid else []
                )

        # finally attach all states + transitions
        self.dto["states"].extend(state_map.values())
        self.dto["transitions"].extend(transitions)
        # ensure every new state is in workflow[0]["stateIds"]
        for st in state_map.values():
            sid = st["id"]
            if sid not in self.dto["workflow"][0]["stateIds"]:
                self.dto["workflow"][0]["stateIds"].append(sid)

    def _add_none_state_if_missing(self):
        # no-op here since we always seed "none" above
        pass
