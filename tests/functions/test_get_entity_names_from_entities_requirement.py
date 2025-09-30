import json
import os
import tempfile
import pytest
from unittest.mock import Mock, patch, AsyncMock
import aiofiles

from functions.utility_service import UtilityService
from entity.model import AgenticFlowEntity


class TestGetEntityNamesFromEntitiesRequirement:
    """Test the get_entity_names_from_entities_requirement function"""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for UtilityService"""
        return {
            'workflow_helper_service': Mock(),
            'entity_service': Mock(),
            'cyoda_auth_service': Mock(),
            'workflow_converter_service': Mock(),
            'scheduler_service': Mock(),
            'data_service': Mock(),
            'dataset': None,
            'mock': True
        }

    @pytest.fixture
    def utility_service(self, mock_dependencies):
        """Create UtilityService instance with mocked dependencies"""
        return UtilityService(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create a mock AgenticFlowEntity"""
        entity = Mock(spec=AgenticFlowEntity)
        entity.branch_id = "test-branch"
        entity.repository_name = "test-repo"
        return entity

    @pytest.fixture
    def sample_entities_data(self):
        """Sample entities requirement data"""
        return [
            {"User": {
                "entity_data_example": {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }},
            {"Product": {
                "entity_data_example": {
                    "title": "Sample Product",
                    "price": 99.99
                }
            }},
            {"Order": {
                "entity_data_example": {
                    "orderId": "12345",
                    "status": "pending"
                }
            }}
        ]

    @pytest.mark.asyncio
    async def test_get_entity_names_success(self, utility_service, mock_entity, sample_entities_data):
        """Test successful extraction of entity names"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            project_dir = os.path.join(temp_dir, "test-branch", "test-repo", "src", "main", "java", "com", "java_template", "prototype")
            os.makedirs(project_dir, exist_ok=True)

            entities_file = os.path.join(project_dir, "entities_requirement.json")

            # Write sample data to file
            with open(entities_file, 'w') as f:
                json.dump(sample_entities_data, f)

            # Mock config.PROJECT_DIR and ensure entity has proper attributes
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity,
                    input_file="src/main/java/com/java_template/prototype/entities_requirement.json"
                )

                # Verify results
                assert result == ["User", "Product", "Order"]

    @pytest.mark.asyncio
    async def test_get_entity_names_file_not_found(self, utility_service, mock_entity):
        """Test behavior when entities requirement file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock config.PROJECT_DIR
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function with non-existent file
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity,
                    input_file="src/main/java/com/java_template/prototype/entities_requirement.json"
                )

                # Should return empty list
                assert result == []

    @pytest.mark.asyncio
    async def test_get_entity_names_invalid_json(self, utility_service, mock_entity):
        """Test behavior with invalid JSON content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            project_dir = os.path.join(temp_dir, "test-branch", "test-repo", "src", "main", "java", "com", "java_template", "prototype")
            os.makedirs(project_dir, exist_ok=True)

            entities_file = os.path.join(project_dir, "entities_requirement.json")

            # Write invalid JSON to file
            with open(entities_file, 'w') as f:
                f.write("invalid json content")

            # Mock config.PROJECT_DIR
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity,
                    input_file="src/main/java/com/java_template/prototype/entities_requirement.json"
                )

                # Should return empty list
                assert result == []

    @pytest.mark.asyncio
    async def test_get_entity_names_empty_list(self, utility_service, mock_entity):
        """Test behavior with empty entities list"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            project_dir = os.path.join(temp_dir, "test-branch", "test-repo", "src", "main", "java", "com", "java_template", "prototype")
            os.makedirs(project_dir, exist_ok=True)

            entities_file = os.path.join(project_dir, "entities_requirement.json")

            # Write empty list to file
            with open(entities_file, 'w') as f:
                json.dump([], f)

            # Mock config.PROJECT_DIR
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity,
                    input_file="src/main/java/com/java_template/prototype/entities_requirement.json"
                )

                # Should return empty list
                assert result == []

    @pytest.mark.asyncio
    async def test_get_entity_names_default_file_path(self, utility_service, mock_entity, sample_entities_data):
        """Test using default file path when input_file parameter is not provided"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            project_dir = os.path.join(temp_dir, "test-branch", "test-repo", "src", "main", "java", "com", "java_template", "prototype")
            os.makedirs(project_dir, exist_ok=True)

            entities_file = os.path.join(project_dir, "entities_requirement.json")

            # Write sample data to file
            with open(entities_file, 'w') as f:
                json.dump(sample_entities_data, f)

            # Mock config.PROJECT_DIR
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function without input_file parameter
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity
                )

                # Verify results
                assert result == ["User", "Product", "Order"]

    @pytest.mark.asyncio
    async def test_get_entity_names_malformed_structure(self, utility_service, mock_entity):
        """Test behavior with malformed JSON structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            project_dir = os.path.join(temp_dir, "test-branch", "test-repo", "src", "main", "java", "com", "java_template", "prototype")
            os.makedirs(project_dir, exist_ok=True)

            entities_file = os.path.join(project_dir, "entities_requirement.json")

            # Write malformed structure (not a list)
            malformed_data = {"not": "a list"}
            with open(entities_file, 'w') as f:
                json.dump(malformed_data, f)

            # Mock config.PROJECT_DIR
            with patch('common.config.config.config') as mock_config:
                mock_config.PROJECT_DIR = temp_dir

                # Call the function
                result = await utility_service.get_entity_names_from_entities_requirement(
                    technical_id="test-id",
                    entity=mock_entity,
                    input_file="src/main/java/com/java_template/prototype/entities_requirement.json"
                )

                # Should return empty list
                assert result == []
