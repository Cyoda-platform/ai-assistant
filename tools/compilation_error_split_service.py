import json
import logging
import os
from typing import List, Dict, Any

import common.config.const as const
from common.utils.utils import read_file_util
from entity.chat.chat import ChatEntity
from tools.base_service import BaseWorkflowService


logger = logging.getLogger(__name__)


class CompilationErrorSplitService(BaseWorkflowService):
    """
    Service responsible for parsing compilation output JSON and extracting file paths
    with errors for parallel processing.
    """

    async def get_files_with_compilation_errors(self, technical_id: str, entity: ChatEntity, **params):
        """
        Split function that parses project_compilation_output.json and returns file paths
        with compilation errors for parallel processing.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - input_file: Path to the compilation output JSON file (optional)

        Returns:
            JSON string containing list of file paths with errors
        """
        try:
            # Get input file path with default
            input_file = params.get('input_file', 'src/main/java/com/java_template/prototype/project_compilation_output.json')

            # Get repository information from entity
            branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM)
            repository_name = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)

            # Construct full file path
            from common.config.config import config
            if branch_id and repository_name:
                full_path = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/{input_file}"
            else:
                # Fallback to just the input file path if entity doesn't have branch/repo info
                full_path = input_file

            # Read and parse JSON file using the utility function
            try:
                content = await read_file_util(
                    filename=full_path,
                    technical_id=branch_id,
                    repository_name=repository_name
                )

                compilation_data = json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON from '{full_path}': {e}")
                return json.dumps([])
            except Exception as e:
                self.logger.error(f"Failed to read file '{full_path}': {e}")
                return json.dumps([])

            # Extract file paths with errors
            files_with_errors = compilation_data.get("files_with_errors", [])

            if not files_with_errors:
                self.logger.info("No files with compilation errors found")
                return json.dumps([])

            # Extract just the file paths for splitting
            file_paths = []
            for file_error in files_with_errors:
                file_path = file_error.get("file_path")
                if file_path and file_path.startswith((
                        "src/main/java/com/java_template/application",
                        "src/test/java/com/java_template/application/processor"
                )):
                    file_paths.append(file_path)
                    self.logger.info(f"Found file with errors: {file_path}")

            self.logger.info(f"Total files with compilation errors: {len(file_paths)}")

            # Return the list of file paths for job splitting
            return file_paths

        except Exception as e:
            return self._handle_error(entity, e, f"Error processing compilation output: {e}")


# Note: Service instantiation will be handled by the workflow system
# The service will be initialized with proper dependencies when needed
