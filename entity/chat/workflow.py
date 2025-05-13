import json
import logging
import os
import httpx
import aiofiles
import common.config.const as const

from bs4 import BeautifulSoup
from typing import Any
from common.ai.nltk_service import get_most_similar_entity
from common.config.config import config
from common.exception.exceptions import GuestChatsLimitExceededException
from common.utils.batch_converter import convert_state_diagram_to_jsonl_dataset
from common.utils.batch_parallel_code import build_workflow_from_jsonl
from common.utils.chat_util_functions import _launch_transition
from common.utils.function_extractor import extract_function
from common.utils.result_validator import validate_ai_result
from common.utils.utils import get_project_file_name, _git_push, _save_file, clone_repo, \
    parse_from_string, read_file_util, send_cyoda_request
from common.utils.workflow_enricher import enrich_workflow
from common.workflow.workflow_to_state_diagram_converter import convert_to_mermaid
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity
from entity.workflow import Workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

entry_point_to_stack = {
}


class ChatWorkflow(Workflow):
    def __init__(self, dataset,
                 workflow_helper_service,
                 entity_service,
                 scheduler,
                 cyoda_auth_service,
                 #openapi_functions,  # todo will need factory soon
                 mock=False):
        self.dataset = dataset
        self.workflow_helper_service = workflow_helper_service
        self.entity_service = entity_service
        self.mock = mock
        self.scheduler = scheduler
        self.cyoda_auth_service = cyoda_auth_service
        #self.openapi_functions = openapi_functions

    async def save_env_file(self, technical_id, entity: ChatEntity, **params):
        file_name = await get_project_file_name(chat_id=technical_id, file_name=params.get("filename"), git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))
        async with aiofiles.open(file_name, 'r') as template_file:
            content = await template_file.read()

        # Replace CHAT_ID_VAR with $chat_id
        updated_content = content.replace('CHAT_ID_VAR', technical_id)

        # Save the updated content to a new file
        async with aiofiles.open(file_name, 'w') as new_file:
            await new_file.write(updated_content)
        await _git_push(technical_id, [file_name], "Added env file template")

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
        scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
            entity_service=self.entity_service,
            awaited_entity_ids=[build_id],
            triggered_entity_id=technical_id,
            scheduled_action=scheduled_action
        )
        entity.scheduled_entities.append(scheduled_entity_id)

        return f"Successfully scheduled {scheduled_action.value.replace('_', ' ')} with build ID {build_id}. Would you like to discuss anything else while my assistant is working on the job?"

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
        extra_payload = {
            "repository_url": config.CLIENT_QUART_TEMPLATE_REPOSITORY_URL,
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
        extra_payload = {
            "repository_url": config.CLIENT_QUART_TEMPLATE_REPOSITORY_URL,
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

        await clone_repo(chat_id=technical_id)

        # Call the async _save_file function
        await _save_file(chat_id=technical_id,
                         _data=technical_id,
                         item='README.txt',
                         git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))
        # todo - need to get from memory
        entity.workflow_cache['branch_name'] = technical_id
        return const.BRANCH_READY_NOTIFICATION.format(branch_name=technical_id)

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
            new_content = parse_from_string(escaped_code=params.get("new_content"))
            await _save_file(chat_id=technical_id,
                             _data=new_content,
                             item=params.get("filename"),
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))
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
        return await read_file_util(filename=params.get("filename"), technical_id=technical_id)

    async def set_additional_question_flag(self, technical_id: str, entity: ChatEntity, **params: Any) -> None:
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

        additional_flag = params.get("require_additional_question_flag")

        # Ensure the nested dictionary for conditions exists.
        conditions = entity.transitions_memory.conditions

        # Set the flag for the specified transition.
        conditions.setdefault(transition, {})["require_additional_question"] = additional_flag

    async def is_stage_completed(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        transition = params.get("transition")
        if transition is None:
            raise ValueError("Missing required parameter: 'transition'")

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
        await _save_file(chat_id=technical_id,
                         _data=result,
                         item=output_file_path,
                         git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))

    async def convert_workflow_json_to_state_diagram(self, technical_id, entity: ChatEntity, **params):
        input_file_path = params.get("input_file_path")
        with open(input_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        mermaid_diagram = convert_to_mermaid(data)
        return mermaid_diagram

    async def save_entity_templates(self, technical_id, entity: ChatEntity, **params):
        file_path = await get_project_file_name(technical_id, "entity/entities_data_design.json", git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))

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
            await _save_file(chat_id=technical_id,
                             _data=data_str,
                             item=target_item,
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))

    async def is_chat_locked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        return entity.locked

    async def is_chat_unlocked(self, technical_id: str, entity: ChatEntity, **params: Any) -> bool:
        return not entity.locked

    async def build_general_application(self, technical_id: str, entity: ChatEntity, **params: Any):
        workflow_name = const.ModelName.GEN_APP_ENTITY.value
        user_request = params.get("user_request")
        if not user_request:
            return "parameter user_request is required"
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            entity_service=self.entity_service,
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=workflow_name,
            user_request=user_request,
            workflow_cache=params)
        return f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. You'll be notified when it is in progress."

    async def unlock_chat(self, technical_id: str, entity: ChatEntity, **params: Any):
        entity.locked = False

    async def lock_chat(self, technical_id: str, entity: ChatEntity, **params: Any):
        entity.locked = True

    # =================================== generating_gen_app_workflow =============================

    async def register_workflow_with_app(self, technical_id, entity: AgenticFlowEntity, **params):
        filename = params.get("filename")
        try:
            file_path = await get_project_file_name(technical_id, filename, git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                input_json = json.loads(content)
            await _save_file(chat_id=technical_id,
                             _data=input_json.get("file_without_workflow").get("code"),
                             item=f"routes/routes.py",
                             git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id))
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
                    workflow_name=const.ModelName.GENERATING_GEN_APP_WORKFLOW.value,
                    workflow_cache=workflow_cache,
                    edge_messages_store=edge_messages_store)
                awaited_entity_ids.append(child_technical_id)

            if awaited_entity_ids:
                scheduled_entity_id = await self.workflow_helper_service.launch_scheduled_workflow(
                    entity_service=self.entity_service,
                    awaited_entity_ids=awaited_entity_ids,
                    triggered_entity_id=technical_id)
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
        await _save_file(
            chat_id=entity.parent_id,
            _data=code_without_function,
            item=f"entity/{entity.workflow_cache.get("entity_name")}/workflow.py",
            git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
        )
        return extracted_function

    async def save_workflow_configuration(self, technical_id, entity: AgenticFlowEntity, **params):
        "design_workflow_from_code"
        edge_message_id = entity.edge_messages_store.get(params.get("transition"))
        message_content = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                             entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                             entity_version=config.ENTITY_VERSION,
                                                             technical_id=edge_message_id,
                                                             meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        workflow_json = json.loads(message_content)
        workflow = enrich_workflow(workflow_json)
        await _save_file(
            chat_id=entity.parent_id,
            _data=json.dumps(workflow, indent=4, sort_keys=True),  # Prettified JSON
            item=f"entity/{entity.workflow_cache.get('entity_name')}/workflow.json",
            git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
        )

    # =================================== generating_gen_app_workflow end =============================
    # ==================================== scheduler flow =======================================

    async def schedule_workflow_tasks(self, technical_id, entity: SchedulerEntity, **params):
        result = self.scheduler.schedule_workflow_task(technical_id=technical_id,
                                                       awaited_entity_ids=entity.awaited_entity_ids,
                                                       scheduled_action=config.ScheduledAction(entity.scheduled_action))
        return result

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
        git_branch_id = params.get(const.GIT_BRANCH_PARAM)
        if git_branch_id and git_branch_id == "main":
            logger.exception("Modifications to main branch are not allowed")
            return "Modifications to main branch are not allowed"
        await clone_repo(chat_id=git_branch_id)
        app_api = await read_file_util(filename="routes/routes.py", technical_id=git_branch_id)
        entities_description = []
        project_entities_list = await self.get_entities_list(branch_id=git_branch_id)
        for project_entity in project_entities_list:
            workflow_code = await read_file_util(technical_id=git_branch_id,
                                                 filename=f"entity/{project_entity}/workflow.py")
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
        git_branch_id: str = params.get(const.GIT_BRANCH_PARAM, entity.workflow_cache.get(const.GIT_BRANCH_PARAM))
        if git_branch_id:
            if git_branch_id == "main":
                logger.exception("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"
            await clone_repo(chat_id=git_branch_id)

        # One-off resolution for workflows that need an entity_name
        if resolve_entity_name:
            entity_name = await self._resolve_entity_name(
                entity_name=params.get("entity_name"),
                branch_id=git_branch_id,
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
            #raise GuestChatsLimitExceededException()
            return "Sorry, deploying Cyoda env is available only to logged in users. Please sign up or login!"
        # todo cloud manager needs to return namespace
        params['cyoda_env_name'] = f"{entity.user_id.lower()}.{config.CLIENT_HOST}"
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
            #raise GuestChatsLimitExceededException()
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

    async def init_setup_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        if entity.user_id.startswith('guest'):
            #raise GuestChatsLimitExceededException()
            return "Sorry, setting up Cyoda env is available only to logged in users. Please sign up or login!"
        # todo cloud manager needs to return namespace
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.INIT_SETUP_WORKFLOW.value,
            params=params,
        )


    async def add_new_entity_for_existing_app(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.ADD_NEW_ENTITY.value,
            params=params,
        )

    async def add_new_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.ADD_NEW_WORKFLOW.value,
            params=params,
            resolve_entity_name=True,
        )

    async def edit_api_existing_app(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.EDIT_API_EXISTING_APP.value,
            params=params,
            resolve_entity_name=False,
        )

    async def edit_existing_processors(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.EDIT_EXISTING_PROCESSORS.value,
            params=params,
            resolve_entity_name=True,
        )

    async def edit_existing_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        return await self._schedule_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            workflow_name=const.ModelName.EDIT_EXISTING_WORKFLOW.value,
            params=params,
            resolve_entity_name=True,
        )

    async def fail_workflow(
            self, technical_id: str, entity: AgenticFlowEntity, **params
    ) -> str:
        logger.exception(f"failed workflow {technical_id}")
        return const.Notifications.FAILED_WORKFLOW.value.format(technical_id=technical_id)

    async def get_entities_list(self, branch_id: str) -> list:
        entity_dir = f"{config.PROJECT_DIR}/{branch_id}/{config.REPOSITORY_NAME}/entity"

        # List all subdirectories (each subdirectory is an entity)
        entities = [name for name in os.listdir(entity_dir)
                    if os.path.isdir(os.path.join(entity_dir, name))]

        return entities

    def parse_from_string(self, escaped_code: str) -> str:
        return escaped_code.encode("utf-8").decode("unicode_escape")

    async def _resolve_entity_name(self, entity_name: str, branch_id: str) -> str:
        entity_names = await self.get_entities_list(branch_id=branch_id)
        resolved_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
        return resolved_name if resolved_name else entity_name



