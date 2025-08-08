import json
import os
import asyncio
from typing import Any, Dict, List
from pathlib import Path

import common.config.const as const
from common.config.config import config
from common.utils.utils import _save_file
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class WorkflowOrchestratorService(BaseWorkflowService):
    """
    Service responsible for generating Java workflow orchestrators from workflow JSON files.
    Reads workflow configurations and creates orchestrator classes with conditional logic.
    """

    def __init__(self,
                 workflow_helper_service,
                 entity_service,
                 cyoda_auth_service,
                 workflow_converter_service,
                 scheduler_service,
                 data_service,
                 dataset=None,
                 mock=False):
        super().__init__(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )
        self._file_write_lock = asyncio.Lock()

    async def generate_workflow_orchestrators(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Generate Java workflow orchestrators from workflow JSON files in a directory.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including workflow_directory_path

        Returns:
            Success message with generated orchestrators count or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["workflow_directory_path"]
            )
            if not is_valid:
                return error_msg

            workflow_directory_path = params.get("workflow_directory_path")
            
            # Get repository information
            repository_name = self._get_repository_name(entity)
            git_branch_id = self._get_git_branch_id(entity, technical_id)
            
            # Read workflow JSON files from directory
            workflow_files = await self._read_workflow_files(
                workflow_directory_path, git_branch_id, repository_name
            )
            
            if not workflow_files:
                return f"No workflow JSON files found in directory: {workflow_directory_path}"
            
            # Generate orchestrators for each workflow
            generated_count = 0
            async with self._file_write_lock:
                for entity_name, workflow_json in workflow_files.items():
                    orchestrator_code = self._generate_orchestrator_code(entity_name, workflow_json)
                    orchestrator_path = f"src/main/java/com/java_template/application/orchestrator/{entity_name}WorkflowOrchestrator.java"
                    
                    await _save_file(
                        _data=orchestrator_code,
                        item=orchestrator_path,
                        git_branch_id=git_branch_id,
                        repository_name=repository_name
                    )
                    generated_count += 1
                    self.logger.info(f"Generated orchestrator for {entity_name}")

            return f"Successfully generated {generated_count} workflow orchestrators from {len(workflow_files)} workflow files"

        except Exception as e:
            self.logger.exception("Error generating workflow orchestrators: %s", str(e))
            return self._handle_error(entity, e, "Error generating workflow orchestrators")

    async def _read_workflow_files(self, directory_path: str, git_branch_id: str, repository_name: str) -> Dict[str, Dict]:
        """
        Read all workflow JSON files from the specified directory.

        Args:
            directory_path: Path to directory containing workflow JSON files
            git_branch_id: Git branch identifier
            repository_name: Repository name

        Returns:
            Dictionary mapping entity names to their workflow JSON content
        """
        workflow_files = {}
        
        try:
            # Construct full directory path
            full_directory_path = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}/{directory_path}"
            
            if not os.path.exists(full_directory_path):
                self.logger.warning(f"Workflow directory does not exist: {full_directory_path}")
                return workflow_files
            
            # Read all JSON files in the directory
            for filename in os.listdir(full_directory_path):
                if filename.endswith('.json'):
                    entity_name = filename[:-5]  # Remove .json extension
                    file_path = os.path.join(full_directory_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            workflow_json = json.load(f)
                            workflow_files[entity_name] = workflow_json
                            self.logger.info(f"Read workflow file: {filename}")
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON in file {filename}: {e}")
                    except Exception as e:
                        self.logger.error(f"Error reading file {filename}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error reading workflow directory {directory_path}: {e}")
        
        return workflow_files

    def _generate_orchestrator_code(self, entity_name: str, workflow_json: Dict) -> str:
        """
        Generate Java orchestrator code from workflow JSON.

        Args:
            entity_name: Name of the entity (e.g., "Job")
            workflow_json: Workflow JSON configuration

        Returns:
            Complete Java orchestrator class code
        """
        states = workflow_json.get("states", {})
        
        # Generate conditional logic for all transitions
        transition_logic = self._generate_transition_logic(states)
        
        orchestrator_code = f'''package com.java_template.application.orchestrator;

import com.cyoda.plugins.mapping.entity.CyodaEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class {entity_name}WorkflowOrchestrator {{
    
    private static final Logger logger = LoggerFactory.getLogger({entity_name}WorkflowOrchestrator.class);
    
    @Autowired
    private ProcessorsFactory processorsFactory;
    
    @Autowired
    private CriteriaFactory criteriaFactory;
    
    public String run(String technicalId, CyodaEntity entity, String transition) {{
        logger.info("Running {{}} workflow orchestrator for transition: {{}}", "{entity_name}", transition);
        
        String nextTransition = transition;
        
        try {{
{transition_logic}
        }} catch (Exception e) {{
            logger.error("Error processing transition: " + transition, e);
            nextTransition = "error_state";
        }}
        
        logger.info("Transition {{}} resulted in next state: {{}}", transition, nextTransition);
        return nextTransition;
    }}
}}'''
        
        return orchestrator_code

    def _generate_transition_logic(self, states: Dict) -> str:
        """
        Generate conditional logic for all workflow transitions.

        Args:
            states: States dictionary from workflow JSON

        Returns:
            Java conditional logic code
        """
        logic_blocks = []
        
        for state_name, state_config in states.items():
            transitions = state_config.get("transitions", [])
            
            for transition in transitions:
                transition_name = transition.get("name")
                next_state = transition.get("next")
                processors = transition.get("processors", [])
                criterion = transition.get("criterion")
                
                if not transition_name:
                    continue
                
                # Generate if block for this transition
                if_block = f'            if ("{transition_name}".equals(transition)) {{'
                
                # Add processor execution
                if processors:
                    for processor in processors:
                        processor_name = processor.get("name")
                        if processor_name:
                            if_block += f'\n                processorsFactory.get("{processor_name}").process(technicalId, entity);'
                
                # Add criteria checking
                if criterion and criterion.get("type") == "function":
                    criterion_name = criterion.get("function", {}).get("name")
                    if criterion_name and next_state:
                        if_block += f'\n                if (criteriaFactory.get("{criterion_name}").check(technicalId, entity)) {{'
                        if_block += f'\n                    nextTransition = "{next_state}";'
                        if_block += f'\n                }} else {{'
                        if_block += f'\n                    nextTransition = "failed";'
                        if_block += f'\n                }}'
                elif next_state:
                    if_block += f'\n                nextTransition = "{next_state}";'
                
                if_block += '\n            }'
                logic_blocks.append(if_block)
        
        return '\n\n'.join(logic_blocks) if logic_blocks else '            // No transitions defined'

    def _get_repository_name(self, entity: AgenticFlowEntity) -> str:
        """Get repository name from entity or use default Java repository."""
        return entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM, "java-client-template")

    def _get_git_branch_id(self, entity: AgenticFlowEntity, technical_id: str) -> str:
        """Get git branch ID from entity or use technical_id as fallback."""
        return entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
