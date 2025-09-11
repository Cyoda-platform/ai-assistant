import asyncio
import logging
import os
from typing import Dict, Any
from pathlib import Path
import common.config.const as const
from entity.model import AgenticFlowEntity, ChatMemory
from workflow.config_builder import ConfigBuilder
from common.utils.utils import save_all, read_file_util

logger = logging.getLogger(__name__)


class AuggieProcessor:
    """
    Handles processing of Auggie agent configurations by executing scripts.
    """

    def __init__(self, ai_agent, method_registry, memory_manager, cls_instance,
                 entity_service, cyoda_auth_service, config_builder=None):
        """
        Initialize the Auggie processor.

        Args:
            ai_agent: AI agent instance
            method_registry: Method registry for function calling
            memory_manager: Memory manager for chat operations
            cls_instance: Class instance for AI agent function calling
            entity_service: Entity service for edge message handling
            cyoda_auth_service: Cyoda auth service
            config_builder: Optional ConfigBuilder instance for message resolution
        """
        self.ai_agent = ai_agent
        self.method_registry = method_registry
        self.memory_manager = memory_manager
        self.cls_instance = cls_instance
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.config_builder = config_builder or ConfigBuilder()

    async def process_auggie_agent(self, config: Dict[str, Any], entity: AgenticFlowEntity,
                                  memory: ChatMemory, technical_id: str) -> str:
        """
        Process Auggie agent configuration by executing the specified script.

        Args:
            config: Configuration with script_path, prompt, model
            entity: Agentic flow entity
            memory: Chat memory
            technical_id: Technical identifier

        Returns:
            Response string with execution status
        """
        try:
            # Validate required configuration
            script_path = config.get("script_path")
            prompt = config.get("prompt", "")
            model = config.get("model", "")

            if not script_path:
                return "Error: script_path is required in Auggie agent configuration"

            # Validate agent type
            if config.get("type") != "agent" or config.get("agent_type") != "auggie":
                return "Error: Configuration must have type='agent' and agent_type='auggie'"

            # Resolve script path relative to project root (same as config_builder.py)
            resolved_script_path = self._resolve_script_path(script_path)

            # Check if script exists
            if not os.path.exists(resolved_script_path):
                return f"Error: Script not found at path: {resolved_script_path}"

            # Execute the script asynchronously
            logger.info(f"🚀 Executing Auggie script: {script_path}")
            logger.info(f"🎯 Model: {model}")

            # Get workspace and branch info from entity
            branch_id = self._get_git_branch_id(entity)
            repository_name = self._get_repository_name(entity)

            # Build workspace path (matching your current pattern)
            from common.config.config import config as app_config
            workspace_dir = f"{app_config.PROJECT_DIR}/{branch_id}/{repository_name}" if branch_id and repository_name else None

            # Handle input files and append to prompt
            enhanced_prompt = await self._enhance_prompt_with_input_files(config, prompt, entity, branch_id, repository_name)

            result = await self._execute_script(resolved_script_path, enhanced_prompt, model, workspace_dir, branch_id)

            # Save all entity changes after successful script execution
            if result and not result.startswith("Error"):
                logger.info("💾 Saving entity changes after Auggie script execution")
                commit_success = await self._commit_all_changes(branch_id, repository_name)
                if commit_success:
                    logger.info(f"🎉 [{branch_id}] All Auggie tasks completed and committed successfully!")
                else:
                    logger.warning(f"⚠️ [{branch_id}] Tasks completed but failed to commit changes")
                logger.info("✅ Entity changes saved successfully")

            return result

        except Exception as e:
            logger.exception(f"Error in Auggie agent processing: {e}")
            return f"Sorry, I'm having trouble with the Auggie agent: {str(e)}"

    async def _execute_script(
            self,
            script_path: str,
            prompt: str,
            model: str,
            workspace_dir: str = None,
            branch_id: str = None,
            timeout_seconds: int = 1800,   # 1/2 hour default
            kill_grace_seconds: int = 5    # wait before force-killing
    ) -> str:
        """
        Execute the specified script asynchronously with a timeout.
        Passes parameters as command line arguments.

        Args:
            script_path: Path to the script to execute
            prompt: Prompt to pass as argument
            model: Model to pass as argument
            workspace_dir: Workspace directory path
            branch_id: Branch ID
            timeout_seconds: Max time (in seconds) before forcibly stopping the process
            kill_grace_seconds: Time to wait after terminate() before kill()

        Returns:
            Script execution result
        """
        try:
            # Determine script execution command with arguments
            cmd_args = [prompt, model]
            if workspace_dir:
                cmd_args.append(workspace_dir)
            if branch_id:
                cmd_args.append(branch_id)

            if script_path.endswith('.py'):
                cmd = ["python", script_path] + cmd_args
            elif script_path.endswith('.sh'):
                cmd = ["bash", script_path] + cmd_args
            else:
                # Try to execute directly
                cmd = [script_path] + cmd_args

            logger.info(f"🔧 Executing command: {' '.join(cmd[:2])} [prompt] [model] [workspace] [branch]")
            logger.info(f"🎯 Model: {model}")
            if workspace_dir:
                logger.info(f"📁 Workspace: {workspace_dir}")
            if branch_id:
                logger.info(f"🌿 Branch: {branch_id}")

            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else ".",
            )
            logger.info(f"Started process {process.pid}")

            try:
                # Enforce timeout on the process itself
                await asyncio.wait_for(process.wait(), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"⏰ Script exceeded {timeout_seconds} seconds, terminating... process {process.pid}")
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass  # already gone

                try:
                    await asyncio.wait_for(process.wait(), timeout=kill_grace_seconds)
                except asyncio.TimeoutError:
                    logger.error(f"⚠️ Script did not terminate, killing... process {process.pid}")
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                    await process.wait()

            # Collect remaining output
            stdout, stderr = await process.communicate()

            stdout_str = stdout.decode('utf-8', errors="replace") if stdout else ""
            stderr_str = stderr.decode('utf-8', errors="replace") if stderr else ""

            if process.returncode == 0:
                logger.info(f"✅ Script executed successfully process {process.pid}")
                if stdout_str:
                    logger.debug(f"📋 Script output: {stdout_str[:200]}{'...' if len(stdout_str) > 200 else ''}")
                return stdout_str if stdout_str else f"Script executed successfully (no output)  process {process.pid}"
            else:
                logger.error(f"❌ Script failed with return code {process.returncode}")
                if stderr_str:
                    logger.error(f"❌ Script error: {stderr_str}  process {process.pid}")
                return f"Error: Script failed with return code {process.returncode}. Error: {stderr_str}  process {process.pid}"

        except Exception as e:
            logger.exception(f"Error executing script: {e} ")
            return f"Error executing script: {str(e)}"


    def _find_project_root(self) -> Path:
        """
        Find the project root directory by looking for key files.
        Same logic as config_builder.py

        Returns:
            Path to the project root directory
        """
        # Start from current file's directory and walk up
        current_path = Path(__file__).parent

        # Look for project indicators
        project_indicators = ['app.py', 'workflow_configs', '.git', 'requirements.txt']

        for parent in [current_path] + list(current_path.parents):
            if any((parent / indicator).exists() for indicator in project_indicators):
                return parent

        # Fallback: if we can't find project root, use current working directory
        cwd = Path.cwd()
        logger.warning(f"Could not determine project root, using current working directory: {cwd}")
        return cwd

    def _resolve_script_path(self, script_path: str) -> str:
        """
        Resolve script path relative to project root if it's a relative path.
        Same logic as config_builder.py

        Args:
            script_path: Script path (relative or absolute)

        Returns:
            Resolved absolute script path
        """
        path_obj = Path(script_path)

        # If path is relative, resolve it relative to project root
        if not path_obj.is_absolute():
            project_root = self._find_project_root()
            resolved_path = project_root / script_path
            return str(resolved_path)
        else:
            return script_path

    def _get_git_branch_id(self, entity: AgenticFlowEntity) -> str:
        """
        Get git branch ID from entity workflow cache.

        Args:
            entity: Agentic flow entity

        Returns:
            Git branch ID or None if not found
        """
        return entity.workflow_cache.get(const.GIT_BRANCH_PARAM)

    def _get_repository_name(self, entity: AgenticFlowEntity) -> str:
        """
        Get repository name for the entity.

        Args:
            entity: Agentic flow entity

        Returns:
            Repository name
        """
        from common.utils.utils import get_repository_name
        return get_repository_name(entity)

    async def _enhance_prompt_with_input_files(self, config: Dict[str, Any], prompt: str,
                                             entity: AgenticFlowEntity, branch_id: str,
                                             repository_name: str) -> str:
        """
        Enhance the prompt by appending input file contents with reference and file path.

        Args:
            config: Agent configuration
            prompt: Original prompt
            entity: Agentic flow entity
            branch_id: Git branch ID
            repository_name: Repository name

        Returns:
            Enhanced prompt with input file contents
        """
        try:
            input_config = config.get("input")
            if not input_config:
                return prompt

            local_fs_files = input_config.get("local_fs", [])
            if not local_fs_files:
                return prompt

            if not branch_id or not repository_name:
                logger.warning("Missing branch_id or repository_name for reading input files")
                return prompt

            # Read input files using utility function
            input_contents = []
            for file_path in local_fs_files:
                try:
                    content = await read_file_util(
                        filename=file_path,
                        technical_id=branch_id,
                        repository_name=repository_name,
                        git_branch_id=branch_id
                    )

                    if content and not content.startswith("Error during reading file"):
                        input_contents.append(f"Reference: {file_path}\n{content}")
                        logger.info(f"Successfully read input file: {file_path}")
                    else:
                        logger.warning(f"Input file not found or error reading: {file_path}")
                        input_contents.append(f"Reference: {file_path}\n[File not found or error reading file]")

                except Exception as e:
                    logger.error(f"Error reading input file {file_path}: {e}")
                    input_contents.append(f"Reference: {file_path}\n[Error reading file: {e}]")

            # Append input file contents to prompt
            if input_contents:
                enhanced_prompt = prompt + "\n\n" + "\n\n".join(input_contents)
                logger.info(f"Enhanced prompt with {len(local_fs_files)} input files")
                return enhanced_prompt

            return prompt

        except Exception as e:
            logger.exception(f"Error enhancing prompt with input files: {e}")
            return prompt



    async def _commit_all_changes(self, branch_id: str, repository_name: str) -> bool:
        """
        Commit all changes made by Auggie CLI to the repository.

        Args:
            branch_id: Git branch ID
            repository_name: Repository name
            completed_tasks: Number of completed tasks

        Returns:
            True if commit was successful, False otherwise
        """
        try:
            from common.config.config import config
            work_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}"

            # Generate commit message
            commit_message = f"Generated code using Auggie CLI - tasks completed"
            logger.info(f"📁 [{branch_id}] Working in directory: {work_dir}")
            logger.info(f"💬 [{branch_id}] Commit message: {commit_message}")

            # Execute git commands to add and commit all changes
            logger.debug(f"📦 [{branch_id}] Adding all changes to git...")
            process = await asyncio.create_subprocess_exec(
                "git", "add", ".",
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"❌ [{branch_id}] Git add failed: {stderr.decode('utf-8')}")
                return False

            # Check if there are changes to commit
            logger.debug(f"🔍 [{branch_id}] Checking for changes to commit...")
            process = await asyncio.create_subprocess_exec(
                "git", "diff", "--cached", "--quiet",
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

            # If return code is 0, there are no changes to commit
            if process.returncode == 0:
                logger.info(f"ℹ️ [{branch_id}] No changes to commit from Auggie tasks")
                return True

            # Commit changes
            logger.debug(f"💾 [{branch_id}] Committing changes...")
            process = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", commit_message,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"❌ [{branch_id}] Git commit failed: {stderr.decode('utf-8')}")
                return False

            logger.info(f"✅ [{branch_id}] Changes committed successfully")

            # Push changes
            logger.debug(f"🚀 [{branch_id}] Pushing changes to remote...")
            process = await asyncio.create_subprocess_exec(
                "git", "push",
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"❌ [{branch_id}] Git push failed: {stderr.decode('utf-8')}")
                return False

            logger.info(f"🎉 [{branch_id}] Successfully committed and pushed Auggie changes: {commit_message}")
            return True

        except Exception as e:
            logger.exception(f"Error committing Auggie changes: {e}")
            return False


