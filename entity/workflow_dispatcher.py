import json
import os
import common.config.const as const
import aiofiles
import inspect
import logging
from typing import List

from common.config.config import config as env_config
from common.utils.batch_parallel_code import batch_process_file

from common.utils.chat_util_functions import enrich_config_message
from common.utils.utils import _save_file, _post_process_response, get_current_timestamp_num
from entity.chat.model.chat import AgenticFlowEntity
from entity.model import FlowEdgeMessage, ChatMemory, AIMessage, WorkflowEntity, ModelConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowDispatcher:
    def __init__(self, cls, cls_instance, ai_agent, entity_service, cyoda_auth_service, mock=False):
        self.cls = cls
        self.cls_instance = cls_instance
        self.methods_dict = self._collect_subclass_methods()
        self.ai_agent = ai_agent
        self.entity_service = entity_service
        self.cyoda_auth_service=cyoda_auth_service

    def _collect_subclass_methods(self):

        # Using inspect.getmembers ensures we only get functions defined on the class
        methods = {}
        for name, func in inspect.getmembers(self.cls,
                                             predicate=inspect.isfunction):
            # Create a unique key to avoid collisions
            key = f"{name}"
            methods[key] = func
        return methods

    async def dispatch_function(self, function_name, **params):
        try:
            if function_name in self.methods_dict:
                response = await self.methods_dict[function_name](self.cls_instance,
                                                                  **params)
            else:
                raise ValueError(f"Unknown processing step: {function_name}")
            return response
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error processing event: {e}")
            return None

    async def process_event(self, entity: WorkflowEntity, action, technical_id):

        response = "returned empty response"
        try:
            config = action.get("config")
            action_name = action.get("name")

            if config and config.get("type") and isinstance(entity, AgenticFlowEntity):
                entity = AgenticFlowEntity(**entity.model_dump())
                entity, response = await self._handle_config_based_event(config=config,
                                                                 entity=entity,
                                                                 technical_id=technical_id)
            elif config and config.get("type") and isinstance(entity, WorkflowEntity):
                if config["type"] == "function":
                    params = config["function"].get("parameters", {})
                    response = await self.methods_dict[config["function"]["name"]](self.cls_instance,
                                                                                   technical_id=technical_id,
                                                                                   entity=entity,
                                                                                   **params)
            elif action_name in self.methods_dict:
                response = await self._execute_method(method_name=action_name,
                                                      technical_id=technical_id,
                                                      entity=entity)

            else:
                raise ValueError(f"Unknown processing step: {action_name}")

        except Exception as e:
            entity.failed = True
            entity.last_modified = get_current_timestamp_num()
            entity.error = f"Error: {e}"
            logger.exception(f"Exception occurred while processing event: {e}")

        logger.info(f"{action}: {response}")
        entity.last_modified = get_current_timestamp_num()
        return entity, response

    async def _execute_method(self, method_name, technical_id, entity: WorkflowEntity):
        try:
            return await self.methods_dict[method_name](self.cls_instance,
                                                        technical_id=technical_id,
                                                        entity=entity)
        except Exception as e:
            logger.exception(f"Error executing method '{method_name}': {e}")
            entity.failed = True
            entity.error = f"Error executing method '{method_name}': {e}"
            raise

    async def _handle_config_based_event(self, config, entity: AgenticFlowEntity, technical_id):
        response = None
        config_type = config.get("type")
        finished_flow = entity.chat_flow.finished_flow
        child_entities_size_before = len(entity.child_entities)

        if config_type in ("notification", "question") and config.get(config_type):
            message_content = self._format_message(config, entity.workflow_cache, config_type)
            await self._append_to_memory(entity, message_content, config.get("memory_tags"))

        elif config_type == "function":
            params = config["function"].get("parameters", {})
            response = await self.methods_dict[config["function"]["name"]](
                self.cls_instance,
                technical_id=technical_id,
                entity=entity,
                **params
            )
            if response:
                await self._append_to_memory(entity, response, config.get("memory_tags"))

        elif config_type in ("prompt", "agent", "batch"):
            chat_memory = await self._get_chat_memory(entity.memory_id)
            response = await self._run_ai_agent(
                config=config,
                entity=entity,
                chat_memory=chat_memory,
                finished_flow=finished_flow,
                technical_id=technical_id
            )
            await self._update_chat_memory(entity.memory_id, chat_memory)

        new_entities = entity.child_entities[child_entities_size_before:] if child_entities_size_before < len(
            entity.child_entities) else []

        await self._finalize_response(
            technical_id=technical_id,
            config=config,
            entity=entity,
            finished_flow=finished_flow,
            new_entities=new_entities,
            response=response
        )
        return entity, response

    async def _run_ai_agent(self, config, entity: AgenticFlowEntity, chat_memory: ChatMemory, finished_flow, technical_id):
        if self._check_and_update_iteration(config=config, entity=entity):
            return "Let's proceed to the next iteration"

        await self._append_messages(entity=entity, memory=chat_memory, config=config, finished_flow=finished_flow)
        response = await self._get_ai_agent_response(config=config, entity=entity, technical_id=technical_id,
                                                     memory=chat_memory)
        return response

    def _check_and_update_iteration(self, config, entity):
        max_iteration = config.get("max_iteration")
        if max_iteration is None:
            return False
        transition = entity.current_transition
        iterations = entity.transitions_memory.current_iteration
        if transition not in iterations:
            iterations[transition] = 0
            entity.transitions_memory.max_iteration[transition] = max_iteration
        current_iteration = iterations[transition]
        if current_iteration > max_iteration:
            return True
        iterations[transition] = current_iteration + 1
        return False

    async def _append_messages(self, entity, config, memory: ChatMemory, finished_flow: List[FlowEdgeMessage]):
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        if config.get("messages"):
            config_messages: List[AIMessage] = []
            for config_message in config.get("messages"):
                try:
                    config_message = await enrich_config_message(entity=entity,
                                                                 config_message=config_message,
                                                                 entity_service=self.entity_service,
                                                                 cyoda_auth_service=self.cyoda_auth_service)
                except Exception as e:
                    logger.exception(e)
                    logger.error(config_message)
                edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                     entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                                                                     entity_version=env_config.ENTITY_VERSION,
                                                                     entity=config_message,
                                                                     meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                config_messages.append(AIMessage(edge_message_id=edge_message_id))
            for memory_tag in memory_tags:
                memory.messages.setdefault(memory_tag, []).extend(config_messages)
        if finished_flow:
            latest_message = next(
                (msg for msg in reversed(finished_flow) if msg.type == "answer"),
                None
            )
            if latest_message and latest_message.type == "answer" and not latest_message.consumed:
                message_content = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                                     entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                                                                     entity_version=env_config.ENTITY_VERSION,
                                                                     technical_id=latest_message.edge_message_id,
                                                                     meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                answer_content = message_content.get("answer")
                for memory_tag in memory_tags:
                    edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                         entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                                                                         entity_version=env_config.ENTITY_VERSION,
                                                                         entity={"role": "user",
                                                                                 "content": answer_content},
                                                                         meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                    memory.messages.get(memory_tag).append(AIMessage(edge_message_id=edge_message_id))
                latest_message.consumed = True

    async def _get_ai_agent_response(self, config, entity: AgenticFlowEntity, memory: ChatMemory, technical_id):
        if config.get("type") == "batch":
            input_file_path = config.get("input").get("local_fs")[0]
            output_file_path = config.get("output").get("local_fs")[0]
            await batch_process_file(input_file_path=input_file_path, output_file_path=output_file_path)
            return f"Scheduled batch processing for {input_file_path}"

        messages = await self._get_ai_memory(entity=entity, config=config, memory=memory, technical_id=technical_id)

        ai_agent_resp = await self.ai_agent.run_agent(
            methods_dict=self.methods_dict,
            cls_instance=self.cls_instance,
            entity=entity,
            technical_id=technical_id,
            tools=config.get("tools"),
            model=ModelConfig.model_validate(config.get("model")),
            tool_choice=config.get("tool_choice"),
            messages=messages,
            response_format=config.get("response_format")
        )
        edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                             entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                                                             entity_version=env_config.ENTITY_VERSION,
                                                             entity={"role": "assistant", "content": ai_agent_resp},
                                                             meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        for memory_tag in memory_tags:
            memory.messages.get(memory_tag).append(AIMessage(edge_message_id=edge_message_id))
        return ai_agent_resp

    async def _get_ai_memory(self, entity, config, memory: ChatMemory, technical_id):
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        messages = []
        for memory_tag in memory_tags:
            entity_messages: List[AIMessage] = memory.messages.get(memory_tag)
            for entity_message in entity_messages:
                message_content = await self.entity_service.get_item(token=self.cyoda_auth_service,
                                                                     entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                                                                     entity_version=env_config.ENTITY_VERSION,
                                                                     technical_id=entity_message.edge_message_id,
                                                                     meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                messages.append(str(message_content))
            # todo verify that the copy is deep
        input_data = config.get("input")
        if input_data:
            branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
            local_fs = input_data.get("local_fs")
            for file_name in local_fs:
                try:
                    formatted_filename = file_name.format(**entity.workflow_cache)
                except Exception as e:
                    formatted_filename = file_name
                    logger.exception(e)
                file_contents = await self._read_local_file(file_name=formatted_filename, technical_id=branch_id)
                messages.append({"role": "user", "content": f"Reference: {file_name}: \n {file_contents}"})
            #todo add edge messages
        return messages

    async def _read_local_file(self, file_name, technical_id):
        target_dir = os.path.join(f"{env_config.PROJECT_DIR}/{technical_id}/{env_config.REPOSITORY_NAME}", "")
        file_path = os.path.join(target_dir, file_name)
        try:
            async with aiofiles.open(file_path, 'r') as file:
                file_contents = await file.read()
        except Exception as e:
            logger.exception("Error during reading file")
        return file_contents

    async def _finalize_response(self, technical_id, entity: AgenticFlowEntity, config, finished_flow, response, new_entities):

        await self.add_edge_message(message=config, flow=finished_flow, user_id=entity.user_id)
        config_type = config["type"]

        if config_type in ("function", "prompt", "agent"):

            if response and response != "None":
                notification = {
                    "allow_anonymous_users": config.get("allow_anonymous_users", False),
                    "publish": config.get("publish", False),
                    "question": _post_process_response(response = f"{response}", config=config),
                    "approve": config.get("approve", False),
                    "type": "question",
                }
                await self.add_edge_message(message=notification,
                                                                flow=finished_flow,
                                                                user_id=entity.user_id)


            await self._write_to_output(entity=entity,
                                        config=config,
                                        response=response,
                                        technical_id=technical_id)
        if new_entities:
            await self.add_edge_message(message={"type": "child_entities",
                                                 "child_entities": new_entities}, flow=finished_flow,
                                        user_id=entity.user_id)

    async def add_edge_message(self, message: dict, flow: List[FlowEdgeMessage], user_id) -> FlowEdgeMessage:
        edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                             entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                                                             entity_version=env_config.ENTITY_VERSION,
                                                             entity=message,
                                                             meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
        flow_edge_message = FlowEdgeMessage(type=message["type"],
                                            publish=message.get("publish", False),
                                            edge_message_id=edge_message_id,
                                            user_id=user_id)
        flow.append(flow_edge_message)
        return flow_edge_message

    async def _write_to_output(self, entity, config, response, technical_id):
        if config.get("output"):
            if config.get("output").get("local_fs"):
                local_files = config.get("output").get("local_fs")
                for cache_key in local_files:
                    if cache_key.endswith(".json"):
                        try:
                            parsed_json = json.loads(response)
                            response = json.dumps(parsed_json, indent=4, sort_keys=True)
                        except json.JSONDecodeError as err:
                            logger.error(f"Invalid JSON format for file {cache_key}: {err}")
                    try:
                        formatted_filename = cache_key.format(**entity.workflow_cache)
                    except Exception as e:
                        formatted_filename = cache_key
                        logger.exception(e)
                    branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
                    await _save_file(chat_id=branch_id, _data=response, item=formatted_filename)
            if config.get("output").get("workflow_cache"):
                cache_keys = config.get("output").get("workflow_cache")
                for cache_key in cache_keys:
                    entity.workflow_cache[cache_key] = response
            if config.get("output").get("cyoda_edge_message"):
                edge_messages = config.get("output").get("cyoda_edge_message")
                for edge_message in edge_messages:
                    edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                         entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                                         entity_version=env_config.ENTITY_VERSION,
                                                                         entity=response,
                                                                         meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                    entity.edge_messages_store[edge_message] = edge_message_id

    def _format_message(self, config, workflow_cache, key):
        try:
            return config[key].format(**workflow_cache)
        except Exception as e:
            logger.exception(e)
            return config[key]

    async def _get_chat_memory(self, memory_id):
        return await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_MEMORY.value,
            entity_version=env_config.ENTITY_VERSION,
            technical_id=memory_id
        )

    async def _append_to_memory(self, entity, content, memory_tags=None):
        chat_memory = await self._get_chat_memory(entity.memory_id)
        edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity={"role": "assistant", "content": content},
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        tags = memory_tags or [env_config.GENERAL_MEMORY_TAG]
        for tag in tags:
            chat_memory.messages.get(tag).append(AIMessage(edge_message_id=edge_message_id))

        await self._update_chat_memory(entity.memory_id, chat_memory)

    async def _update_chat_memory(self, memory_id, chat_memory):
        await self.entity_service.update_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_MEMORY.value,
            entity_version=env_config.ENTITY_VERSION,
            technical_id=memory_id,
            entity=chat_memory,
            meta={const.TransitionKey.UPDATE.value: "update"}
        )



