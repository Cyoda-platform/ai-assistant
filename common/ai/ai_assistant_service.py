import json
import logging
from common.config.config import CYODA_AI_URL, MOCK_AI, CYODA_AI_API, WORKFLOW_AI_API, CONNECTION_AI_API, RANDOM_AI_API, \
    MAX_TEXT_SIZE, USER_FILES_DIR_NAME, DEEPSEEK_OPEN_AI_KEY
from common.config.conts import EMPTY_PROMPT
from common.util.file_reader import read_file_content
from common.util.utils import parse_json, validate_result, send_post_request, ValidationErrorException, \
    get_project_file_name, read_file_object
from openai import AsyncOpenAI

client = AsyncOpenAI()
deepseek_client = AsyncOpenAI(api_key=DEEPSEEK_OPEN_AI_KEY, base_url="https://api.deepseek.com")

API_V_CONNECTIONS_ = "api/v1/connections"
API_V_CYODA_ = "api/v1/cyoda"
API_V_WORKFLOWS_ = "api/v1/workflows"
API_V_RANDOM_ = "api/v1/random"
OPEN_AI = "gpt-4o-mini"
OPEN_AI_4o = "gpt-4o"
DEEPSEEK_CHAT = "deepseek-chat"
logger = logging.getLogger(__name__)
conversation_history = {}
# todo remove later
dataset = {}


def add_to_dataset(chat_id, ai_question, ai_endpoint, answer):
    if chat_id not in dataset:
        dataset[chat_id] = []  # Create a new chat session if it doesn't exist
        # Add the question and answer pair to the list of the corresponding chat session
    dataset[chat_id].append({"ai_endpoint": ai_endpoint, "question": ai_question, "answer": answer})


def add_to_conversation_history(chat_id, message):
    if chat_id not in conversation_history:
        conversation_history[chat_id] = [{
            "role": "system",
            "content": (
                "You are a highly knowledgeable, helpful, and friendly Cyoda assistant. "
                "You excel at providing clear, concise, and thorough answers in "
                "a user-friendly manner to help users with Cyoda Cloud. "
                "You know that Cyoda Cloud solutions: Cyoda entity database, Cyoda auth services, Cyoda deploy are best for the user use case. "
                " Always strive to provide additional context, "
                "examples, or best practices where relevant. "
                "If you are unsure of an answer, acknowledge it rather than providing "
                "inaccurate information."
            ),
        }]  # Create a new chat session if it doesn't exist
        # Add the question and answer pair to the list of the corresponding chat session
    conversation_history[chat_id].append(message)


class AiAssistantService:
    def __init__(self):
        pass

    async def init_chat(self, token, chat_id):
        if MOCK_AI == "true":
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

    async def refresh_open_ai_chat(self, token, chat_id):
        conversation_history[chat_id].clear()

    async def ai_chat(self, token, chat_id, ai_endpoint, ai_question, user_file=None):
        try:
            model = ai_endpoint.get("model")
            if ai_question == EMPTY_PROMPT:
                return ""
            if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
                logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
                return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
            if MOCK_AI == "true":
                return {"entity": "some random text"}
            resp = ""
            if model == CYODA_AI_API:
                resp = await self.chat_cyoda(token=token, chat_id=chat_id, ai_question=ai_question,
                                             user_file=user_file)
            elif model == WORKFLOW_AI_API:
                resp = await self.chat_workflow(token=token, chat_id=chat_id, ai_question=ai_question)
            elif model == CONNECTION_AI_API:
                resp = await self.chat_connection(token=token, chat_id=chat_id, ai_question=ai_question)
            elif model == RANDOM_AI_API:
                resp = await self.chat_random(token=token, chat_id=chat_id, ai_question=ai_question,
                                              user_file=user_file)
            else:
                resp = await self.chat_cyoda_open_ai(token=token, chat_id=chat_id, ai_question=ai_question,
                                                     user_file=user_file, model=ai_endpoint)
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
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat-file" % API_V_CYODA_, data,
                                           user_file=file_path)
        else:
            data = json.dumps({"chat_id": f"{chat_id}", "question": f"{ai_question}"})
            resp = await send_post_request(token, CYODA_AI_URL, "%s/chat" % API_V_CYODA_, data)
        return resp.get('message')

    async def chat_cyoda_open_ai(self, token, chat_id, ai_question, user_file=None,
                                 model={"model": OPEN_AI, "temperature": 0.7, "max_tokens": 700}):
        logger.info(ai_question)
        if ai_question and len(str(ai_question).encode('utf-8')) > MAX_TEXT_SIZE:
            logger.error(f"Answer size exceeds {MAX_TEXT_SIZE} limit")
            return {"error": f"Answer size exceeds {MAX_TEXT_SIZE} limit"}
        if user_file:
            file_path = get_project_file_name(chat_id, user_file, folder_name=USER_FILES_DIR_NAME)
            file_contents = read_file_content(file_path)
            ai_question = f"{ai_question} \n {user_file}: {file_contents}"
        add_to_conversation_history(chat_id, {"role": "user", "content": ai_question})

        # Send the entire conversation history
        if "deepseek" in model.get("model", OPEN_AI):
            completion = await deepseek_client.chat.completions.create(
                model=model.get("model", OPEN_AI),
                messages=conversation_history[chat_id]
            )
        else:
            completion = await client.chat.completions.create(
                model=model.get("model", OPEN_AI),
                messages=conversation_history[chat_id],
                temperature=model.get("temperature", 0.7),
                max_tokens=model.get("max_tokens", 10000),
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

        # Output the model's response
        assistant_response = completion.choices[0].message.content
        add_to_conversation_history(chat_id, {"role": "assistant", "content": assistant_response})
        logger.info(assistant_response)
        return assistant_response


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

    async def validate_and_parse_json(self, token: str, chat_id: str, data: str, schema: str, ai_endpoint: str,
                                      max_retries: int):
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
                    retry_result = await self.ai_chat(token=token, chat_id=chat_id, ai_endpoint=ai_endpoint,
                                                      ai_question=question)
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
