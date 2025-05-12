import pytest
import pytest_asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import httpx

import common.config.const as const
from common.config.config import config
from common.exception.exceptions import GuestChatsLimitExceededException
from entity.chat.workflow import ChatWorkflow
from entity.chat import workflow as wf_mod
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

    # stub get_project_file_name to return the template path
    async def mock_get_project_file_name(chat_id, file_name, git_branch_id=None):
        return str(template)

    monkeypatch.setattr(
        "entity.chat.workflow.get_project_file_name",
        mock_get_project_file_name
    )

    # stub _git_push
    monkeypatch.setattr("entity.chat.workflow._git_push", AsyncMock())

    await workflow.save_env_file(
        technical_id="chat123",
        entity=DummyChatEntity(),
        filename="env.template"
    )

    # confirm replacement
    content = template.read_text()
    assert content == "ID=chat123\n"

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
        "entity.chat.workflow.parse_from_string",
        lambda escaped_code: "decoded"
    )
    monkeypatch.setattr("entity.chat.workflow._save_file", AsyncMock())
    ent = DummyChatEntity()
    out = await workflow.save_file("id", ent, new_content="xyz", filename="f.txt")
    assert out == "File saved successfully"

@pytest.mark.asyncio
async def test_save_file_error(workflow, monkeypatch):
    def bad_parse(*args, **kwargs):
        raise ValueError("bad")
    monkeypatch.setattr(
        "entity.chat.workflow.parse_from_string",
        bad_parse
    )
    ent = DummyChatEntity()
    out = await workflow.save_file("id", ent, new_content="x", filename="f")
    assert "Error during saving file" in out
    assert ent.failed is True

@pytest.mark.asyncio
async def test_read_file(workflow, monkeypatch):
    monkeypatch.setattr(
        "entity.chat.workflow.read_file_util",
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
        "entity.chat.workflow.convert_state_diagram_to_jsonl_dataset",
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
        "entity.chat.workflow.build_workflow_from_jsonl",
        mock_build
    )
    monkeypatch.setattr(
        "entity.chat.workflow._save_file",
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
        "entity.chat.workflow.convert_to_mermaid",
        lambda d: "MERMAID"
    )
    out = await workflow.convert_workflow_json_to_state_diagram(
        "id", DummyChatEntity(),
        input_file_path=str(p)
    )
    assert out == "MERMAID"

@pytest.mark.asyncio
async def test_save_entity_templates(tmp_project_dir, workflow, monkeypatch):
    # Place design file under PROJECT_DIR/repo/entity
    design_dir = tmp_project_dir / "myrepo" / "entity"
    design_dir.mkdir(parents=True, exist_ok=True)
    design_file = design_dir / "entities_data_design.json"
    design = {
        "entities": [
            {"entity_name": "E1", "entity_data_example": {"x": 1}},
            {"entity_name": None}
        ]
    }
    design_file.write_text(json.dumps(design))

    # Patch get_project_file_name to accept the git_branch_id argument
    async def mock_get_project_file_name(chat_id, fn, git_branch_id=None):
        return str(design_file)

    monkeypatch.setattr(
        "entity.chat.workflow.get_project_file_name",
        mock_get_project_file_name
    )

    # Patch _save_file
    sf = AsyncMock()
    monkeypatch.setattr("entity.chat.workflow._save_file", sf)

    await workflow.save_entity_templates("id", DummyChatEntity())

    # Verify _save_file called once with correct params
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
        "entity.chat.workflow.get_most_similar_entity",
        lambda target, entity_list: "Bar"
    )
    out = await workflow._resolve_entity_name("Brr", branch_id="x")
    assert out == "Bar"












class DummyAgenticEntity:
    def __init__(self):
        self.user_id = "UserX"
        self.parent_id = "chatParent"
        self.workflow_cache = {"entity_name": "ent1"}
        self.edge_messages_store = {"t1": "edge-1"}
        self.awaited_entity_ids = ["e1", "e2"]
        self.scheduled_action = config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
        self.triggered_entity_id = "parent-123"
        self.triggered_entity_next_transition = "next-trans"

# ─── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_edit_existing_app_design_additional_feature_main_branch(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    params = {const.GIT_BRANCH_PARAM: "main", "user_request": "xyz"}
    # stub clone_repo shouldn't be called
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())

    out = await workflow.edit_existing_app_design_additional_feature("tech-5", ent, **params)
    assert out == "Modifications to main branch are not allowed"

@pytest.mark.asyncio
async def test_get_cyoda_guidelines(monkeypatch, workflow):
    # stub _fetch_data
    monkeypatch.setattr(workflow, "_fetch_data", AsyncMock(return_value="GUIDE"))
    out = await workflow.get_cyoda_guidelines("tech-6", DummyAgenticEntity(), workflow_name="wf1")
    assert out == "GUIDE"

@pytest.mark.asyncio
async def test__schedule_workflow_success(monkeypatch, workflow):
    # stub clone_repo
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())
    # stub launch_agentic_workflow
    monkeypatch.setattr(workflow.workflow_helper_service, "launch_agentic_workflow", AsyncMock(return_value="child-123"))
    ent = DummyAgenticEntity()

    res = await workflow._schedule_workflow(
        "tech-7",
        ent,
        entity_model=const.ModelName.CHAT_ENTITY.value,
        workflow_name="WF_NAME",
        params={const.GIT_BRANCH_PARAM: "branch-X"},
    )
    assert "child-123" in res
    wf_mod.clone_repo.assert_awaited_once()

@pytest.mark.asyncio
async def test__schedule_workflow_main_branch(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    res = await workflow._schedule_workflow(
        "tech-8",
        ent,
        entity_model="m",
        workflow_name="W",
        params={const.GIT_BRANCH_PARAM: "main"},
    )
    assert res == "Modifications to main branch are not allowed"

@pytest.mark.asyncio
async def test_deploy_cyoda_env_guest_and_success(monkeypatch, workflow):
    guest = DummyAgenticEntity()
    guest.user_id = "guest123"
    with pytest.raises(GuestChatsLimitExceededException):
        await workflow.deploy_cyoda_env("t", guest)

    user = DummyAgenticEntity()
    # stub _schedule_workflow
    monkeypatch.setattr(workflow, "_schedule_workflow", AsyncMock(return_value="OKAY"))
    res = await workflow.deploy_cyoda_env("t2", user)
    assert res == "OKAY"

@pytest.mark.asyncio
async def test_deploy_user_application_guest_and_success(monkeypatch, workflow):
    guest = DummyAgenticEntity()
    guest.user_id = "guestX"
    with pytest.raises(GuestChatsLimitExceededException):
        await workflow.deploy_user_application("t", guest)

    user = DummyAgenticEntity()
    monkeypatch.setattr(workflow, "_schedule_workflow", AsyncMock(return_value="DONE"))
    res = await workflow.deploy_user_application("t2", user)
    assert res == "DONE"

@pytest.mark.asyncio
async def test_add_new_entity_and_workflow_delegate(monkeypatch, workflow):
    # stub _schedule_workflow
    monkeypatch.setattr(workflow, "_schedule_workflow", AsyncMock(return_value="R1"))
    ent = DummyAgenticEntity()
    r1 = await workflow.add_new_entity_for_existing_app("t", ent, foo=1)
    assert r1 == "R1"
    r2 = await workflow.add_new_workflow("t", ent, foo=2)
    assert r2 == "R1"



@pytest.mark.asyncio
async def test_schedule_workflow_tasks(workflow, scheduler):
    ent = SimpleNamespace(
        awaited_entity_ids=["a", "b"],
        scheduled_action=config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
    )
    result = await workflow.schedule_workflow_tasks("tech-2", ent)
    assert result == "task-ok"
    scheduler.schedule_workflow_task.assert_called_once_with(
        technical_id="tech-2",
        awaited_entity_ids=ent.awaited_entity_ids,
        scheduled_action=config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
    )

@pytest.mark.asyncio
async def test_edit_existing_app_design_additional_feature_success(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    params = {"user_request": "do stuff", const.GIT_BRANCH_PARAM: "branch-1"}

    # stub clone_repo
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())
    # stub get_entities_list
    monkeypatch.setattr(workflow, "get_entities_list", AsyncMock(return_value=["entA", "entB"]))
    # stub read_file_util for *all* three calls:
    #   1) routes/routes.py
    #   2) entity/entA/workflow.py
    #   3) entity/entB/workflow.py
    monkeypatch.setattr(wf_mod, "read_file_util", AsyncMock(side_effect=[
        "def api(): pass",  # first call
        "codeA",             # second call
        "codeB",             # third call
    ]))
    # stub entity_service.add_item twice
    monkeypatch.setattr(workflow.entity_service, "add_item", AsyncMock(side_effect=["api-id", "desc-id"]))
    # stub launch_agentic_workflow
    monkeypatch.setattr(workflow.workflow_helper_service, "launch_agentic_workflow", AsyncMock(return_value="child-999"))

    out = await workflow.edit_existing_app_design_additional_feature("tech-4", ent, **params)
    assert out.startswith("Successfully scheduled workflow for updating user application")
    assert "child-999" in out

@pytest.mark.asyncio
async def test_parse_from_string_and_get_entities_list(tmp_project_dir, workflow):
    # parse_from_string is sync
    assert workflow.parse_from_string("\\u0041") == "A"

    # build fake entity dirs under tmp_project_dir
    branch = "branch123"
    base = tmp_project_dir / branch / config.REPOSITORY_NAME / "entity"
    base.mkdir(parents=True)
    (base / "E1").mkdir()
    (base / "E2").mkdir()

    # now await the async get_entities_list
    entities = await workflow.get_entities_list(branch)
    assert set(entities) == {"E1", "E2"}

@pytest.mark.asyncio
async def test__resolve_entity_name(monkeypatch, workflow):
    # 1) stub get_entities_list
    monkeypatch.setattr(workflow, "get_entities_list", AsyncMock(return_value=["apple", "banana"]))
    # 2) first patch returns "banana"
    monkeypatch.setattr(wf_mod, "get_most_similar_entity", lambda target, entity_list: "banana")
    res = await workflow._resolve_entity_name("banan", branch_id="b")
    assert res == "banana"

    # 3) second patch returns None (must use same kw names!)
    monkeypatch.setattr(wf_mod, "get_most_similar_entity", lambda target, entity_list: None)
    res2 = await workflow._resolve_entity_name("unknown", branch_id="b")
    assert res2 == "unknown"

# ─── Tests for clone_repo ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clone_repo_sets_branch_and_saves(tmp_path, monkeypatch, workflow):
    ent = DummyChatEntity()
    # stub out the global clone_repo and _save_file
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    res = await workflow.clone_repo("branch-XYZ", ent)

    wf_mod.clone_repo.assert_awaited_once_with(chat_id="branch-XYZ")
    wf_mod._save_file.assert_awaited_once_with("branch-XYZ", "branch-XYZ", "README.txt")
    assert ent.workflow_cache["branch_name"] == "branch-XYZ"
    assert res == const.BRANCH_READY_NOTIFICATION.format(branch_name="branch-XYZ")


# ─── Tests for init_chats ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_true(monkeypatch, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "true")
    ent = DummyChatEntity()
    # should simply return None and do nothing
    assert await workflow.init_chats("tech", ent) is None

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_false(monkeypatch, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "false")
    ent = DummyChatEntity()
    # still returns None
    assert await workflow.init_chats("tech", ent) is None


# ─── Tests for reset_failed_entity ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_failed_entity_clears_flag(workflow):
    ent = DummyAgenticEntity()
    ent.failed = True
    out = await workflow.reset_failed_entity("tech-id", ent)
    assert ent.failed is False
    assert out == "Retrying last step"


@pytest.mark.asyncio
async def test_validate_workflow_design_success(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    ent.edge_messages_store = {"tr": "edge-456"}
    # stub get_item
    monkeypatch.setattr(workflow.entity_service, "get_item", AsyncMock(return_value="raw-result"))
    # stub validate_ai_result
    monkeypatch.setattr(wf_mod, "validate_ai_result", lambda source, fname: (True, "GOOD"))
    out = await workflow.validate_workflow_design("tech", ent, transition="tr")
    assert out == "GOOD"

@pytest.mark.asyncio
async def test_validate_workflow_design_failure(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    ent.edge_messages_store = {"tr": "edge-789"}
    monkeypatch.setattr(workflow.entity_service, "get_item", AsyncMock(return_value="raw"))
    monkeypatch.setattr(wf_mod, "validate_ai_result", lambda source, fname: (False, "BAD"))
    out = await workflow.validate_workflow_design("tech", ent, transition="tr")
    assert out is None


# ─── Tests for has_workflow_code_validation_succeeded/failed ──────────────────

@pytest.mark.asyncio
async def test_has_validation_succeeded_and_failed(monkeypatch, workflow):
    ent = DummyAgenticEntity()
    ent.edge_messages_store = {"x": "edge-ok", "y": "edge-none"}

    # get_item returns non‐None for "edge-ok"
    async def fake_get(token, entity_model, entity_version, technical_id, meta):
        return "something" if technical_id == "edge-ok" else None

    monkeypatch.setattr(workflow.entity_service, "get_item", fake_get)

    ok = await workflow.has_workflow_code_validation_succeeded("t", ent, transition="x")
    not_ok = await workflow.has_workflow_code_validation_succeeded("t", ent, transition="y")
    assert ok is True
    assert not_ok is False

    failed = await workflow.has_workflow_code_validation_failed("t", ent, transition="x")
    not_failed = await workflow.has_workflow_code_validation_failed("t", ent, transition="y")
    assert failed is False
    assert not_failed is True


# ─── Tests for save_extracted_workflow_code ───────────────────────────────────

@pytest.mark.asyncio
async def test_save_extracted_workflow_code(monkeypatch, tmp_path, workflow):
    ent = DummyAgenticEntity()
    ent.parent_id = "parent123"
    ent.workflow_cache = {"entity_name": "MyEnt"}
    ent.edge_messages_store = {"go": "edge-xyz"}

    # stub get_item
    monkeypatch.setattr(workflow.entity_service, "get_item", AsyncMock(return_value="SRC_CODE"))
    # stub extract_function
    monkeypatch.setattr(wf_mod, "extract_function",
                        lambda source, function_name: ("no_fn_body", "fn_body"))
    # stub _save_file
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    out = await workflow.save_extracted_workflow_code("tech", ent, transition="go")
    wf_mod._save_file.assert_awaited_once_with(
        chat_id="parent123",
        _data="no_fn_body",
        item="entity/MyEnt/workflow.py"
    )
    assert out == "fn_body"


# ─── Tests for edit_existing_workflow & fail_workflow ─────────────────────────

@pytest.mark.asyncio
async def test_fail_workflow_returns_notification(workflow):
    ent = DummyAgenticEntity()
    out = await workflow.fail_workflow("FAIL-123", ent)
    expected = const.Notifications.FAILED_WORKFLOW.value.format(technical_id="FAIL-123")
    assert out == expected

@pytest.mark.asyncio
async def test_schedule_deploy_user_application_with_branch(monkeypatch, workflow):
    # arrange
    ent = DummyChatEntity()
    ent.workflow_cache = { const.GIT_BRANCH_PARAM: "feature-xyz" }
    expected_payload = {
        "repository_url": config.CLIENT_QUART_TEMPLATE_REPOSITORY_URL,
        "branch": "feature-xyz",
        "is_public": "true"
    }
    called = {}
    async def fake_schedule_deploy(technical_id, entity, scheduled_action, extra_payload):
        called.update({
            "technical_id": technical_id,
            "entity": entity,
            "scheduled_action": scheduled_action,
            "extra_payload": extra_payload
        })
        return "deploy-success"
    monkeypatch.setattr(workflow, "_schedule_deploy", fake_schedule_deploy)

    # act
    out = await workflow.schedule_deploy_user_application("tech-42", ent, foo="bar")

    # assert
    assert out == "deploy-success"
    assert called["technical_id"] == "tech-42"
    assert called["entity"] is ent
    assert called["scheduled_action"] == config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY
    assert called["extra_payload"] == expected_payload


@pytest.fixture
def chat_entity():
    """Minimal ChatEntity substitute."""
    return SimpleNamespace(
        user_id="User1",
        parent_id="parent-chat",
        workflow_cache={},
        edge_messages_store={},
        failed=False,
        transitions_memory=SimpleNamespace(
            conditions={}, current_iteration={}, max_iteration={}
        ),
    )

@pytest.fixture
def agentic_entity(chat_entity):
    """Extend chat_entity with AgenticFlowEntity–specific fields."""
    ae = chat_entity
    ae.awaited_entity_ids = []
    ae.scheduled_action = None
    return ae


# ─── schedule_deploy_user_application ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_schedule_deploy_user_application_with_branch(monkeypatch, chat_entity, workflow):
    chat_entity.workflow_cache = { const.GIT_BRANCH_PARAM: "feature-xyz" }
    expected = {
        "repository_url": config.CLIENT_QUART_TEMPLATE_REPOSITORY_URL,
        "branch": "feature-xyz",
        "is_public": "true",
    }
    called = {}
    async def fake_sched(technical_id, entity, scheduled_action, extra_payload):
        called.update({
            "technical_id": technical_id,
            "entity": entity,
            "scheduled_action": scheduled_action,
            "extra_payload": extra_payload,
        })
        return "deploy-success"

    monkeypatch.setattr(workflow, "_schedule_deploy", fake_sched)

    out = await workflow.schedule_deploy_user_application("tech-42", chat_entity)
    assert out == "deploy-success"
    assert called["technical_id"] == "tech-42"
    assert called["entity"] is chat_entity
    assert called["scheduled_action"] == config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY
    assert called["extra_payload"] == expected

# ─── clone_repo ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clone_repo_sets_branch_and_saves(monkeypatch, chat_entity, workflow):
    # stub the external helpers
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    res = await workflow.clone_repo("branch-XYZ", chat_entity)

    wf_mod.clone_repo.assert_awaited_once_with(chat_id="branch-XYZ")
    wf_mod._save_file.assert_awaited_once_with("branch-XYZ", "branch-XYZ", "README.txt")
    assert chat_entity.workflow_cache["branch_name"] == "branch-XYZ"
    assert res == const.BRANCH_READY_NOTIFICATION.format(branch_name="branch-XYZ")


# ─── init_chats ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_true(monkeypatch, chat_entity, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "true")
    assert await workflow.init_chats("tech", chat_entity) is None

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_false(monkeypatch, chat_entity, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "false")
    # still just returns None
    assert await workflow.init_chats("tech", chat_entity) is None


# ─── reset_failed_entity ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_failed_entity_clears_flag(agentic_entity, workflow):
    agentic_entity.failed = True
    out = await workflow.reset_failed_entity("tech-id", agentic_entity)
    assert agentic_entity.failed is False
    assert out == "Retrying last step"


# ─── validate_workflow_design ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_validate_workflow_design_success(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"tr": "edge-456"}
    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="raw-result")
    )
    monkeypatch.setattr(
        wf_mod, "validate_ai_result", lambda source, fname: (True, "GOOD")
    )

    out = await workflow.validate_workflow_design("tech", chat_entity, transition="tr")
    assert out == "GOOD"

@pytest.mark.asyncio
async def test_validate_workflow_design_failure(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"tr": "edge-789"}
    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="raw")
    )
    monkeypatch.setattr(
        wf_mod, "validate_ai_result", lambda source, fname: (False, "BAD")
    )

    out = await workflow.validate_workflow_design("tech", chat_entity, transition="tr")
    assert out is None


# ─── has_workflow_code_validation ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_has_validation_succeeded_and_failed(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"x": "edge-ok", "y": "edge-none"}

    async def fake_get(token, entity_model, entity_version, technical_id, meta):
        return "something" if technical_id == "edge-ok" else None

    monkeypatch.setattr(workflow.entity_service, "get_item", fake_get)

    ok = await workflow.has_workflow_code_validation_succeeded(
        "t", chat_entity, transition="x"
    )
    not_ok = await workflow.has_workflow_code_validation_succeeded(
        "t", chat_entity, transition="y"
    )
    assert ok is True
    assert not_ok is False

    failed = await workflow.has_workflow_code_validation_failed(
        "t", chat_entity, transition="x"
    )
    not_failed = await workflow.has_workflow_code_validation_failed(
        "t", chat_entity, transition="y"
    )
    assert failed is False
    assert not_failed is True


# ─── save_extracted_workflow_code ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_extracted_workflow_code(monkeypatch, chat_entity, workflow):
    chat_entity.parent_id = "parent123"
    chat_entity.workflow_cache = {"entity_name": "MyEnt"}
    chat_entity.edge_messages_store = {"go": "edge-xyz"}

    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="SRC_CODE")
    )
    monkeypatch.setattr(
        wf_mod, "extract_function", lambda source, function_name: ("no_fn_body", "fn_body")
    )
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    out = await workflow.save_extracted_workflow_code("tech", chat_entity, transition="go")
    wf_mod._save_file.assert_awaited_once_with(
        chat_id="parent123",
        _data="no_fn_body",
        item="entity/MyEnt/workflow.py"
    )
    assert out == "fn_body"


# ─── edit_existing_workflow & fail_workflow ───────────────────────────────────

@pytest.mark.asyncio
async def test_fail_workflow_returns_notification(chat_entity, workflow):
    out = await workflow.fail_workflow("FAIL-123", chat_entity)
    expected = const.Notifications.FAILED_WORKFLOW.value.format(technical_id="FAIL-123")
    assert out == expected




@pytest.fixture
def chat_entity():
    """Minimal ChatEntity substitute."""
    return SimpleNamespace(
        user_id="User1",
        parent_id="parent-chat",
        workflow_cache={},
        edge_messages_store={},
        failed=False,
        transitions_memory=SimpleNamespace(
            conditions={}, current_iteration={}, max_iteration={}
        ),
    )

@pytest.fixture
def agentic_entity(chat_entity):
    """Extend chat_entity with AgenticFlowEntity–specific fields."""
    ae = chat_entity
    ae.awaited_entity_ids = []
    ae.scheduled_action = None
    return ae


# ─── schedule_deploy_user_application ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_schedule_deploy_user_application_without_branch(monkeypatch, chat_entity, workflow):
    # no git_branch in cache
    expected = {
        "repository_url": config.CLIENT_QUART_TEMPLATE_REPOSITORY_URL,
        "branch": None,
        "is_public": "true",
    }
    async def fake_sched(*args, **kwargs):
        return kwargs["extra_payload"]

    monkeypatch.setattr(workflow, "_schedule_deploy", fake_sched)

    out = await workflow.schedule_deploy_user_application("tech-99", chat_entity)
    assert out == expected


# ─── clone_repo ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clone_repo_sets_branch_and_saves(monkeypatch, chat_entity, workflow):
    monkeypatch.setattr(wf_mod, "clone_repo", AsyncMock())
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    res = await workflow.clone_repo("branch-XYZ", chat_entity)

    wf_mod.clone_repo.assert_awaited_once_with(chat_id="branch-XYZ")
    wf_mod._save_file.assert_awaited_once_with("branch-XYZ", "branch-XYZ", "README.txt")
    assert chat_entity.workflow_cache["branch_name"] == "branch-XYZ"
    assert res == const.BRANCH_READY_NOTIFICATION.format(branch_name="branch-XYZ")


# ─── init_chats ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_true(monkeypatch, chat_entity, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "true")
    assert await workflow.init_chats("tech", chat_entity) is None

@pytest.mark.asyncio
async def test_init_chats_when_mock_ai_false(monkeypatch, chat_entity, workflow):
    monkeypatch.setattr(config, "MOCK_AI", "false")
    assert await workflow.init_chats("tech", chat_entity) is None


# ─── reset_failed_entity ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_failed_entity_clears_flag(agentic_entity, workflow):
    agentic_entity.failed = True
    out = await workflow.reset_failed_entity("tech-id", agentic_entity)
    assert agentic_entity.failed is False
    assert out == "Retrying last step"


# ─── validate_workflow_design ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_validate_workflow_design_success(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"tr": "edge-456"}
    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="raw-result")
    )
    monkeypatch.setattr(
        wf_mod, "validate_ai_result", lambda source, fname: (True, "GOOD")
    )

    out = await workflow.validate_workflow_design("tech", chat_entity, transition="tr")
    assert out == "GOOD"

@pytest.mark.asyncio
async def test_validate_workflow_design_failure(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"tr": "edge-789"}
    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="raw")
    )
    monkeypatch.setattr(
        wf_mod, "validate_ai_result", lambda source, fname: (False, "BAD")
    )

    out = await workflow.validate_workflow_design("tech", chat_entity, transition="tr")
    assert out is None


# ─── has_workflow_code_validation ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_has_validation_succeeded_and_failed(monkeypatch, chat_entity, workflow):
    chat_entity.edge_messages_store = {"x": "edge-ok", "y": "edge-none"}

    async def fake_get(token, entity_model, entity_version, technical_id, meta):
        return "something" if technical_id == "edge-ok" else None

    monkeypatch.setattr(workflow.entity_service, "get_item", fake_get)

    ok = await workflow.has_workflow_code_validation_succeeded(
        "t", chat_entity, transition="x"
    )
    not_ok = await workflow.has_workflow_code_validation_succeeded(
        "t", chat_entity, transition="y"
    )
    assert ok is True
    assert not_ok is False

    failed = await workflow.has_workflow_code_validation_failed(
        "t", chat_entity, transition="x"
    )
    not_failed = await workflow.has_workflow_code_validation_failed(
        "t", chat_entity, transition="y"
    )
    assert failed is False
    assert not_failed is True


# ─── save_extracted_workflow_code ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_extracted_workflow_code(monkeypatch, chat_entity, workflow):
    chat_entity.parent_id = "parent123"
    chat_entity.workflow_cache = {"entity_name": "MyEnt"}
    chat_entity.edge_messages_store = {"go": "edge-xyz"}

    monkeypatch.setattr(
        workflow.entity_service, "get_item", AsyncMock(return_value="SRC_CODE")
    )
    monkeypatch.setattr(
        wf_mod, "extract_function", lambda source, function_name: ("no_fn_body", "fn_body")
    )
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    out = await workflow.save_extracted_workflow_code("tech", chat_entity, transition="go")
    wf_mod._save_file.assert_awaited_once_with(
        chat_id="parent123",
        _data="no_fn_body",
        item="entity/MyEnt/workflow.py"
    )
    assert out == "fn_body"


# ─── edit_existing_workflow & fail_workflow ───────────────────────────────────

@pytest.mark.asyncio
async def test_edit_existing_workflow_delegates(monkeypatch, chat_entity, workflow):
    fake = AsyncMock(return_value="EDIT_OK")
    monkeypatch.setattr(workflow, "_schedule_workflow", fake)

    out = await workflow.edit_existing_workflow("t-id", chat_entity, foo="bar")
    assert out == "EDIT_OK"

    fake.assert_awaited_once_with(
        technical_id="t-id",
        entity=chat_entity,
        entity_model=const.ModelName.CHAT_ENTITY.value,
        workflow_name=const.ModelName.EDIT_EXISTING_WORKFLOW.value,
        params={"foo": "bar"},
        resolve_entity_name=True,
    )

@pytest.mark.asyncio
async def test_fail_workflow_returns_notification(chat_entity, workflow):
    out = await workflow.fail_workflow("FAIL-123", chat_entity)
    expected = const.Notifications.FAILED_WORKFLOW.value.format(technical_id="FAIL-123")
    assert out == expected

@pytest.mark.asyncio
async def test_register_workflow_with_app_no_models(monkeypatch, tmp_path, chat_entity, workflow):
    # JSON with empty entity_models → should trigger the "no workflows" exception path
    json_data = {
        "entity_models": [],
        "file_without_workflow": {"code": "xyz"}
    }
    json_str = json.dumps(json_data)

    monkeypatch.setattr(
        wf_mod, "get_project_file_name",
        lambda tech, fname: str(tmp_path / "f")
    )
    monkeypatch.setattr(
        wf_mod.aiofiles, "open",
        lambda path, mode: DummyAioFile(json_str)
    )
    monkeypatch.setattr(
        wf_mod.json, "load",
        lambda content: json_data
    )
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    # Run
    await workflow.register_workflow_with_app("tech456", chat_entity, filename="f")

    # Should have flipped the failed flag and recorded the error
    assert chat_entity.failed is True
    assert "No workflows generated for tech456" in chat_entity.error



#==========================


@pytest.fixture
def flow_entity():
    """Minimal AgenticFlowEntity substitute."""
    return SimpleNamespace(
        user_id="User1",
        parent_id="parent-chat",
        workflow_cache={},
        edge_messages_store={},
        failed=False,
        error=None,
        scheduled_entities=[],
        transitions_memory=SimpleNamespace(
            conditions={}, current_iteration={}, max_iteration={}
        ),
    )

# ─── Dummy aiofiles.open context manager ───────────────────────────────────────

class DummyAioFile:
    def __init__(self, content: str):
        self._content = content
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def read(self):
        return self._content

# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_workflow_with_app_success(tmp_path, monkeypatch, flow_entity, workflow):
    # Prepare JSON with two entity_models and file_without_workflow
    json_data = {
        "entity_models": [
            {
                "cat_data": {
                    "name": "process_cat_data",
                    "code_with_necessary_imports_and_constants": "import x",
                    "content": "async def process_cat_data(entity): pass"
                }
            },
            {
                "dog_data": {
                    "name": "process_dog_data",
                    "code_with_necessary_imports_and_constants": "import y",
                    "content": "async def process_dog_data(entity): pass"
                }
            }
        ],
        "file_without_workflow": {
            "code": "from dataclasses import dataclass"
        }
    }
    json_str = json.dumps(json_data)

    # Stub get_project_file_name → a dummy path
    fake_path = tmp_path / "work.json"
    fake_path.write_text("ignored")
    monkeypatch.setattr(
        wf_mod, "get_project_file_name",
        lambda tech, fname: str(fake_path)
    )

    # Stub aiofiles.open to yield our JSON
    monkeypatch.setattr(
        wf_mod.aiofiles, "open",
        lambda path, mode: DummyAioFile(json_str)
    )

    # Stub json.load to parse our JSON string
    monkeypatch.setattr(
        wf_mod.json, "load",
        lambda f: json_data
    )

    # Stub out save, add_item, launch_agentic, launch_scheduled
    save_file = AsyncMock()
    monkeypatch.setattr(wf_mod, "_save_file", save_file)

    add_item = AsyncMock(side_effect=["edge1", "edge2"])
    monkeypatch.setattr(workflow.entity_service, "add_item", add_item)

    launch_agentic = AsyncMock(side_effect=["child1", "child2"])
    monkeypatch.setattr(
        workflow.workflow_helper_service,
        "launch_agentic_workflow",
        launch_agentic
    )

    launch_sched = AsyncMock(return_value="schedule123")
    monkeypatch.setattr(
        workflow.workflow_helper_service,
        "launch_scheduled_workflow",
        launch_sched
    )

    # Execute
    await workflow.register_workflow_with_app("tech123", flow_entity, filename="work.json")

    # Assertions
    save_file.assert_awaited_once_with(
        chat_id="tech123",
        _data="from dataclasses import dataclass",
        item="routes/routes.py"
    )

    assert add_item.await_count == 2

    # Check workflow_cache passed to each launch_agentic_workflow
    _, kwargs1 = launch_agentic.await_args_list[0]
    assert kwargs1["workflow_cache"] == {
        "workflow_function": "process_cat_data",
        "entity_name": "cat_data"
    }
    _, kwargs2 = launch_agentic.await_args_list[1]
    assert kwargs2["workflow_cache"] == {
        "workflow_function": "process_dog_data",
        "entity_name": "dog_data"
    }

    # Check scheduled_workflow appended
    launch_sched.assert_awaited_once_with(
        entity_service=workflow.entity_service,
        awaited_entity_ids=["child1", "child2"],
        triggered_entity_id="tech123"
    )
    assert flow_entity.scheduled_entities == ["schedule123"]
    assert flow_entity.failed is False


@pytest.mark.asyncio
async def test_register_workflow_with_app_no_models(tmp_path, monkeypatch, flow_entity, workflow):
    # JSON with empty entity_models
    json_data = {
        "entity_models": [],
        "file_without_workflow": {"code": "xyz"}
    }
    json_str = json.dumps(json_data)

    monkeypatch.setattr(
        wf_mod, "get_project_file_name",
        lambda tech, fname: str(tmp_path / "f")
    )
    monkeypatch.setattr(
        wf_mod.aiofiles, "open",
        lambda path, mode: DummyAioFile(json_str)
    )
    monkeypatch.setattr(
        wf_mod.json, "load",
        lambda f: json_data
    )
    monkeypatch.setattr(wf_mod, "_save_file", AsyncMock())

    # Execute
    await workflow.register_workflow_with_app("tech456", flow_entity, filename="f")

    # Should have flipped the failed flag and recorded the error
    assert flow_entity.failed is True
    assert "No workflows generated for tech456" in flow_entity.error


@pytest.mark.asyncio
async def test_register_workflow_with_app_file_error(monkeypatch, flow_entity, workflow):
    # Make get_project_file_name return anything
    monkeypatch.setattr(
        wf_mod, "get_project_file_name",
        lambda tech, fname: "/nonexistent"
    )
    # Stub aiofiles.open as a sync function that raises
    def fake_open(path, mode):
        raise Exception("open failed")
    monkeypatch.setattr(wf_mod.aiofiles, "open", fake_open)

    # Execute
    await workflow.register_workflow_with_app("tech789", flow_entity, filename="unused.json")

    # Should catch the exception and set failed + error
    assert flow_entity.failed is True
    assert "open failed" in flow_entity.error