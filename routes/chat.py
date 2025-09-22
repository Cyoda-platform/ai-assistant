from datetime import timedelta
from quart import Blueprint, request, jsonify, Response
from quart_rate_limiter import rate_limit

import common.config.const as const
from common.config.config import config
from common.utils.auth_utils import auth_optional, auth_required
from routes.chat_utils import extract_auth_info, get_json_data, get_form_data, get_mixed_data
from routes.rl_key_functions import token_key_function
from services.factory import chat_service

chat_bp = Blueprint('chat', __name__, url_prefix=f"{config.API_PREFIX}/chats")


@chat_bp.route('', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def list_chats():
    _, user_id = await extract_auth_info()
    chats = await chat_service.list_chats(user_id)
    return jsonify({"chats": chats})


@chat_bp.route('', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def create_chat():
    _, user_id = await extract_auth_info()

    # Handle both JSON (no files) and form data (with files) requests
    (name, description), user_file, user_files = await get_mixed_data(
        'name', 'description',
        file_key='file',      # Single file for backward compatibility
        files_key='files'     # Multiple files for new functionality
    )

    # Build req_data from form fields or use existing JSON structure
    if name is not None or description is not None:
        # Form data request
        req_data = {}
        if name is not None:
            req_data['name'] = name
        if description is not None:
            req_data['description'] = description
    else:
        # JSON request (fallback for backward compatibility)
        req_data = await request.get_json()

    result = await chat_service.add_chat(user_id, req_data, user_files=user_files, user_file=user_file)
    return jsonify(result), 400 if result.get("error") else 200


@chat_bp.route('/<technical_id>', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def get_chat_route(technical_id):
    header, _ = await extract_auth_info()
    result = await chat_service.get_chat(header, technical_id)
    return jsonify({"chat_body": result})


@chat_bp.route('/<technical_id>', methods=['DELETE'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def delete_chat_route(technical_id):
    header, _ = await extract_auth_info()
    result = await chat_service.delete_chat(header, technical_id)
    return jsonify(result), 200


@chat_bp.route('/<technical_id>/files/<blob_id>', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def download_file_route(technical_id, blob_id):
    """Download a file by blob ID from a chat."""
    header, _ = await extract_auth_info()
    result = await chat_service.download_file(header, technical_id, blob_id)

    if "error" in result:
        return jsonify(result), 400

    # Return file as response with appropriate headers
    response = Response(
        result["content"],
        mimetype=result["content_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            "Content-Length": str(result["file_size"]),
            "Cache-Control": "no-cache"
        }
    )
    return response


@chat_bp.route('/<technical_id>', methods=['PUT'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def rename_chat_route(technical_id):
    header, _ = await extract_auth_info()
    chat_name, chat_description = await get_json_data('chat_name', 'chat_description')
    result = await chat_service.rename_chat(header, technical_id, chat_name, chat_description)
    return jsonify(result), 200


@chat_bp.route('/<technical_id>/text-questions', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(days=1), key_function=token_key_function)
@auth_required
async def submit_text_question_route(technical_id):
    header, _ = await extract_auth_info()
    question, = await get_json_data('question')
    return await chat_service.submit_text_question(header, technical_id, question)


@chat_bp.route('/<technical_id>/questions', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(days=1), key_function=token_key_function)
@auth_required
async def submit_question_route(technical_id):
    header, _ = await extract_auth_info()
    (question,), user_file, user_files = await get_form_data(
        'question',
        file_key='file',      # Single file for backward compatibility
        files_key='files'     # Multiple files for new functionality
    )
    return await chat_service.submit_question(header, technical_id, question, user_file, user_files)


@chat_bp.route('/<technical_id>/text-answers', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def submit_text_answer_route(technical_id):
    header, _ = await extract_auth_info()

    # Handle both JSON (no files) and form data (with files) requests
    (answer,), user_file, user_files = await get_mixed_data(
        'answer',
        file_key='file',      # Single file for backward compatibility
        files_key='files'     # Multiple files for new functionality
    )

    return await chat_service.submit_text_answer(header, technical_id, answer, user_files=user_files, user_file=user_file)


@chat_bp.route('/<technical_id>/answers', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def submit_answer_route(technical_id):
    header, _ = await extract_auth_info()
    (answer,), user_file, user_files = await get_form_data(
        'answer',
        file_key='file',      # Single file for backward compatibility
        files_key='files'     # Multiple files for new functionality
    )
    return await chat_service.submit_answer(header, technical_id, answer, user_file=user_file, user_files=user_files)


@chat_bp.route('/<technical_id>/approve', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def approve_route(technical_id):
    header, _ = await extract_auth_info()
    return await chat_service.approve(header, technical_id)


@chat_bp.route('/<technical_id>/rollback', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def rollback_route(technical_id):
    header, _ = await extract_auth_info()
    result = await chat_service.rollback(header, technical_id)
    return jsonify(result), 200


@chat_bp.route('/<technical_id>/push-notify', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
async def push_notify_route(technical_id):
    return jsonify({"error": const.Notifications.OPERATION_NOT_SUPPORTED.value}), 400


@chat_bp.route('/transfer', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def transfer_chats_route():
    guest_token, = await get_json_data('guest_token')
    header, _ = await extract_auth_info()
    result = await chat_service.transfer_chats(guest_token=guest_token, auth_header=header)
    return jsonify(result), 200
