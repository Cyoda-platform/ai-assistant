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

    async def validate_workflow_processors(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Validate presence of all processors and criteria referenced in workflow configurations
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_directory, processor_directory, criteria_directory
            
        Returns:
            Validation result message with detailed analysis
        """
        try:
            # Validate required parameters
            required_params = ["workflow_directory", "processor_directory", "criteria_directory"]
            is_valid, error_msg = await self._validate_required_params(params, required_params)
            if not is_valid:
                return error_msg

            # Get repository information using repository resolver
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Get paths from parameters
            workflow_directory = params.get("workflow_directory")
            processor_directory = params.get("processor_directory") 
            criteria_directory = params.get("criteria_directory")

            # Get full file paths
            workflow_dir = await get_project_file_name(
                file_name=workflow_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )
            
            processor_dir = await get_project_file_name(
                file_name=processor_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )
            
            criteria_dir = await get_project_file_name(
                file_name=criteria_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            # Extract processors and criteria from workflows
            workflow_processors, workflow_criteria = await self._extract_workflow_components(workflow_dir)
            
            # Get existing implementations
            existing_processors = await self._get_existing_files(processor_dir, '.java')
            existing_criteria = await self._get_existing_files(criteria_dir, '.java')
            
            # Generate validation report
            validation_result = self._generate_validation_report(
                workflow_processors, workflow_criteria,
                existing_processors, existing_criteria
            )
            
            return validation_result
            
        except Exception as e:
            return self._handle_error(entity, e, "Error validating workflow processors and criteria")

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

    async def _get_existing_files(self, directory: str, extension: str) -> Set[str]:
        """Get set of existing file names (without extension) in directory"""
        existing = set()
        
        try:
            if not os.path.exists(directory):
                self.logger.warning(f"Directory does not exist: {directory}")
                return existing
                
            if not os.path.isdir(directory):
                self.logger.warning(f"Path is not a directory: {directory}")
                return existing
            
            # Scan directory for files with specified extension
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        # Remove extension to get class name
                        class_name = file[:-len(extension)]
                        existing.add(class_name)
                        self.logger.debug(f"Found existing file: {class_name}")
            
            self.logger.info(f"Found {len(existing)} existing files in {directory}")
            return existing
            
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            return existing

    def _generate_validation_report(self, workflow_processors: Set[str], workflow_criteria: Set[str],
                                  existing_processors: Set[str], existing_criteria: Set[str]) -> str:
        """Generate comprehensive validation report"""
        
        # Find missing and extra components
        missing_processors = workflow_processors - existing_processors
        missing_criteria = workflow_criteria - existing_criteria
        extra_processors = existing_processors - workflow_processors
        extra_criteria = existing_criteria - workflow_criteria
        
        # Build detailed report
        report_lines = []
        report_lines.append("🔍 **WORKFLOW PROCESSOR VALIDATION REPORT**")
        report_lines.append("=" * 50)
        
        # Summary section
        report_lines.append("\n📊 **VALIDATION SUMMARY**")
        report_lines.append(f"• Workflow processors required: {len(workflow_processors)}")
        report_lines.append(f"• Workflow criteria required: {len(workflow_criteria)}")
        report_lines.append(f"• Processors implemented: {len(existing_processors)}")
        report_lines.append(f"• Criteria implemented: {len(existing_criteria)}")
        report_lines.append(f"• Missing processors: {len(missing_processors)}")
        report_lines.append(f"• Missing criteria: {len(missing_criteria)}")
        
        # Status determination
        has_missing = missing_processors or missing_criteria
        status = "❌ VALIDATION FAILED" if has_missing else "✅ VALIDATION PASSED"
        report_lines.append(f"\n🎯 **STATUS**: {status}")
        
        # Missing components section
        if missing_processors:
            report_lines.append(f"\n🚨 **MISSING PROCESSORS** ({len(missing_processors)}):")
            for processor in sorted(missing_processors):
                report_lines.append(f"  • {processor}")
        
        if missing_criteria:
            report_lines.append(f"\n🚨 **MISSING CRITERIA** ({len(missing_criteria)}):")
            for criterion in sorted(missing_criteria):
                report_lines.append(f"  • {criterion}")
        
        # Extra components section (informational)
        if extra_processors:
            report_lines.append(f"\nℹ️  **EXTRA PROCESSORS** ({len(extra_processors)}) - Not required by workflows:")
            for processor in sorted(extra_processors):
                report_lines.append(f"  • {processor}")
        
        if extra_criteria:
            report_lines.append(f"\nℹ️  **EXTRA CRITERIA** ({len(extra_criteria)}) - Not required by workflows:")
            for criterion in sorted(extra_criteria):
                report_lines.append(f"  • {criterion}")
        
        # Detailed listings
        if workflow_processors:
            report_lines.append(f"\n📋 **ALL WORKFLOW PROCESSORS** ({len(workflow_processors)}):")
            for processor in sorted(workflow_processors):
                status_icon = "✅" if processor in existing_processors else "❌"
                report_lines.append(f"  {status_icon} {processor}")
        
        if workflow_criteria:
            report_lines.append(f"\n📋 **ALL WORKFLOW CRITERIA** ({len(workflow_criteria)}):")
            for criterion in sorted(workflow_criteria):
                status_icon = "✅" if criterion in existing_criteria else "❌"
                report_lines.append(f"  {status_icon} {criterion}")
        
        # Recommendations
        report_lines.append("\n🎯 **RECOMMENDATIONS**:")
        if has_missing:
            report_lines.append("1. Implement missing processors and criteria listed above")
            report_lines.append("2. Follow established patterns from existing implementations")
            report_lines.append("3. Ensure proper error handling and validation")
            report_lines.append("4. Add comprehensive logging and monitoring")
            report_lines.append("5. Test implementations thoroughly before deployment")
        else:
            report_lines.append("✅ All required processors and criteria are implemented!")
            report_lines.append("• Consider reviewing extra components for potential cleanup")
            report_lines.append("• Ensure all implementations follow best practices")
            report_lines.append("• Verify comprehensive test coverage")
        
        return "\n".join(report_lines)

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
