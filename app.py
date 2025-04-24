import asyncio
import datetime
import functools
import json
import logging
import threading
import uuid
from datetime import timedelta
from typing import List

import jwt
import aiohttp
import aiofiles

from quart import Quart, request, jsonify, send_from_directory
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit

from common.config.config import MOCK_AI, ENTITY_VERSION, API_PREFIX, MAX_TEXT_SIZE, \
    MAX_FILE_SIZE, CHAT_REPOSITORY, RAW_REPOSITORY_URL, AUTH_SECRET_KEY, \
    CYODA_ENTITY_TYPE_EDGE_MESSAGE, MAX_GUEST_CHATS, ENABLE_AUTH, CYODA_API_URL
from common.config.conts import QUESTIONS_QUEUE_MODEL_NAME, FLOW_EDGE_MESSAGE_MODEL_NAME, \
    CHAT_MODEL_NAME, UPDATE_TRANSITION, MEMORY_MODEL_NAME, RATE_LIMIT, APPROVE, TRANSFER_CHATS_ENTITY
from common.exception.exceptions import ChatNotFoundException, InvalidTokenException
from common.service.entity_service_interface import EntityService
from common.util.chat_util_functions import trigger_manual_transition, get_user_message, add_answer_to_finished_flow
from common.util.utils import current_timestamp, clone_repo, \
    validate_token, send_get_request
from entity.chat.data.data import APP_BUILDER_FLOW, DESIGN_PLEASE_WAIT, \
    OPERATION_NOT_SUPPORTED_WARNING, ADDITIONAL_QUESTION_ROLLBACK_WARNING
from entity.chat.model.chat import ChatEntity
from entity.model.model import QuestionsQueue, FlowEdgeMessage, ChatMemory, ModelConfig
from logic.init import BeanFactory

logger = logging.getLogger('django')

app = Quart(__name__, static_folder='static', static_url_path='')
app = cors(app, allow_origin="*")
rate_limiter = RateLimiter(app)
factory = BeanFactory(config={"CHAT_REPOSITORY": "cyoda"})
ai_agent = factory.get_services()["ai_agent"]
entity_service: EntityService = factory.get_services()["entity_service"]
flow_processor = factory.get_services()["flow_processor"]
chat_lock = factory.get_services()["chat_lock"]
fsm_implementation = factory.get_services()["fsm"]
grpc_client = factory.get_services()["grpc_client"]
cyoda_auth_service = factory.get_services()["cyoda_auth_service"]


async def load_fsm():
    try:
        FILENAME = "/home/kseniia/PycharmProjects/ai_assistant/entity/chat/data/workflow_prototype/workflow.json"
        async with aiofiles.open(FILENAME, "r") as f:
            data = await f.read()
        fsm = json.loads(data)
        return fsm
    except Exception as e:
        logger.exception(f"Error reading JSON file: {e}")
        return None


def start_background_loop(loop):
    """
    Set and run the event loop in a separate thread.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Create a new event loop for the gRPC streaming task.
grpc_loop = asyncio.new_event_loop()
grpc_thread = threading.Thread(target=start_background_loop, args=(grpc_loop,), daemon=True)
grpc_thread.start()


@app.before_serving
async def add_cors_headers():
    @app.after_request
    async def apply_cors(response):
        # Set CORS headers for all HTTP requests
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'  # Allow these methods
        response.headers['Access-Control-Allow-Headers'] = '*'  # Allow these headers
        response.headers['Access-Control-Allow-Credentials'] = 'true'  # Allow credentials
        return response

    # await init_cyoda(cyoda_auth_service)
    logger.info("Starting gRPC stream on a dedicated background thread.")

    # Schedule the asynchronous gRPC stream on the background event loop.
    # This returns a concurrent.futures.Future which you can later cancel or inspect.
    app.background_task = asyncio.run_coroutine_threadsafe(
        grpc_client.grpc_stream(),
        grpc_loop
    )


@app.errorhandler(InvalidTokenException)
async def handle_unauthorized_exception(error):
    logger.exception(error)
    return jsonify({"error": str(error)}), 401


@app.errorhandler(ChatNotFoundException)
async def handle_chat_not_found_exception(error):
    logger.exception(error)
    return jsonify({"error": str(error)}), 404


@app.errorhandler(Exception)
async def handle_any_exception(error):
    logger.exception(error)
    return jsonify({"error": str(error)}), 500


# Decorator to enforce authorization
def auth_required(func):
    @functools.wraps(func)  # This ensures the original function's name and metadata are preserved
    async def wrapper(*args, **kwargs):
        if ENABLE_AUTH:
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise InvalidTokenException("Invalid token")

            user_id = _get_user_id(auth_header=auth_header)
            if user_id.startswith('guest.'):
                return jsonify({"error": "This action is not available. Please sign in to proceed"}), 403

            token = auth_header.split(" ")[1]
            response = await send_get_request(token, CYODA_API_URL, "v1")

            if not response or (response.get("status") and response.get("status") == 401):
                raise InvalidTokenException("Invalid token")

        # If the token is valid, proceed to the requested route
        return await func(*args, **kwargs)

    return wrapper


# Decorator to enforce authorization
def auth_required_to_proceed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not ENABLE_AUTH:
            return await func(*args, **kwargs)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise InvalidTokenException("Missing Authorization header")

        token = _extract_bearer_token(auth_header)
        user_id = _get_user_id(auth_header=auth_header)

        # Guests don’t need an external check
        if not user_id.startswith("guest."):
            await _validate_with_cyoda(token)

        return await func(*args, **kwargs)

    return wrapper


def _extract_bearer_token(auth_header: str) -> str:
    """
    Expects header like "Bearer <token>". Raises if malformed.
    """
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenException("Invalid Authorization header format")
    return parts[1]


async def _validate_with_cyoda(token: str):
    """
    Calls the external Cyoda API to validate the token.
    Raises InvalidTokenException on any failure.
    """
    response = await send_get_request(token, CYODA_API_URL, "v1")
    # Treat missing response or 401 status as invalid
    if not response or response.get("status") == 401:
        raise InvalidTokenException("Invalid token")


def _get_user_token(auth_header):
    if not auth_header:
        return None
    token = auth_header.split(" ")[1]
    return token


@app.after_serving
async def shutdown():
    app.background_task.cancel()
    await app.background_task
    logger.info("Shutting down background gRPC stream.")

    # Cancel the gRPC stream task if it exists.
    if hasattr(app, 'background_task'):
        app.background_task.cancel()

    # Stop the background event loop.
    grpc_loop.call_soon_threadsafe(grpc_loop.stop)
    # Wait for the background thread to complete.
    grpc_thread.join()


@app.route('/')
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def index():
    # Ensure that 'index.html' is located in the 'static' folder
    return await send_from_directory(app.static_folder, 'index.html')


@app.route(API_PREFIX + '/chat-flow', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def get_chat_flow():
    return jsonify(APP_BUILDER_FLOW)


@app.route(API_PREFIX + '/chats', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
@auth_required_to_proceed
async def get_chats():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header=auth_header)
    if not user_id:
        return jsonify({"error": "Invalid token"}), 401
    chats: List[ChatEntity] = await _get_entities_by_user_name_and_workflow_name(user_id=user_id, entity_model=CHAT_MODEL_NAME, workflow_name=CHAT_MODEL_NAME)
    if not user_id.startswith('guest.'):
        transfer_chats_entities = await _get_entities_by_user_name(user_id=user_id, entity_model=TRANSFER_CHATS_ENTITY)
        if transfer_chats_entities:
            transfer_chats_entity = transfer_chats_entities[0]
            guest_user_id = transfer_chats_entity['guest_user_id']
            linked_guest_chats: List[ChatEntity] = await _get_entities_by_user_name_and_workflow_name(user_id=guest_user_id, entity_model=CHAT_MODEL_NAME, workflow_name=CHAT_MODEL_NAME)
            if linked_guest_chats:
                chats.extend(linked_guest_chats)

    chats_view = [{
        'technical_id': chat.technical_id,
        'name': chat.name,
        'description': chat.description,
        'date': "2025-01-30T23:48:21.073+00:00"
    } for chat in chats]

    return jsonify({"chats": chats_view})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
@auth_required_to_proceed
async def get_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    chat: ChatEntity = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    dialogue = await process_message(finished_flow=chat.chat_flow.finished_flow,
                                     dialogue=[],
                                     auth_header=auth_header)

    chats_view = {
        'technical_id': technical_id,
        'name': chat.name,
        'description': chat.description,
        'date': chat.description,
        'dialogue': dialogue
    }
    return jsonify({"chat_body": chats_view})

#todo
@app.route(API_PREFIX + '/get_guest_token', methods=['GET'])
@rate_limit(limit=10, period=timedelta(weeks=50))
async def get_guest_token():
    session_id = uuid.uuid4()
    payload = {
        "sub": f"guest.{session_id}",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=50)
    }

    # Generate the token using HS256 algorithm
    token = jwt.encode(payload, AUTH_SECRET_KEY, algorithm="HS256")
    return jsonify({"access_token": token})


@app.route(API_PREFIX + '/chats/<technical_id>', methods=['DELETE'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def delete_chat(technical_id):
    auth_header = request.headers.get('Authorization')
    await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    entity_service.delete_item(token=cyoda_auth_service,
                               entity_model=CHAT_MODEL_NAME,
                               entity_version=ENTITY_VERSION,
                               technical_id=technical_id,
                               meta={})

    return jsonify({"message": "Chat deleted", "technical_id": technical_id})


@app.route(API_PREFIX + '/transfer-chats', methods=['POST'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
@auth_required
async def transfer_chats():
    req_data = await request.get_json()
    guest_token = req_data.get('guest_token')
    guest_user_id = _get_user_id(auth_header=f"Bearer {guest_token}")

    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header=auth_header)

    transfer_chats_entities = await _get_entities_by_user_name(user_id=user_id, entity_model=TRANSFER_CHATS_ENTITY)

    if transfer_chats_entities:
        # todo = probably can allow update
        return jsonify(
            {
                "message": "Sorry, your guest chats have already been transferred. Only one guest session is allowed."}), 403

    transfer_chats_entity = {
        "user_id": user_id,
        "guest_user_id": guest_user_id
    }
    await entity_service.add_item(token=cyoda_auth_service,
                                  entity_model=TRANSFER_CHATS_ENTITY,
                                  entity_version=ENTITY_VERSION,
                                  entity=transfer_chats_entity)


@app.route(API_PREFIX + '/chats', methods=['POST'])
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
@auth_required_to_proceed
async def add_chat():
    auth_header = request.headers.get('Authorization')
    user_id = _get_user_id(auth_header=auth_header)
    # todo auth!!
    if user_id.startswith('guest.'):
        user_chats = await _get_entities_by_user_name_and_workflow_name(user_id=user_id, entity_model=CHAT_MODEL_NAME, workflow_name=CHAT_MODEL_NAME)
        if len(user_chats) >= MAX_GUEST_CHATS:
            return jsonify({"error": "Max guest chats limit reached, please sign in to proceed"}), 403
    req_data = await request.get_json()

    edge_message_id = await entity_service.add_item(token=cyoda_auth_service,
                                                    entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                                                    entity_version=ENTITY_VERSION,
                                                    entity={
                                                        "current_transition": "",
                                                        "current_state": "",
                                                        "type": "notification",
                                                        "publish": True,
                                                        "consumed": True,
                                                        "notification": "Hi! I'm Cyoda 🧚. Let me take a look at your question. I'll be right back! ✨"
                                                    },
                                                    meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE})

    greeting_edge_message = FlowEdgeMessage(user_id=user_id, type="notification", publish=True,
                                            edge_message_id=edge_message_id)
    questions_queue = QuestionsQueue(new_questions=[greeting_edge_message],
                                     user_id=user_id)

    questions_queue_id = await entity_service.add_item(token=cyoda_auth_service,
                                                       entity_model=QUESTIONS_QUEUE_MODEL_NAME,
                                                       entity_version=ENTITY_VERSION,
                                                       entity=questions_queue)

    memory_id = await entity_service.add_item(token=cyoda_auth_service,
                                              entity_model=MEMORY_MODEL_NAME,
                                              entity_version=ENTITY_VERSION,
                                              entity=ChatMemory.model_validate({"messages": {}}))
    init_question = req_data.get('name')
    if init_question and len(str(init_question).encode('utf-8')) > MAX_TEXT_SIZE:
        return jsonify({"error": "Answer size exceeds 1MB limit"}), 400
    chat_entity = ChatEntity.model_validate({
        "user_id": user_id,
        "chat_id": "",
        "date": current_timestamp(),
        "questions_queue_id": str(questions_queue_id),
        "name": init_question[:25] + '...' if len(init_question) > 25 else init_question,
        "description": req_data.get('description'),
        "chat_flow": {"current_flow": [], "finished_flow": []},
        "current_transition": "",
        "current_state": "",
        "workflow_name": CHAT_MODEL_NAME,
        "transitions_memory": {
            "conditions": {},
            "current_iteration": {},
            "max_iteration": {}
        },
        "memory_id": memory_id,
    })

    answer_message_id = await add_answer_to_finished_flow(entity_service=entity_service,
                                                          answer=init_question,
                                                          chat=chat_entity,
                                                          cyoda_auth_service=cyoda_auth_service)

    chat_entity.chat_flow.finished_flow.append(FlowEdgeMessage(type="answer",
                                                               publish=True,
                                                               edge_message_id=answer_message_id,
                                                               consumed=False,
                                                               user_id=user_id))

    chat_entity.chat_flow.finished_flow.append(greeting_edge_message)

    technical_id = await entity_service.add_item(token=cyoda_auth_service,
                                                 entity_model=CHAT_MODEL_NAME,
                                                 entity_version=ENTITY_VERSION,
                                                 entity=chat_entity)

    return jsonify(
        {"message": "Chat created", "technical_id": technical_id, "answer_technical_id": answer_message_id}), 200


# polling for new questions here
@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['GET'])
@rate_limit(RATE_LIMIT, timedelta(seconds=10))
async def get_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat: ChatEntity = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    questions_queue_id = chat.questions_queue_id
    return await poll_questions(chat=chat,
                                questions_queue_id=questions_queue_id)


@app.route(API_PREFIX + '/chats/<technical_id>/text-questions', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(days=1))
async def submit_question_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    req_data = await request.get_json()
    question = req_data.get('question')
    res = await _submit_question_helper(auth_header=auth_header, chat=chat, question=question,
                                        technical_id=technical_id)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/questions', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(days=1))
async def submit_question(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    req_data = await request.form
    req_data = req_data.to_dict()
    question = req_data.get('question')
    file = await request.files
    user_file = file.get('file')
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    res = await _submit_question_helper(auth_header=auth_header,
                                        chat=chat,
                                        question=question,
                                        technical_id=technical_id,
                                        user_file=user_file)
    return res


@app.route(API_PREFIX + '/chats/<technical_id>/push-notify', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def push_notify(technical_id):
    return jsonify({"error": OPERATION_NOT_SUPPORTED_WARNING}), 400

@app.route(API_PREFIX + '/chats/<technical_id>/approve', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def approve(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    return await _submit_answer_helper(answer=APPROVE, chat=chat)


@app.route(API_PREFIX + '/chats/<technical_id>/rollback', methods=['POST'])
@auth_required
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def rollback(technical_id):
    auth_header = request.headers.get('Authorization')
    req_data = await request.get_json()
    if not req_data.get('question') or not req_data.get('stack'):
        return jsonify({"error": ADDITIONAL_QUESTION_ROLLBACK_WARNING}), 400
    question = req_data.get('question') if req_data else None
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    return await rollback_dialogue_script(technical_id, auth_header, chat, question)


@app.route(API_PREFIX + '/chats/<technical_id>/text-answers', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def submit_answer_text(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)

    req_data = await request.get_json()
    answer = req_data.get('answer')
    if answer and len(str(answer).encode('utf-8')) > MAX_TEXT_SIZE:
        return jsonify({"error": "Answer size exceeds 1MB limit"}), 400
    return await _submit_answer_helper(answer=answer, chat=chat)


@app.route(API_PREFIX + '/chats/<technical_id>/answers', methods=['POST'])
@auth_required_to_proceed
@rate_limit(RATE_LIMIT, timedelta(minutes=1))
async def submit_answer(technical_id):
    auth_header = request.headers.get('Authorization')
    chat = await _get_chat_for_user(request=request, auth_header=auth_header, technical_id=technical_id)
    req_data = await request.form
    req_data = req_data.to_dict()
    answer = req_data.get('answer')

    # Check if a file has been uploaded
    file = await request.files
    user_file = file.get('file')
    answer = await get_user_message(message=answer, user_file=user_file)
    if user_file.content_length > MAX_FILE_SIZE:
        return {"error": f"File size exceeds {MAX_FILE_SIZE} limit"}
    return await _submit_answer_helper(answer=answer,chat=chat, user_file=user_file)


async def _get_chat_for_user(auth_header, technical_id, request=None):
    user_id = _get_user_id(auth_header=auth_header)
    if not user_id:
        raise InvalidTokenException()

    chat: ChatEntity = await entity_service.get_item(token=cyoda_auth_service,
                                                     entity_model=CHAT_MODEL_NAME,
                                                     entity_version=ENTITY_VERSION,
                                                     technical_id=technical_id)

    if not chat and CHAT_REPOSITORY == "local":
        # todo check here
        async with chat_lock:
            chat: ChatEntity = await entity_service.get_item(token=cyoda_auth_service,
                                                             entity_model=CHAT_MODEL_NAME,
                                                             entity_version=ENTITY_VERSION,
                                                             technical_id=technical_id)
            if not chat:
                await clone_repo(chat_id=technical_id)

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{RAW_REPOSITORY_URL}/{technical_id}/entity/chat.json") as response:
                        data = await response.text()
                chat = ChatEntity.model_validate(json.loads(data))
                if not chat:
                    raise ChatNotFoundException()

                await entity_service.add_item(token=cyoda_auth_service,
                                              entity_model=CHAT_MODEL_NAME,
                                              entity_version=ENTITY_VERSION,
                                              entity=chat)

    elif not chat:
        raise ChatNotFoundException()
    await _validate_chat_owner(chat=chat, user_id=user_id)

    return chat

async def _validate_chat_owner(chat, user_id):
    # If it’s the same user, nothing to do
    if chat.user_id == user_id:
        return

    # Only allow a guest → registered transfer
    is_guest_to_registered = (
        chat.user_id.startswith("guest.")
        and not user_id.startswith("guest.")
    )
    if not is_guest_to_registered:
        raise InvalidTokenException()

    # Look up any transfer record for this registered user
    entities = await _get_entities_by_user_name(
        user_id=user_id,
        entity_model=TRANSFER_CHATS_ENTITY
    )
    if not entities:
        raise InvalidTokenException()

    # Verify that the guest ID matches
    guest_user_id = entities[0]["guest_user_id"]
    if guest_user_id != chat.user_id:
        raise InvalidTokenException()

def _get_user_id(auth_header):
    try:
        token = auth_header.split(" ")[1]
        # Decode the JWT without verifying the signature
        # The `verify=False` option ensures that we do not verify the signature
        # This is useful for extracting the payload only.
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        if user_id.startswith('guest.'):
            validate_token(token)
        return user_id
    except jwt.InvalidTokenError:
        return None


async def _get_entities_by_user_name(user_id, entity_model):
    return await entity_service.get_items_by_condition(token=cyoda_auth_service,
                                                       entity_model=entity_model,
                                                       entity_version=ENTITY_VERSION,
                                                       condition={"cyoda": {
                                                           "operator": "AND",
                                                           "conditions": [
                                                               {
                                                                   "jsonPath": "$.user_id",
                                                                   "operatorType": "EQUALS",
                                                                   "value": user_id,
                                                                   "type": "simple"
                                                               }
                                                           ],
                                                           "type": "group"
                                                       },
                                                           "local": {"key": "user_id", "value": user_id}})

async def _get_entities_by_user_name_and_workflow_name(user_id, entity_model, workflow_name):
    return await entity_service.get_items_by_condition(token=cyoda_auth_service,
                                                       entity_model=entity_model,
                                                       entity_version=ENTITY_VERSION,
                                                       condition={"cyoda": {
                                                           "operator": "AND",
                                                           "conditions": [
                                                               {
                                                                   "jsonPath": "$.user_id",
                                                                   "operatorType": "EQUALS",
                                                                   "value": user_id,
                                                                   "type": "simple"
                                                               },
                                                               {
                                                                   "jsonPath": "$.workflow_name",
                                                                   "operatorType": "EQUALS",
                                                                   "value": workflow_name,
                                                                   "type": "simple"
                                                               }
                                                           ],
                                                           "type": "group"
                                                       },
                                                           "local": {"key": "user_id", "value": user_id}})

async def _submit_question_helper(auth_header, technical_id, chat, question, user_file=None):
    # Check if a file has been uploaded

    # Validate input
    if not question:
        return jsonify({"message": "Invalid entity"}), 400

    # Return mock response if AI mock mode is enabled
    if MOCK_AI == "true":
        return jsonify({"message": "mock ai answer"}), 200

    # Process file if provided
    if user_file:
        question = await get_user_message(message=question, user_file=user_file)

    # Call AI service with the file
    result = await ai_agent.run(
        methods_dict=None,
        cls_instance=None,
        entity=chat,
        technical_id=technical_id,
        tools=None,
        model=ModelConfig(),
        tool_choice=None,
        messages=[{"role": "user", "content": question}]
    )

    return jsonify({"message": result}), 200


async def _submit_answer_helper(answer, chat: ChatEntity, user_file=None):
    is_valid, validated_answer = _validate_answer(answer=answer, user_file=user_file)
    if not is_valid:
        return jsonify({"message": validated_answer}), 400
    # todo
    if len(chat.child_entities) > MAX_GUEST_CHATS:
        return jsonify({"error": "Max guest chats limit reached, please sign in to proceed"}), 403
    edge_message_id = await trigger_manual_transition(entity_service=entity_service,
                                                      chat=chat,
                                                      answer=validated_answer,
                                                      user_file=user_file,
                                                      cyoda_auth_service=cyoda_auth_service)
    return jsonify({"answer_technical_id": edge_message_id}), 200


async def rollback_dialogue_script(technical_id, auth_header, chat: ChatEntity, question):
    pass


async def _initialize_question_queue(chat):
    pass


def _validate_answer(answer, user_file):
    if not answer:
        if not user_file:
            return False, "Invalid entity"
        return True, "please, consider the contents of this file"
    return True, answer


def _append_wait_notification(question_queue):
    wait_notification = {
        "notification": f"Thank you for your answer! {DESIGN_PLEASE_WAIT}",
        "prompt": {},
        "answer": None,
        "function": None,
        "iteration": 0,
        "max_iteration": 0
    }
    question_queue.append(wait_notification)


async def poll_questions(chat, questions_queue_id):
    try:
        questions_queue: QuestionsQueue = await entity_service.get_item(token=cyoda_auth_service,
                                                                        entity_model=QUESTIONS_QUEUE_MODEL_NAME,
                                                                        entity_version=ENTITY_VERSION,
                                                                        technical_id=questions_queue_id)
        questions_to_user = []

        if questions_queue.new_questions and questions_queue.current_state == 'idle':

            await lock_questions_queue(questions_queue_id)

            questions_queue: QuestionsQueue = await entity_service.get_item(token=cyoda_auth_service,
                                                                            entity_model=QUESTIONS_QUEUE_MODEL_NAME,
                                                                            entity_version=ENTITY_VERSION,
                                                                            technical_id=questions_queue_id)

            while questions_queue.new_questions:
                message: FlowEdgeMessage = questions_queue.new_questions.pop(0)

                message_content = await entity_service.get_item(token=cyoda_auth_service,
                                                                entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                                                                entity_version=ENTITY_VERSION,
                                                                technical_id=message.edge_message_id,
                                                                meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE})

                questions_to_user.append(message_content)
                questions_queue.asked_questions.append(message)

            await entity_service.update_item(token=cyoda_auth_service,
                                             entity_model=QUESTIONS_QUEUE_MODEL_NAME,
                                             entity_version=ENTITY_VERSION,
                                             technical_id=questions_queue_id,
                                             entity=questions_queue,
                                             meta={UPDATE_TRANSITION: "dequeue_message"})

        return jsonify({"questions": questions_to_user}), 200
    except Exception as e:
        logger.exception(e)
        return jsonify({"questions": []}), 200  # No Content


async def lock_questions_queue(questions_queue_id):
    while True:
        try:
            result = await entity_service.update_item(token=cyoda_auth_service,
                                                      entity_model=QUESTIONS_QUEUE_MODEL_NAME,
                                                      entity_version=ENTITY_VERSION,
                                                      technical_id=questions_queue_id,
                                                      entity=None,
                                                      meta={UPDATE_TRANSITION: "lock_for_dequeue"})
            return result
        except Exception as e:
            logging.exception("failed_transition_to_lock_for_dequeue_entity_questions_queue...")
            # Delay before retrying to prevent tight looping
            await asyncio.sleep(1)


async def process_message(finished_flow: List[FlowEdgeMessage], auth_header, dialogue: list) -> list:
    for message in finished_flow:
        if ((message.type in ["question", "notification"] and getattr(message, "publish", False))
                or message.type == "answer"):
            message_content = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                entity_version=ENTITY_VERSION,
                technical_id=message.edge_message_id,
                meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            message_content['technical_id'] = message.edge_message_id
            dialogue.append(message_content)

        # If the message contains child entities, retrieve and process each child recursively
        if message.type == "child_entities":
            message_content = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                entity_version=ENTITY_VERSION,
                technical_id=message.edge_message_id,
                meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            child_entities = message_content.get("child_entities", [])
            for child_entity_id in child_entities:
                child_entity: ChatEntity = await entity_service.get_item(
                    token=cyoda_auth_service,
                    entity_model=CHAT_MODEL_NAME,
                    entity_version=ENTITY_VERSION,
                    technical_id=child_entity_id
                )
                child_entity_finished_flow = child_entity.chat_flow.finished_flow
                await process_message(finished_flow=child_entity_finished_flow, auth_header=auth_header,
                                      dialogue=dialogue)
    return dialogue


if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=5000, threaded=True)
