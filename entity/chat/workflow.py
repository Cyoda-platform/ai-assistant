import json
import logging
import os
import httpx
import aiofiles
import common.config.const as const

from bs4 import BeautifulSoup
from typing import Any, List

from common.ai.nltk_service import get_most_similar_entity
from common.config.config import config
from common.utils.batch_converter import convert_state_diagram_to_jsonl_dataset
from common.utils.batch_parallel_code import build_workflow_from_jsonl
from common.utils.chat_util_functions import _launch_transition
from common.utils.function_extractor import extract_function
from common.utils.result_validator import validate_ai_result
from common.utils.utils import get_project_file_name, _git_push, _save_file, clone_repo, \
    parse_from_string, read_file_util, send_cyoda_request, get_repository_name, delete_file
from common.workflow.workflow_to_state_diagram_converter import convert_to_mermaid
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity
from entity.workflow import Workflow

logger = logging.getLogger(__name__)

entry_point_to_stack = {
}


class ChatWorkflow(Workflow):
    def __init__(self, dataset,
                 workflow_helper_service,
                 entity_service,
                 cyoda_auth_service,
                 workflow_converter_service,  # todo will need factory soon
                 scheduler_service,
                 mock=False):
        self.dataset = dataset
        self.workflow_helper_service = workflow_helper_service
        self.entity_service = entity_service
        self.mock = mock
        self.cyoda_auth_service = cyoda_auth_service
        self.workflow_converter_service = workflow_converter_service
        self.scheduler_service = scheduler_service

    async def save_env_file(self, technical_id, entity: ChatEntity, **params):
        repository_name = get_repository_name(entity)
        file_name = await get_project_file_name(file_name=params.get("filename"),
                                                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM,
                                                                                        technical_id),
                                                repository_name=repository_name
                                                )
        async with aiofiles.open(file_name, 'r') as template_file:
            content = await template_file.read()

        # Replace CHAT_ID_VAR with $chat_id
        updated_content = content.replace('CHAT_ID_VAR', technical_id)

        # Save the updated content to a new file
        async with aiofiles.open(file_name, 'w') as new_file:
            await new_file.write(updated_content)
        await _git_push(technical_id, [file_name], "Added env file template", repository_name=repository_name)

    # todo need to refactor and add a different service for cloud manager integration
    async def _schedule_deploy(
            self,
            technical_id: str,
            entity: ChatEntity,
            scheduled_action: config.ScheduledAction,
            extra_payload: dict | None = None
    ) -> str:
        # Determine endpoint from action
        try:
            base_url = config.ACTION_URL_MAP[scheduled_action]
        except KeyError:
            raise ValueError(f"Unsupported scheduled action: {scheduled_action}")

        # Prepare request payload
        payload = {
            "chat_id": str(technical_id),
            "user_name": str(entity.user_id)
        }
        if extra_payload:
            payload.update(extra_payload)

        data = json.dumps(payload)
        # Send the deployment request
        resp = await send_cyoda_request(
            cyoda_auth_service=self.cyoda_auth_service,
            method="post",
            base_url=base_url,
            path='',
            data=data
        )

        # Validate response
        build_info = resp.get("json", {})
        build_id = build_info.get("build_id")
        if not build_id:
            raise ValueError("No build_id found in the response")

        # Schedule the workflow
        # todo check for the next transition
        scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
            entity_service=self.entity_service,
            awaited_entity_ids=[build_id],
            triggered_entity_id=technical_id,
            scheduled_action=scheduled_action
        )
        entity.scheduled_entities.append(scheduled_entity_id)

        return f"Successfully scheduled {scheduled_action.value.replace('_', ' ')} with build ID {build_id}."

    async def schedule_deploy_env(
            self,
            technical_id: str,
            entity: ChatEntity,
            **params
    ) -> str:
        return await self._schedule_deploy(
            technical_id,
            entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
        )

    async def schedule_build_user_application(
            self,
            technical_id: str,
            entity: ChatEntity,
            **params
    ) -> str:
        repository_name = get_repository_name(entity)
        repository_url = f"{config.REPOSITORY_URL.format(repository_name=repository_name)}.git"
        extra_payload = {
            "repository_url": repository_url,
            "branch": entity.workflow_cache.get(const.GIT_BRANCH_PARAM),
            "is_public": "true"
        }
        return await self._schedule_deploy(
            technical_id,
            entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_USER_APP_BUILD,
            extra_payload=extra_payload
        )

    async def schedule_deploy_user_application(
            self,
            technical_id: str,
            entity: ChatEntity,
            **params
    ) -> str:
        repository_name = get_repository_name(entity)
        repository_url = f"{config.REPOSITORY_URL.format(repository_name=repository_name)}.git"
        extra_payload = {
            "repository_url": repository_url,
            "branch": entity.workflow_cache.get(const.GIT_BRANCH_PARAM),
            "is_public": "true"
        }
        return await self._schedule_deploy(
            technical_id,
            entity,
            scheduled_action=config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY,
            extra_payload=extra_payload
        )

    async def clone_repo(self, technical_id, entity: ChatEntity, **params):
        """
        Clone the GitHub repository to the target directory.
        If the repository should not be copied, it ensures the target directory exists.
        """

        repository_name = get_repository_name(entity)

        await clone_repo(git_branch_id=technical_id, repository_name=repository_name)

        # Call the async _save_file function
        await _save_file(_data=technical_id,
                         item='README.txt',
                         git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                         repository_name=repository_name)
        # todo - need to get from memory
        entity.workflow_cache[const.GIT_BRANCH_PARAM] = technical_id
        return const.BRANCH_READY_NOTIFICATION.format(repository_name=repository_name, git_branch=technical_id)

    async def init_chats(self, technical_id, entity: ChatEntity, **params):
        if config.MOCK_AI == "true":
            return
        pass

    async def web_search(self, technical_id, entity: ChatEntity, **params) -> str:
        """
        Performs a Google Custom Search using API key and search engine ID from environment variables.
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": config.GOOGLE_SEARCH_KEY,
                "cx": config.GOOGLE_SEARCH_CX,
                "q": params.get("query"),
                "num": 1  # Retrieve only the first result
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if "items" in data and data["items"]:
                first_item = data["items"][0]
                snippet = first_item.get("snippet")
                result = snippet if snippet else "No snippet available."
            else:
                result = "No results found."
        except Exception as e:
            entity.failed = True
            entity.error = f"Error: {e}"
            result = f"Error during search: {e}"
        return result

    async def read_link(self, technical_id, entity: ChatEntity, **params) -> str:
        """
        Reads the content of a given URL and returns its textual content.
        """
        return await self._fetch_data(url=params.get("url"))

    async def _fetch_data(self, url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            if paragraphs:
                content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                result = content
            else:
                result = soup.get_text(strip=True)
        except Exception as e:
            logger.exception(e)
            return "Sorry, there were issues while doing your task. Please retry."
        return result

    async def web_scrape(self, technical_id, entity: ChatEntity, **params) -> str:
        """
        Scrapes a webpage at the given URL using the provided CSS selector and returns the extracted text.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(params.get("url"))
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.select(params.get("selector"))
            if elements:
                content = "\n".join(element.get_text(separator=" ", strip=True) for element in elements)
                result = content
            else:
                result = "No elements found for the given selector."
        except Exception as e:
            entity.failed = True
            entity.error = f"Error: {e}"
            result = f"Error during web scraping: {e}"
        return result

    async def save_file(self, technical_id, entity: ChatEntity, **params) -> str:
        """
        Saves data to a file using the provided chat id and file name.
        """
        try:
            repository_name = get_repository_name(entity)
            if repository_name.startswith("java"):
                new_content = params.get("new_content")
            else:
                new_content = parse_from_string(escaped_code=params.get("new_content"))
            # new_content = parse_from_string(escaped_code=params.get("new_content"))
            await _save_file(_data=new_content,
                             item=params.get("filename"),
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                             repository_name=get_repository_name(entity))
            return "File saved successfully"
        except Exception as e:
            entity.failed = True
            entity.error = f"Error: {e}"
            return f"Error during saving file: {e}"

    async def read_file(self, technical_id, entity: ChatEntity, **params) -> str:
        """
        Reads data from a file using the provided chat id and file name.
        """
        # Await the asynchronous git_pull function.
        return await read_file_util(filename=params.get("filename"), technical_id=technical_id,
                                    repository_name=get_repository_name(entity))

    async def finish_discussion(self, technical_id: str, entity: AgenticFlowEntity, **params: Any) -> None:
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

        additional_flag = False

        # Ensure the nested dictionary for conditions exists.
        conditions = entity.transitions_memory.conditions

        # Set the flag for the specified transition.
        conditions.setdefault(transition, {})["require_additional_question"] = additional_flag

    async def is_stage_completed(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        if params.get('params'):
            logger.exception("Wrong value for params")
            params = params.get('params')
        transition = params.get("transition")
        if transition is None:
            logger.exception("Missing required parameter: 'transition'")
            return False

        transitions = entity.transitions_memory
        current_iteration = transitions.current_iteration
        max_iteration = transitions.max_iteration

        if transition in current_iteration:
            allowed_max = max_iteration.get(transition, config.MAX_ITERATION)
            if current_iteration[transition] > allowed_max:
                return True

        conditions = transitions.conditions
        # If the condition for the transition does not exist, assume stage is not completed.
        if transition not in conditions:
            return False

        # Return the inverse of the require_additional_question flag.
        return not conditions[transition].get("require_additional_question", True)

    async def not_stage_completed(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        completed = await self.is_stage_completed(technical_id=technical_id, entity=entity, params=params)
        return not completed

    async def get_weather(self, technical_id, entity: ChatEntity, **params):
        # Example implementation; replace with actual API integration
        return {
            "city": params.get("city"),
            "temperature": "18°C",
            "condition": "Sunny"
        }

    async def get_humidity(self, technical_id, entity: ChatEntity, **params):
        # Example implementation; replace with actual API integration
        return {
            "city": params.get("city"),
            "humidity": "55%"
        }

    async def convert_diagram_to_dataset(self, technical_id, entity: ChatEntity, **params):
        input_file_path = params.get("input_file_path")
        output_file_path = params.get("output_file_path")
        convert_state_diagram_to_jsonl_dataset(input_file_path=input_file_path,
                                               output_file_path=output_file_path)

    async def convert_workflow_processed_dataset_to_json(self, technical_id, entity: ChatEntity, **params):
        input_file_path = params.get("input_file_path")
        output_file_path = params.get("output_file_path")
        result = await build_workflow_from_jsonl(input_file_path=input_file_path)
        await _save_file(_data=result,
                         item=output_file_path,
                         git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                         repository_name=get_repository_name(entity))

    async def convert_workflow_json_to_state_diagram(self, technical_id, entity: ChatEntity, **params):
        input_file_path = params.get("input_file_path")
        with open(input_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        mermaid_diagram = convert_to_mermaid(data)
        return mermaid_diagram

    async def save_entity_templates(self, technical_id, entity: ChatEntity, **params):
        file_path = await get_project_file_name(file_name="entity/entities_data_design.json",
                                                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM,
                                                                                        technical_id),
                                                repository_name=get_repository_name(entity))

        try:
            async with aiofiles.open(file_path, 'r') as f:
                file_contents = await f.read()
            # Parse JSON contents from the file
            entity_design_data = json.loads(file_contents)
        except Exception as exc:
            logger.exception(f"Failed to load or parse file {file_path}: {exc}")
            return  # Exit early if file read or JSON parsing fails

        # Retrieve list of entities, or use an empty list if key is missing
        entities = entity_design_data.get("entities", [])

        for entity_data in entities:
            entity_name = entity_data.get('entity_name')
            entity_data_example = entity_data.get('entity_data_example')

            # Validate required data
            if not entity_name:
                logger.warning("Missing 'entity_name' in entity data: %s", entity_data)
                continue

            # Build the target file path for this entity's template
            target_item = f"entity/{entity_name}/{entity_name}.json"
            # Convert entity data to JSON string, using a default if None
            data_str = json.dumps(entity_data_example, indent=4,
                                  sort_keys=True) if entity_data_example is not None else "{}"

            # Save the file asynchronously
            await _save_file(_data=data_str,
                             item=target_item,
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                             repository_name=get_repository_name(entity))

    async def is_chat_locked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        return entity.locked

    async def is_chat_unlocked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        return not entity.locked

    async def build_general_application(self, technical_id: str, entity: ChatEntity, **params: Any):
        user_request = params.get("user_request")
        programming_language = params.get("programming_language")

        if not user_request:
            return "parameter user_request is required"
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.GEN_APP_ENTITY_JAVA.value if programming_language == "JAVA" else const.ModelName.GEN_APP_ENTITY_PYTHON.value
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            entity_service=self.entity_service,
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            user_request=user_request,
            workflow_cache=params,
            resume_transition=const.TransitionKey.BUILD_NEW_APP.value)

        return f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. You'll be notified when it is in progress."

    async def unlock_chat(self, technical_id: str, entity: ChatEntity, **params: Any):
        entity.locked = False

    async def lock_chat(self, technical_id: str, entity: ChatEntity, **params: Any):
        entity.locked = True

    # =================================== generating_gen_app_workflow =============================

    async def register_workflow_with_app(self, technical_id, entity: AgenticFlowEntity, **params):
        filename = params.get("filename")
        routes_file = params.get("routes_file")
        try:
            file_path = await get_project_file_name(file_name=filename,
                                                    git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM,
                                                                                            technical_id),
                                                    repository_name=get_repository_name(entity))
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                input_json = json.loads(content)
            await _save_file(_data=input_json.get("file_without_workflow").get("code"),
                             item=routes_file,
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                             repository_name=get_repository_name(entity))
            awaited_entity_ids = []
            for item in input_json.get("entity_models"):
                # For each key-value pair in the dictionary, where key is the entity name and value is the code snippet
                if not isinstance(item, dict):
                    continue
                entity_model_name = item.get("entity_model_name")
                if not entity_model_name or not isinstance(entity_model_name, str):
                    continue
                workflow_function = item.get("workflow_function")
                if not workflow_function or not isinstance(workflow_function, dict):
                    continue
                workflow_cache = {
                    'workflow_function': workflow_function.get('name'),
                    'entity_name': entity_model_name,
                    const.GIT_BRANCH_PARAM: entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
                }
                edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                     entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                                     entity_version=config.ENTITY_VERSION,
                                                                     entity=json.dumps(workflow_function),
                                                                     meta={
                                                                         "type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                edge_messages_store = {
                    'code': edge_message_id,
                }

                child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                    entity_service=self.entity_service,
                    technical_id=technical_id,
                    entity=entity,
                    entity_model=const.ModelName.AGENTIC_FLOW_ENTITY.value,
                    workflow_name=const.ModelName.GENERATING_GEN_APP_WORKFLOW_JAVA.value if entity.workflow_name.endswith(
                        "java") else const.ModelName.GENERATING_GEN_APP_WORKFLOW_PYTHON.value,
                    workflow_cache=workflow_cache,
                    edge_messages_store=edge_messages_store)
                awaited_entity_ids.append(child_technical_id)

            if awaited_entity_ids:
                # todo, need some way to identify next allowed transition
                scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
                    entity_service=self.entity_service,
                    awaited_entity_ids=awaited_entity_ids,
                    triggered_entity_id=technical_id,
                    triggered_entity_next_transition="update_routes_file"
                )
                entity.scheduled_entities.append(scheduled_entity_id)
            else:
                raise Exception(f"No workflows generated for {technical_id}")
        except Exception as e:
            entity.failed = True
            entity.error = f"Error: {e}"
            logger.exception(e)

    async def reset_failed_entity(self, technical_id, entity: AgenticFlowEntity, **params):
        entity.failed = False
        return "Retrying last step"

    async def validate_workflow_design(self, technical_id, entity: AgenticFlowEntity, **params):
        edge_message_id = entity.edge_messages_store.get(params.get("transition"))
        result = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                    entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                    entity_version=config.ENTITY_VERSION,
                                                    technical_id=edge_message_id,
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        is_valid, formatted_result = validate_ai_result(result, "result.py")
        if is_valid:
            return formatted_result
        return None

    async def has_workflow_code_validation_succeeded(self, technical_id: str, entity: AgenticFlowEntity,
                                                     **params: Any) -> bool:
        edge_message_id = entity.edge_messages_store.get(params.get("transition"))
        result = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                    entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                    entity_version=config.ENTITY_VERSION,
                                                    technical_id=edge_message_id,
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        return result is not None

    async def has_workflow_code_validation_failed(self, technical_id: str, entity: AgenticFlowEntity,
                                                  **params: Any) -> bool:
        edge_message_id = entity.edge_messages_store.get(params.get("transition"))
        result = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                    entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                    entity_version=config.ENTITY_VERSION,
                                                    technical_id=edge_message_id,
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        return result is None

    async def save_extracted_workflow_code(self, technical_id, entity: AgenticFlowEntity, **params):
        edge_message_id = entity.edge_messages_store.get(params.get("transition"))
        source = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                    entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                    entity_version=config.ENTITY_VERSION,
                                                    technical_id=edge_message_id,
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})

        code_without_function, extracted_function = extract_function(
            source=source,
            function_name=entity.workflow_cache.get("workflow_function"))
        logger.info(extracted_function)
        await _save_file(_data=code_without_function,
                         item=f"entity/{entity.workflow_cache.get("entity_name")}/workflow.py",
                         git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                         repository_name=get_repository_name(entity)
                         )
        return extracted_function

    # =================================== generating_gen_app_workflow end =============================
    # ==================================== scheduler flow =======================================

    async def trigger_parent_entity(self, technical_id, entity: SchedulerEntity, **params):
        "design_workflow_from_code"
        await _launch_transition(entity_service=self.entity_service,
                                 technical_id=entity.triggered_entity_id,
                                 cyoda_auth_service=self.cyoda_auth_service,
                                 transition=entity.triggered_entity_next_transition)

    async def edit_existing_app_design_additional_feature(self,
                                                          technical_id,
                                                          entity: AgenticFlowEntity,
                                                          **params):
        # Clean up chat_id if needed
        repository_name = get_repository_name(entity)
        git_branch_id = params.get(const.GIT_BRANCH_PARAM)
        if git_branch_id and git_branch_id == "main":
            logger.exception("Modifications to main branch are not allowed")
            return "Modifications to main branch are not allowed"
        await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)
        if repository_name.startswith("java"):
            filename = "src/main/java/com/java_template/controller/Controller.java"
        else:
            filename = "routes/routes.py"
        app_api = await read_file_util(filename=filename,
                                       technical_id=git_branch_id,
                                       repository_name=get_repository_name(entity))
        entities_description = []
        project_entities_list = await self.get_entities_list(branch_id=git_branch_id,
                                                             repository_name=get_repository_name(entity))
        for project_entity in project_entities_list:
            if repository_name.startswith("java"):
                filename = f"src/main/java/com/java_template/entity/{project_entity}/{project_entity}Workflow.java"
            else:
                filename = f"entity/{project_entity}/workflow.py"
            workflow_code = await read_file_util(technical_id=git_branch_id,
                                                 filename=filename,
                                                 repository_name=get_repository_name(entity))
            entities_description.append({project_entity: workflow_code})

        workflow_cache = {
            'user_request': params.get("user_request")
        }
        app_api_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                        entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                        entity_version=config.ENTITY_VERSION,
                                                        entity=app_api,
                                                        meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})

        entities_description_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                     entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                                     entity_version=config.ENTITY_VERSION,
                                                                     entity=json.dumps(entities_description),
                                                                     meta={
                                                                         "type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})

        edge_messages_store = {
            'app_api': app_api_id,
            'entities_description': entities_description_id,
        }
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            entity_service=self.entity_service,
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.ADD_NEW_FEATURE.value,
            workflow_cache=workflow_cache,
            edge_messages_store=edge_messages_store)

        return f"Successfully scheduled workflow for updating user application {child_technical_id}. I'll be right back - please don't ask anything else."

    async def resume_build_general_application(self,
                                               technical_id,
                                               entity: AgenticFlowEntity,
                                               **params):
        # Clean up chat_id if needed

        programming_language = params.get("programming_language")
        git_branch_id = params.get(const.GIT_BRANCH_PARAM)

        transition = params.get("transition")
        repository_name = config.JAVA_REPOSITORY_NAME if programming_language == "JAVA" else config.PYTHON_REPOSITORY_NAME
        if git_branch_id and git_branch_id == "main":
            logger.exception("Modifications to main branch are not allowed")
            return "Modifications to main branch are not allowed"
        await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)

        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            entity_service=self.entity_service,
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.GEN_APP_ENTITY_PYTHON.value,
            workflow_cache=params,
            resume_transition=transition,
            edge_messages_store=None)

        return f"Successfully scheduled workflow for updating user application {child_technical_id}. I'll be right back - please don't ask anything else."

    # ========== general function

    async def get_cyoda_guidelines(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        url = f"{config.DATA_REPOSITORY_URL}/get_cyoda_guidelines/{params.get("workflow_name")}.adoc"
        return await self._fetch_data(url=url)

    # ==========

    async def _schedule_workflow(
            self,
            technical_id: str,
            entity: AgenticFlowEntity,
            entity_model: str,
            workflow_name: str,
            params: dict,
            resolve_entity_name: bool = False,
    ) -> str:
        # Clone the repo based on branch ID if provided
        repository_name = get_repository_name(entity)
        git_branch_id: str = params.get(const.GIT_BRANCH_PARAM, entity.workflow_cache.get(const.GIT_BRANCH_PARAM))
        if git_branch_id:
            if git_branch_id == "main":
                logger.exception("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"
            await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)

        # One-off resolution for workflows that need an entity_name
        if resolve_entity_name:
            entity_name = await self._resolve_entity_name(
                entity_name=params.get("entity_name"),
                branch_id=git_branch_id,
                repository_name=get_repository_name(entity)
            )
            params["entity_name"] = entity_name

        # Launch the actual agentic workflow
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            entity_service=self.entity_service,
            technical_id=technical_id,
            entity=entity,
            entity_model=entity_model,
            workflow_name=workflow_name,
            workflow_cache=params,
            edge_messages_store={},
        )

        return (
            f"Successfully scheduled workflow to implement the task. I'll be right back with a new dialogue plan. Please don't ask anything just yet i'm back."
            f"{child_technical_id}"
        )

    # ==========================deploy================================
    async def deploy_cyoda_env(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        if entity.user_id.startswith('guest'):
            # raise GuestChatsLimitExceededException()
            return "Sorry, deploying Cyoda env is available only to logged in users. Please sign up or login!"
        # todo cloud manager needs to return namespace
        params['cyoda_env_name'] = f"{entity.user_id.lower()}.{config.CLIENT_HOST}"
        if params.get("transition"):
            await self.finish_discussion(technical_id=technical_id, entity=entity, **params)
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.DeploymentFlow.DEPLOY_CYODA_ENV.value,
            params=params,
        )

    async def deploy_user_application(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        if entity.user_id.startswith('guest'):
            # raise GuestChatsLimitExceededException()
            return "Sorry, deploying client application is available only to logged in users. Please sign up or login!"

        # todo cloud manager needs to return namespace
        params['user_env_name'] = f"client-{entity.user_id.lower()}.{config.CLIENT_HOST}"

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.DeploymentFlow.DEPLOY_USER_APPLICATION.value,
            params=params,
        )

    # ==========================editing========================================

    async def delete_files(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        files: List[str] = params.get("files")
        for file_name in files:
            await delete_file(_data=technical_id,
                              item=file_name,
                              git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                              repository_name=get_repository_name(entity))
        return ''

    async def init_setup_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        if entity.user_id.startswith('guest'):
            # raise GuestChatsLimitExceededException()
            return "Sorry, setting up Cyoda env is available only to logged in users. Please sign up or login!"
        # todo cloud manager needs to return namespace
        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.INIT_SETUP_WORKFLOW_JAVA.value if programming_language == "JAVA" else const.ModelName.INIT_SETUP_WORKFLOW_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
        )

    async def add_new_entity_for_existing_app(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.ADD_NEW_ENTITY_JAVA.value if programming_language == "JAVA" else const.ModelName.ADD_NEW_ENTITY_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
        )

    async def add_new_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:

        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.ADD_NEW_WORKFLOW_JAVA.value if programming_language == "JAVA" else const.ModelName.ADD_NEW_WORKFLOW_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
            resolve_entity_name=True,
        )

    async def edit_api_existing_app(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:

        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.EDIT_API_EXISTING_APP_JAVA.value if programming_language == "JAVA" else const.ModelName.EDIT_API_EXISTING_APP_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
            resolve_entity_name=False,
        )

    async def edit_existing_processors(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.EDIT_EXISTING_PROCESSORS_JAVA.value if programming_language == "JAVA" else const.ModelName.EDIT_EXISTING_PROCESSORS_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
            resolve_entity_name=True,
        )

    async def edit_existing_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:

        programming_language = params.get("programming_language")
        if not programming_language:
            return "parameter programming_language is required"
        workflow_name = const.ModelName.EDIT_EXISTING_WORKFLOW_JAVA.value if programming_language == "JAVA" else const.ModelName.EDIT_EXISTING_WORKFLOW_PYTHON.value

        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            params=params,
            resolve_entity_name=True,
        )

    async def fail_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        logger.exception(f"failed workflow {technical_id}")
        return const.Notifications.FAILED_WORKFLOW.value.format(technical_id=technical_id)

    async def get_entities_list(self, branch_id: str, repository_name: str) -> list:
        entity_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/entity"

        if repository_name.startswith("java"):
            entity_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}/src/main/java/com/java_template/entity"

        # List all subdirectories (each subdirectory is an entity)
        entities = [name for name in os.listdir(entity_dir)
                    if os.path.isdir(os.path.join(entity_dir, name))]

        return entities

    async def check_scheduled_entity_status(self, technical_id: str, entity: SchedulerEntity, **params):
        status, next_transition = await self.scheduler_service.run_for_entity(technical_id=technical_id, entity=entity)
        if status:
            entity.status = status
        if next_transition:
            entity.triggered_entity_next_transition = next_transition

    def parse_from_string(self, escaped_code: str) -> str:
        return escaped_code.encode("utf-8").decode("unicode_escape")

    async def _resolve_entity_name(self, entity_name: str, branch_id: str, repository_name: str) -> str:
        entity_names = await self.get_entities_list(branch_id=branch_id, repository_name=repository_name)
        resolved_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
        return resolved_name if resolved_name else entity_name

    async def convert_workflow_to_dto(
            self,
            technical_id: str,
            entity: AgenticFlowEntity,
            **params: Any,
    ) -> str:
        success_msg = "Successfully converted workflow config to cyoda dto"
        error_msg = "Error while converting workflow"
        try:
            # 1) Extract & validate parameters
            entity_name = entity.workflow_cache.get("entity_name", params.get("entity_name"))
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, params.get(const.GIT_BRANCH_PARAM))

            if not (entity_name or git_branch_id):
                raise ValueError("Missing entity_name in workflow_cache")

            workflow_file_tmpl = params.get("workflow_file_name")
            output_file_tmpl = params.get("output_file_name")
            if not (workflow_file_tmpl and output_file_tmpl):
                raise ValueError("Both workflow_file_name and output_file_name are required")

            entity_version = params.get("entity_version", config.CLIENT_ENTITY_VERSION)
            repo_name = get_repository_name(entity)

            # 2) Compute file names
            workflow_filename = workflow_file_tmpl.format(entity_name=entity_name)
            output_filename = output_file_tmpl.format(entity_name=entity_name)

            # 3) Load, transform, persist original workflow
            project_path = await get_project_file_name(
                git_branch_id=git_branch_id,
                file_name=workflow_filename,
                repository_name=repo_name,
            )
            workflow = await self.workflow_helper_service.read_json(project_path)

            ordered_fsm = await self.workflow_helper_service.order_states_in_fsm(workflow)

            # 2) Convert to DTO
            dto = await self.workflow_converter_service.convert_workflow(
                workflow_contents=workflow,
                entity_name=entity_name,
                entity_version=entity_version,
                technical_id=git_branch_id,
            )

            # 3) Persist both JSON blobs in a loop
            to_save = [
                (workflow_filename, ordered_fsm),
                (output_filename, dto),
            ]
            for path_or_item, data in to_save:
                await self.workflow_helper_service.persist_json(
                    path_or_item=path_or_item,
                    data=data,
                    git_branch_id=git_branch_id,
                    repository_name=repo_name,
                )

            return success_msg

        except Exception:
            logger.exception("Failed to convert workflow for %s", technical_id)
            return error_msg
