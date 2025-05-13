from types import SimpleNamespace

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import entity.workflow_dispatcher as wfd
from entity.workflow_dispatcher import WorkflowDispatcher, AIMessage, FlowEdgeMessage

# A dummy class whose methods will be dispatched
class DummyClass:
    async def process(self, technical_id, entity=None):
        return f"processed {technical_id}"

    async def raises_error(self, technical_id, entity=None):
        raise RuntimeError("test error")

# Fixture to build a dispatcher around DummyClass
@pytest_asyncio.fixture
async def dispatcher():
    dummy_inst = DummyClass()
    ai_agent = MagicMock()
    entity_service = MagicMock()
    cyoda_auth_service = MagicMock()
    return WorkflowDispatcher(DummyClass, dummy_inst, ai_agent, entity_service, cyoda_auth_service)

# A minimal stand-in for WorkflowEntity
class DummyEntity:
    def __init__(self):
        self.failed = False
        self.last_modified = None
        self.error = None

@pytest.mark.asyncio
async def test_dispatch_function_known(dispatcher):
    # should return the value from DummyClass.process
    res = await dispatcher.dispatch_function("process", technical_id="t1")
    assert res == "processed t1"

@pytest.mark.asyncio
async def test_dispatch_function_unknown(dispatcher):
    # unknown function => catches ValueError and returns None
    res = await dispatcher.dispatch_function("does_not_exist")
    assert res is None

@pytest.mark.asyncio
async def test_execute_method_success(dispatcher):
    ent = DummyEntity()
    resp = await dispatcher._execute_method("process", technical_id="xyz", entity=ent)
    assert resp == "processed xyz"

@pytest.mark.asyncio
async def test_execute_method_failure(dispatcher):
    ent = DummyEntity()
    # calling a method that raises should propagate and mark entity.failed
    with pytest.raises(RuntimeError):
        await dispatcher._execute_method("raises_error", technical_id="id", entity=ent)
    assert ent.failed is True
    assert "raises_error" in ent.error

@pytest.mark.asyncio
async def test_process_event_success(dispatcher, monkeypatch):
    ent = DummyEntity()
    action = {"name": "process"}
    # make timestamp predictable
    monkeypatch.setattr(wfd, "get_current_timestamp_num", lambda: 123)
    out_ent, resp = await dispatcher.process_event(ent, action, technical_id="abc")
    assert resp == "processed abc"
    assert out_ent.last_modified == 123
    assert out_ent.failed is False

@pytest.mark.asyncio
async def test_process_event_unknown(dispatcher, monkeypatch):
    ent = DummyEntity()
    action = {"name": "unknown"}
    monkeypatch.setattr(wfd, "get_current_timestamp_num", lambda: 456)
    out_ent, resp = await dispatcher.process_event(ent, action, technical_id="abc")
    # on unknown step it logs and returns default response
    assert resp == "returned empty response"
    assert out_ent.failed is True
    assert "Unknown processing step" in out_ent.error
    assert out_ent.last_modified == 456




#=================================================================================


# -- Fixtures --

@pytest_asyncio.fixture
async def wd():
    class TempHandler:
        pass

    dummy_inst = TempHandler()
    ai_agent = AsyncMock()
    entity_service = MagicMock()
    cyoda_auth_service = MagicMock()

    return WorkflowDispatcher(
        TempHandler,
        dummy_inst,
        ai_agent,
        entity_service,
        cyoda_auth_service
    )

@pytest_asyncio.fixture
async def test_entity():
    ent = SimpleNamespace()
    ent.child_entities = []
    ent.chat_flow = SimpleNamespace(finished_flow=[])
    ent.workflow_cache = {}
    ent.memory_id = "mem123"
    ent.user_id = "user_abc"
    return ent

# -- Tests for _check_and_update_iteration --

def test_check_and_update_iteration_no_max(wd):
    config = {}
    tm = SimpleNamespace(current_iteration={}, max_iteration={})
    ent = SimpleNamespace(current_transition="step1", transitions_memory=tm)

    # No max_iteration => always False, no side-effects
    assert wd._check_and_update_iteration(config, ent) is False
    assert ent.transitions_memory.current_iteration == {}

def test_check_and_update_iteration_under_and_over(wd):
    config = {"max_iteration": 2}
    tm = SimpleNamespace(current_iteration={}, max_iteration={})
    ent = SimpleNamespace(current_transition="stepA", transitions_memory=tm)

    # 1st call: initialize and increment to 1
    assert wd._check_and_update_iteration(config, ent) is False
    assert tm.current_iteration["stepA"] == 1
    assert tm.max_iteration["stepA"] == 2

    # 2nd call: increment to 2
    assert wd._check_and_update_iteration(config, ent) is False
    assert tm.current_iteration["stepA"] == 2

    # 3rd call: current 2 == max 2 -> it still increments (to 3) but returns False
    assert wd._check_and_update_iteration(config, ent) is False
    assert tm.current_iteration["stepA"] == 3

    # 4th call: now 3 > 2 => returns True
    assert wd._check_and_update_iteration(config, ent) is True

# -- Tests for _format_message --

def test_format_message_success(wd):
    cache = {"name": "Alice"}
    fmt = "Hello, {name}!"
    assert wd._format_message(fmt, cache) == "Hello, Alice!"

def test_format_message_missing_key(wd, caplog):
    cache = {"name": "Alice"}
    fmt = "Bye, {unknown}!"
    res = wd._format_message(fmt, cache)
    assert res == fmt
    assert "KeyError" in caplog.text

# -- Tests for _handle_config_based_event --

@pytest.mark.asyncio
async def test_handle_config_based_event_notification(wd, test_entity):
    wd._append_to_ai_memory = AsyncMock()
    wd._finalize_response   = AsyncMock(return_value=None)

    cfg = {
        "type": "notification",
        "notification": "Alert: {level}",
        "memory_tags": ["alerts"]
    }
    test_entity.workflow_cache = {"level": "HIGH"}

    ent, resp = await wd._handle_config_based_event(cfg, test_entity, technical_id="T1")

    assert ent is test_entity
    assert resp is None

    wd._append_to_ai_memory.assert_awaited_once_with(
        test_entity, "Alert: HIGH", ["alerts"]
    )
    wd._finalize_response.assert_awaited_once_with(
        technical_id="T1",
        config=cfg,
        entity=test_entity,
        finished_flow=test_entity.chat_flow.finished_flow,
        new_entities=[],
        response=None
    )

#=========================================



@pytest.mark.asyncio
async def test_add_edge_message(wd, test_entity):
    # Return a string so FlowEdgeMessage accepts it
    wd.entity_service.add_item = AsyncMock(return_value="555")
    flow = []
    msg = {"type": "notification", "foo": "bar"}

    fem = await wd.add_edge_message(message=msg, flow=flow, user_id=test_entity.user_id)

    assert isinstance(fem, FlowEdgeMessage)
    assert fem.edge_message_id == "555"
    assert fem.type == "notification"
    assert fem.user_id == test_entity.user_id
    assert flow == [fem]

# -- Tests for _handle_config_based_event --

@pytest.mark.asyncio
async def test_handle_config_based_event_notification(wd, test_entity):
    wd._append_to_ai_memory = AsyncMock()
    wd._finalize_response   = AsyncMock(return_value=None)

    cfg = {
        "type": "notification",
        "notification": "Alert: {level}",
        "memory_tags": ["alerts"]
    }
    test_entity.workflow_cache = {"level": "HIGH"}

    ent, resp = await wd._handle_config_based_event(cfg, test_entity, technical_id="T1")

    assert ent is test_entity
    assert resp is None

    wd._append_to_ai_memory.assert_awaited_once_with(
        test_entity, "Alert: HIGH", ["alerts"]
    )
    wd._finalize_response.assert_awaited_once_with(
        technical_id="T1",
        config=cfg,
        entity=test_entity,
        finished_flow=test_entity.chat_flow.finished_flow,
        new_entities=[],
        response=None
    )

@pytest.mark.asyncio
async def test_handle_config_based_event_function_branch(wd, test_entity):
    fake_fn = AsyncMock(return_value="OKAY")
    wd.methods_dict = {"myfunc": fake_fn}
    wd._append_to_ai_memory = AsyncMock()
    wd._finalize_response   = AsyncMock(return_value=None)

    cfg = {
        "type": "function",
        "function": {
            "name": "myfunc",
            "parameters": {"x": 42}
        },
        "memory_tags": ["tagX"]
    }

    ent, resp = await wd._handle_config_based_event(cfg, test_entity, technical_id="T42")

    assert resp == "OKAY"
    fake_fn.assert_awaited_once_with(
        wd.cls_instance,
        technical_id="T42",
        entity=test_entity,
        x=42
    )
    wd._append_to_ai_memory.assert_awaited_once_with(
        test_entity, "OKAY", ["tagX"]
    )
    wd._finalize_response.assert_awaited_once()

# -- Test for _get_ai_agent_response batch branch --

@pytest.mark.asyncio
async def test_get_ai_agent_response_batch(wd):
    # Patch module‐level function, not wd.batch_process_file
    wfd.batch_process_file = AsyncMock()

    cfg = {
        "type": "batch",
        "input":  {"local_fs": ["in.txt"]},
        "output": {"local_fs": ["out.json"]}
    }
    res = await wd._get_ai_agent_response(cfg, entity=None, memory=None, technical_id="B1")
    assert res == "Scheduled batch processing for in.txt"

    wfd.batch_process_file.assert_awaited_once_with(
        input_file_path="in.txt",
        output_file_path="out.json"
    )



#===============================================


@pytest_asyncio.fixture
async def disp2():
    """A clean dispatcher using a local handler class."""
    class Handler:
        pass

    inst = Handler()
    ai = AsyncMock()
    svc = MagicMock()
    auth = MagicMock()
    return WorkflowDispatcher(Handler, inst, ai, svc, auth)


@pytest.fixture
def ent2():
    """Minimal entity with required attributes."""
    e = SimpleNamespace()
    e.child_entities = []
    e.chat_flow = SimpleNamespace(finished_flow=[])
    e.workflow_cache = {}
    e.memory_id = "m123"
    e.user_id = "u456"
    e.edge_messages_store = {"msg1": "eid1"}  # for cyoda_edge_message tests
    return e


# -- _append_messages tests --

@pytest.mark.asyncio
async def test_append_messages_with_config_messages(disp2, ent2):
    # stub enrich_config_message to echo with an added field
    wfd.enrich_config_message = AsyncMock(side_effect=lambda **kw: dict(**kw["config_message"], enriched=True))
    # stub add_item to return incrementing string IDs
    disp2.entity_service.add_item = AsyncMock(side_effect=["A1", "A2"])

    memory = SimpleNamespace(messages={})
    cfg = {
        "messages": [{"foo": 1}, {"bar": 2}],
        "memory_tags": ["tag1", "tag2"]
    }
    # no finished_flow
    await disp2._append_messages(ent2, cfg, memory, finished_flow=[])

    # ensure enrich called for each message
    assert wfd.enrich_config_message.await_count == 2
    # add_item called twice for the two messages
    assert disp2.entity_service.add_item.await_count == 2

    # both tags should now have two AIMessage each
    for tag in ("tag1", "tag2"):
        assert tag in memory.messages
        assert all(isinstance(m, AIMessage) for m in memory.messages[tag])
        assert [m.edge_message_id for m in memory.messages[tag]] == ["A1", "A2"]

# -- _get_ai_agent_response (non-batch) --

@pytest.mark.asyncio
async def test_get_ai_agent_response_non_batch(disp2, ent2):
    # stub _get_ai_memory to return some prior messages
    disp2._get_ai_memory = AsyncMock(return_value=[{"role":"user","content":"hi"}])
    # stub AI agent
    disp2.ai_agent.run_agent = AsyncMock(return_value="REPLY")
    # stub add_item for storing assistant response
    disp2.entity_service.add_item = AsyncMock(return_value="MSGID")

    memory = SimpleNamespace(messages={"mt": []})
    cfg = {
        "type": "agent",
        "memory_tags": ["mt"],
        "tools": None,
        "model": {"some": "config"},
        "tool_choice": None,
        "response_format": None
    }

    res = await disp2._get_ai_agent_response(cfg, ent2, memory, technical_id="TID")
    assert res == "REPLY"

    # ensure run_agent was called with our stubbed messages
    disp2.ai_agent.run_agent.assert_awaited_once()
    # ensure we saved the assistant reply into memory
    disp2.entity_service.add_item.assert_awaited_once_with(
        token=disp2.cyoda_auth_service,
        entity_model=wfd.const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
        entity_version=wfd.env_config.ENTITY_VERSION,
        entity={"role": "assistant", "content": "REPLY"},
        meta={"type": wfd.env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
    )
    assert memory.messages["mt"][0].edge_message_id == "MSGID"


# -- _get_ai_memory tests --

@pytest.mark.asyncio
async def test_get_ai_memory_with_local_fs(disp2, ent2, tmp_path, monkeypatch):
    # prepare memory with one AIMessage
    mem = SimpleNamespace(messages={})
    mem.messages["mt"] = [AIMessage(edge_message_id="X1")]
    # stub get_item for the AI_MEMORY_EDGE_MESSAGE
    disp2.entity_service.get_item = AsyncMock(return_value={"role":"assistant","content":"old"})
    # stub read_local_file to return custom text
    monkeypatch.setattr(disp2, "_read_local_file", AsyncMock(return_value="FILE_CONTENT"))

    cfg = {
        "memory_tags": ["mt"],
        "input": {"local_fs": ["fileA.txt"]}
    }
    ent2.workflow_cache = {}  # no branch key, so technical_id is used
    msgs = await disp2._get_ai_memory(ent2, cfg, mem, technical_id="BR")

    # first message is the fetched memory
    assert {"role":"assistant","content":"old"} in msgs
    # second is our file reference
    assert any("Reference: fileA.txt" in m["content"] for m in msgs)


@pytest.mark.asyncio
async def test_get_ai_memory_with_cyoda_edge_message(disp2, ent2):
    mem = SimpleNamespace(messages={"mt":[AIMessage(edge_message_id="X2")]})
    # stub get_item twice: once for AI_MEMORY_EDGE_MESSAGE, once for EDGE_MESSAGE_STORE
    disp2.entity_service.get_item = AsyncMock(side_effect=[
        {"foo": "bar"},        # for AI_MEMORY_EDGE_MESSAGE
        {"stored": "data"}      # for EDGE_MESSAGE_STORE
    ])

    cfg = {
        "memory_tags": ["mt"],
        "input": {"cyoda_edge_message": ["msg1"]}
    }
    msgs = await disp2._get_ai_memory(ent2, cfg, mem, technical_id="BR")

    # should retrieve first the AI memory, then the stored message
    assert {"foo": "bar"} in msgs
    assert any("Reference: {'stored': 'data'}" in m["content"] for m in msgs)


@pytest_asyncio.fixture
async def disp2():
    class Handler:
        pass

    inst = Handler()
    ai = AsyncMock()
    svc = MagicMock()
    auth = MagicMock()
    return WorkflowDispatcher(Handler, inst, ai, svc, auth)


@pytest.fixture
def ent2():
    e = SimpleNamespace()
    e.child_entities = []
    e.chat_flow = SimpleNamespace(finished_flow=[])
    e.workflow_cache = {}
    e.memory_id = "m123"
    e.user_id = "u456"
    e.edge_messages_store = {"msg1": "eid1"}
    return e


# -- _append_messages tests --

@pytest.mark.asyncio
async def test_append_messages_with_config_messages(disp2, ent2):
    wfd.enrich_config_message = AsyncMock(
        side_effect=lambda **kw: {**kw["config_message"], "enriched": True}
    )
    disp2.entity_service.add_item = AsyncMock(side_effect=["A1", "A2"])

    memory = SimpleNamespace(messages={})
    cfg = {
        "messages": [{"foo": 1}, {"bar": 2}],
        "memory_tags": ["tag1", "tag2"]
    }

    await disp2._append_messages(ent2, cfg, memory, finished_flow=[])

    assert wfd.enrich_config_message.await_count == 2
    assert disp2.entity_service.add_item.await_count == 2

    for tag in ("tag1", "tag2"):
        assert tag in memory.messages
        ids = [m.edge_message_id for m in memory.messages[tag]]
        assert ids == ["A1", "A2"]


# -- _get_ai_agent_response (non-batch) --

@pytest.mark.asyncio
async def test_get_ai_agent_response_non_batch(disp2, ent2):
    disp2._get_ai_memory = AsyncMock(return_value=[{"role": "user", "content": "hi"}])
    disp2.ai_agent.run_agent = AsyncMock(return_value="REPLY")
    disp2.entity_service.add_item = AsyncMock(return_value="MSGID")

    memory = SimpleNamespace(messages={"mt": []})
    cfg = {
        "type": "agent",
        "memory_tags": ["mt"],
        "tools": None,
        "model": {"some": "config"},
        "tool_choice": None,
        "response_format": None
    }

    res = await disp2._get_ai_agent_response(cfg, ent2, memory, technical_id="TID")
    assert res == "REPLY"

    disp2.ai_agent.run_agent.assert_awaited_once()
    disp2.entity_service.add_item.assert_awaited_once_with(
        token=disp2.cyoda_auth_service,
        entity_model=wfd.const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
        entity_version=wfd.env_config.ENTITY_VERSION,
        entity={"role": "assistant", "content": "REPLY"},
        meta={"type": wfd.env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
    )
    assert memory.messages["mt"][0].edge_message_id == "MSGID"


# -- _get_ai_memory tests --

@pytest.mark.asyncio
async def test_get_ai_memory_with_local_fs(disp2, ent2, tmp_path, monkeypatch):
    mem = SimpleNamespace(messages={"mt": [AIMessage(edge_message_id="X1")]})
    disp2.entity_service.get_item = AsyncMock(return_value={"role": "assistant", "content": "old"})
    monkeypatch.setattr(disp2, "_read_local_file", AsyncMock(return_value="FILE_CONTENT"))

    cfg = {
        "memory_tags": ["mt"],
        "input": {"local_fs": ["fileA.txt"]}
    }
    ent2.workflow_cache = {}
    msgs = await disp2._get_ai_memory(ent2, cfg, mem, technical_id="BR")

    # first entry from AI memory
    assert {"role": "assistant", "content": "old"} in msgs
    # then the file reference
    assert any(
        m.get("content", "").startswith("Reference: fileA.txt")
        for m in msgs
    )


@pytest.mark.asyncio
async def test_get_ai_memory_with_cyoda_edge_message(disp2, ent2):
    mem = SimpleNamespace(messages={"mt": [AIMessage(edge_message_id="X2")]})
    disp2.entity_service.get_item = AsyncMock(side_effect=[
        {"foo": "bar"},     # AI memory fetch
        {"stored": "data"}  # EDGE_MESSAGE_STORE fetch
    ])

    cfg = {
        "memory_tags": ["mt"],
        "input": {"cyoda_edge_message": ["msg1"]}
    }
    msgs = await disp2._get_ai_memory(ent2, cfg, mem, technical_id="BR")

    # should include the AI memory dict
    assert {"foo": "bar"} in msgs

    # should include exactly the user-reference dict
    expected = {"role": "user", "content": "Reference: {'stored': 'data'}"}
    assert expected in msgs