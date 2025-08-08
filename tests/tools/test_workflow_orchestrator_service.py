import pytest
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from tools.workflow_orchestrator_service import WorkflowOrchestratorService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestWorkflowOrchestratorService:
    """Test cases for WorkflowOrchestratorService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WorkflowOrchestratorService."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create WorkflowOrchestratorService instance."""
        return WorkflowOrchestratorService(**mock_dependencies)

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            const.REPOSITORY_NAME_PARAM: "java-client-template"
        }
        entity.workflow_name = "test_workflow"
        entity.failed = False
        entity.error = None
        return entity

    @pytest.fixture
    def sample_workflow_json(self):
        """Create sample workflow JSON for testing."""
        return {
            "version": "1.0",
            "name": "Job Workflow",
            "desc": "Workflow for Job entity managing ingestion states and transitions",
            "initialState": "none",
            "active": True,
            "states": {
                "scheduled": {
                    "transitions": [
                        {
                            "name": "validate_and_start_ingesting",
                            "next": "ingesting",
                            "manual": False,
                            "processors": [
                                {
                                    "name": "JobValidationProcessor",
                                    "executionMode": "SYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "ingesting": {
                    "transitions": [
                        {
                            "name": "ingest_data_and_save_laureates",
                            "next": "succeeded",
                            "manual": False,
                            "criterion": {
                                "type": "function",
                                "function": {
                                    "name": "IngestionSuccessCriterion",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            },
                            "processors": [
                                {
                                    "name": "DataIngestionProcessor",
                                    "executionMode": "SYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        },
                        {
                            "name": "ingest_data_failure",
                            "next": "failed",
                            "manual": False,
                            "criterion": {
                                "type": "function",
                                "function": {
                                    "name": "IngestionFailureCriterion",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            }
                        }
                    ]
                },
                "succeeded": {
                    "transitions": [
                        {
                            "name": "notify_subscribers",
                            "next": "notified_subscribers",
                            "manual": False,
                            "processors": [
                                {
                                    "name": "SubscribersNotifierProcessor",
                                    "executionMode": "SYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "failed": {
                    "transitions": []
                },
                "notified_subscribers": {
                    "transitions": []
                }
            }
        }

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_success(self, service, mock_agentic_entity, sample_workflow_json):
        """Test successful generation of workflow orchestrators."""
        # Mock parameters
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        # Mock file system operations
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Job.json', 'User.json']), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_workflow_json))), \
             patch('tools.workflow_orchestrator_service._save_file', new_callable=AsyncMock) as mock_save:
            
            result = await service.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            # Verify success message
            assert "Successfully generated 2 workflow orchestrators" in result
            
            # Verify _save_file was called for each workflow
            assert mock_save.call_count == 2
            
            # Verify the generated orchestrator paths
            call_args_list = mock_save.call_args_list
            saved_paths = [call[1]['item'] for call in call_args_list]
            
            expected_paths = [
                "src/main/java/com/java_template/application/orchestrator/JobWorkflowOrchestrator.java",
                "src/main/java/com/java_template/application/orchestrator/UserWorkflowOrchestrator.java"
            ]
            
            for expected_path in expected_paths:
                assert expected_path in saved_paths

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_missing_params(self, service, mock_agentic_entity):
        """Test error handling for missing required parameters."""
        result = await service.generate_workflow_orchestrators(
            technical_id="test_123",
            entity=mock_agentic_entity
        )
        
        assert "Missing required parameter" in result

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_no_directory(self, service, mock_agentic_entity):
        """Test handling when workflow directory doesn't exist."""
        params = {"workflow_directory_path": "nonexistent/path"}
        
        with patch('os.path.exists', return_value=False):
            result = await service.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            assert "No workflow JSON files found" in result

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_no_json_files(self, service, mock_agentic_entity):
        """Test handling when no JSON files are found in directory."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['README.md', 'config.txt']):
            
            result = await service.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            assert "No workflow JSON files found" in result

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_invalid_json(self, service, mock_agentic_entity):
        """Test handling of invalid JSON files."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Invalid.json']), \
             patch('builtins.open', mock_open(read_data="invalid json content")):
            
            result = await service.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            assert "No workflow JSON files found" in result

    def test_generate_orchestrator_code_basic(self, service, sample_workflow_json):
        """Test generation of basic orchestrator code."""
        orchestrator_code = service._generate_orchestrator_code("Job", sample_workflow_json)
        
        # Verify class structure
        assert "public class JobWorkflowOrchestrator" in orchestrator_code
        assert "package com.java_template.application.orchestrator;" in orchestrator_code
        assert "@Component" in orchestrator_code
        assert "ProcessorsFactory processorsFactory" in orchestrator_code
        assert "CriteriaFactory criteriaFactory" in orchestrator_code
        
        # Verify method signature
        assert "public String run(String technicalId, CyodaEntity entity, String transition)" in orchestrator_code

    def test_generate_transition_logic_with_processors(self, service):
        """Test generation of transition logic with processors."""
        states = {
            "scheduled": {
                "transitions": [
                    {
                        "name": "validate_and_start",
                        "next": "ingesting",
                        "processors": [{"name": "ValidationProcessor"}]
                    }
                ]
            }
        }
        
        logic = service._generate_transition_logic(states)
        
        assert 'if ("validate_and_start".equals(transition))' in logic
        assert 'processorsFactory.get("ValidationProcessor").process(technicalId, entity)' in logic
        assert 'nextTransition = "ingesting"' in logic

    def test_generate_transition_logic_with_criteria(self, service):
        """Test generation of transition logic with criteria."""
        states = {
            "processing": {
                "transitions": [
                    {
                        "name": "check_result",
                        "next": "success",
                        "criterion": {
                            "type": "function",
                            "function": {"name": "SuccessCriterion"}
                        }
                    }
                ]
            }
        }
        
        logic = service._generate_transition_logic(states)
        
        assert 'if ("check_result".equals(transition))' in logic
        assert 'criteriaFactory.get("SuccessCriterion").check(technicalId, entity)' in logic
        assert 'nextTransition = "success"' in logic
        assert 'nextTransition = "failed"' in logic

    def test_generate_transition_logic_with_processors_and_criteria(self, service):
        """Test generation of transition logic with both processors and criteria."""
        states = {
            "processing": {
                "transitions": [
                    {
                        "name": "process_and_check",
                        "next": "success",
                        "processors": [{"name": "DataProcessor"}],
                        "criterion": {
                            "type": "function",
                            "function": {"name": "ValidationCriterion"}
                        }
                    }
                ]
            }
        }
        
        logic = service._generate_transition_logic(states)
        
        assert 'processorsFactory.get("DataProcessor").process(technicalId, entity)' in logic
        assert 'criteriaFactory.get("ValidationCriterion").check(technicalId, entity)' in logic

    def test_get_repository_name_from_cache(self, service, mock_agentic_entity):
        """Test getting repository name from entity cache."""
        mock_agentic_entity.workflow_cache[const.REPOSITORY_NAME_PARAM] = "custom-repo"
        
        repo_name = service._get_repository_name(mock_agentic_entity)
        
        assert repo_name == "custom-repo"

    def test_get_git_branch_id_from_cache(self, service, mock_agentic_entity):
        """Test getting git branch ID from entity cache."""
        mock_agentic_entity.workflow_cache[const.GIT_BRANCH_PARAM] = "feature-branch"
        
        branch_id = service._get_git_branch_id(mock_agentic_entity, "fallback_id")
        
        assert branch_id == "feature-branch"

    def test_get_git_branch_id_fallback(self, service):
        """Test fallback to technical_id when branch not in cache."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {}

        branch_id = service._get_git_branch_id(entity, "fallback_id")

        assert branch_id == "fallback_id"

    @pytest.mark.asyncio
    async def test_read_workflow_files_success(self, service):
        """Test successful reading of workflow files."""
        workflow_json = {"name": "Test Workflow", "states": {}}

        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Job.json', 'User.json', 'README.md']), \
             patch('builtins.open', mock_open(read_data=json.dumps(workflow_json))):

            result = await service._read_workflow_files(
                "src/main/java/com/java_template/application/workflow",
                "test_branch",
                "java-client-template"
            )

            assert len(result) == 2
            assert "Job" in result
            assert "User" in result
            assert result["Job"]["name"] == "Test Workflow"

    @pytest.mark.asyncio
    async def test_read_workflow_files_directory_not_exists(self, service):
        """Test reading workflow files when directory doesn't exist."""
        with patch('os.path.exists', return_value=False):
            result = await service._read_workflow_files(
                "nonexistent/path",
                "test_branch",
                "java-client-template"
            )

            assert result == {}

    def test_generate_transition_logic_empty_states(self, service):
        """Test generation of transition logic with empty states."""
        logic = service._generate_transition_logic({})

        assert logic == "            // No transitions defined"

    def test_generate_transition_logic_no_transitions(self, service):
        """Test generation of transition logic with states but no transitions."""
        states = {
            "initial": {
                "transitions": []
            },
            "final": {}
        }

        logic = service._generate_transition_logic(states)

        assert logic == "            // No transitions defined"

    def test_generate_transition_logic_missing_transition_name(self, service):
        """Test handling of transitions without names."""
        states = {
            "state1": {
                "transitions": [
                    {
                        "next": "state2",
                        "processors": [{"name": "TestProcessor"}]
                    }
                ]
            }
        }

        logic = service._generate_transition_logic(states)

        # Should skip transitions without names
        assert logic == "            // No transitions defined"

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_exception_handling(self, service, mock_agentic_entity):
        """Test exception handling during orchestrator generation."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}

        # Mock an exception during the _save_file operation instead
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Job.json']), \
             patch('builtins.open', mock_open(read_data='{"states": {}}')), \
             patch('tools.workflow_orchestrator_service._save_file', side_effect=Exception("Save file error")):

            result = await service.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )

            assert "Error generating workflow orchestrators" in result
            assert mock_agentic_entity.failed is True

    def test_generate_orchestrator_code_complex_workflow(self, service):
        """Test generation of orchestrator code for complex workflow."""
        complex_workflow = {
            "states": {
                "start": {
                    "transitions": [
                        {
                            "name": "begin_processing",
                            "next": "processing",
                            "processors": [
                                {"name": "InitProcessor"},
                                {"name": "ValidationProcessor"}
                            ]
                        }
                    ]
                },
                "processing": {
                    "transitions": [
                        {
                            "name": "success_path",
                            "next": "completed",
                            "processors": [{"name": "SuccessProcessor"}],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "SuccessCriterion"}
                            }
                        },
                        {
                            "name": "failure_path",
                            "next": "failed",
                            "criterion": {
                                "type": "function",
                                "function": {"name": "FailureCriterion"}
                            }
                        }
                    ]
                }
            }
        }

        orchestrator_code = service._generate_orchestrator_code("Complex", complex_workflow)

        # Verify multiple processors are handled
        assert 'processorsFactory.get("InitProcessor").process(technicalId, entity)' in orchestrator_code
        assert 'processorsFactory.get("ValidationProcessor").process(technicalId, entity)' in orchestrator_code

        # Verify multiple transitions with criteria
        assert 'if ("success_path".equals(transition))' in orchestrator_code
        assert 'if ("failure_path".equals(transition))' in orchestrator_code
        assert 'criteriaFactory.get("SuccessCriterion").check(technicalId, entity)' in orchestrator_code
