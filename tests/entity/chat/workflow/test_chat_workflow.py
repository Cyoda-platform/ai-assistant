import pytest
import pytest_asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import aiofiles

import common.config.const as const
from common.config.config import config
from entity.chat.workflow.workflow import ChatWorkflow

# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
def tmp_project_dir(tmp_path, monkeypatch):
    # Create a fake repo under tmp_path
    repo = tmp_path / "myrepo"
    (repo / "entity").mkdir(parents=True)
    # Override config
    monkeypatch.setattr(config, "PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(config, "REPOSITORY_NAME", "myrepo")
    return tmp_path

@pytest_asyncio.fixture
def helper(monkeypatch):
    h = MagicMock()
    h.launch_scheduled_workflow = AsyncMock(return_value="sched-xyz")
    return h

@pytest_asyncio.fixture
def entity_service():
    svc = MagicMock()
    svc.add_item = AsyncMock(return_value="child-123")
    return svc

@pytest_asyncio.fixture
def scheduler():
    s = MagicMock()
    s.schedule_workflow_task = MagicMock(return_value="task-ok")
    return s

@pytest_asyncio.fixture
def workflow(helper, entity_service, scheduler):
    return ChatWorkflow(
        dataset=None,
        workflow_helper_service=helper,
        entity_service=entity_service,
        scheduler=scheduler,
        cyoda_auth_service="token-abc"
    )

# ─── Dummy Entity ───────────────────────────────────────────────────────────

class DummyChatEntity:
    def __init__(self):
        self.user_id = "User1"
        self.workflow_cache = {"git_branch": "feature-1"}
        self.scheduled_entities = []
        self.locked = False
        self.transitions_memory = SimpleNamespace(
            conditions={}, current_iteration={}, max_iteration={}
        )

# ─── Tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_env_file(tmp_path, monkeypatch, workflow):
    # create template
    template = tmp_path / "env.template"
    template.write_text("ID=CHAT_ID_VAR\n")
    # stub get_project_file_name to return that path
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.get_project_file_name",
        lambda chat_id, file_name: str(template)
    )
    # stub git_push
    monkeypatch.setattr("entity.chat.workflow.workflow._git_push", AsyncMock())

    await workflow.save_env_file(
        technical_id="chat123",
        entity=DummyChatEntity(),
        filename="env.template"
    )

    # confirm replacement
    content = template.read_text()
    assert "ID=chat123" in content

@pytest.mark.asyncio
async def test_schedule_deploy_env_success(monkeypatch, workflow):
    action = config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
    # point the URL map
    monkeypatch.setitem(config.ACTION_URL_MAP, action, "https://ci.example/build")
    # stub send_cyoda_request to return a plain dict
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.send_cyoda_request",
        AsyncMock(return_value={"json": {"build_id": "build789"}})
    )

    ent = DummyChatEntity()
    result = await workflow.schedule_deploy_env("chat123", ent)

    assert "build789" in result
    assert ent.scheduled_entities == ["sched-xyz"]

@pytest.mark.asyncio
async def test_web_search_success(monkeypatch, workflow):
    snippet = "Hello world!"
    fake = MagicMock(json=lambda: {"items":[{"snippet": snippet}]}, raise_for_status=lambda: None)
    async def fake_get(self, url, params=None):
        return fake
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    out = await workflow.web_search("id", DummyChatEntity(), query="foo")
    assert out == snippet

@pytest.mark.asyncio
async def test_web_search_failure(monkeypatch, workflow):
    async def bad_get(self, url, params=None):
        raise RuntimeError("boom")
    monkeypatch.setattr(httpx.AsyncClient, "get", bad_get)

    ent = DummyChatEntity()
    out = await workflow.web_search("id", ent, query="foo")
    assert "Error during search" in out
    assert ent.failed is True

@pytest.mark.asyncio
async def test_fetch_data_paragraphs(workflow, monkeypatch):
    html = "<p>Para1</p><p>Para2</p>"
    fake = MagicMock(text=html, raise_for_status=lambda: None)
    async def fake_get(self, url):
        return fake
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    out = await workflow._fetch_data("http://x")
    assert "Para1" in out and "Para2" in out

@pytest.mark.asyncio
async def test_fetch_data_no_paragraphs(workflow, monkeypatch):
    html = "Just text"
    fake = MagicMock(text=html, raise_for_status=lambda: None)
    async def fake_get(self, url):
        return fake
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    out = await workflow._fetch_data("http://x")
    assert out == "Just text"

@pytest.mark.asyncio
async def test_fetch_data_error(workflow, monkeypatch):
    async def bad(self, url):
        raise Exception("fail")
    monkeypatch.setattr(httpx.AsyncClient, "get", bad)

    out = await workflow._fetch_data("url")
    assert "issues while doing your task" in out

@pytest.mark.asyncio
async def test_web_scrape_success(workflow, monkeypatch):
    html = '<span class="a">X</span><span class="a">Y</span>'
    fake = MagicMock(text=html, raise_for_status=lambda: None)
    async def fake_get(self, url):
        return fake
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    out = await workflow.web_scrape("id", DummyChatEntity(), url="u", selector=".a")
    assert "X" in out and "Y" in out

@pytest.mark.asyncio
async def test_web_scrape_no_match(workflow, monkeypatch):
    fake = MagicMock(text="<html></html>", raise_for_status=lambda: None)
    async def fake_get(self, url):
        return fake
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    out = await workflow.web_scrape("id", DummyChatEntity(), url="u", selector=".zzz")
    assert "No elements found" in out

@pytest.mark.asyncio
async def test_save_file_success(workflow, monkeypatch):
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.parse_from_string",
        lambda escaped_code: "decoded"
    )
    monkeypatch.setattr("entity.chat.workflow.workflow._save_file", AsyncMock())
    ent = DummyChatEntity()
    out = await workflow.save_file("id", ent, new_content="xyz", filename="f.txt")
    assert out == "File saved successfully"

@pytest.mark.asyncio
async def test_save_file_error(workflow, monkeypatch):
    def bad_parse(*args, **kwargs):
        raise ValueError("bad")
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.parse_from_string",
        bad_parse
    )
    ent = DummyChatEntity()
    out = await workflow.save_file("id", ent, new_content="x", filename="f")
    assert "Error during saving file" in out
    assert ent.failed is True

@pytest.mark.asyncio
async def test_read_file(workflow, monkeypatch):
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.read_file_util",
        AsyncMock(return_value="OK")
    )
    out = await workflow.read_file("id", DummyChatEntity(), filename="any")
    assert out == "OK"

@pytest.mark.asyncio
async def test_set_additional_question_flag_missing_transition(workflow):
    ent = DummyChatEntity()
    with pytest.raises(ValueError):
        await workflow.set_additional_question_flag("id", ent)

@pytest.mark.asyncio
async def test_set_additional_question_flag_sets_flag(workflow):
    ent = DummyChatEntity()
    await workflow.set_additional_question_flag(
        "id",
        ent,
        transition="T",
        require_additional_question_flag=False
    )
    assert ent.transitions_memory.conditions["T"]["require_additional_question"] is False

@pytest.mark.asyncio
async def test_is_stage_completed_iterations_and_conditions(workflow):
    ent = DummyChatEntity()
    # iteration > max
    ent.transitions_memory.current_iteration["X"] = 5
    ent.transitions_memory.max_iteration["X"] = 3
    out1 = await workflow.is_stage_completed("id", ent, transition="X")
    assert out1 is True

    # condition requires no additional question
    ent.transitions_memory.current_iteration.clear()
    ent.transitions_memory.conditions["Y"] = {"require_additional_question": False}
    out2 = await workflow.is_stage_completed("id", ent, transition="Y")
    assert out2 is True

    # no condition entry
    ent.transitions_memory.conditions.clear()
    out3 = await workflow.is_stage_completed("id", ent, transition="Z")
    assert out3 is False

@pytest.mark.asyncio
async def test_is_chat_locked_and_unlocked(workflow):
    ent = DummyChatEntity()
    ent.locked = True
    assert await workflow.is_chat_locked("id", ent) is True
    assert await workflow.is_chat_unlocked("id", ent) is False

@pytest.mark.asyncio
async def test_get_weather_and_humidity(workflow):
    ent = DummyChatEntity()
    w = await workflow.get_weather("id", ent, city="Montevideo")
    h = await workflow.get_humidity("id", ent, city="Montevideo")
    assert w["city"] == "Montevideo" and "°C" in w["temperature"]
    assert h["humidity"].endswith("%")

@pytest.mark.asyncio
async def test_convert_diagram_and_processed_dataset(workflow, monkeypatch):
    # verify convert_state_diagram_to_jsonl_dataset is called
    mock_convert = MagicMock()
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.convert_state_diagram_to_jsonl_dataset",
        mock_convert
    )
    await workflow.convert_diagram_to_dataset(
        "id", DummyChatEntity(),
        input_file_path="in", output_file_path="out"
    )
    assert mock_convert.call_count == 1

    # verify build_workflow_from_jsonl and _save_file are awaited
    mock_build = AsyncMock(return_value="RES")
    mock_save = AsyncMock()
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.build_workflow_from_jsonl",
        mock_build
    )
    monkeypatch.setattr(
        "entity.chat.workflow.workflow._save_file",
        mock_save
    )

    await workflow.convert_workflow_processed_dataset_to_json(
        "id", DummyChatEntity(),
        input_file_path="in2", output_file_path="out2"
    )
    assert mock_build.await_count == 1
    assert mock_save.await_count == 1


@pytest.mark.asyncio
async def test_convert_json_to_state_diagram(workflow, tmp_path, monkeypatch):
    data = {"foo": "bar"}
    p = tmp_path / "data.json"
    p.write_text(json.dumps(data))
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.convert_to_mermaid",
        lambda d: "MERMAID"
    )
    out = await workflow.convert_workflow_json_to_state_diagram(
        "id", DummyChatEntity(),
        input_file_path=str(p)
    )
    assert out == "MERMAID"

@pytest.mark.asyncio
async def test_save_entity_templates(tmp_project_dir, workflow, monkeypatch):
    # place design file under PROJECT_DIR/repo/entity
    design_dir = tmp_project_dir / "myrepo" / "entity"
    design_dir.mkdir(parents=True, exist_ok=True)
    design_file = design_dir / "entities_data_design.json"
    design = {"entities":[{"entity_name":"E1","entity_data_example":{"x":1}},{"entity_name":None}]}
    design_file.write_text(json.dumps(design))

    monkeypatch.setattr(
        "entity.chat.workflow.workflow.get_project_file_name",
        lambda chat_id, fn: str(design_file)
    )
    sf = AsyncMock()
    monkeypatch.setattr("entity.chat.workflow.workflow._save_file", sf)

    await workflow.save_entity_templates("id", DummyChatEntity())
    # should have been called once for E1
    assert sf.await_count == 1
    args = sf.await_args_list[0][1]
    assert args["item"] == "entity/E1/E1.json"

@pytest.mark.asyncio
async def test_build_general_application(workflow):
    # missing user_request
    out1 = await workflow.build_general_application("id", DummyChatEntity())
    assert "parameter user_request is required" in out1

    # success
    workflow.workflow_helper_service.launch_agentic_workflow = AsyncMock(return_value="child-abc")
    out2 = await workflow.build_general_application(
        "id", DummyChatEntity(), user_request="hey"
    )
    assert "child-abc" in out2

@pytest.mark.asyncio
async def test_get_entities_list(tmp_project_dir, workflow):
    # create branch directory under PROJECT_DIR
    base = tmp_project_dir / "anything" / "myrepo" / "entity"
    base.mkdir(parents=True, exist_ok=True)
    (base / "A").mkdir()
    (base / "B").mkdir()

    res = await workflow.get_entities_list(branch_id="anything")
    assert set(res) == {"A", "B"}

def test_parse_from_string(workflow):
    s = "Line1\\nLine2"
    out = workflow.parse_from_string(s)
    assert out == "Line1\nLine2"

@pytest.mark.asyncio
async def test_resolve_entity_name(workflow, monkeypatch):
    # stub the list and the similarity function in module under test
    monkeypatch.setattr(workflow, "get_entities_list", AsyncMock(return_value=["Foo","Bar"]))
    monkeypatch.setattr(
        "entity.chat.workflow.workflow.get_most_similar_entity",
        lambda target, entity_list: "Bar"
    )
    out = await workflow._resolve_entity_name("Brr", branch_id="x")
    assert out == "Bar"
