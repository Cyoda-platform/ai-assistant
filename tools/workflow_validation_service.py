import json
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService
from tools.repository_resolver import resolve_repository_name_with_language_param
from common.utils.utils import get_project_file_name
import common.config.const as const


class WorkflowValidationService(BaseWorkflowService):
    """
    Service responsible for validating that workflow processors and criteria
    have been properly implemented and match the workflow configuration.
    """

    async def validate_workflow_implementation(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Validate that all processors and criteria from workflow configuration
        have been implemented and no extra ones exist.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_file_path, processors_path, criteria_path

        Returns:
            Validation result message
        """
        pass
        # try:
        #     # Get repository information using repository resolver
        #     repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
        #     git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
        #
        #     # Get paths from parameters with defaults
        #     workflow_file_path = params.get("workflow_file_path",
        #         "com/java_template/application/workflow")
        #     processors_path = params.get("processors_path",
        #         "src/main/java/com/java_template/application/processor")
        #     criteria_path = params.get("criteria_path",
        #         "src/main/java/com/java_template/application/criteria")
        #
        #     # Get full file paths
        #     workflow_file = await get_project_file_name(
        #         file_name=workflow_file_path,
        #         git_branch_id=git_branch_id,
        #         repository_name=repository_name
        #     )
        #
        #     # Extract expected processors and criteria from workflow
        #     expected_processors, expected_criteria = await self._extract_workflow_components(workflow_file)
        #
        #     # Get implemented processors and criteria
        #     implemented_processors = await self._get_implemented_processors(git_branch_id, repository_name, processors_path)
        #     implemented_criteria = await self._get_implemented_criteria(git_branch_id, repository_name, criteria_path)
        #
        #     # Perform validation
        #     validation_result = self._validate_implementation(
        #         expected_processors, expected_criteria,
        #         implemented_processors, implemented_criteria
        #     )
        #
        #     return validation_result
        #
        # except Exception as e:
        #     return self._handle_error(entity, e, "Error validating workflow implementation")

    async def _extract_workflow_components(self, workflow_file_path: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract processor and criteria names from workflow configuration.
        Scans all JSON files in the directory if a directory is provided.

        Args:
            workflow_file_path: Path to workflow JSON file or directory containing workflow files

        Returns:
            Tuple of (processor_names, criteria_names)
        """
        processors = set()
        criteria = set()

        try:
            # Check if the path is a directory or file
            if os.path.isdir(workflow_file_path):
                # Find all JSON files in the directory
                json_files = [f for f in os.listdir(workflow_file_path) if f.endswith('.json')]
                if not json_files:
                    raise FileNotFoundError(f"No JSON workflow files found in directory: {workflow_file_path}")

                self.logger.info(f"Found {len(json_files)} workflow files in directory: {workflow_file_path}")

                # Process each JSON file in the directory
                for json_file in json_files:
                    workflow_file = os.path.join(workflow_file_path, json_file)
                    file_processors, file_criteria = await self._extract_components_from_file(workflow_file)
                    processors.update(file_processors)
                    criteria.update(file_criteria)
                    self.logger.info(f"Processed {json_file}: {len(file_processors)} processors, {len(file_criteria)} criteria")
            else:
                # Single file
                processors, criteria = await self._extract_components_from_file(workflow_file_path)

            self.logger.info(f"Total extracted: {len(processors)} processors and {len(criteria)} criteria from workflow(s)")
            return processors, criteria

        except Exception as e:
            self.logger.error(f"Error extracting workflow components: {e}")
            raise

    async def _extract_components_from_file(self, workflow_file: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract processor and criteria names from a single workflow JSON file.

        Args:
            workflow_file: Path to a single workflow JSON file

        Returns:
            Tuple of (processor_names, criteria_names)
        """
        processors = set()
        criteria = set()

        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)

        # Traverse workflow states to find processors and criteria
        states = workflow_data.get("states", {})
        for state_name, state_data in states.items():
            transitions = state_data.get("transitions", {})
            for transition_name, transition_data in transitions.items():

                # Check for processor functions in actions
                action = transition_data.get("action", {})
                if action:
                    config = action.get("config", {})
                    if config.get("type") == "function":
                        function_info = config.get("function", {})
                        function_name = function_info.get("name")
                        if function_name:
                            processors.add(function_name)

                # Check for criteria functions in conditions
                condition = transition_data.get("condition", {})
                if condition:
                    # Handle direct function conditions
                    config = condition.get("config", {})
                    if config and config.get("type") == "function":
                        function_info = config.get("function", {})
                        function_name = function_info.get("name")
                        if function_name:
                            criteria.add(function_name)

                    # Handle named criteria (group conditions)
                    criteria_name = condition.get("name")
                    if criteria_name:
                        criteria.add(criteria_name)

        return processors, criteria

    async def _get_implemented_processors(self, git_branch_id: str, repository_name: str, processors_path: str) -> Set[str]:
        """
        Get list of implemented processor class names.
        Scans the processors directory for Java files.

        Args:
            git_branch_id: Git branch identifier
            repository_name: Repository name
            processors_path: Path to processors directory

        Returns:
            Set of implemented processor names
        """
        processors = set()

        try:
            processor_dir = await get_project_file_name(
                file_name=processors_path,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            if os.path.exists(processor_dir) and os.path.isdir(processor_dir):
                # Scan directory for Java files
                java_files = [f for f in os.listdir(processor_dir) if f.endswith('.java')]
                self.logger.info(f"Found {len(java_files)} Java files in processors directory: {processor_dir}")

                for file_name in java_files:
                    # Extract class name from file name (remove .java extension)
                    class_name = file_name[:-5]
                    processors.add(class_name)
                    self.logger.debug(f"Found processor: {class_name}")
            elif os.path.exists(processor_dir):
                self.logger.warning(f"Processors path exists but is not a directory: {processor_dir}")
            else:
                self.logger.warning(f"Processors directory does not exist: {processor_dir}")

            self.logger.info(f"Found {len(processors)} implemented processors")
            return processors

        except Exception as e:
            self.logger.error(f"Error getting implemented processors: {e}")
            return set()

    async def _get_implemented_criteria(self, git_branch_id: str, repository_name: str, criteria_path: str) -> Set[str]:
        """
        Get list of implemented criteria class names.
        Scans the criteria directory for Java files.

        Args:
            git_branch_id: Git branch identifier
            repository_name: Repository name
            criteria_path: Path to criteria directory

        Returns:
            Set of implemented criteria names
        """
        criteria = set()

        try:
            criteria_dir = await get_project_file_name(
                file_name=criteria_path,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            if os.path.exists(criteria_dir) and os.path.isdir(criteria_dir):
                # Scan directory for Java files
                java_files = [f for f in os.listdir(criteria_dir) if f.endswith('.java')]
                self.logger.info(f"Found {len(java_files)} Java files in criteria directory: {criteria_dir}")

                for file_name in java_files:
                    # Extract class name from file name (remove .java extension)
                    class_name = file_name[:-5]
                    criteria.add(class_name)
                    self.logger.debug(f"Found criteria: {class_name}")
            elif os.path.exists(criteria_dir):
                self.logger.warning(f"Criteria path exists but is not a directory: {criteria_dir}")
            else:
                self.logger.warning(f"Criteria directory does not exist: {criteria_dir}")

            self.logger.info(f"Found {len(criteria)} implemented criteria")
            return criteria

        except Exception as e:
            self.logger.error(f"Error getting implemented criteria: {e}")
            return set()

    def _validate_implementation(self, expected_processors: Set[str], expected_criteria: Set[str],
                                implemented_processors: Set[str], implemented_criteria: Set[str]) -> str:
        """
        Validate that implementation matches expectations.
        Focus on missing components only, not extra ones.

        Args:
            expected_processors: Expected processor names from workflow
            expected_criteria: Expected criteria names from workflow
            implemented_processors: Actually implemented processor names
            implemented_criteria: Actually implemented criteria names

        Returns:
            Validation result message
        """
        issues = []

        # Check for missing processors
        missing_processors = expected_processors - implemented_processors
        if missing_processors:
            issues.append(f"Missing processors: {', '.join(sorted(missing_processors))}")

        # Check for missing criteria
        missing_criteria = expected_criteria - implemented_criteria
        if missing_criteria:
            issues.append(f"Missing criteria: {', '.join(sorted(missing_criteria))}")

        # Report extra components for information only (not as errors)
        extra_processors = implemented_processors - expected_processors
        extra_criteria = implemented_criteria - expected_criteria

        info_messages = []
        if extra_processors:
            info_messages.append(f"Extra processors found (keeping them): {', '.join(sorted(extra_processors))}")
        if extra_criteria:
            info_messages.append(f"Extra criteria found (keeping them): {', '.join(sorted(extra_criteria))}")

        if not issues:
            result = "✅ Workflow implementation validation passed! All required processors and criteria are implemented."
            if info_messages:
                result += "\n\nℹ️  Additional components found:\n" + "\n".join(f"• {msg}" for msg in info_messages)
            return result
        else:
            result = f"❌ Workflow implementation validation failed:\n" + "\n".join(f"• {issue}" for issue in issues)
            if info_messages:
                result += "\n\nℹ️  Additional components found:\n" + "\n".join(f"• {msg}" for msg in info_messages)
            return result
