import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from tools.github_operations_service import GitHubOperationsService
from entity.chat.chat import ChatEntity


class TestGitHubWorkflowService:
    """Test GitHub workflow operations service"""

    @pytest.fixture
    def github_service(self):
        """Create a GitHub operations service instance for testing"""
        return GitHubOperationsService(
            workflow_helper_service=AsyncMock(),
            entity_service=AsyncMock(),
            cyoda_auth_service=AsyncMock(),
            workflow_converter_service=AsyncMock(),
            scheduler_service=AsyncMock(),
            data_service=AsyncMock(),
            dataset=None,
            mock=True
        )

    @pytest.fixture
    def mock_entity(self):
        """Create a mock chat entity"""
        entity = ChatEntity(
            memory_id="test_memory_id",
            technical_id="test_tech_id",
            user_id="test_user_id"
        )
        entity.failed = False
        entity.error = None
        return entity

    @pytest.mark.asyncio
    async def test_trigger_github_workflow_success(self, github_service, mock_entity):
        """Test successful GitHub workflow trigger"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            # Mock the GitHub API request
            with patch.object(github_service, '_make_github_api_request') as mock_api:
                with patch.object(github_service, '_wait_for_run_to_appear') as mock_wait:
                    with patch.object(github_service, '_find_run_by_tracker_id') as mock_find:
                        mock_api.return_value = {"status": "success"}
                        mock_find.return_value = "12345"

                        result = await github_service.trigger_github_workflow(
                            "tech_id", mock_entity,
                            repo="test-repo",
                            workflow_id="build.yml",
                            ref="main",
                            inputs={"build_type": "compile-only"}
                        )

                        # Parse the JSON result
                        result_data = json.loads(result)
                        
                        assert result_data["status"] == "success"
                        assert result_data["run_id"] == "12345"
                        assert "tracker_id" in result_data
                        assert result_data["repository"] == "test-owner/test-repo"
                        assert result_data["ref"] == "main"

                        # Verify API was called correctly
                        mock_api.assert_called_once()
                        call_args = mock_api.call_args
                        assert call_args[1]["method"] == "POST"
                        assert "dispatches" in call_args[1]["path"]

    @pytest.mark.asyncio
    async def test_trigger_github_workflow_missing_params(self, github_service, mock_entity):
        """Test GitHub workflow trigger with missing required parameters"""
        result = await github_service.trigger_github_workflow(
            "tech_id", mock_entity,
            repo="test-repo"
            # Missing workflow_id
        )

        assert "Missing required parameters" in result
        assert "workflow_id" in result

    @pytest.mark.asyncio
    async def test_trigger_github_workflow_no_token(self, github_service, mock_entity):
        """Test GitHub workflow trigger without GitHub token"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = None

            result = await github_service.trigger_github_workflow(
                "tech_id", mock_entity,
                repo="test-repo",
                workflow_id="build.yml"
            )

            assert "GH_TOKEN not configured" in result

    @pytest.mark.asyncio
    async def test_monitor_workflow_run_success(self, github_service, mock_entity):
        """Test successful workflow run monitoring"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            # Mock the GitHub API response
            mock_response = {
                "id": 12345,
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/test-owner/test-repo/actions/runs/12345",
                "name": "Build",
                "head_branch": "main",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:05:00Z"
            }

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = mock_response

                result = await github_service.monitor_workflow_run(
                    "tech_id", mock_entity,
                    repo="test-repo",
                    run_id="12345"
                )

                # Parse the JSON result
                result_data = json.loads(result)
                
                assert result_data["run_id"] == 12345
                assert result_data["status"] == "completed"
                assert result_data["conclusion"] == "success"
                assert result_data["repository"] == "test-owner/test-repo"

                # Verify API was called correctly
                mock_api.assert_called_once()
                call_args = mock_api.call_args
                assert call_args[1]["method"] == "GET"
                assert "actions/runs/12345" in call_args[1]["path"]

    @pytest.mark.asyncio
    async def test_get_workflow_run_status_success(self, github_service, mock_entity):
        """Test getting workflow run status"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            # Mock the GitHub API response
            mock_response = {
                "status": "completed",
                "conclusion": "success"
            }

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = mock_response

                result = await github_service.get_workflow_run_status(
                    "tech_id", mock_entity,
                    repo="test-repo",
                    run_id="12345"
                )

                assert result == "completed - success"

                # Verify API was called correctly
                mock_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_run_by_tracker_id(self, github_service):
        """Test finding workflow run by tracker ID"""
        mock_runs_response = {
            "workflow_runs": [
                {"id": 12345},
                {"id": 12346}
            ]
        }
        
        mock_run_details = {
            "inputs": {
                "tracker_id": "test_tracker_123",
                "build_type": "compile-only"
            }
        }

        with patch.object(github_service, '_make_github_api_request') as mock_api:
            # First call returns list of runs, second call returns run details
            mock_api.side_effect = [mock_runs_response, mock_run_details]

            result = await github_service._find_run_by_tracker_id(
                "test-owner", "test-repo", "build.yml", "test_tracker_123"
            )

            assert result == "12345"
            assert mock_api.call_count == 2

    @pytest.mark.asyncio
    async def test_run_github_action_success(self, github_service, mock_entity):
        """Test successful GitHub action run with completion"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            # Mock the trigger workflow response
            trigger_response = {
                "status": "success",
                "run_id": "12345",
                "tracker_id": "test_tracker_123",
                "repository": "test-owner/test-repo",
                "ref": "main"
            }

            # Mock the final monitor response
            monitor_response = {
                "run_id": 12345,
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/test-owner/test-repo/actions/runs/12345",
                "workflow_name": "Build",
                "repository": "test-owner/test-repo",
                "head_branch": "main",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:05:00Z"
            }

            with patch.object(github_service, 'trigger_github_workflow') as mock_trigger:
                with patch.object(github_service, 'get_workflow_run_status') as mock_status:
                    with patch.object(github_service, 'monitor_workflow_run') as mock_monitor:
                        with patch('asyncio.sleep') as mock_sleep:  # Speed up the test

                            mock_trigger.return_value = json.dumps(trigger_response)
                            mock_status.return_value = "completed - success"
                            mock_monitor.return_value = json.dumps(monitor_response)

                            result = await github_service.run_github_action(
                                "tech_id", mock_entity,
                                repo="test-repo",
                                workflow_id="build.yml",
                                timeout_minutes=0.1  # Short timeout for testing
                            )

                            # Parse the result
                            result_data = json.loads(result)

                            assert result_data["status"] == "completed"
                            assert result_data["conclusion"] == "success"
                            assert result_data["success"] is True
                            assert result_data["run_id"] == "12345"
                            assert result_data["tracker_id"] == "test_tracker_123"
                            assert "elapsed_time_seconds" in result_data
                            assert result_data["html_url"] == "https://github.com/test-owner/test-repo/actions/runs/12345"

                            # Verify methods were called
                            mock_trigger.assert_called_once()
                            mock_status.assert_called()
                            mock_monitor.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_github_action_timeout(self, github_service, mock_entity):
        """Test GitHub action run with timeout"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            # Mock the trigger workflow response
            trigger_response = {
                "status": "success",
                "run_id": "12345",
                "tracker_id": "test_tracker_123",
                "repository": "test-owner/test-repo",
                "ref": "main"
            }

            with patch.object(github_service, 'trigger_github_workflow') as mock_trigger:
                with patch.object(github_service, 'get_workflow_run_status') as mock_status:
                    with patch('asyncio.sleep') as mock_sleep:  # Speed up the test

                        mock_trigger.return_value = json.dumps(trigger_response)
                        mock_status.return_value = "in_progress"  # Never completes

                        result = await github_service.run_github_action(
                            "tech_id", mock_entity,
                            repo="test-repo",
                            workflow_id="build.yml",
                            timeout_minutes=0.001  # Very short timeout for testing
                        )

                        # Parse the result
                        result_data = json.loads(result)

                        assert result_data["status"] == "timeout"
                        assert "did not complete within" in result_data["message"]
                        assert result_data["run_id"] == "12345"
                        assert result_data["tracker_id"] == "test_tracker_123"
                        assert "elapsed_time_seconds" in result_data
                        assert "timeout_seconds" in result_data

                        # Verify trigger was called but monitor wasn't (due to timeout)
                        mock_trigger.assert_called_once()
                        mock_status.assert_called()

    @pytest.mark.asyncio
    async def test_run_github_action_trigger_failure(self, github_service, mock_entity):
        """Test GitHub action run when trigger fails"""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"

            with patch.object(github_service, 'trigger_github_workflow') as mock_trigger:
                mock_trigger.return_value = "Error: Failed to trigger workflow"

                result = await github_service.run_github_action(
                    "tech_id", mock_entity,
                    repo="test-repo",
                    workflow_id="build.yml"
                )

                assert "Failed to trigger workflow" in result
                mock_trigger.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_github_action_missing_params(self, github_service, mock_entity):
        """Test GitHub action run with missing required parameters"""
        result = await github_service.run_github_action(
            "tech_id", mock_entity,
            repo="test-repo"
            # Missing workflow_id
        )

        assert "Missing required parameters" in result
        assert "workflow_id" in result
