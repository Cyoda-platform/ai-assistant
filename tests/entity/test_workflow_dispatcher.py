import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import entity.workflow_dispatcher as wfd
from entity.workflow_dispatcher import WorkflowDispatcher

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
