import json
import logging
import aiofiles
from common.config.config import CYODA_AI_URL, MOCK_AI, CYODA_AI_API, WORKFLOW_AI_API, CONNECTION_AI_API, RANDOM_AI_API, \
    MAX_TEXT_SIZE, USER_FILES_DIR_NAME
from common.util.utils import parse_json, validate_result, send_post_request, ValidationErrorException, \
    get_project_file_name, read_file_object

API_V_CONNECTIONS_ = "api/v1/connections"
API_V_CYODA_ = "api/v1/cyoda"
API_V_WORKFLOWS_ = "api/v1/workflows"
API_V_RANDOM_ = "api/v1/random"
logger = logging.getLogger(__name__)

#todo remove later
dataset = {}
def add_to_dataset(chat_id, ai_question, ai_endpoint, answer):
    if chat_id not in dataset:
        dataset[chat_id] = []  # Create a new chat session if it doesn't exist
        # Add the question and answer pair to the list of the corresponding chat session
    dataset[chat_id].append({"ai_endpoint": ai_endpoint, "question": ai_question, "answer": answer})


class AiAssistantService:
    def __init__(self):
        pass

    async def init_chat(self, token, chat_id):
        if MOCK_AI=="true":
            return {"success": True}
        data = json.dumps({"chat_id": f"{chat_id}"})
        endpoints = [API_V_CYODA_, API_V_WORKFLOWS_, API_V_RANDOM_]
        for endpoint in endpoints:
            await send_post_request(token, CYODA_AI_URL, "%s/initial" % endpoint, data)
        return {"success": True}

    async def init_workflow_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = await send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_WORKFLOWS_, data)
        return resp.get('message')

    async def init_connections_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = await send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_CONNECTIONS_, data)
        return resp.get('message')

    async def init_random_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = await send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_RANDOM_, data)
        return resp.get('message')

    async def init_cyoda_chat(self, token, chat_id):
        data = json.dumps({"chat_id": f"{chat_id}"})
        resp = await send_post_request(token, CYODA_AI_URL, "%s/initial" % API_V_RANDOM_, data)
        return resp.get('message')

    async def ai_chat(self, token, chat_id, ai_endpoint, ai_question, user_file=None):
        try:
            if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
                logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
                return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
            if MOCK_AI=="true":
                return {"entity": "some random text"}
            if user_file and user_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_description = await self.chat_random(token=token, chat_id=chat_id, ai_question="Please, return detailed file description", user_file=user_file)
                ai_question = f"{ai_question}. File description: {file_description}"
                user_file_txt = user_file.rsplit('.', 1)[0] + '.txt'
                async with aiofiles.open(get_project_file_name(chat_id, user_file_txt, folder_name=USER_FILES_DIR_NAME), 'w') as output:
                    await output.write(file_description)
            if ai_endpoint == CYODA_AI_API:
                resp = await self.chat_cyoda(token=token, chat_id=chat_id, ai_question=ai_question, user_file=user_file if user_file and not user_file.lower().endswith(('.jpg', '.jpeg', '.png')) else None)
            elif ai_endpoint == WORKFLOW_AI_API:
                resp = await self.chat_workflow(token=token, chat_id=chat_id, ai_question=ai_question)
            elif ai_endpoint == CONNECTION_AI_API:
                resp = await self.chat_connection(token=token, chat_id=chat_id, ai_question=ai_question)
            elif ai_endpoint == RANDOM_AI_API:
                resp = await self.chat_random(token=token, chat_id=chat_id, ai_question=ai_question, user_file=user_file)
            else:
                return {"error": "Invalid endpoint"}
            add_to_dataset(ai_endpoint=ai_endpoint, ai_question=ai_question, chat_id=chat_id, answer=resp)
            return resp
        except Exception as e:
            logger.exception(e)
            return {"error": "Error while AI processing"}

    async def chat_cyoda(self, token, chat_id, ai_question, user_file=None):
        if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
            logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
            return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
        if user_file:
            file_path = get_project_file_name(chat_id, user_file, folder_name=USER_FILES_DIR_NAME)
            data = {"chat_id": f"{chat_id}", "question": f"{ai_question}"}
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat-file" % API_V_CYODA_, data, user_file=file_path)
        else:
            data = json.dumps({"chat_id": f"{chat_id}", "question": f"{ai_question}"})
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CYODA_, data)
        return resp.get('message')


    async def chat_workflow(self, token, chat_id, ai_question):
        if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
            logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
            return {"error": "Answer size exceeds 1MB limit"}
        data = json.dumps({
            "question": f"{ai_question}",
            "return_object": "workflow",
            "chat_id": f"{chat_id}",
            "class_name": "com.cyoda.tdb.model.treenode.TreeNodeEntity"
        })
        resp = await send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_WORKFLOWS_, data)
        return resp.get('message')

    async def export_workflow_to_cyoda_ai(self, token, chat_id, data):
        try:
            data = json.dumps({
                "name": data["name"],
                "chat_id": chat_id,
                "class_name": data["class_name"],
                "transitions": data["transitions"]
            })
            resp = await send_post_request(token, CYODA_AI_URL, "%s/generate-workflow" % API_V_WORKFLOWS_, data)
            return resp.get('message')
        except Exception as e:
            logger.error(f"Failed to export workflow: {e}")

    async def validate_and_parse_json(self, token:str, chat_id: str, data: str, schema: str, ai_endpoint:str, max_retries: int):
        try:
            parsed_data = parse_json(data)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Invalid JSON entity provided.") from e

        attempt = 0
        while attempt <= max_retries:
            try:
                parsed_data = await validate_result(parsed_data, '', schema)
                logger.info(f"JSON validation successful on attempt {attempt + 1}.")
                return parsed_data
            except ValidationErrorException as e:
                logger.warning(
                    f"JSON validation failed on attempt {attempt + 1} with error: {e.message}"
                )
                if attempt < max_retries:
                    question = (
                        f"Retry the last step. JSON validation failed with error: {e.message}. "
                        f"using this json schema: {json.dumps(schema)}. "
                        f"Return only the DTO JSON."
                    )
                    retry_result = await self.ai_chat(token=token, chat_id=chat_id, ai_endpoint=ai_endpoint, ai_question=question)
                    parsed_data = parse_json(retry_result)
            finally:
                attempt += 1
        logger.error(f"Maximum retry attempts reached. Validation failed. Attempt: {attempt}")
        raise ValueError("JSON validation failed after retries.")


    async def chat_connection(self, token, chat_id, ai_question):
        if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
            logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
            return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
        data = json.dumps({
            "question": f"{ai_question}",
            "return_object": "import-connections",
            "chat_id": f"{chat_id}"
        })
        resp = await send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CONNECTIONS_, data)
        return resp.get('message')


    async def chat_random(self, token, chat_id, ai_question, user_file=None):
        if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
            logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
            return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
        if user_file:
            file_path = get_project_file_name(chat_id, user_file, folder_name=USER_FILES_DIR_NAME)
            data = {"chat_id": f"{chat_id}", "question": f"{ai_question}"}
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat-file" % API_V_RANDOM_, data,
                                           user_file=file_path)
        else:
            data = json.dumps({"chat_id": f"{chat_id}", "question": f"{ai_question}"})
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_RANDOM_, data)
        return resp.get('message')
