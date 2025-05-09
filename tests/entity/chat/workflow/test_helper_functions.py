import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import common.config.const as const
from common.config.config import config
import entity.chat.workflow.helper_functions as hf
from entity.chat.model.chat import ChatEntity
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
    return hf.WorkflowHelperService(cyoda_auth_service=cyoda_auth_service)

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
