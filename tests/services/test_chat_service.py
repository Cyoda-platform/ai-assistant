import asyncio
import random
from types import SimpleNamespace
import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock

import services.chat_service as chat_service
from services.chat_service import ChatService
from common.exception.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    GuestChatsLimitExceededException, ChatNotFoundException,
)
from common.config import const
from common.config.config import config


@pytest.fixture
def service_mocks():
    entity_service = MagicMock()
    entity_service.get_items_by_condition = AsyncMock()
    entity_service.add_item = AsyncMock()
    entity_service.get_item = AsyncMock()
    entity_service.delete_item = AsyncMock()

    ai_agent = MagicMock()
    ai_agent.run_agent = AsyncMock()

    cyoda_auth_service = MagicMock()
    chat_lock = asyncio.Lock()

    svc = ChatService(entity_service, cyoda_auth_service, chat_lock, ai_agent)
    return svc, entity_service, ai_agent


def make_jwt(payload: dict) -> str:
    # content doesn’t matter since we always patch jwt.decode in tests
    return "dummy.jwt.token"


@pytest.mark.parametrize("header,exc_type", [
    (None, InvalidTokenException),
    ("", InvalidTokenException),
    ("Bearer ", InvalidTokenException),
])
def test_get_user_id_no_header(header, exc_type, service_mocks):
    svc, _, _ = service_mocks
    with pytest.raises(exc_type):
        svc._get_user_id(header)


def test_get_user_id_invalid_token(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode in _get_user_id should raise InvalidTokenError → method returns None
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(jwt.InvalidTokenError()))
    assert svc._get_user_id("Bearer foo.bar") is None


def test_get_user_id_expired_token(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode in _get_user_id should raise ExpiredSignatureError → method raises TokenExpiredException
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(jwt.ExpiredSignatureError()))
    with pytest.raises(TokenExpiredException):
        svc._get_user_id("Bearer expired.token")


def test_get_user_id_success_non_guest(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode returns payload with caas_org_id
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: {"caas_org_id": "user123"})
    user_id = svc._get_user_id(f"Bearer {make_jwt({'caas_org_id': 'user123'})}")
    assert user_id == "user123"


def test_get_user_id_success_guest(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # jwt.decode returns a guest ID
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: {"caas_org_id": "guest.foo"})
    called = False

    def fake_validate(token, *args, **kwargs):
        nonlocal called
        called = True

    # patch the validate_token that chat_service imported
    monkeypatch.setattr(chat_service, "validate_token", fake_validate)

    user_id = svc._get_user_id(f"Bearer {make_jwt({'caas_org_id': 'guest.foo'})}")
    assert user_id == "guest.foo"
    assert called, "validate_token should be called for guest tokens"


def test_validate_answer_empty_no_file(service_mocks):
    svc, _, _ = service_mocks
    valid, msg = svc._validate_answer("", None)
    assert not valid
    assert msg == "Invalid entity"


def test_validate_answer_empty_with_file(service_mocks):
    svc, _, _ = service_mocks
    fake_file = SimpleNamespace()
    valid, msg = svc._validate_answer("", fake_file)
    assert valid
    assert msg == "Consider the file contents"


def test_validate_answer_nonempty(service_mocks):
    svc, _, _ = service_mocks
    valid, msg = svc._validate_answer("foo", None)
    assert valid
    assert msg == "foo"


@pytest.mark.asyncio
async def test_list_chats_invalid_token(service_mocks):
    svc, _, _ = service_mocks
    with pytest.raises(InvalidTokenException):
        await svc.list_chats("")


@pytest.mark.asyncio
async def test_list_chats_no_transfers(service_mocks):
    svc, entity_service, _ = service_mocks
    chat_obj = SimpleNamespace(
        technical_id="c1", name="N1", description="D1", date="2025-05-01"
    )
    # first: user chats; second: no transfers
    entity_service.get_items_by_condition.side_effect = [
        [chat_obj],
        [],
    ]

    result = await svc.list_chats("user1")
    assert result == [{
        "technical_id": "c1",
        "name": "N1",
        "description": "D1",
        "date": "2025-05-01",
    }]
    assert entity_service.get_items_by_condition.call_count == 2


@pytest.mark.asyncio
async def test_list_chats_with_transfers(service_mocks):
    svc, entity_service, _ = service_mocks
    chat1 = SimpleNamespace(
        technical_id="c1", name="A", description="D", date="2025-05-02"
    )
    chat2 = SimpleNamespace(
        technical_id="c2", name="B", description="E", date="2025-05-03"
    )
    # user chats, transfers entry, then guest chats
    entity_service.get_items_by_condition.side_effect = [
        [chat1],
        [{"guest_user_id": "guest.x"}],
        [chat2],
    ]

    result = await svc.list_chats("user1")
    ids = {c["technical_id"] for c in result}
    assert ids == {"c1", "c2"}


@pytest.mark.asyncio
async def test_add_chat_guest_limit_exceeded(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    monkeypatch.setattr(config, "MAX_GUEST_CHATS", 1)
    entity_service.get_items_by_condition.return_value = [1]  # already has 1
    with pytest.raises(GuestChatsLimitExceededException):
        await svc.add_chat("guest.abc", {"name": "hello"})


@pytest.mark.asyncio
async def test_add_chat_name_too_large(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    long_name = "x" * 100
    monkeypatch.setattr(config, "MAX_TEXT_SIZE", 10)
    out = await svc.add_chat("user1", {"name": long_name})
    assert out == {"error": "Answer size exceeds 1MB limit"}


@pytest.mark.asyncio
async def test_add_chat_success(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    # only these three add_item calls now (greeting, memory, chat)
    entity_service.add_item.side_effect = ["edge123", "mem456", "chat789"]

    # patch out the real add_answer_to_finished_flow so it doesn't invoke entity_service
    monkeypatch.setattr(
        chat_service,
        "add_answer_to_finished_flow",
        AsyncMock(return_value="ans999"),
    )
    monkeypatch.setattr(
        chat_service,
        "current_timestamp",
        lambda: "T0"
    )
    monkeypatch.setattr(
        chat_service,
        "get_current_timestamp_num",
        lambda: 42
    )

    res = await svc.add_chat("user1", {"name": "hello", "description": "desc"})
    assert res == {
        "message": "Chat created",
        "technical_id": "chat789",
        "answer_technical_id": "ans999",
    }
    assert entity_service.add_item.call_count == 3


@pytest.mark.asyncio
async def test_delete_chat(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    # stub owner check so no exception
    monkeypatch.setattr(svc, "_get_chat_for_user", AsyncMock(return_value=SimpleNamespace()))
    res = await svc.delete_chat("Bearer t", "tid123")

    assert res == {"message": "Chat deleted", "technical_id": "tid123"}
    entity_service.delete_item.assert_awaited_once_with(
        token=svc.cyoda_auth_service,
        entity_model=const.ModelName.CHAT_ENTITY.value,
        entity_version=config.ENTITY_VERSION,
        technical_id="tid123",
        meta={},
    )


@pytest.mark.asyncio
async def test_submit_text_question_empty(service_mocks):
    svc, _, _ = service_mocks
    # Stub out authentication and chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # Submit an empty question should return an error and 400 status
    result, status = await svc.submit_text_question("Bearer token", "tid123", "")
    assert status == 400
    assert result == {"error": "Invalid entity"}


@pytest.mark.asyncio
async def test_submit_question_file_too_large(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # stub chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # set max file size to a small value
    monkeypatch.setattr(config, "MAX_FILE_SIZE", 10)
    fake_file = SimpleNamespace(content_length=20)
    result = await svc.submit_question("Bearer token", "tid123", "question", fake_file)
    assert result == {"error": "File size exceeds 10 limit"}


@pytest.mark.asyncio
async def test_submit_question_file_too_large(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # stub chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # reduce the max file size limit
    monkeypatch.setattr(config, "MAX_FILE_SIZE", 10)
    fake_file = SimpleNamespace(content_length=20)
    result = await svc.submit_question("Bearer token", "tid123", "hello", fake_file)
    assert result == {"error": "File size exceeds 10 limit"}


@pytest.mark.asyncio
async def test_submit_text_question_mock_ai(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # stub chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # enable mock AI
    monkeypatch.setattr(config, "MOCK_AI", "true")
    # any question should yield the mock response
    result, status = await svc.submit_text_question("Bearer token", "tid123", "hello?")
    assert status == 200
    assert result == {"message": "mock ai answer"}


@pytest.mark.asyncio
async def test_submit_text_answer_size_exceeded(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # stub chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # reduce the max text size limit
    monkeypatch.setattr(config, "MAX_TEXT_SIZE", 5)
    # create an answer longer than the limit
    answer = "abcdef"
    result = await svc.submit_text_answer("Bearer token", "tid123", answer)
    assert result == {"error": "Answer size exceeds 1MB limit"}


@pytest.mark.asyncio
async def test_submit_text_answer_size_exceeded(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # stub chat retrieval
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    # reduce the max text size limit
    monkeypatch.setattr(config, "MAX_TEXT_SIZE", 5)
    # create an answer longer than the limit
    answer = "abcdef"
    result = await svc.submit_text_answer("Bearer token", "tid123", answer)
    assert result == {"error": "Answer size exceeds 1MB limit"}


@pytest.mark.asyncio
async def test_get_entities_processing_data_no_nodes(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # send_cyoda_request returns no pmNodes → should catch ValueError and return {}
    monkeypatch.setattr(chat_service, "send_cyoda_request", AsyncMock(return_value={"json": {}}))
    result = await svc._get_entities_processing_data("tidX", {"childA", "childB"})
    assert result == {}

@pytest.mark.asyncio
async def test_get_entities_processing_data_success(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    # 1st call: return a host; 2nd & 3rd: return events for parent and child
    resp_nodes = {"json": {"pmNodes": [{"hostname": "host123"}]}}
    resp_parent = {"json": {"entityVersions": [10, 20], "possibleTransitions": ["t1"]}}
    resp_child = {"json": {"entityVersions": [30], "possibleTransitions": ["t2", "t3"]}}
    send_mock = AsyncMock(side_effect=[resp_nodes, resp_parent, resp_child])
    monkeypatch.setattr(chat_service, "send_cyoda_request", send_mock)
    # stub entity_service.get_item to return an entity with workflow_name
    ent = SimpleNamespace(workflow_name="my_workflow")
    entity_service.get_item = AsyncMock(side_effect=[ent, ent])
    result = await svc._get_entities_processing_data("parentId", {"childId"})
    # verify both IDs present
    assert set(result.keys()) == {"parentId", "childId"}
    assert result["parentId"] == {
        "workflow_name": "my_workflow",
        "entity_versions": [10, 20],
        "next_transitions": ["t1"]
    }
    assert result["childId"] == {
        "workflow_name": "my_workflow",
        "entity_versions": [30],
        "next_transitions": ["t2", "t3"]
    }

@pytest.mark.asyncio
async def test_rollback_failed_workflows(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Force timestamp threshold to catch all
    monkeypatch.setattr(chat_service, "get_current_timestamp_num", lambda lower_timedelta: 0)
    # Create two entities: one CHAT_ENTITY with an unconsumed answer, one AGENTIC_FLOW_ENTITY
    chat_entity = SimpleNamespace(
        technical_id="c1",
        workflow_name=const.ModelName.CHAT_ENTITY.value,
        chat_flow=SimpleNamespace(finished_flow=[SimpleNamespace(type="answer", consumed=False)])
    )
    agentic_entity = SimpleNamespace(
        technical_id="a1",
        workflow_name=const.ModelName.AGENTIC_FLOW_ENTITY.value,
        chat_flow=SimpleNamespace(finished_flow=[])
    )
    # _get_entities_by_condition returns first [chat_entity], then [agentic_entity]
    svc._get_entities_by_condition = AsyncMock(side_effect=[[chat_entity], [agentic_entity]])
    # stub _launch_transition
    lt = AsyncMock()
    monkeypatch.setattr(chat_service, "_launch_transition", lt)
    # run rollback
    await svc.rollback_failed_workflows()
    # Expect three calls: chat manual_retry, chat process_user_input, agentic manual_retry
    from common.config.const import TransitionKey
    assert lt.await_count == 3
    lt.assert_any_await(svc.entity_service, "c1", svc.cyoda_auth_service, None, TransitionKey.MANUAL_RETRY.value)
    lt.assert_any_await(svc.entity_service, "c1", svc.cyoda_auth_service, None, TransitionKey.PROCESS_USER_INPUT.value)
    lt.assert_any_await(svc.entity_service, "a1", svc.cyoda_auth_service, None, TransitionKey.MANUAL_RETRY.value)


@pytest.mark.asyncio
async def test_get_chat_success(monkeypatch, service_mocks):
    svc, _, _ = service_mocks

    # 1) Stub _get_chat_for_user to return a chat with a finished_flow
    chat_obj = SimpleNamespace(
        name="ChatName",
        description="Desc",
        date="2025-05-10",
        chat_flow=SimpleNamespace(finished_flow=["msg1", "msg2"])
    )
    monkeypatch.setattr(svc, "_get_chat_for_user", AsyncMock(return_value=chat_obj))

    # 2) Stub _process_message to return dialogue and child_entities
    fake_dialogue = [{"text": "hello"}]
    fake_children = {"childA"}
    monkeypatch.setattr(svc, "_process_message", AsyncMock(return_value=(fake_dialogue, fake_children)))

    # 3) Stub _get_entities_processing_data to return a dummy map
    fake_entities_data = {
        "childA": {
            "workflow_name": "wf",
            "entity_versions": [],
            "next_transitions": []
        }
    }
    monkeypatch.setattr(svc, "_get_entities_processing_data", AsyncMock(return_value=fake_entities_data))

    # Call get_chat
    result = await svc.get_chat("Bearer token", "tech123")

    # Verify output matches inputs (no post-processing of dialogue in current implementation)
    assert result == {
        "technical_id": "tech123",
        "name": "ChatName",
        "description": "Desc",
        "date": "2025-05-10",
        "dialogue": fake_dialogue,
        "entities_data": fake_entities_data
    }

    # Ensure helpers were called correctly
    svc._get_chat_for_user.assert_awaited_once_with("Bearer token", "tech123")
    svc._process_message.assert_awaited_once_with(
        finished_flow=chat_obj.chat_flow.finished_flow,
        auth_header="Bearer token",
        dialogue=[],
        child_entities=set()
    )
    svc._get_entities_processing_data.assert_awaited_once_with(
        technical_id="tech123",
        child_entities=fake_children
    )


@pytest.mark.asyncio
async def test_get_chat_invalid_token(service_mocks):
    svc, _, _ = service_mocks
    # Stub _get_chat_for_user to raise InvalidTokenException
    svc._get_chat_for_user = AsyncMock(side_effect=InvalidTokenException("no auth"))
    with pytest.raises(InvalidTokenException):
        await svc.get_chat("Bearer token", "tech123")


@pytest.mark.asyncio
async def test_process_message_basic(service_mocks):
    svc, entity_service, _ = service_mocks
    # Two messages: a question and a notification
    msgs = [
        SimpleNamespace(type="question", publish=True, edge_message_id="e1"),
        SimpleNamespace(type="notification", publish=True, edge_message_id="e2")
    ]

    async def fake_get_item(token, entity_model, entity_version, technical_id, meta=None):
        if technical_id == "e1":
            return {"question": "Hello?", "approve": False}
        if technical_id == "e2":
            return {"notification": "Info"}
        return {}
    entity_service.get_item = AsyncMock(side_effect=fake_get_item)

    dialogue, children = await svc._process_message(
        finished_flow=msgs,
        auth_header="Bearer token",
        dialogue=[],
        child_entities=set()
    )

    assert dialogue == [
        {"question": "Hello?", "approve": False, "technical_id": "e1"},
        {"notification": "Info", "technical_id": "e2"}
    ]
    assert children == set()

@pytest.mark.asyncio
async def test_process_message_question_with_approve(service_mocks):
    svc, entity_service, _ = service_mocks
    # A question message with approve flag
    msgs = [SimpleNamespace(type="question", publish=True, edge_message_id="e3")]

    async def fake_get_item(token, entity_model, entity_version, technical_id, meta=None):
        return {"question": "Proceed?", "approve": True}
    entity_service.get_item = AsyncMock(side_effect=fake_get_item)

    dialogue, _ = await svc._process_message(
        finished_flow=msgs,
        auth_header="Bearer token",
        dialogue=[],
        child_entities=set()
    )

    expected = "Proceed?\n\n" + const.Notifications.APPROVE_INSTRUCTION_MESSAGE.value
    assert dialogue[0]["question"] == expected
    assert dialogue[0]["technical_id"] == "e3"

@pytest.mark.asyncio
async def test_process_message_answer_auto_approve(service_mocks, monkeypatch):
    svc, entity_service, _ = service_mocks
    # An answer message equal to the APPROVE notification
    msgs = [SimpleNamespace(type="answer", publish=True, edge_message_id="e4")]

    async def fake_get_item(token, entity_model, entity_version, technical_id, meta=None):
        return {"answer": const.Notifications.APPROVE.value}
    entity_service.get_item = AsyncMock(side_effect=fake_get_item)

    # Force random.choice to pick the second ApproveAnswer
    monkeypatch.setattr(random, "choice", lambda seq: list(const.ApproveAnswer)[1])

    dialogue, _ = await svc._process_message(
        finished_flow=msgs,
        auth_header="Bearer token",
        dialogue=[],
        child_entities=set()
    )

    expected_answer = list(const.ApproveAnswer)[1].value
    assert dialogue[0]["answer"] == expected_answer
    assert dialogue[0]["technical_id"] == "e4"

@pytest.mark.asyncio
async def test_process_message_child_entities_recursive(service_mocks):
    svc, entity_service, _ = service_mocks
    # A child_entities message that references "child1"
    msgs = [SimpleNamespace(type="child_entities", publish=True, edge_message_id="ce1")]

    async def fake_get_item(token, entity_model, entity_version, technical_id, meta=None):
        # First, fetch the FLOW_EDGE_MESSAGE for "ce1"
        if entity_model == const.ModelName.FLOW_EDGE_MESSAGE.value:
            if technical_id == "ce1":
                return {"child_entities": ["child1"]}
            # Later, fetch the nested edge message "e5"
            if technical_id == "e5":
                return {"notification": "Nested"}
        # Fetch the child chat entity for "child1"
        if entity_model == const.ModelName.CHAT_ENTITY.value:
            return SimpleNamespace(
                chat_flow=SimpleNamespace(
                    finished_flow=[SimpleNamespace(type="notification", publish=True, edge_message_id="e5")]
                )
            )
        return {}
    entity_service.get_item = AsyncMock(side_effect=fake_get_item)

    dialogue, children = await svc._process_message(
        finished_flow=msgs,
        auth_header="Bearer token",
        dialogue=[],
        child_entities=set()
    )

    assert dialogue == [{"notification": "Nested", "technical_id": "e5"}]
    assert children == {"child1"}


@pytest.mark.asyncio
async def test_submit_question_helper_empty(service_mocks):
    svc, _, _ = service_mocks
    # No question provided
    res, status = await svc._submit_question_helper("Bearer token", "tid", "", None)
    assert status == 400
    assert res == {"error": "Invalid entity"}

@pytest.mark.asyncio
async def test_submit_question_helper_with_file(monkeypatch, service_mocks):
    svc, _, ai_agent = service_mocks
    # Disable mock AI
    monkeypatch.setattr(chat_service.config, "MOCK_AI", "false")
    # Stub get_user_message to rewrite the question
    fake_file = SimpleNamespace()
    monkeypatch.setattr(chat_service, "get_user_message", AsyncMock(return_value="file_q"))
    # Stub AI agent run
    ai_agent.run_agent = AsyncMock(return_value="ai_response")
    res, status = await svc._submit_question_helper("Bearer token", "tid", "orig_q", fake_file)
    # AI agent should be called with rewritten question
    ai_agent.run_agent.assert_awaited_once()
    assert status == 200
    assert res == {"message": "ai_response"}


@pytest.mark.asyncio
async def test_submit_answer_helper_guest_limit(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Set guest max messages to 1
    monkeypatch.setattr(chat_service.const, "MAX_GUEST_CHAT_MESSAGES", 1)
    chat = SimpleNamespace(user_id="guest.x", chat_flow=SimpleNamespace(finished_flow=[1,2]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 403
    assert res == {"error": "Maximum messages reached"}

@pytest.mark.asyncio
async def test_submit_answer_helper_user_limit(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Set chat max messages to 1
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 1)
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[1,2]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 403
    assert res == {"error": "Maximum messages reached"}

@pytest.mark.asyncio
async def test_submit_answer_helper_invalid_answer(service_mocks):
    svc, _, _ = service_mocks
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    # Empty answer and no file => invalid
    res, status = await svc._submit_answer_helper("", chat)
    assert status == 400
    assert res == {"message": "Invalid entity"}

@pytest.mark.asyncio
async def test_submit_answer_helper_transition_success(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Stub max limits high
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 100)
    # Stub validate passes
    # Stub transition returns transitioned
    monkeypatch.setattr(chat_service, "trigger_manual_transition", AsyncMock(return_value=("eid", True)))
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 200
    assert res == {"answer_technical_id": "eid"}

@pytest.mark.asyncio
async def test_submit_answer_helper_transition_pending(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 100)
    # Stub transition returns not transitioned
    monkeypatch.setattr(chat_service, "trigger_manual_transition", AsyncMock(return_value=("eid", False)))
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 409
    assert res == {"message": const.Notifications.DESIGN_PLEASE_WAIT.value}

@pytest.mark.asyncio
async def test_rollback_dialogue_script_root(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Stub _launch_transition
    lt = AsyncMock()
    monkeypatch.setattr(chat_service, "_launch_transition", lt)
    chat = SimpleNamespace(
        current_state="XYZ",
        child_entities=[],
        scheduled_entities=[],
        chat_flow=SimpleNamespace(finished_flow=[])
    )
    result = await svc._rollback_dialogue_script("root", chat)
    assert result is True
    from common.config.const import TransitionKey
    for t in (TransitionKey.MANUAL_RETRY.value,
              TransitionKey.UNLOCK_CHAT.value,
              TransitionKey.PROCESS_USER_INPUT.value):
        lt.assert_any_await(svc.entity_service, "root", svc.cyoda_auth_service, None, t)

@pytest.mark.asyncio
async def test_submit_question_helper_empty(service_mocks):
    svc, _, _ = service_mocks
    dummy_chat = SimpleNamespace()
    # Empty question should return error 400
    res, status = await svc._submit_question_helper("Bearer token", "tid", dummy_chat, "")
    assert status == 400
    assert res == {"error": "Invalid entity"}

@pytest.mark.asyncio
async def test_submit_question_helper_mock_ai(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    dummy_chat = SimpleNamespace()
    # Enable mock AI
    monkeypatch.setattr(chat_service.config, "MOCK_AI", "true")
    # Non-empty question triggers mock path
    res, status = await svc._submit_question_helper("Bearer token", "tid", dummy_chat, "q")
    assert status == 200
    assert res == {"message": "mock ai answer"}



@pytest.mark.asyncio
async def test_submit_question_helper_no_file(monkeypatch, service_mocks):
    svc, _, ai_agent = service_mocks
    dummy_chat = SimpleNamespace()
    # Disable mock AI
    monkeypatch.setattr(chat_service.config, "MOCK_AI", "false")
    ai_agent.run_agent = AsyncMock(return_value="res")
    res, status = await svc._submit_question_helper("Bearer token", "tid", dummy_chat, "hello")
    ai_agent.run_agent.assert_awaited_once()
    assert status == 200
    assert res == {"message": "res"}

@pytest.mark.asyncio
async def test_submit_answer_helper_guest_limit(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Guest has too many messages
    monkeypatch.setattr(chat_service.const, "MAX_GUEST_CHAT_MESSAGES", 1)
    chat = SimpleNamespace(user_id="guest.x", chat_flow=SimpleNamespace(finished_flow=[1,2]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 403
    assert res == {"error": "Maximum messages reached"}

@pytest.mark.asyncio
async def test_submit_answer_helper_user_limit(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Registered user has too many messages
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 1)
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[1,2]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 403
    assert res == {"error": "Maximum messages reached"}

@pytest.mark.asyncio
async def test_submit_answer_helper_invalid_answer(service_mocks):
    svc, _, _ = service_mocks
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    # Empty answer without file is invalid
    res, status = await svc._submit_answer_helper("", chat)
    assert status == 400
    assert res == {"message": "Invalid entity"}

@pytest.mark.asyncio
async def test_submit_answer_helper_transition_success(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Stub limits high
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 100)
    # Stub trigger_manual_transition returns transitioned
    monkeypatch.setattr(chat_service, "trigger_manual_transition", AsyncMock(return_value=("eid", True)))
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 200
    assert res == {"answer_technical_id": "eid"}

@pytest.mark.asyncio
async def test_submit_answer_helper_transition_pending(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    monkeypatch.setattr(chat_service.const, "MAX_CHAT_MESSAGES", 100)
    # Stub transition returns not transitioned
    monkeypatch.setattr(chat_service, "trigger_manual_transition", AsyncMock(return_value=("eid", False)))
    chat = SimpleNamespace(user_id="user1", chat_flow=SimpleNamespace(finished_flow=[]))
    res, status = await svc._submit_answer_helper("ans", chat)
    assert status == 409
    assert res == {"message": const.Notifications.DESIGN_PLEASE_WAIT.value}

@pytest.mark.asyncio
async def test_rollback_dialogue_script_root(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # Stub _launch_transition
    lt = AsyncMock()
    monkeypatch.setattr(chat_service, "_launch_transition", lt)
    # Chat not locked → root path
    chat = SimpleNamespace(
        current_state="XYZ",
        child_entities=[],
        scheduled_entities=[],
        chat_flow=SimpleNamespace(finished_flow=[])
    )
    result = await svc._rollback_dialogue_script("root", chat)
    assert result is True
    from common.config.const import TransitionKey
    for t in (TransitionKey.MANUAL_RETRY.value,
              TransitionKey.UNLOCK_CHAT.value,
              TransitionKey.PROCESS_USER_INPUT.value):
        lt.assert_any_await(svc.entity_service, "root", svc.cyoda_auth_service, None, t)

@pytest.mark.asyncio
async def test_rollback_dialogue_script_child(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    lt = AsyncMock()
    monkeypatch.setattr(chat_service, "_launch_transition", lt)
    from common.config.const import TransitionKey
    # Chat locked with one child and an unconsumed answer
    chat = SimpleNamespace(
        current_state=TransitionKey.LOCKED_CHAT.value + "_X",
        child_entities=["child1"],
        scheduled_entities=[],
        chat_flow=SimpleNamespace(finished_flow=[SimpleNamespace(type="answer", consumed=False)])
    )
    # Stub retrieving the child chat entity
    child = SimpleNamespace(
        technical_id="child1",
        current_state="OK",
        child_entities=[],
        scheduled_entities=[]
    )
    entity_service.get_item = AsyncMock(return_value=child)
    result = await svc._rollback_dialogue_script("root", chat)
    assert result is True
    lt.assert_any_await(svc.entity_service, "child1", svc.cyoda_auth_service, None, TransitionKey.MANUAL_RETRY.value)
    lt.assert_any_await(svc.entity_service, "child1", svc.cyoda_auth_service, None, TransitionKey.PROCESS_USER_INPUT.value)


@pytest.mark.asyncio
async def test_submit_answer_file_too_large(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    # prevent actual file‐reading
    monkeypatch.setattr(chat_service, "get_user_message", AsyncMock(return_value="ignored"))
    svc._get_chat_for_user = AsyncMock(return_value=SimpleNamespace())
    monkeypatch.setattr(config, "MAX_FILE_SIZE", 10)
    fake_file = SimpleNamespace(content_length=20)
    res = await svc.submit_answer("Bearer token", "tid", "ans", fake_file)
    assert res == {"error": "File size exceeds 10 limit"}

@pytest.mark.asyncio
async def test_submit_answer_delegates_to_helper(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    dummy_chat = SimpleNamespace()
    svc._get_chat_for_user = AsyncMock(return_value=dummy_chat)
    monkeypatch.setattr(chat_service, "get_user_message", AsyncMock(return_value="msg"))
    monkeypatch.setattr(svc, "_submit_answer_helper", AsyncMock(return_value={"ok": True}))
    res = await svc.submit_answer("Bearer token", "tid", "ans", None)
    svc._submit_answer_helper.assert_awaited_once_with("msg", dummy_chat, None)
    assert res == {"ok": True}

@pytest.mark.asyncio
async def test_approve_delegates_to_submit_answer_helper(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    dummy_chat = SimpleNamespace()
    svc._get_chat_for_user = AsyncMock(return_value=dummy_chat)
    monkeypatch.setattr(svc, "_submit_answer_helper", AsyncMock(return_value={"approved": True}))
    res = await svc.approve("Bearer token", "tid")
    svc._submit_answer_helper.assert_awaited_once_with(const.Notifications.APPROVE.value, dummy_chat)
    assert res == {"approved": True}

@pytest.mark.asyncio
async def test_rollback_returns_success(monkeypatch, service_mocks):
    svc, _, _ = service_mocks
    dummy_chat = SimpleNamespace()
    svc._get_chat_for_user = AsyncMock(return_value=dummy_chat)
    monkeypatch.setattr(svc, "_rollback_dialogue_script", AsyncMock())
    res = await svc.rollback("Bearer token", "tid")
    svc._rollback_dialogue_script.assert_awaited_once_with("tid", dummy_chat)
    assert res == {"message": "Successfully restarted the workflow"}

@pytest.mark.asyncio
async def test_get_chat_for_user_invalid_token(service_mocks):
    svc, _, _ = service_mocks
    svc._get_user_id = lambda header: None
    with pytest.raises(InvalidTokenException):
        await svc._get_chat_for_user(None, "tid")

@pytest.mark.asyncio
async def test_get_chat_for_user_not_found_non_local(monkeypatch, service_mocks):
    svc, entity_service, _ = service_mocks
    svc._get_user_id = lambda header: "user1"
    entity_service.get_item = AsyncMock(return_value=None)
    monkeypatch.setattr(config, "CHAT_REPOSITORY", "remote")
    with pytest.raises(ChatNotFoundException):
        await svc._get_chat_for_user("Bearer token", "tid")

@pytest.mark.asyncio
async def test_get_chat_for_user_success(service_mocks):
    svc, entity_service, _ = service_mocks
    svc._get_user_id = lambda header: "user1"
    chat = SimpleNamespace(user_id="user1")
    entity_service.get_item = AsyncMock(return_value=chat)
    result = await svc._get_chat_for_user("Bearer token", "tid123")
    assert result is chat

@pytest.mark.asyncio
async def test_validate_chat_owner_invalid(service_mocks):
    svc, _, _ = service_mocks
    chat = SimpleNamespace(user_id="other")
    with pytest.raises(InvalidTokenException):
        await svc._validate_chat_owner(chat, "user1")

@pytest.mark.asyncio
async def test_validate_chat_owner_guest_to_registered_success(service_mocks):
    svc, entity_service, _ = service_mocks
    chat = SimpleNamespace(user_id="guest.x")
    entity_service.get_items_by_condition = AsyncMock(return_value=[{"guest_user_id": "guest.x"}])
    # should not raise
    await svc._validate_chat_owner(chat, "user1")

@pytest.mark.asyncio
async def test_validate_chat_owner_guest_to_registered_failure(service_mocks):
    svc, entity_service, _ = service_mocks
    chat = SimpleNamespace(user_id="guest.x")
    entity_service.get_items_by_condition = AsyncMock(return_value=[])
    with pytest.raises(InvalidTokenException):
        await svc._validate_chat_owner(chat, "user1")