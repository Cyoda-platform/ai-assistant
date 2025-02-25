import copy
import json
import asyncio
import os
import logging
from copy import deepcopy

import aiofiles

from common.ai.ai_assistant_service import dataset, OPEN_AI
from common.config.config import MOCK_AI, CYODA_AI_API, PROJECT_DIR, REPOSITORY_NAME, CLONE_REPO, \
    REPOSITORY_URL, VALIDATION_MAX_RETRIES
from common.util.utils import read_file, get_project_file_name, parse_json
from entity.chat.data.data import BRANCH_READY_NOTIFICATION
from entity.chat.workflow.gen_and_validation.app_postprocessor import app_post_process
from entity.chat.workflow.gen_and_validation.entity_names_extractor import extract_entity_names
from entity.chat.workflow.gen_and_validation.function_extractor import extract_function
from entity.chat.workflow.gen_and_validation.json_extractor import extract_and_validate_json
from entity.chat.workflow.gen_and_validation.result_validator import validate_ai_result
from entity.chat.workflow.gen_and_validation.workflow_enricher import enrich_workflow
from entity.chat.workflow.gen_and_validation.workflow_extractor import analyze_code_with_libcst
from entity.chat.workflow.helper_functions import _save_file, _send_notification, \
    _build_context_from_project_files, run_chat, git_pull, _git_push
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


async def generate_entities_template(token, _event, chat):
    try:
        file_path = get_project_file_name(chat["chat_id"], "entity/prototype_cyoda.py")
        # Open the file asynchronously
        async with aiofiles.open(file_path, 'r') as f:
            # Read the content of the file
            entities_text = await f.read()

    except Exception as e:
        logger.exception(e)
    entities_list = extract_entity_names(entities_text)

    event_copy = deepcopy(_event)
    event_copy["function"]["prompt"]["text"] = event_copy["function"]["prompt"]["text"].format(
        entities_list=json.dumps(entities_list))
    entity_data_design = await run_chat(chat=chat, _event=event_copy, token=token,
                                        ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                            "model_api") else event_copy.get("function").get("model_api"),
                                        chat_id=chat["chat_id"])
    is_valid, formatted_result = validate_ai_result(entity_data_design, "entity/entities_data_design.json")
    if is_valid:
        entity_data_design = formatted_result
    else:
        retry = VALIDATION_MAX_RETRIES
        while retry > 0:
            retry_event = copy.deepcopy(_event)
            retry_event["function"]["prompt"]["text"] = formatted_result
            result = await run_chat(chat=chat, _event=retry_event, token=token,
                                    ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                        "model_api") else event_copy.get("function").get("model_api"),
                                    chat_id=chat["chat_id"])
            is_valid, formatted_result = validate_ai_result(result, _event.get("file_name"))
            if is_valid:
                entity_data_design = formatted_result
                retry = -1
            else:
                retry -= 1
    await _save_file(chat_id=chat["chat_id"],
                     _data=json.dumps(entity_data_design),
                     item=f"entity/entities_data_design.json")

    for entity in entity_data_design["entities"]:
        if entity.get('entity_name') in entities_list:
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


async def register_workflow_with_app(token, _event, chat):
    file_pattern = "entity/prototype_cyoda_workflow.py"
    code_without_workflow, workflow_json = "", {}
    try:
        file_path = get_project_file_name(chat["chat_id"], file_pattern)
        # Open the file asynchronously
        async with aiofiles.open(file_path, 'r') as f:
            # Read the content of the file
            input_code = await f.read()
        try:
            code_without_workflow, workflow_json = analyze_code_with_libcst(input_code)
        except Exception as e:
            #todo add retry here
            logger.exception(e)

    except Exception as e:
        logger.exception(e)


    await _save_file(chat_id=chat["chat_id"],
                     _data=app_post_process(code_without_workflow),
                     item=f"app.py")


    # Iterate over each dictionary in the list
    for item in workflow_json:
        # For each key-value pair in the dictionary, where key is the entity name and value is the code snippet
        for entity_name, entity_value in item.items():
            event_copy = deepcopy(_event)
            event_copy["function"]["prompt"]["text"] = event_copy["function"]["prompt"]["text"].format(
                code=entity_value.get("code"), workflow_function=f"process_{entity_name}")
            result = await run_chat(chat=chat, _event=event_copy, token=token, ai_endpoint=event_copy["function"]["prompt"]["api"],
                                    chat_id=chat["chat_id"])

            is_valid, formatted_result = validate_ai_result(result, "result.py")
            if is_valid:
                result = formatted_result
            else:
                retry = VALIDATION_MAX_RETRIES
                while retry > 0:
                    retry_event = copy.deepcopy(_event)
                    retry_event["function"]["prompt"]["text"] = formatted_result
                    result = await run_chat(chat=chat, _event=retry_event, token=token,
                                            ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                                "model_api") else event_copy.get("function").get("model_api"),
                                            chat_id=chat["chat_id"])
                    is_valid, formatted_result = validate_ai_result(result, _event.get("file_name"))
                    if is_valid:
                        result = formatted_result
                        retry = -1
                    else:
                        retry -= 1

            code_without_function, extracted_function = "", ""
            try:
                code_without_function, extracted_function = extract_function(result, entity_value.get("workflow_function"))
                logger.info(extracted_function)
                await _save_file(
                    chat_id=chat["chat_id"],
                    _data=code_without_function,
                    item=f"entity/{entity_name}/workflow.py"
                )
                event_copy["function"]["prompt"]["text"] = event_copy["function"]["workflow_prompt"].format(
                    code=extracted_function)
                result = await run_chat(chat=chat, _event=event_copy, token=token,
                                        ai_endpoint=event_copy["function"]["prompt"]["api"],
                                        chat_id=chat["chat_id"])
                is_valid, formatted_result = validate_ai_result(result, "result.json")
                if is_valid:
                    result = formatted_result
                else:
                    retry = VALIDATION_MAX_RETRIES
                    while retry > 0:
                        retry_event = copy.deepcopy(_event)
                        retry_event["function"]["prompt"]["text"] = formatted_result
                        result = await run_chat(chat=chat, _event=retry_event, token=token,
                                                ai_endpoint=CYODA_AI_API if not event_copy.get("function").get(
                                                    "model_api") else event_copy.get("function").get("model_api"),
                                                chat_id=chat["chat_id"])
                        is_valid, formatted_result = validate_ai_result(result, _event.get("file_name"))
                        if is_valid:
                            result = formatted_result
                            retry = -1
                        else:
                            retry -= 1
                workflow = enrich_workflow(result)
                await _save_file(
                    chat_id=chat["chat_id"],
                    _data=json.dumps(workflow),
                    item=f"entity/{entity_name}/workflow.json"
                )


            except Exception as e:
                #todo need retry here
                logger.exception(e)


    await _send_notification(chat=chat, event=_event, notification_text=_event.get("notification_text"))


def main():
    if __name__ == "__main__":
        pass


if __name__ == "__main__":
    main()


