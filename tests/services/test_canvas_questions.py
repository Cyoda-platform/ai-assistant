import asyncio
import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from services.chat_service import ChatService
from entity.model import ModelConfig, AIMessage


@pytest.fixture
def service_mocks():
    entity_service = MagicMock()
    entity_service.get_items_by_condition = AsyncMock()
    entity_service.add_item = AsyncMock()
    entity_service.get_item = AsyncMock()
    entity_service.get_items = AsyncMock()
    entity_service.delete_item = AsyncMock()

    ai_agent = MagicMock()
    ai_agent.run_agent = AsyncMock()

    cyoda_auth_service = MagicMock()
    chat_lock = asyncio.Lock()

    data_service = MagicMock()
    data_service.get_entities_by_user_name = AsyncMock()
    data_service.get_entities_by_user_name_and_workflow_name = AsyncMock()

    svc = ChatService(entity_service, cyoda_auth_service, chat_lock, ai_agent, data_service)
    return svc, entity_service, data_service, ai_agent


def create_selective_mock_open(prompt_content):
    """
    Create a mock that only mocks the prompt file, allowing schema files to load normally.
    """
    original_open = open

    def selective_open(file, *args, **kwargs):
        # Convert to Path for comparison
        file_path = Path(file) if not isinstance(file, Path) else file

        # Only mock the system_prompt.md file
        if 'system_prompt.md' in str(file_path):
            return mock_open(read_data=prompt_content)()

        # For all other files (including schemas), use real open
        return original_open(file, *args, **kwargs)

    return selective_open


@pytest.mark.asyncio
async def test_submit_canvas_question_entity_json(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    # Mock AI response
    entity_config = {
        "name": "pet",
        "version": "1",
        "description": "Pet entity for adoption system",
        "fields": [
            {"name": "name", "type": "string", "required": True, "description": "Pet name"},
            {"name": "age", "type": "integer", "required": True, "description": "Pet age in years"},
            {"name": "breed", "type": "string", "required": False, "description": "Pet breed"}
        ],
        "relationships": []
    }
    ai_agent.run_agent.return_value = json.dumps(entity_config)

    # Mock file reading for system prompt only
    mock_prompt = "You are a helpful AI assistant for generating application configurations."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id="chat123",
            question="Create a Pet entity with name, age, and breed",
            response_type="entity_json",
            context={"app_name": "Pet Adoption System"}
        )

    # Verify result structure
    assert "message" in result
    assert "hook" in result
    assert result["hook"]["type"] == "entity_config"
    assert result["hook"]["action"] == "preview"
    assert result["hook"]["data"] == entity_config

    # Verify AI agent was called correctly
    ai_agent.run_agent.assert_awaited_once()
    call_args = ai_agent.run_agent.call_args
    assert call_args.kwargs["technical_id"] == "chat123"
    assert call_args.kwargs["tools"] is None
    assert call_args.kwargs["model"].model_name == "gpt-4o"
    assert "response_format" in call_args.kwargs
    assert call_args.kwargs["response_format"]["name"] == "entity_config_schema"


@pytest.mark.asyncio
async def test_submit_canvas_question_workflow_json(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    # Mock AI response
    workflow_config = {
        "name": "pet_workflow",
        "version": "1.0",
        "description": "Pet lifecycle workflow",
        "initialState": "initial",
        "active": True,
        "states": {
            "initial": {
                "transitions": [
                    {"name": "create_pet", "next": "active", "manual": False}
                ]
            },
            "active": {
                "transitions": [
                    {"name": "adopt_pet", "next": "adopted", "manual": True}
                ]
            },
            "adopted": {
                "transitions": []
            }
        }
    }
    ai_agent.run_agent.return_value = json.dumps(workflow_config)

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id=None,
            question="Create a workflow for pet adoption",
            response_type="workflow_json",
            context={}
        )

    assert result["hook"]["type"] == "workflow_config"
    assert result["hook"]["data"] == workflow_config

    # When chat_id is None, should use default
    call_args = ai_agent.run_agent.call_args
    assert call_args.kwargs["technical_id"] == "canvas_question"


@pytest.mark.asyncio
async def test_submit_canvas_question_app_config_json(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    app_config = {
        "name": "Pet Adoption System",
        "description": "System for managing pet adoptions",
        "language": "python",
        "entities": [
            {"name": "pet", "version": "1", "workflows": [{"name": "pet_workflow", "version": "1.0"}]},
            {"name": "adopter", "version": "1", "workflows": []}
        ],
        "environments": [
            {"name": "development", "description": "Dev environment"},
            {"name": "production", "description": "Prod environment"}
        ]
    }
    ai_agent.run_agent.return_value = json.dumps(app_config)

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id="chat456",
            question="Create an app config for pet adoption system",
            response_type="app_config_json",
            context={"language": "python"}
        )

    assert result["hook"]["type"] == "app_config"
    assert result["hook"]["data"] == app_config


@pytest.mark.asyncio
async def test_submit_canvas_question_environment_json(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    env_config = {
        "name": "production",
        "description": "Production environment",
        "config": {
            "database_url": "postgresql://prod-db:5432/petdb",
            "api_url": "https://api.petadoption.com",
            "debug": False
        }
    }
    ai_agent.run_agent.return_value = json.dumps(env_config)

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id="chat789",
            question="Create a production environment config",
            response_type="environment_json",
            context={}
        )

    assert result["hook"]["type"] == "environment_config"
    assert result["hook"]["data"] == env_config


@pytest.mark.asyncio
async def test_submit_canvas_question_with_context(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    ai_agent.run_agent.return_value = json.dumps({"name": "test", "version": "1", "fields": []})

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        await svc.submit_canvas_question(
            chat_id="chat123",
            question="Create an entity",
            response_type="entity_json",
            context={
                "app_name": "My App",
                "existing_entities": ["user", "product"],
                "existing_workflows": ["user_workflow"],
                "language": "python"
            }
        )

    # Verify context was added to question
    call_args = ai_agent.run_agent.call_args
    messages = call_args.kwargs["messages"]
    user_message = messages[1].content

    assert "Application: My App" in user_message
    assert "Existing entities: user, product" in user_message
    assert "Existing workflows: user_workflow" in user_message
    assert "Language: python" in user_message


@pytest.mark.asyncio
async def test_submit_canvas_question_invalid_json_response(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    # AI returns invalid JSON
    ai_agent.run_agent.return_value = "This is not JSON"

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id="chat123",
            question="Create an entity",
            response_type="entity_json",
            context={}
        )

    assert "error" in result
    assert "Failed to generate configuration" in result["error"]
    assert "not valid JSON" in result["details"]["message"]


@pytest.mark.asyncio
async def test_submit_canvas_question_ai_agent_exception(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    # AI agent raises exception
    ai_agent.run_agent.side_effect = Exception("AI service unavailable")

    mock_prompt = "You are a helpful AI assistant."
    with patch("builtins.open", side_effect=create_selective_mock_open(mock_prompt)):
        result = await svc.submit_canvas_question(
            chat_id="chat123",
            question="Create an entity",
            response_type="entity_json",
            context={}
        )

    assert "error" in result
    assert "Failed to generate configuration" in result["error"]
    assert "AI service unavailable" in result["details"]["message"]


@pytest.mark.asyncio
async def test_submit_canvas_question_prompt_load_failure(service_mocks):
    svc, entity_service, data_service, ai_agent = service_mocks

    ai_agent.run_agent.return_value = json.dumps({"name": "test", "version": "1", "fields": []})

    # Create a mock that fails for prompt file but allows schema files
    def failing_open(file, *args, **kwargs):
        file_path = Path(file) if not isinstance(file, Path) else file
        if 'system_prompt.md' in str(file_path):
            raise FileNotFoundError("Prompt file not found")
        return open(file, *args, **kwargs)

    with patch("builtins.open", side_effect=failing_open):
        result = await svc.submit_canvas_question(
            chat_id="chat123",
            question="Create an entity",
            response_type="entity_json",
            context={}
        )

    # Should still work with default prompt
    assert "hook" in result

    # Verify default prompt was used
    call_args = ai_agent.run_agent.call_args
    messages = call_args.kwargs["messages"]
    system_message = messages[0].content
    assert "helpful AI assistant" in system_message

