import asyncio
import copy
import glob
import json
import logging
import os

import aiofiles
import black

from common.config.config import MOCK_AI, VALIDATION_MAX_RETRIES, PROJECT_DIR, REPOSITORY_NAME, REPOSITORY_URL, \
    WORKFLOW_AI_API, ENTITY_VERSION
from common.config.conts import SCHEDULER_ENTITY
from common.repository.cyoda.cyoda_repository import cyoda_token
from common.util.chat_util_functions import add_answer_to_finished_flow
from common.util.utils import get_project_file_name, read_file, format_json_if_needed, parse_workflow_json, \
    _save_file, current_timestamp
from entity.chat.data.data import PUSHED_CHANGES_NOTIFICATION
from entity.chat.model.chat import ChatEntity
from entity.model.model import SchedulerEntity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowHelperService:
    def __init__(self, mock=False):
        self.mock = mock

    if MOCK_AI == "true":
        # generate_mock_data()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.dirname(current_dir)
        # Build the file path
        mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
        try:
            with open(mock_external_data_path, 'r') as file:
                data = file.read()
        except Exception as e:
            logger.error(f"Failed to read JSON file {mock_external_data_path}: {e}")
            raise
        json_mock_data = json.loads(data)

    async def _get_valid_result(self, _data, schema, token, ai_endpoint, chat_id):
        if MOCK_AI == "true" and not isinstance(_data, dict):
            return _data
        result = await self.ai_service.validate_and_parse_json(token=token,
                                                               ai_endpoint=ai_endpoint,
                                                               chat_id=chat_id,
                                                               data=_data,
                                                               schema=schema,
                                                               max_retries=VALIDATION_MAX_RETRIES)
        return result

    async def run_chat(self, chat, _event, token, ai_endpoint, chat_id, additional_prompt=None):
        event_prompt, prompt = await self.build_prompt(_event, chat) if not additional_prompt else (
            {"prompt": additional_prompt}, additional_prompt)
        user_file_name = None
        if _event.get("user_file") and _event.get("user_file_processed") is False:
            user_file_name = _event.get("user_file")
            _event["user_file_processed"] = True

        result = await self._get_chat_response(
            prompt=prompt,
            token=token,
            ai_endpoint=ai_endpoint,
            chat_id=chat_id,
            user_file=user_file_name,
        )

        if event_prompt.get("schema"):
            try:
                result = await self._get_valid_result(_data=result,
                                                      schema=event_prompt["schema"],
                                                      token=token,
                                                      ai_endpoint=ai_endpoint,
                                                      chat_id=chat_id)
            except Exception as e:
                return {"success": "false", "error": str(e)}
        return result

    async def build_prompt(self, _event, chat):
        if _event.get("function") and _event["function"].get("prompt"):
            event_prompt = _event["function"]["prompt"]
        else:
            event_prompt = _event.get("prompt", {})
        prompt_text = await self._enrich_prompt_with_context(_event, chat, event_prompt)
        prompt = f'{prompt_text}: {_event.get("answer", "")}' if _event.get(
            "answer") else prompt_text
        prompt = f'{prompt}. Use this json schema http://json-schema.org/draft-07/schema# to understand how to structure your answer: {event_prompt.get("schema", "")}. It will be validated against this schema. Return only json (python dictionary)' if event_prompt.get(
            "schema") else prompt
        return event_prompt, prompt

    async def _enrich_prompt_with_context(self, _event, chat, event_prompt):
        prompt_text = event_prompt.get("text", "")
        if event_prompt.get("attached_files"):
            attached_files = event_prompt.get("attached_files")
            contents = []
            for file_pattern in attached_files:
                file_path = get_project_file_name(chat["chat_id"], file_pattern)
                # Check if the file exists before trying to open it
                if os.path.isfile(file_path):
                    async with aiofiles.open(file_path, "r") as f:
                        contents.append({file_pattern: await f.read()})
            prompt_text = prompt_text + " \n " + json.dumps(contents)

        prompt_context = _event.get("context", {}).get("prompt", {})
        if prompt_context:
            # Loop through each item in the context dictionary
            for prompt_context_item, prompt_item_values in prompt_context.items():
                chat_context = chat.get('cache', {})
                # Assuming prompt_item_value is a dictionary with keys to resolve in chat_context
                if isinstance(prompt_item_values, list):
                    for item in prompt_item_values:
                        chat_context = chat_context.get(item, {})
                # After finding the correct value in chat_context, replace in the prompt_text
                if chat_context:
                    prompt_text = prompt_text.replace(f'${prompt_context_item}', str(chat_context))
        return prompt_text

    async def _get_chat_response(self, prompt, token, ai_endpoint, chat_id, user_file=None):
        """Get chat response either from the AI service or mock entity."""
        if MOCK_AI == "true":
            return self._mock_ai(prompt)
        resp = await self.ai_service.ai_chat(token=token, ai_endpoint=ai_endpoint, chat_id=chat_id, ai_question=prompt,
                                             user_file=user_file)
        return resp

    def _mock_ai(self, prompt_text):
        return self.json_mock_data.get(prompt_text[:15], json.dumps({"entity": "some random text"}))

    def get_event_template(self, event, question='', notification='', answer=None, prompt=None, file_name=None,
                           editable=False,
                           publish=False):
        # Predefined keys for the final JSON structure
        final_json = {
            "question": question,  # Sets the provided question
            "prompt": prompt if prompt else {},  # Sets the provided prompt
            "notification": notification,
            "answer": '',  # Initially no answer
            "function": event.get('prompt', {}).get('function', {}),  # Placeholder for function
            "index": event.get('index', 0),  # Default index
            "iteration": event.get('iteration', 0),  # Initial iteration count
            "max_iteration": event.get('max_iteration', 0),
            "data": event.get('data', {}),
            "entity": event.get('entity', {}),
            "file_name": file_name if file_name else event.get('file_name', ''),
            "context": event.get('context', {}),
            "approve": True,
            "editable": False,  # editable todo
            "publish": publish if publish else event.get('publish', {})
        }
        exclusion_values = ['stack']  # Values to be excluded from the final JSON

        # Iterate through additional key-value pairs in the event object
        for key, value in event.items():
            if key not in final_json and key not in exclusion_values:  # Only add key-value pairs not already in final_json
                final_json[key] = value

        return final_json

    def _format_code(self, code):
        try:
            # Format the code using black's formatting
            formatted_code = black.format_str(code, mode=black.Mode())
            return formatted_code
        except Exception as e:
            print(f"Error formatting code: {e}")
            return code  # Return the original code if formatting fails

    async def _export_workflow_to_cyoda_ai(self, token, chat_id, _data):
        if MOCK_AI == "true":
            return
        if _data.get("transitions"):
            _data.get("transitions")[0]["start_state"] = "None"

        await self.ai_service.export_workflow_to_cyoda_ai(token=token, chat_id=chat_id, data=_data)

    async def _send_notification(self, chat, event, notification_text, file_name=None, editable=False, publish=False):
        stack = chat["chat_flow"]["current_flow"]
        stack.append({"notification": notification_text})
        return stack

    async def _send_notification_with_file(self, chat, event, notification_text, file_name, editable):
        stack = chat["chat_flow"]["current_flow"]
        notification_event = self.get_event_template(notification=notification_text,
                                                     event=event,
                                                     question='',
                                                     answer='',
                                                     prompt={},
                                                     file_name=file_name,
                                                     editable=editable)
        stack.append(notification_event)
        return stack

    async def _build_context_from_project_files(self, chat, files, excluded_files):
        contents = []
        for file_pattern in files:
            root_path = get_project_file_name(chat["chat_id"], file_pattern)
            if "**" in root_path or os.path.isdir(root_path):
                # Use glob to get all files matching the pattern (including files in subdirectories)
                for file_path in glob.glob(root_path,
                                           recursive=True):  # recursive=True to include files in subdirectories
                    try:
                        if os.path.isfile(file_path) and not any(
                                file_path.endswith(excluded) for excluded in excluded_files):
                            async with aiofiles.open(file_path, "r") as f:
                                contents.append({file_path: await f.read()})
                    except Exception as e:
                        logger.exception(e)
            else:
                try:
                    file_path = get_project_file_name(chat["chat_id"], file_pattern)
                    # Check if the file exists before trying to open it
                    if os.path.isfile(file_path):
                        async with aiofiles.open(file_path, "r") as f:
                            contents.append({file_pattern: await f.read()})
                except:
                    logger.exception(e)
        return contents

    async def save_result_to_file(self, chat, _event, _data):
        file_name = _event.get("file_name")
        if file_name:
            await _save_file(chat_id=chat["chat_id"], _data=_data, item=file_name)
            notification_text = PUSHED_CHANGES_NOTIFICATION.format(file_name=file_name, repository_url=REPOSITORY_URL,
                                                                   chat_id=chat["chat_id"])
            await self._send_notification(chat=chat, event=_event, notification_text=notification_text,
                                          file_name=file_name,
                                          editable=True, publish=True)

    # Helper function to generate file name from template
    def get_file_name(self, template, entity_name):
        return template.format(entity_name=entity_name)

    # Helper function to construct file paths
    def get_file_path(self, target_dir, file_name):
        return os.path.join(target_dir, file_name)

    # Async function to read files concurrently
    async def read_files_concurrently(self, file_paths):
        file_contents = await asyncio.gather(*[read_file(file_path) for file_path in file_paths])
        return file_contents

    # Main function for getting resources
    async def _get_resources(self, entity, files_notifications, target_dir):
        entity_name = entity.get("entity_name")

        # Define a map for 'code', 'doc', and 'entity' file types
        file_types = {
            "code": files_notifications.get("code", {}),
            "doc": files_notifications.get("doc", {}),
            "entity": files_notifications.get("entity", {})
        }

        # Generate file names using the map and templates
        file_names = {
            file_type: self.get_file_name(file_info.get("file_name", ""), entity_name)
            for file_type, file_info in file_types.items()
        }

        # Construct file paths
        file_paths = {
            file_type: self.get_file_path(target_dir, file_name)
            for file_type, file_name in file_names.items()
        }

        # Read the files concurrently
        file_contents = await self.read_files_concurrently(list(file_paths.values()))

        # Return the results in the desired order
        return (
            file_names["code"],  # Code file name
            file_contents[1],  # Doc file content
            file_contents[2],  # Entity file content
            entity_name  # Entity name
        )

    async def get_remote_branches(self, chat_id):
        clone_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}"

        try:
            # Start the git branch -r command asynchronously to get remote branches
            process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'branch', '-r',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for the process to complete
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                remote_branches = stdout.decode('utf-8').splitlines()
                # Clean the output to remove "origin/" prefix if you only want branch names
                remote_branches = [branch.strip().replace("origin/", "") for branch in remote_branches]
                return remote_branches
            else:
                error_message = stderr.decode('utf-8')
                raise Exception(f"Error fetching remote branches: {error_message}")

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def comment_out_non_code(self, text):
        if '```python' in text:
            lines = text.splitlines()
            in_python_block = False
            commented_lines = []

            for line in lines:
                if line.strip().startswith("```python"):
                    # Comment out the ```python line
                    commented_lines.append(f"# {line}")
                    in_python_block = True
                elif line.strip().startswith("```") and in_python_block:
                    # Comment out the ``` line
                    commented_lines.append(f"# {line}")
                    in_python_block = False
                elif in_python_block:
                    # Keep lines inside the Python block as-is
                    commented_lines.append(line)
                else:
                    # Comment out lines outside the Python block
                    commented_lines.append(f"# {line}")

            return "\n".join(commented_lines)
        else:
            return text

    # what workflow could you recommend for this sketch: class_name = com.cyoda.tdb.model.treenode.TreeNodeEntity, name = job, workflow transitions: [{"name": "create_report", "start_state": "initial", "end_state": "report_generated", "process": "create_report"}]. All transitions automated, no criteria needed, only externalized processors allowed, calculation node = 3fc5df73-e8db-11ef-81a1-40c2ba0ac9eb, calculation_response_timeout_ms = 120000, sync_process=false, new_transaction_for_async=true.  Return only json without any comments.
    async def generate_cyoda_workflow(self, token, entity_name, entity_workflow, chat_id, file_name):
        # sourcery skip: use-named-expression
        if MOCK_AI == "true":
            return
        try:
            transitions = [{
                "name": item.get("action", ""),
                "start_state": item.get("start_state", ""),
                "end_state": item.get("end_state", ""),
                "process": item.get("action", ""),
                "externalized_processor_name": item.get("action", "")
            } for item in entity_workflow]
            ai_question = f"what workflow could you recommend for this sketch: class_name = com.cyoda.tdb.model.treenode.TreeNodeEntity, name = {entity_name}, workflow transitions: {json.dumps(transitions)}. All transitions automated, no criteria needed, only externalized processors allowed, calculation node = {chat_id}, calculation_response_timeout_ms = 120000, sync_process=false, new_transaction_for_async=true.  Return only json without any comments."
            resp = await self.ai_service.ai_chat(token=token, chat_id=chat_id, ai_endpoint={"model": WORKFLOW_AI_API},
                                                 ai_question=ai_question)
            logger.info(resp)
            workflow = parse_workflow_json(resp)
            workflow_json = json.loads(workflow)
            workflow_json["name"] = f"{workflow_json["name"]}:ENTITY_VERSION_VAR:{chat_id}"
            workflow_json["workflow_criteria"] = {
                "externalized_criteria": [

                ],
                "condition_criteria": [
                    {
                        "name": f"{entity_name}:ENTITY_VERSION_VAR:{chat_id}",
                        "description": "Workflow criteria",
                        "condition": {
                            "group_condition_operator": "AND",
                            "conditions": [
                                {
                                    "field_name": "entityModelName",
                                    "is_meta_field": True,
                                    "operation": "equals",
                                    "value": entity_name,
                                    "value_type": "strings"
                                },
                                {
                                    "field_name": "entityModelVersion",
                                    "is_meta_field": True,
                                    "operation": "equals",
                                    "value": "ENTITY_VERSION_VAR",
                                    "value_type": "strings"
                                }
                            ]
                        }
                    }
                ]
            }
            await _save_file(chat_id=chat_id, _data=json.dumps(workflow_json), item=file_name)
        except Exception as e:
            logger.error(f"Error generating workflow: {e}")
            logger.exception("Error generating workflow")

    def _process_question(self, question):
        if question.get("processed"):
            return question
        if question.get("question"):
            question["question_key"] = question.get("question")
            question = format_json_if_needed(question, "question")

        if question.get("notification"):
            question = format_json_if_needed(question, "notification")
        if question.get("question") and question.get("ui_config"):
            # Create a deep copy of the question object
            new_question = copy.deepcopy(question)
            result = []

            # Iterating through display_keys in the ui_config
            for key_object in new_question.get("ui_config", {}).get("display_keys", []):
                # Extract the key from the key_object (the dictionary key)
                if isinstance(key_object, dict):
                    for key, value in key_object.items():
                        # Append the corresponding value from the "question" dictionary using the extracted key
                        if key in new_question.get("question", {}):
                            result.append(value)
                            result.append(new_question.get("question").get(key))

            # Combine the values into a single string
            new_question["question"] = " ".join(str(item) for item in result)

            return new_question
        if question.get("question") and question.get("example_answers"):
            question["question"] = f"""
    {question["question"]}
    
    ***Example answers***:
    {'\n\n'.join([answer.strip() for answer in question.get("example_answers", [])])}
    """
        # Return the original question if conditions are not met
        question["processed"] = True
        return question

    # =============================
    async def launch_agentic_workflow(self,
                                      entity_service,
                                      technical_id,
                                      entity,
                                      entity_model,
                                      user_request=None,
                                      workflow_cache=None,
                                      edge_messages_store=None):

        child_entity: ChatEntity = ChatEntity.model_validate({
            "user_id": entity.user_id,
            "chat_id": "",
            "parent_id": technical_id,
            "date": current_timestamp(),
            "questions_queue_id": entity.questions_queue_id,
            "memory_id": entity.memory_id,
            "chat_flow": {"current_flow": [], "finished_flow": []},
            "current_transition": "",
            "current_state": "",
            "workflow_cache": workflow_cache,
            "edge_messages_store": edge_messages_store,
            "transitions_memory": {
                "conditions": {},
                "current_iteration": {},
                "max_iteration": {}
            }
        })
        if user_request:
            await add_answer_to_finished_flow(entity_service=entity_service,
                                              answer=user_request,
                                              chat=child_entity)
        child_technical_id = await entity_service.add_item(token=cyoda_token,
                                                           entity_model=entity_model,
                                                           entity_version=ENTITY_VERSION,
                                                           entity=child_entity)
        # lock parent chat
        entity.locked = True
        entity.child_entities.append(child_technical_id)
        return child_technical_id

    async def launch_scheduled_workflow(self,
                                        entity_service,
                                        awaited_entity_ids,
                                        triggered_entity_id):

        child_entity: SchedulerEntity = SchedulerEntity.model_validate({
            "user_id": "system",
            "awaited_entity_ids": awaited_entity_ids,
            "triggered_entity_id": triggered_entity_id
        })

        child_technical_id = await entity_service.add_item(token=cyoda_token,
                                                           entity_model=SCHEDULER_ENTITY,
                                                           entity_version=ENTITY_VERSION,
                                                           entity=child_entity)

        return child_technical_id
