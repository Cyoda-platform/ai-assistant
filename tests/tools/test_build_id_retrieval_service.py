import pytest
from unittest.mock import AsyncMock, MagicMock
from tools.build_id_retrieval_service import BuildIdRetrievalService
from entity.model import AgenticFlowEntity
import common.config.const as const
from common.config.config import config


class TestBuildIdRetrievalService:
    
    @pytest.fixture
    def service(self):
        """Create BuildIdRetrievalService instance with mocked dependencies."""
        return BuildIdRetrievalService(
            workflow_helper_service=MagicMock(),
            entity_service=AsyncMock(),
            cyoda_auth_service="test_token",
            workflow_converter_service=MagicMock(),
            scheduler_service=MagicMock(),
            data_service=MagicMock(),
            dataset=None,
            mock=True
        )
    
    @pytest.fixture
    def agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.parent_id = "parent_123"
        return entity
    
    @pytest.fixture
    def parent_entity(self):
        """Create mock parent entity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "parent_123"
        entity.parent_id = ""
        entity.child_entities = ["deploy_123"]
        return entity
    
    @pytest.fixture
    def deploy_entity(self):
        """Create mock deployment entity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "deploy_123"
        entity.parent_id = "parent_123"
        entity.workflow_name = "deploy_cyoda_env"
        entity.last_modified = 1234567890
        entity.workflow_cache = {"build_id": "test-build-id-123"}
        return entity
    
    @pytest.mark.asyncio
    async def test_get_build_id_success(self, service, agentic_entity, parent_entity, deploy_entity):
        """Test successful build ID retrieval."""
        # Setup mocks - first call returns parent, second call returns deploy entity
        service.entity_service.get_item.side_effect = [parent_entity, deploy_entity]

        # Execute
        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        # Verify
        assert result == "test-build-id-123"
        # Should be called twice: once for parent, once for child
        assert service.entity_service.get_item.call_count == 2
    
    @pytest.mark.asyncio
    async def test_no_parent_id(self, service):
        """Test when entity has no parent_id."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.parent_id = None

        result = await service.get_build_id_from_context("tech_id", entity)

        assert result == "Build ID not found - no parent entity"
    
    @pytest.mark.asyncio
    async def test_parent_entity_not_found(self, service, agentic_entity):
        """Test when parent entity is not found."""
        service.entity_service.get_item.return_value = None

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - parent entity not found"
    
    @pytest.mark.asyncio
    async def test_no_child_entities(self, service, agentic_entity):
        """Test when no child entities are found."""
        # Create parent entity with empty child_entities list
        parent_entity = MagicMock(spec=AgenticFlowEntity)
        parent_entity.child_entities = []
        service.entity_service.get_item.return_value = parent_entity

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - no child entities found"
    
    @pytest.mark.asyncio
    async def test_no_deploy_entities(self, service, agentic_entity, parent_entity):
        """Test when no deploy_cyoda_env entities are found."""
        # Create non-deploy entity
        other_entity = MagicMock(spec=AgenticFlowEntity)
        other_entity.workflow_name = "other_workflow"

        # First call returns parent, second call returns non-deploy entity
        service.entity_service.get_item.side_effect = [parent_entity, other_entity]

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - no deployment entities found"
    
    @pytest.mark.asyncio
    async def test_no_workflow_cache(self, service, agentic_entity, parent_entity):
        """Test when deployment entity has no workflow_cache."""
        # Create deploy entity without workflow_cache
        deploy_entity = MagicMock(spec=AgenticFlowEntity)
        deploy_entity.technical_id = "deploy_123"
        deploy_entity.workflow_name = "deploy_cyoda_env"
        deploy_entity.last_modified = 1234567890
        deploy_entity.workflow_cache = None

        # First call returns parent, second call returns deploy entity
        service.entity_service.get_item.side_effect = [parent_entity, deploy_entity]

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - no workflow cache in deployment entity"
    
    @pytest.mark.asyncio
    async def test_no_build_id_in_cache(self, service, agentic_entity, parent_entity):
        """Test when workflow_cache exists but has no build_id."""
        # Create deploy entity with empty workflow_cache
        deploy_entity = MagicMock(spec=AgenticFlowEntity)
        deploy_entity.technical_id = "deploy_123"
        deploy_entity.workflow_name = "deploy_cyoda_env"
        deploy_entity.last_modified = 1234567890
        deploy_entity.workflow_cache = {"other_key": "other_value"}

        # First call returns parent, second call returns deploy entity
        service.entity_service.get_item.side_effect = [parent_entity, deploy_entity]

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - no build_id in workflow cache"
    
    @pytest.mark.asyncio
    async def test_multiple_deploy_entities_latest_selected(self, service, agentic_entity):
        """Test that the latest deployment entity is selected when multiple exist."""
        # Create parent entity with multiple child entities
        parent_entity = MagicMock(spec=AgenticFlowEntity)
        parent_entity.child_entities = ["deploy_old", "deploy_new"]

        # Create multiple deploy entities with different timestamps
        older_entity = MagicMock(spec=AgenticFlowEntity)
        older_entity.workflow_name = "deploy_cyoda_env"
        older_entity.last_modified = 1234567800  # older
        older_entity.workflow_cache = {"build_id": "old-build-id"}

        newer_entity = MagicMock(spec=AgenticFlowEntity)
        newer_entity.workflow_name = "deploy_cyoda_env"
        newer_entity.last_modified = 1234567900  # newer
        newer_entity.workflow_cache = {"build_id": "new-build-id"}

        # First call returns parent, subsequent calls return deploy entities
        service.entity_service.get_item.side_effect = [parent_entity, older_entity, newer_entity]

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "new-build-id"
    
    @pytest.mark.asyncio
    async def test_entity_service_exception(self, service, agentic_entity):
        """Test handling of entity service exceptions."""
        service.entity_service.get_item.side_effect = Exception("Database error")

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - error retrieving parent entity"

    @pytest.mark.asyncio
    async def test_get_child_entities_exception(self, service, agentic_entity, parent_entity):
        """Test handling of child entity retrieval exceptions."""
        # First call returns parent, second call raises exception
        service.entity_service.get_item.side_effect = [parent_entity, Exception("Query error")]

        result = await service.get_build_id_from_context("tech_id", agentic_entity)

        assert result == "Build ID not found - error retrieving child entities"
