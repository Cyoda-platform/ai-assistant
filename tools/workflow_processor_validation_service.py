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


class WorkflowProcessorValidationService(BaseWorkflowService):
    """
    Service responsible for validating that workflow processors and criteria
    have been properly implemented and match the workflow configuration.
    """

    async def validate_workflow_processors(self, technical_id: str, entity: AgenticFlowEntity, **params) -> List[str]:
        """
        Extract and return list of required processors from workflow JSON files

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_directory

        Returns:
            List of required processor names from workflow configurations
        """
        try:
            # Get repository information using repository resolver
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Get paths from parameters
            workflow_directory = params.get("workflow_directory", "src/main/resources/workflow")

            # Get full file paths
            workflow_dir = await get_project_file_name(
                file_name=workflow_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            # Extract processors from workflows
            workflow_processors, _ = await self._extract_workflow_components(workflow_dir)

            return sorted(list(workflow_processors))

        except Exception as e:
            self.logger.error(f"Error extracting workflow processors: {e}")
            return []


    async def validate_workflow_criteria(self, technical_id: str, entity: AgenticFlowEntity, **params) -> List[str]:
        """
        Extract and return list of required criteria from workflow JSON files

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_directory

        Returns:
            List of required criteria names from workflow configurations
        """
        try:
            # Get repository information using repository resolver
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Get paths from parameters
            workflow_directory = params.get("workflow_directory", "src/main/resources/workflow")

            # Get full file paths
            workflow_dir = await get_project_file_name(
                file_name=workflow_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            # Extract criteria from workflows
            _, workflow_criteria = await self._extract_workflow_components(workflow_dir)

            return sorted(list(workflow_criteria))

        except Exception as e:
            self.logger.error(f"Error extracting workflow criteria: {e}")
            return []




    async def _extract_workflow_components(self, workflow_directory: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract processor and criteria names from workflow configuration files.
        
        Args:
            workflow_directory: Directory containing workflow JSON files
            
        Returns:
            Tuple of (processor_names, criteria_names)
        """
        processors = set()
        criteria = set()
        
        try:
            if not os.path.exists(workflow_directory):
                self.logger.warning(f"Workflow directory does not exist: {workflow_directory}")
                return processors, criteria
                
            # Scan for JSON files
            json_files = []
            for root, dirs, files in os.walk(workflow_directory):
                for file in files:
                    if file.endswith('.json'):
                        json_files.append(os.path.join(root, file))
            
            if not json_files:
                self.logger.warning(f"No JSON workflow files found in: {workflow_directory}")
                return processors, criteria
                
            self.logger.info(f"Found {len(json_files)} workflow files to analyze")
            
            # Process each JSON file
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        workflow_data = json.load(f)
                    
                    file_processors, file_criteria = self._extract_from_workflow(workflow_data)
                    processors.update(file_processors)
                    criteria.update(file_criteria)
                    
                    self.logger.debug(f"Processed {json_file}: {len(file_processors)} processors, {len(file_criteria)} criteria")
                    
                except (json.JSONDecodeError, IOError) as e:
                    self.logger.warning(f"Error processing workflow file {json_file}: {e}")
                    continue
            
            self.logger.info(f"Total extracted: {len(processors)} processors, {len(criteria)} criteria")
            return processors, criteria
            
        except Exception as e:
            self.logger.error(f"Error extracting workflow components: {e}")
            raise

    def _extract_from_workflow(self, workflow_data: Dict) -> Tuple[Set[str], Set[str]]:
        """Extract processor and criteria names from workflow configuration"""
        processors = set()
        criteria = set()
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                # Look for processor names in transitions
                if "processors" in obj and isinstance(obj["processors"], list):
                    for processor in obj["processors"]:
                        if isinstance(processor, dict) and "name" in processor:
                            class_name = processor["name"]
                            processors.add(class_name)
                
                # Look for criteria in criterion objects
                if "criterion" in obj and isinstance(obj["criterion"], dict):
                    criterion = obj["criterion"]
                    if criterion.get("type") == "function" and "function" in criterion:
                        func = criterion["function"]
                        if "name" in func:
                            criteria.add(func["name"])
                
                # Recursively process nested objects
                for value in obj.values():
                    extract_recursive(value)
                    
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)

        extract_recursive(workflow_data)
        return processors, criteria