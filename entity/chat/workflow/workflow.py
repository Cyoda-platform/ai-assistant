import json
import asyncio
import os
import logging
from copy import deepcopy

import aiofiles

from common.ai.ai_assistant_service import dataset, OPEN_AI, DEEPSEEK_CHAT
from common.config.config import MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL
from common.config.conts import WORKFLOW_STACK, \
    ENTITY_STACK, PROCESSORS_STACK, EXTERNAL_SOURCES_PULL_BASED_RAW_DATA, WEB_SCRAPING_PULL_BASED_RAW_DATA, \
    TRANSACTIONAL_PULL_BASED_RAW_DATA
from common.util.utils import read_file, get_project_file_name, parse_json
from entity.chat.data.data import PUSHED_CHANGES_NOTIFICATION, BRANCH_READY_NOTIFICATION
from entity.chat.workflow.gen_and_validation.additional_code_extractor import extract_non_endpoint_functions_code
from entity.chat.workflow.gen_and_validation.api_generator import generate_api_code
from entity.chat.workflow.gen_and_validation.entities_design_enricher import add_related_secondary_entities
from entity.chat.workflow.gen_and_validation.entities_design_generator import extract_endpoints, generate_spec
from entity.chat.workflow.gen_and_validation.workflow_generator import generate_workflow_code
from entity.chat.workflow.helper_functions import _save_file, _sort_entities, _send_notification, \
    _build_context_from_project_files, run_chat, _send_notification_with_file, git_pull, \
    generate_data_ingestion_code_for_entity, save_result_to_file, _git_push, \
    generate_cyoda_workflow
from logic.init import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entry_point_to_stack = {
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
    chat_id = chat["chat_id"]
    await git_pull(chat_id)
    if _event.get("function").get("model_api") and _event.get("function").get("model_api").get("model") == OPEN_AI:
        await ai_service.refresh_open_ai_chat(token, chat_id)
        return
    await ai_service.init_cyoda_chat(token=token, chat_id=chat_id)
    contents = {}
    if _event["context"] and _event["context"]["files"]:
        contents = await _build_context_from_project_files(chat=chat, files=_event["context"]["files"],
                                                           excluded_files=_event["context"].get("excluded_files"))
    _event.setdefault('function', {}).setdefault("prompt", {})
    _event["function"]["prompt"][
        "text"] = f"Please remember these files contents and reuse later: {json.dumps(contents)} . Do not do any mapping logic - it is not relevant. Just remember the code and the application design to reuse in your future application building. Return confirmation that you remembered everything"
    await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat_id)
    if _event.get("file_name"):
        await _save_file(chat_id=chat_id, _data=json.dumps(chat), item=_event["file_name"])


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
    entities_data = {}
    try:
        file_path = get_project_file_name(chat["chat_id"], "entity/entities_design.json")
        # Open the file asynchronously
        async with aiofiles.open(file_path, 'r') as f:
            # Read the content of the file
            entities_text = await f.read()

        # Parse the JSON from the file content
        entities_data = json.loads(entities_text)
    except Exception as e:
        logger.exception(e)
    entities_list = []
    for entity in entities_data["primary_entities"]:
        entities_list.append(entity.get("entity_name"))
    for entity in entities_data["secondary_entities"]:
        entities_list.append(entity.get("entity_name"))

    event_copy = deepcopy(_event)
    event_copy["function"]["prompt"]["text"] = event_copy["function"]["prompt"]["text"].format(
        entities_list=json.dumps(entities_list))
    entity_data_design = await run_chat(chat=chat, _event=event_copy, token=token,
                                        ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                            "model_api") else event_copy.get("function").get("model_api"),
                                        chat_id=chat["chat_id"])
    await _save_file(chat_id=chat["chat_id"],
                     _data=entity_data_design,
                     item=f"entity/entities_data_design.json")

    entity_data_design_json = entity_data_design
    for entity in entity_data_design_json["entities"]:
        await _save_file(chat_id=chat["chat_id"],
                         _data=json.dumps(entity.get('entity_data_example')),
                         item=f"entity/{entity.get('entity_name')}/{entity.get('entity_name')}.json")
    # Send notification after all tasks are completed
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


async def finish_flow(token, _event, chat):
    chat_id = chat["chat_id"]
    await _save_file(chat_id=chat_id, _data=json.dumps(chat), item=_event["file_name"])
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))
    # todo remove later
    await _save_file(chat_id=chat_id, _data=json.dumps(dataset.get(chat_id)), item=f"entity/dataset_{chat_id}.json")
    del dataset[chat_id]


async def save_env_file(token, _event, chat):
    chat_id = chat["chat_id"]
    file_name = get_project_file_name(chat_id=chat_id, file_name=_event["file_name"])
    async with aiofiles.open(file_name, 'r') as template_file:
        content = await template_file.read()

    # Replace CHAT_ID_VAR with $chat_id
    updated_content = content.replace('CHAT_ID_VAR', chat_id)

    # Save the updated content to a new file
    async with aiofiles.open(file_name, 'w') as new_file:
        await new_file.write(updated_content)
    await _git_push(chat_id, [file_name], "Added env file template")
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


async def remove_api_registration(token, _event, chat):
    # Read the file asynchronously
    chat_id = chat["chat_id"]
    file_name = get_project_file_name(chat_id=chat_id, file_name=_event["file_name"])

    async with aiofiles.open(file_name, 'r') as template_file:
        content = await template_file.read()

    # Define the lines to remove
    line_1 = "from entity.ENTITY_NAME_VAR.api import api_bp_ENTITY_NAME_VAR"
    line_2 = "app.register_blueprint(api_bp_ENTITY_NAME_VAR, url_prefix='/api/ENTITY_NAME_VAR')"

    # Remove the lines by replacing them with an empty string
    content = content.replace(line_1, '')
    content = content.replace(line_2, '')

    # Write the updated content back to the file
    async with aiofiles.open(file_name, 'w') as new_file:
        await new_file.write(content)
    await _git_push(chat_id, [file_name], "Removed api registration template")


async def register_api_with_app(token, _event, chat):
    chat_id = chat["chat_id"]
    app_file_name = get_project_file_name(chat_id=chat_id, file_name="app.py")

    # Read the template file asynchronously
    async with aiofiles.open(app_file_name, 'r') as template_file:
        content = await template_file.read()

    entities_file_pattern = "entity/entities_design.json"
    entities_data = {}
    try:
        file_path = get_project_file_name(chat["chat_id"], entities_file_pattern)
        # Open the file asynchronously
        async with aiofiles.open(file_path, 'r') as f:
            # Read the content of the file
            entities_text = await f.read()

        # Parse the JSON from the file content
        entities_data = json.loads(entities_text)
    except Exception as e:
        logger.exception(e)
    entities_list = []
    for entity in entities_data["primary_entities"]:
        entities_list.append(entity)
    for entity in entities_data["secondary_entities"]:
        entities_list.append(entity)
    for entity in entities_list:
        event_copy = deepcopy(_event)
        endpoint_list = []

        # event_copy["function"]["prompt"]["attached_files"] = [f"entity/{entity.get('entity_name')}/api.py",
        #                                                       "entity/prototype.py"]
        # # Loop through each method (POST, GET, etc.)
        # for method, endpoint_data in entity["endpoints"].items():
        #     for endpoint in endpoint_data:
        #         endpoint_name = endpoint["endpoint"]
        #         description = endpoint["description"]
        #         endpoint_list.append((endpoint_name, method, description))
        # event_copy["function"]["prompt"]["text"] = event_copy["function"]["prompt"]["text"].format(
        #     entity_name=entity.get('entity_name'), entity_endpoints=json.dumps(endpoint_list))
        # result = await run_chat(chat=chat, _event=event_copy, token=token,
        #                         ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
        #                             "model_api") else event_copy.get("function").get("model_api"),
        #                         chat_id=chat["chat_id"])

        api_template_content = generate_api_code(schema=entity)

        await _save_file(chat_id=chat["chat_id"],
                         _data=json.dumps(api_template_content),
                         item=f"entity/{entity.get('entity_name')}/api.py")
        # Send notification after all tasks are completed
        await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))

        # Replace ENTITY_NAME_VAR with _event["entity"]["entity_name"]
        entity_name = entity.get('entity_name')
        content = content.replace('ENTITY_NAME_VAR', entity_name)
        line1 = f"from entity.{entity_name}.api import api_bp_{entity_name}"
        # Create line2
        line2 = "from entity.ENTITY_NAME_VAR.api import api_bp_ENTITY_NAME_VAR"
        # Replace the original line with two lines
        content = content.replace(line1, f"{line1}\n{line2}")

        line1 = f"app.register_blueprint(api_bp_{entity_name}, url_prefix='/api/{entity_name}')"
        # Create line2
        line2 = f"app.register_blueprint(api_bp_ENTITY_NAME_VAR, url_prefix='/api/ENTITY_NAME_VAR')"
        # Replace the original line with two lines
        content = content.replace(line1, f"{line1}\n{line2}")
        # Write the updated content back to the file
    async with aiofiles.open(app_file_name, 'w') as new_file:
        await new_file.write(content)
    await _git_push(chat_id, [app_file_name], "Added api registration")


async def register_workflow_with_app(token, _event, chat):
    entities_file_pattern = "entity/entities_design.json"
    entities_data = {}
    try:
        file_path = get_project_file_name(chat["chat_id"], entities_file_pattern)
        # Open the file asynchronously
        async with aiofiles.open(file_path, 'r') as f:
            # Read the content of the file
            entities_text = await f.read()

        # Parse the JSON from the file content
        entities_data = json.loads(entities_text)
    except Exception as e:
        logger.exception(e)
    for entity in entities_data["primary_entities"]:
        event_copy = deepcopy(_event)
        entity_name = entity.get('entity_name')
        #todo - 1 entity can have mult workflows, e.g. user: signup/login
        suggested_workflow = entity.get("endpoints").get("POST")[0].get("suggested_workflow")

        await generate_cyoda_workflow(token=token, entity_name=entity_name, entity_workflow=suggested_workflow,
                                      chat_id=chat["chat_id"], file_name=f"entity/{entity_name}/workflow.json")

        workflow_template_content = generate_workflow_code(schema=suggested_workflow, entity_name=entity_name)

        prototype = "entity/prototype.py"
        try:
            file_path = get_project_file_name(chat["chat_id"], prototype)
            # Open the file asynchronously
            async with aiofiles.open(file_path, 'r') as f:
                # Read the content of the file
                prototype_content = await f.read()
        except Exception as e:
            logger.exception(e)
        additional_functions_code = extract_non_endpoint_functions_code(prototype_content)
        event_copy["function"]["prompt"]["text"] = event_copy["function"]["prompt"]["text"].format(
            entity_name=entity_name, workflow_code_template=workflow_template_content, additional_functions_code=additional_functions_code)
        result = await run_chat(chat=chat, _event=event_copy, token=token,
                                ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                    "model_api") else event_copy.get("function").get("model_api"),
                                chat_id=chat["chat_id"])

        await _save_file(chat_id=chat["chat_id"],
                         _data=json.dumps(result),
                         item=f"entity/{entity_name}/workflow.py")
        #todo add validation
        # generate tests
        event_copy["function"]["prompt"]["text"] = f"""

Hello, could you write unittest tests for this code:

{result}
       
my_module = 'workflow'
one simple assertion is enough
"""

        event_copy["function"]["prompt"]["attached_files"] = None
        event_copy["function"]["prompt"]["api"] = {"model": DEEPSEEK_CHAT, "temperature": 0.7, "max_tokens": 10000}
        event_copy["function"]["model_api"] = {"model": DEEPSEEK_CHAT, "temperature": 0.7, "max_tokens": 10000}
        # result = await run_chat(chat=chat, _event=event_copy, token=token,
        #                         ai_endpoint = event_copy.get("function").get("model_api"),
        #                         chat_id=chat["chat_id"])
        # await _save_file(chat_id=chat["chat_id"],
        #                  _data=json.dumps(result),
        #                  item=f"entity/{entity_name}/workflow_test.py")

        # Send notification after all tasks are completed
        await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


async def verify_cyoda_doc(token, _event, chat):
    prd_doc_path = _event["function"]["files"]["prd_doc_path"]
    json_doc_path = _event["function"]["files"]["json_doc_path"]
    prd_doc = await read_file(get_project_file_name(chat_id=chat['chat_id'], file_name=prd_doc_path))
    json_doc = await read_file(get_project_file_name(chat_id=chat['chat_id'], file_name=json_doc_path))
    _event["function"]["prompt"]["text"] = _event["function"]["prompt"]["text"].format(json_doc=json_doc,
                                                                                       prd_doc=prd_doc)
    result = await run_chat(chat=chat, _event=_event, token=token, ai_endpoint=CYODA_AI_API, chat_id=chat["chat_id"])
    await save_result_to_file(chat=chat, _data=json.dumps(result), _event=_event)

async def generate_entities_design(token, _event, chat):
    prototype_content = await read_file(get_project_file_name(chat_id=chat['chat_id'], file_name="entity/prototype_cyoda.py"))
    endpoints = extract_endpoints(prototype_content)
    entities_design_spec = generate_spec(endpoints)
    entities_design_spec = add_related_secondary_entities(entities_design_spec)
    await _save_file(chat_id=chat["chat_id"],
                     _data=json.dumps(entities_design_spec),
                     item=f"entity/entities_design.json")

    # Send notification after all tasks are completed
    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


def main_parse_json():
    if __name__ == "__main__":
        resp = "test ```json\n{\n  \"name\": \"hello_world_workflow\",\n  \"description\": \"A simple workflow to send a Hello World email.\",\n  \"workflow_criteria\": {\n    \"externalized_criteria\": [],\n    \"condition_criteria\": []\n  },\n  \"transitions\": [\n    {\n      \"name\": \"send_email\",\n      \"description\": \"Triggered by a scheduled job to send a Hello World email.\",\n      \"start_state\": \"None\",\n      \"start_state_description\": \"Initial state before sending email.\",\n      \"end_state\": \"email_sent\",\n      \"end_state_description\": \"Email has been successfully sent.\",\n      \"automated\": true,\n      \"transition_criteria\": {\n        \"externalized_criteria\": [],\n        \"condition_criteria\": []\n      },\n      \"processes\": {\n        \"schedule_transition_processors\": [],\n        \"externalized_processors\": [\n          {\n            \"name\": \"send_hello_world_email\",\n            \"description\": \"Process to send a Hello World email.\",\n            \"calculation_nodes_tags\": \"3d1da699-c188-11ef-bd5b-40c2ba0ac9eb\",\n            \"attach_entity\": false,\n            \"calculation_response_timeout_ms\": \"5000\",\n            \"retry_policy\": \"FIXED\",\n            \"sync_process\": true,\n            \"new_transaction_for_async\": false,\n            \"none_transactional_for_async\": false,\n            \"processor_criteria\": {\n              \"externalized_criteria\": [],\n              \"condition_criteria\": []\n            }\n          }\n        ]\n      }\n    }\n  ]\n}\n``` test"
        resp = "{'name': 'send_hello_world_email_workflow', 'description': \"Workflow to send a 'Hello World' email at a scheduled time.\", 'workflow_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'transitions': [{'name': 'scheduled_send_email', 'description': \"Triggered by a schedule to send a 'Hello World' email.\", 'start_state': 'None', 'start_state_description': 'Initial state before the email is sent.', 'end_state': 'email_sent', 'end_state_description': 'Email has been successfully sent.', 'automated': True, 'transition_criteria': {'externalized_criteria': [], 'condition_criteria': []}, 'processes': {'schedule_transition_processors': [], 'externalized_processors': [{'name': 'send_email_process', 'description': \"Process to send 'Hello World' email at 5 PM every day.\", 'calculation_nodes_tags': 'd0ada585-c201-11ef-8296-40c2ba0ac9eb', 'attach_entity': True, 'calculation_response_timeout_ms': '5000', 'retry_policy': 'NONE', 'sync_process': True, 'new_transaction_for_async': False, 'none_transactional_for_async': False, 'processor_criteria': {'externalized_criteria': [], 'condition_criteria': []}}]}}]}"
        res = parse_json(resp)
        print(parse_json(resp))
        print(json.dumps(parse_json(resp)))


def main_register_api_with_app():
    if __name__ == "__main__":
        event = {}
        event["entity"] = {}
        event["entity"]["entity_name"] = "test_entity"
        event["file_name"] = "app.py"
        chat = {"chat_id": "f460bfb3-e253-11ef-9cdb-40c2ba0ac9eb"}
        asyncio.run(register_api_with_app("token", event, chat))


def main():
    if __name__ == "__main__":
        pass


if __name__ == "__main__":
    main()
