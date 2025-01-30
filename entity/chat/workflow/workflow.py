import copy
import json
import asyncio
import os
import logging

from common.ai.ai_assistant_service import dataset
from common.config.config import MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL, WORKFLOW_AI_API
from common.config.conts import SCHEDULED_STACK, API_REQUEST_STACK, \
    WORKFLOW_STACK, \
    ENTITY_STACK, PROCESSORS_STACK, EXTERNAL_SOURCES_PULL_BASED_RAW_DATA, WEB_SCRAPING_PULL_BASED_RAW_DATA, \
    TRANSACTIONAL_PULL_BASED_RAW_DATA
from common.config.enums import TextType
from common.util.utils import read_file, get_project_file_name, parse_json, parse_workflow_json
from entity.chat.data.data import scheduler_stack, api_request_stack, workflow_stack, entity_stack, processors_stack, \
    data_ingestion_stack, PUSHED_CHANGES_NOTIFICATION, BRANCH_READY_NOTIFICATION
from entity.chat.workflow.helper_functions import _save_file, _sort_entities, _send_notification, \
    _build_context_from_project_files, run_chat, _send_notification_with_file, git_pull, \
    generate_data_ingestion_code_for_entity, generate_file_contents, save_result_to_file
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entry_point_to_stack = {
    SCHEDULED_STACK: copy.deepcopy(scheduler_stack),
    API_REQUEST_STACK: copy.deepcopy(api_request_stack),
    EXTERNAL_SOURCES_PULL_BASED_RAW_DATA: copy.deepcopy(data_ingestion_stack),
    WEB_SCRAPING_PULL_BASED_RAW_DATA: copy.deepcopy(data_ingestion_stack),
    TRANSACTIONAL_PULL_BASED_RAW_DATA: copy.deepcopy(data_ingestion_stack),
    WORKFLOW_STACK: copy.deepcopy(workflow_stack),
    ENTITY_STACK: copy.deepcopy(entity_stack),
    PROCESSORS_STACK: copy.deepcopy(processors_stack)
}


async def init_chats(token, _event, chat):
    if MOCK_AI == "true":
        return
    await ai_service.init_chat(token=token, chat_id=chat["chat_id"])


async def add_instruction(token, _event, chat):
    file_name = _event["file_name"]
    instruction_text = await read_file(get_project_file_name(chat["chat_id"], file_name))
    _event.setdefault('function', {}).setdefault("prompt", {}).setdefault("text", instruction_text)
    await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


async def refresh_context(token, _event, chat):
    # clean chat history and re-initialize
    await git_pull(chat['chat_id'])
    await ai_service.init_cyoda_chat(token=token, chat_id=chat["chat_id"])
    contents = await _build_context_from_project_files(chat=chat, files=_event["context"]["files"],
                                                       excluded_files=_event["context"].get("excluded_files"))
    _event.setdefault('function', {}).setdefault("prompt", {})
    _event["function"]["prompt"][
        "text"] = f"Please remember these files contents and reuse later: {json.dumps(contents)} . Do not do any mapping logic - it is not relevant. Just remember the code and the application design to reuse in your future application building. Return confirmation that you remembered everything"
    await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])


async def add_design_stack(token, _event, chat) -> list:
    file_name = _event["file_name"]
    file = await read_file(get_project_file_name(chat["chat_id"], file_name))
    design = json.loads(file)
    sorted_entities = sorted(design["entities"], key=_sort_entities)
    reversed_design_entities = sorted_entities[::-1]
    stack = chat["chat_flow"]["current_flow"]
    entities_dict = {ENTITY_STACK: []}
    # Process entities by entity_source or workflow transitions

    for entity in reversed_design_entities:
        entity_source = entity.get("entity_source")
        if entity_source in entry_point_to_stack:
            stack.extend(entry_point_to_stack[entity_source](entity))

    for entity in reversed_design_entities:
        entity_workflow = entity.get("entity_workflow")
        # Add entities with transitions to stack based on workflow
        if entity_workflow and entity_workflow.get("transitions"):
            stack.extend(entry_point_to_stack[PROCESSORS_STACK](entity))
            stack.extend(entry_point_to_stack[WORKFLOW_STACK](entity))
        # Organize entities by entity_type into entities_dict
        entity_type = entity.get("entity_type")
        if entity_type in entry_point_to_stack:
            if entity_type not in entities_dict:
                entities_dict[entity_type] = []
            entities_dict[entity_type].append(entity)
        else:
            entities_dict[ENTITY_STACK].append(entity)
    for stack_key in [ENTITY_STACK, WEB_SCRAPING_PULL_BASED_RAW_DATA, TRANSACTIONAL_PULL_BASED_RAW_DATA,
                      EXTERNAL_SOURCES_PULL_BASED_RAW_DATA]:
        if stack_key in entities_dict:
            stack.extend(entry_point_to_stack.get(stack_key, lambda x: [])(entities_dict[stack_key]))

    ##know your data
    return stack


async def add_user_requirement(token, _event, chat):
    file_name = _event["file_name"]
    ai_question = _event["function"]["prompt"]
    user_requirement = await ai_service.ai_chat(token=token, chat_id=chat["chat_id"], ai_endpoint=CYODA_AI_API,
                                                ai_question=ai_question)
    await _save_file(chat_id=chat["chat_id"], _data=user_requirement, item=file_name)


async def clone_repo(token, _event, chat):
    """
    Clone the GitHub repository to the target directory.
    If the repository should not be copied, it ensures the target directory exists.
    """
    clone_dir = f"{PROJECT_DIR}/{chat['chat_id']}/{REPOSITORY_NAME}"

    if CLONE_REPO != "true":
        # Create the directory asynchronously using asyncio.to_thread
        await asyncio.to_thread(os.makedirs, clone_dir, exist_ok=True)
        logger.info(f"Target directory '{clone_dir}' is created.")
        return

    # Asynchronously clone the repository using subprocess
    clone_process = await asyncio.create_subprocess_exec(
        'git', 'clone', REPOSITORY_URL, clone_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await clone_process.communicate()

    if clone_process.returncode != 0:
        logger.error(f"Error during git clone: {stderr.decode()}")
        return

    # Asynchronously checkout the branch using subprocess
    checkout_process = await asyncio.create_subprocess_exec(
        'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
        'checkout', '-b', str(chat["chat_id"]),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await checkout_process.communicate()

    if checkout_process.returncode != 0:
        logger.error(f"Error during git checkout: {stderr.decode()}")
        return

    logger.info(f"Repository cloned to {clone_dir}")

    # Call the async _save_file function
    await _save_file(chat['chat_id'], chat['chat_id'], 'README.txt')

    # Prepare the notification text
    notification_text = BRANCH_READY_NOTIFICATION.format(chat_id=chat['chat_id'])

    # Call the async _send_notification function
    await _send_notification(chat=chat, event=_event, notification_text=notification_text)


async def save_raw_data_to_entity_file(token, _event, chat) -> str:
    """
    Save the entity to a JSON file inside a specific directory.
    """
    file_name = _event["file_name"]
    await _save_file(chat_id=chat["chat_id"], _data=json.dumps(_event["answer"]), item=file_name)
    notification_text = PUSHED_CHANGES_NOTIFICATION.format(file_name=file_name, repository_url=REPOSITORY_URL,
                                                           chat_id=chat["chat_id"], publish=True)
    await _send_notification(chat=chat, event=_event, notification_text=notification_text)
    return _event["answer"]


async def generate_cyoda_workflow(token, _event, chat):
    # sourcery skip: use-named-expression
    if MOCK_AI == "true":
        return
    try:
        if (_event.get("entity").get("entity_workflow") and _event.get("entity").get("entity_workflow").get(
                "transitions")):
            ai_question = f"what workflow could you recommend for this sketch: {json.dumps(_event.get("entity").get("entity_workflow"))}. All transitions automated, no criteria needed, only externalized processors allowed, calculation node = {chat["chat_id"]}, calculation_response_timeout_ms = 120000, sync_process=false, new_transaction_for_async=true.  Return only json without any comments."
            resp = await ai_service.ai_chat(token=token, chat_id=chat["chat_id"], ai_endpoint=WORKFLOW_AI_API,
                                            ai_question=ai_question)
            workflow = parse_workflow_json(resp)
            workflow_json = json.loads(workflow)
            workflow_json["workflow_criteria"] = {
                "externalized_criteria": [

                ],
                "condition_criteria": [
                    {
                        "name": _event.get("entity").get("entity_name"),
                        "description": "Workflow criteria",
                        "condition": {
                            "group_condition_operator": "AND",
                            "conditions": [
                                {
                                    "field_name": "entityModelName",
                                    "is_meta_field": True,
                                    "operation": "equals",
                                    "value": _event.get("entity").get("entity_name"),
                                    "value_type": "strings"
                                }
                            ]
                        }
                    }
                ]
            }
            await _save_file(chat_id=chat["chat_id"], _data=json.dumps(workflow_json), item=_event["file_name"])
    except Exception as e:
        logger.error(f"Error generating workflow: {e}")
        logger.exception("Error generating workflow")


async def generate_data_ingestion_entities_template(token, _event, chat):
    # todo add a directory /user_files. Scan this directory and formulate the requirements from there
    entities = _event.get("entities", [])
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    for entity in entities:
        try:
            entity_name = entity.get("entity_name")
            for resource_type, notification_info in files_notifications.items():
                file_name_template = notification_info.get("file_name", "")
                file_text_template = notification_info.get("text", "")
                file_name = file_name_template.format(entity_name=entity_name)
                file_text = file_text_template.format(entity_name=entity_name)
                if file_name and file_text:
                    await _save_file(chat_id=chat["chat_id"], _data=json.dumps(file_text), item=file_name)
                    await _send_notification_with_file(chat=chat, event=_event,
                                                       notification_text=f"""
The entity has been saved to: {REPOSITORY_URL}/tree/{chat["chat_id"]}/{file_name}

{file_text}""",
                                                       file_name=file_name,
                                                       editable=True)
        except Exception as e:
            logger.error(f"Unexpected error for entity {entity.get("entity_name")}: {e}")
            logger.exception(e)


async def check_entity_definitions(token, _event, chat):
    await git_pull(chat['chat_id'])
    entities = _event.get("entities", [])
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat["chat_id"]}/{REPOSITORY_NAME}")
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    for entity in entities:
        try:
            entity_name = entity.get("entity_name")
            for resource_type, notification_info in files_notifications.items():
                file_name_template = notification_info.get("file_name", "")
                file_text_template = notification_info.get("text", "")
                file_name = file_name_template.format(entity_name=entity_name)
                file_text = file_text_template.format(entity_name=entity_name)
                if file_name and file_text:
                    file_path = os.path.join(target_dir, file_name)
                    current_file_text = await read_file(file_path)
                    if current_file_text == file_text:
                        notification_text = _event.get("notification_text").format(file_name=file_name)
                        await _send_notification_with_file(chat=chat, event=_event, notification_text=notification_text,
                                                           file_name=file_name, editable=True)
        except Exception as e:
            logger.error(f"Unexpected error for entity {entity.get("entity_name")}: {e}")
            logger.exception(e)


async def generate_data_ingestion_code(token, _event, chat):
    await git_pull(chat['chat_id'])
    entities = _event.get("entities", [])
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat["chat_id"]}/{REPOSITORY_NAME}")
    files_notifications = _event.get("files_notifications", {})
    if not entities:
        logger.warning("No entities found in the event.")
    tasks = []
    for entity in entities:
        # todo add code validation
        tasks.append(
            generate_data_ingestion_code_for_entity(_event, chat, entity, files_notifications, target_dir, token))
    await asyncio.gather(*tasks)
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


async def generate_entities_template(token, _event, chat):
    # Fetch entities from the event
    entities = _event.get("entities", [])
    user_data = f"Please, take into account the user suggestions. User suggestions take higher priority. User says: {_event["answer"]}" if \
        _event["answer"] else ''
    # List of tasks to be executed concurrently
    tasks = []
    for entity in entities:
        # Define a function to handle the task for each entity
        async def handle_entity(_entity):
            ai_question = _event.get("function").get("prompts").get("ai_question").format(
                entity_name=_entity.get("entity_name"), user_data=user_data)
            if ai_question:
                # Generate file contents asynchronously for each entity
                await generate_file_contents(
                    _event=_event,
                    chat=chat,
                    file_name=f"entity/{_entity.get('entity_name')}/{_entity.get('entity_name')}.json",
                    ai_question=ai_question,
                    token=token,
                    text_type=TextType.JSON
                )

        # Add the task to the list
        tasks.append(handle_entity(entity))
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    # Send notification after all tasks are completed
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


async def finish_flow(token, _event, chat):
    chat_id = chat["chat_id"]
    await _save_file(chat_id=chat_id, _data=json.dumps(chat), item=_event["file_name"])
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))
    #todo remove later
    await _save_file(chat_id=chat_id, _data=json.dumps(dataset.get(chat_id)), item=f"entity/dataset_{chat_id}.json")
    del dataset[chat_id]

async def verify_cyoda_doc(token, _event, chat):

    prd_doc_path = _event["function"]["files"]["prd_doc_path"]
    json_doc_path = _event["function"]["files"]["json_doc_path"]
    prd_doc = await read_file(get_project_file_name(chat_id=chat['chat_id'], file_name=prd_doc_path))
    json_doc = await read_file(get_project_file_name(chat_id=chat['chat_id'], file_name=json_doc_path))
    _event["function"]["prompt"]["text"] = _event["function"]["prompt"]["text"].format(json_doc=json_doc, prd_doc=prd_doc)
    result = await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    await save_result_to_file(chat=chat, _data=json.dumps(result), _event=_event)

def main():
    if __name__ == "__main__":
        resp = "test ```json\n{\n  \"name\": \"hello_world_workflow\",\n  \"description\": \"A simple workflow to send a Hello World email.\",\n  \"workflow_criteria\": {\n    \"externalized_criteria\": [],\n    \"condition_criteria\": []\n  },\n  \"transitions\": [\n    {\n      \"name\": \"send_email\",\n      \"description\": \"Triggered by a scheduled job to send a Hello World email.\",\n      \"start_state\": \"None\",\n      \"start_state_description\": \"Initial state before sending email.\",\n      \"end_state\": \"email_sent\",\n      \"end_state_description\": \"Email has been successfully sent.\",\n      \"automated\": true,\n      \"transition_criteria\": {\n        \"externalized_criteria\": [],\n        \"condition_criteria\": []\n      },\n      \"processes\": {\n        \"schedule_transition_processors\": [],\n        \"externalized_processors\": [\n          {\n            \"name\": \"send_hello_world_email\",\n            \"description\": \"Process to send a Hello World email.\",\n            \"calculation_nodes_tags\": \"3d1da699-c188-11ef-bd5b-40c2ba0ac9eb\",\n            \"attach_entity\": false,\n            \"calculation_response_timeout_ms\": \"5000\",\n            \"retry_policy\": \"FIXED\",\n            \"sync_process\": true,\n            \"new_transaction_for_async\": false,\n            \"none_transactional_for_async\": false,\n            \"processor_criteria\": {\n              \"externalized_criteria\": [],\n              \"condition_criteria\": []\n            }\n          }\n        ]\n      }\n    }\n  ]\n}\n``` test"
        resp = "{'name': 'send_hello_world_email_workflow', 'description': \"Workflow to send a 'Hello World' email at a scheduled time.\", 'workflow_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'transitions': [{'name': 'scheduled_send_email', 'description': \"Triggered by a schedule to send a 'Hello World' email.\", 'start_state': 'None', 'start_state_description': 'Initial state before the email is sent.', 'end_state': 'email_sent', 'end_state_description': 'Email has been successfully sent.', 'automated': True, 'transition_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'processes': {'schedule_transition_processors': [], 'externalized_processors': [{'name': 'send_email_process', 'description': \"Process to send 'Hello World' email at 5 PM every day.\", 'calculation_nodes_tags': 'd0ada585-c201-11ef-8296-40c2ba0ac9eb', 'attach_entity': True, 'calculation_response_timeout_ms': '5000', 'retry_policy': 'NONE', 'sync_process': True, 'new_transaction_for_async': False, 'none_transactional_for_async': False, 'processor_criteria': {'externalized_criteria': [], 'condition_criteria': []}}]}}]}"
        res = parse_json(resp)
        print(parse_json(resp))
        print(json.dumps(parse_json(resp)))


if __name__ == "__main__":
    main()
