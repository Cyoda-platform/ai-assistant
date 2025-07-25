import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import common.config.const as const
from common.config.config import config
import entity.chat.helper_functions as hf
from entity.chat.chat import ChatEntity
from entity.model import SchedulerEntity, FlowEdgeMessage

# A minimal stand-in for the parent chat entity
class DummyEntity:
    def __init__(self):
        self.user_id = "user1"
        self.questions_queue_id = "qqueue"
        self.memory_id = "mem1"
        self.child_entities = []
        self.locked = False

@pytest_asyncio.fixture
def cyoda_auth_service():
    return "token123"

@pytest_asyncio.fixture
def service(cyoda_auth_service):
    mock_entity_service = MagicMock()
    return hf.WorkflowHelperService(cyoda_auth_service=cyoda_auth_service, entity_service=mock_entity_service)

@pytest.mark.asyncio
async def test_launch_agentic_workflow_no_user_request(monkeypatch, service, cyoda_auth_service):
    # Patch out external functions
    monkeypatch.setattr(hf, "add_answer_to_finished_flow", AsyncMock())
    monkeypatch.setattr(hf, "current_timestamp", lambda: 999)
    # Mock entity_service
    entity_service = MagicMock()
    entity_service.add_item = AsyncMock(return_value="child123")
    parent = DummyEntity()

    result = await service.launch_agentic_workflow(
        entity_service=entity_service,
        technical_id="parent123",
        entity=parent,
        entity_model="ChatModel",
        workflow_name="wf1",
        user_request=None,
        workflow_cache={"a": 1},
        edge_messages_store={"b": 2},
    )

    # Assertions
    assert result == "child123"
    assert parent.locked is True
    assert parent.child_entities == ["child123"]

    # Verify add_item was called exactly once
    entity_service.add_item.assert_awaited_once()
    kwargs = entity_service.add_item.call_args.kwargs
    assert kwargs["token"] == cyoda_auth_service
    assert kwargs["entity_model"] == "ChatModel"
    assert kwargs["entity_version"] == config.ENTITY_VERSION
    # The "entity" passed should be a ChatEntity
    assert isinstance(kwargs["entity"], ChatEntity)
    # And since no user_request, finished_flow stays empty
    assert kwargs["entity"].chat_flow.finished_flow == []

@pytest.mark.asyncio
async def test_launch_agentic_workflow_with_user_request(monkeypatch, service, cyoda_auth_service):
    # Patch add_answer_to_finished_flow to return a fake message ID
    fake_msg_id = "ans456"
    mock_add = AsyncMock(return_value=fake_msg_id)
    monkeypatch.setattr(hf, "add_answer_to_finished_flow", mock_add)
    monkeypatch.setattr(hf, "current_timestamp", lambda: 123)

    entity_service = MagicMock()
    entity_service.add_item = AsyncMock(return_value="child789")
    parent = DummyEntity()

    result = await service.launch_agentic_workflow(
        entity_service=entity_service,
        technical_id="parent123",
        entity=parent,
        entity_model="ChatModel",
        workflow_name="wf1",
        user_request="hello?",
        workflow_cache={"a": 2},
        edge_messages_store={"b": 3},
    )

    assert result == "child789"
    assert parent.locked is True
    assert parent.child_entities == ["child789"]

    # Verify we called add_answer_to_finished_flow correctly
    mock_add.assert_awaited_once_with(
        entity_service=entity_service,
        answer="hello?",
        cyoda_auth_service=cyoda_auth_service,
        publish=False,
    )

    # Inspect the ChatEntity passed into add_item
    kwargs = entity_service.add_item.call_args.kwargs
    child = kwargs["entity"]
    # finished_flow should now have exactly one FlowEdgeMessage
    assert len(child.chat_flow.finished_flow) == 1
    fe: FlowEdgeMessage = child.chat_flow.finished_flow[0]
    assert isinstance(fe, FlowEdgeMessage)
    assert fe.type == "answer"
    assert fe.publish is False
    assert fe.edge_message_id == fake_msg_id
    assert fe.consumed is False
    assert fe.user_id == parent.user_id

@pytest.mark.asyncio
async def test_launch_scheduled_workflow(monkeypatch, service, cyoda_auth_service):
    entity_service = MagicMock()
    entity_service.add_item = AsyncMock(return_value="sched123")

    result = await service.launch_scheduled_workflow(
        entity_service=entity_service,
        awaited_entity_ids=["e1", "e2"],
        triggered_entity_id="tgt1",
    )

    assert result == "sched123"
    entity_service.add_item.assert_awaited_once()

    kwargs = entity_service.add_item.call_args.kwargs
    assert kwargs["token"] == cyoda_auth_service
    assert kwargs["entity_model"] == const.ModelName.SCHEDULER_ENTITY.value
    assert kwargs["entity_version"] == config.ENTITY_VERSION

    child = kwargs["entity"]
    assert isinstance(child, SchedulerEntity)
    assert child.awaited_entity_ids == ["e1", "e2"]
    assert child.triggered_entity_id == "tgt1"
    # Default scheduled_action is SCHEDULE_ENTITIES_FLOW
    assert child.scheduled_action == config.ScheduledAction.SCHEDULE_ENTITIES_FLOW.value


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_linear_flow(service):
    """Test ordering states in FSM with new format - linear flow."""
    fsm = {
        "version": "1.0",
        "id": "test_workflow",
        "name": "Test workflow",
        "initialState": "state_initial",
        "states": {
            "state_initial": {
                "transitions": [
                    {
                        "id": "transition_to_01",
                        "next": "state_01"
                    }
                ]
            },
            "state_01": {
                "transitions": [
                    {
                        "id": "transition_to_02",
                        "next": "state_02"
                    }
                ]
            },
            "state_02": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that states are ordered correctly
    state_names = list(result["states"].keys())
    assert state_names == ["state_initial", "state_01", "state_02"]

    # Check that other FSM properties are preserved
    assert result["version"] == "1.0"
    assert result["id"] == "test_workflow"
    assert result["initialState"] == "state_initial"


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_with_processors_and_criteria(service):
    """Test ordering states in FSM with new format including processors and criteria."""
    fsm = {
        "version": "1.0",
        "id": "customer_workflow",
        "name": "Customer workflow",
        "initialState": "state_initial",
        "criterion": {
            "type": "simple",
            "jsonPath": "customerType",
            "operation": "EQUALS",
            "value": "premium"
        },
        "states": {
            "state_initial": {
                "transitions": [
                    {
                        "id": "transition_to_01",
                        "next": "state_01"
                    }
                ]
            },
            "state_01": {
                "transitions": [
                    {
                        "id": "transition_to_02",
                        "next": "state_02",
                        "manual": True,
                        "processors": [
                            {
                                "name": "example_function_name",
                                "config": {
                                    "attachEntity": "true",
                                    "calculationNodesTags": "test_tag_01,test_tag_02"
                                }
                            }
                        ]
                    }
                ]
            },
            "state_02": {
                "transitions": [
                    {
                        "id": "transition_with_criterion_simple",
                        "next": "state_criterion_check_01",
                        "processors": [
                            {
                                "name": "example_function_name"
                            }
                        ],
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "example_function_name_returns_bool"
                            }
                        }
                    }
                ]
            },
            "state_criterion_check_01": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that states are ordered correctly
    state_names = list(result["states"].keys())
    assert state_names == ["state_initial", "state_01", "state_02", "state_criterion_check_01"]

    # Check that all FSM properties are preserved
    assert result["version"] == "1.0"
    assert result["id"] == "customer_workflow"
    assert result["initialState"] == "state_initial"
    assert result["criterion"]["type"] == "simple"

    # Check that state content is preserved
    assert result["states"]["state_01"]["transitions"][0]["manual"] is True
    assert len(result["states"]["state_01"]["transitions"][0]["processors"]) == 1
    assert result["states"]["state_02"]["transitions"][0]["criterion"]["type"] == "function"


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_with_orphan_states(service):
    """Test ordering states in FSM with orphan/unreachable states."""
    fsm = {
        "version": "1.0",
        "id": "test_workflow",
        "initialState": "state_a",
        "states": {
            "state_a": {
                "transitions": [
                    {
                        "id": "transition_to_b",
                        "next": "state_b"
                    }
                ]
            },
            "state_b": {
                "transitions": []
            },
            "orphan_state": {
                "transitions": [
                    {
                        "id": "transition_to_nowhere",
                        "next": "another_orphan"
                    }
                ]
            },
            "another_orphan": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that reachable states come first, then orphans
    state_names = list(result["states"].keys())
    assert state_names[:2] == ["state_a", "state_b"]
    assert set(state_names[2:]) == {"orphan_state", "another_orphan"}
    assert len(state_names) == 4


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_branching_flow(service):
    """Test ordering states in FSM with branching flow."""
    fsm = {
        "version": "1.0",
        "id": "branching_workflow",
        "initialState": "start",
        "states": {
            "start": {
                "transitions": [
                    {
                        "id": "branch_a",
                        "next": "path_a"
                    },
                    {
                        "id": "branch_b",
                        "next": "path_b"
                    }
                ]
            },
            "path_a": {
                "transitions": [
                    {
                        "id": "to_end",
                        "next": "end"
                    }
                ]
            },
            "path_b": {
                "transitions": [
                    {
                        "id": "to_end",
                        "next": "end"
                    }
                ]
            },
            "end": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that start comes first
    state_names = list(result["states"].keys())
    assert state_names[0] == "start"
    # Check that all states are present
    assert set(state_names) == {"start", "path_a", "path_b", "end"}
    assert len(state_names) == 4
    # Check that path_a comes before end (since path_a transitions to end)
    assert state_names.index("path_a") < state_names.index("end")


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_empty_transitions(service):
    """Test ordering states in FSM with empty transitions list."""
    fsm = {
        "version": "1.0",
        "id": "simple_workflow",
        "initialState": "only_state",
        "states": {
            "only_state": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that single state is preserved
    state_names = list(result["states"].keys())
    assert state_names == ["only_state"]
    assert result["initialState"] == "only_state"


@pytest.mark.asyncio
async def test_order_states_in_fsm_new_format_missing_transitions(service):
    """Test ordering states in FSM with missing transitions key."""
    fsm = {
        "version": "1.0",
        "id": "minimal_workflow",
        "initialState": "state_without_transitions",
        "states": {
            "state_without_transitions": {},
            "another_state": {
                "transitions": []
            }
        }
    }

    result = await service.order_states_in_fsm(fsm)

    # Check that state without transitions is handled gracefully
    state_names = list(result["states"].keys())
    assert "state_without_transitions" in state_names
    assert "another_state" in state_names
