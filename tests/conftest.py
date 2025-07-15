"""
Pytest configuration file for the AI Assistant test suite.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    config = MagicMock()
    config.PROJECT_DIR = "/test/project"
    config.GENERAL_MEMORY_TAG = "general"
    return config


@pytest.fixture
def mock_logger():
    """Mock logger object."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.exception = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_cyoda_auth_service():
    """Mock Cyoda authentication service."""
    auth_service = MagicMock()
    auth_service.token = "mock_token"
    return auth_service


@pytest.fixture
def mock_entity_service():
    """Mock entity service."""
    service = AsyncMock()
    service.create_item = AsyncMock()
    service.get_item = AsyncMock()
    service.update_item = AsyncMock()
    service.delete_item = AsyncMock()
    return service


@pytest.fixture
def mock_workflow_helper_service():
    """Mock workflow helper service."""
    service = AsyncMock()
    service.register_workflow_with_app = AsyncMock()
    service.validate_workflow_design = AsyncMock()
    service.has_workflow_code_validation_succeeded = AsyncMock()
    service.has_workflow_code_validation_failed = AsyncMock()
    service.save_extracted_workflow_code = AsyncMock()
    return service


@pytest.fixture
def mock_workflow_converter_service():
    """Mock workflow converter service."""
    service = AsyncMock()
    service.convert_diagram_to_dataset = AsyncMock()
    service.convert_workflow_processed_dataset_to_json = AsyncMock()
    service.convert_workflow_json_to_state_diagram = AsyncMock()
    service.convert_workflow_to_dto = AsyncMock()
    return service


@pytest.fixture
def mock_scheduler_service():
    """Mock scheduler service."""
    service = AsyncMock()
    service.create_item = AsyncMock()
    service.get_item = AsyncMock()
    service.update_item = AsyncMock()
    return service


@pytest.fixture
def mock_data_service():
    """Mock data service."""
    service = AsyncMock()
    service.process_data = AsyncMock()
    service.get_data = AsyncMock()
    return service


@pytest.fixture
def mock_memory_manager():
    """Mock memory manager."""
    manager = AsyncMock()
    manager.append_to_ai_memory = AsyncMock()
    manager.get_ai_memory_messages = AsyncMock()
    return manager


@pytest.fixture
def mock_ai_agent_handler():
    """Mock AI agent handler."""
    handler = AsyncMock()
    handler.run_ai_agent = AsyncMock()
    return handler


@pytest.fixture
def mock_event_processor():
    """Mock event processor."""
    processor = AsyncMock()
    processor.process_event = AsyncMock()
    return processor


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to all tests by default
        if "unit" not in item.keywords and "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if "test_integration" in item.name or "test_full_workflow" in item.name:
            item.add_marker(pytest.mark.slow)


# Mock external dependencies that might not be available during testing
@pytest.fixture(autouse=True)
def mock_external_dependencies(monkeypatch):
    """Mock external dependencies that might not be available during testing."""
    import sys

    # Mock optional imports
    try:
        import fitz
    except ImportError:
        mock_fitz = MagicMock()
        sys.modules['fitz'] = mock_fitz

    # Mock OpenAI if not available
    try:
        import openai
    except ImportError:
        mock_openai = MagicMock()
        sys.modules['openai'] = mock_openai

    # Mock other optional dependencies
    optional_modules = [
        "aiofiles",
        "httpx",
        "requests",
        "nltk",
    ]

    for module_name in optional_modules:
        try:
            __import__(module_name)
        except ImportError:
            mock_module = MagicMock()
            sys.modules[module_name] = mock_module


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration for testing."""
    return {
        "type": "ai_agent",
        "model": "gpt-4",
        "prompt": "Test prompt with {variable}",
        "memory_tags": ["general"],
        "max_iterations": 3,
        "input": {
            "local_fs": ["test_file.py"]
        },
        "output": {
            "edge_message": {
                "message_type": "result",
                "content_key": "response"
            }
        },
        "output_variable": "result"
    }


@pytest.fixture
def sample_notification_config():
    """Sample notification configuration for testing."""
    return {
        "type": "notification",
        "notification": "Hello {user_name}! Your task is {task_status}.",
        "memory_tags": ["general"]
    }


@pytest.fixture
def sample_question_config():
    """Sample question configuration for testing."""
    return {
        "type": "question",
        "question": "What is the status of {entity_name}?",
        "memory_tags": ["general"]
    }
