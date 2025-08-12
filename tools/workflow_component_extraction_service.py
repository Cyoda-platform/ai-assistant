import json
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple

from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService
from tools.repository_resolver import resolve_repository_name_with_language_param
from common.utils.utils import get_project_file_name
import common.config.const as const


class WorkflowComponentExtractionService(BaseWorkflowService):
    """
    Service responsible for extracting processor names and criteria function names
    from workflow configuration files to help generate the required components.
    """

    async def extract_workflow_components(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Extract all processor names and criteria function names from workflow configurations
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_directory and output_format
            
        Returns:
            Formatted extraction result with processor and criteria lists
        """
        try:
            # Validate required parameters
            required_params = ["workflow_directory"]
            is_valid, error_msg = await self._validate_required_params(params, required_params)
            if not is_valid:
                return error_msg

            # Get repository information using repository resolver
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Get paths from parameters
            workflow_directory = params.get("workflow_directory")
            output_format = params.get("output_format", "detailed")

            # Get full file path
            workflow_dir = await get_project_file_name(
                file_name=workflow_directory,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            # Extract components from workflows
            processors, criteria = await self._extract_workflow_components(workflow_dir)
            
            # Generate formatted output
            result = self._format_extraction_result(processors, criteria, output_format)
            
            return result
            
        except Exception as e:
            return self._handle_error(entity, e, "Error extracting workflow components")

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
                            name = processor["name"]
                            processors.add(name)
                
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

    def _format_extraction_result(self, processors: Set[str], criteria: Set[str], output_format: str) -> str:
        """Format the extraction results based on the requested format"""
        
        if output_format == "list":
            return self._format_as_list(processors, criteria)
        elif output_format == "summary":
            return self._format_as_summary(processors, criteria)
        else:  # detailed
            return self._format_as_detailed(processors, criteria)

    def _format_as_list(self, processors: Set[str], criteria: Set[str]) -> str:
        """Format as simple lists"""
        result_lines = []
        
        result_lines.append("**PROCESSORS:**")
        for processor in sorted(processors):
            result_lines.append(f"- {processor}")
        
        result_lines.append("\n**CRITERIA:**")
        for criterion in sorted(criteria):
            result_lines.append(f"- {criterion}")
        
        return "\n".join(result_lines)

    def _format_as_summary(self, processors: Set[str], criteria: Set[str]) -> str:
        """Format as summary with counts"""
        result_lines = []
        
        result_lines.append("📊 **WORKFLOW COMPONENT EXTRACTION SUMMARY**")
        result_lines.append("=" * 50)
        result_lines.append(f"• Total Processors Required: {len(processors)}")
        result_lines.append(f"• Total Criteria Required: {len(criteria)}")
        
        if processors:
            result_lines.append(f"\n📋 **PROCESSORS** ({len(processors)}):")
            for processor in sorted(processors):
                result_lines.append(f"  • {processor}")
        
        if criteria:
            result_lines.append(f"\n🔍 **CRITERIA** ({len(criteria)}):")
            for criterion in sorted(criteria):
                result_lines.append(f"  • {criterion}")
        
        return "\n".join(result_lines)

    def _format_as_detailed(self, processors: Set[str], criteria: Set[str]) -> str:
        """Format as detailed analysis"""
        result_lines = []
        
        result_lines.append("🔍 **WORKFLOW COMPONENT EXTRACTION ANALYSIS**")
        result_lines.append("=" * 60)
        
        # Summary section
        result_lines.append("\n📊 **EXTRACTION SUMMARY**")
        result_lines.append(f"• Processors identified: {len(processors)}")
        result_lines.append(f"• Criteria identified: {len(criteria)}")
        result_lines.append(f"• Total components to generate: {len(processors) + len(criteria)}")
        
        # Detailed processor section
        if processors:
            result_lines.append(f"\n🛠️ **PROCESSORS TO GENERATE** ({len(processors)}):")
            result_lines.append("These Java classes need to be created in the processor package:")
            for processor in sorted(processors):
                result_lines.append(f"  ✅ {processor}.java")
                result_lines.append(f"     └─ Package: com.java_template.application.processor")
                result_lines.append(f"     └─ Class: {processor}")
                result_lines.append(f"     └─ Purpose: Business logic processor implementation")
        
        # Detailed criteria section
        if criteria:
            result_lines.append(f"\n🔍 **CRITERIA TO GENERATE** ({len(criteria)}):")
            result_lines.append("These validation functions need to be created in the criteria package:")
            for criterion in sorted(criteria):
                result_lines.append(f"  ✅ {criterion}.java")
                result_lines.append(f"     └─ Package: com.java_template.application.criterion")
                result_lines.append(f"     └─ Function: {criterion}")
                result_lines.append(f"     └─ Purpose: Validation and business rule enforcement")
        
        # Implementation guidance
        result_lines.append("\n🎯 **IMPLEMENTATION GUIDANCE**")
        result_lines.append("**For Processors:**")
        result_lines.append("• Implement business logic based on functional requirements")
        result_lines.append("• Add proper error handling and validation")
        result_lines.append("• Include comprehensive logging")
        result_lines.append("• Follow Spring Boot patterns with @Component annotation")
        
        result_lines.append("\n**For Criteria:**")
        result_lines.append("• Implement validation logic and business rules")
        result_lines.append("• Return boolean results for validation checks")
        result_lines.append("• Add meaningful error messages for failed validations")
        result_lines.append("• Follow functional programming patterns where applicable")
        
        result_lines.append("\n✨ **READY FOR GENERATION**")
        result_lines.append("Use this analysis to generate all required processor and criteria implementations.")
        
        return "\n".join(result_lines)

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
