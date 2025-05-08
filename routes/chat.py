from datetime import timedelta
from quart import Blueprint, request, jsonify
from quart_rate_limiter import rate_limit

import common.config.const as const
from common.config.config import config
from common.utils.auth_utils import auth_optional, auth_required, get_user_id
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__, url_prefix=f"{config.API_PREFIX}/chats")
_chat_service = ChatService()


@chat_bp.route('', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_optional
async def list_chats():
    header = request.headers.get('Authorization', '')
    user_id = await get_user_id(header) if header else None
    chats = await _chat_service.list_chats(user_id)
    return jsonify({"chats": chats})


@chat_bp.route('', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_optional
async def create_chat():
    header = request.headers.get('Authorization', '')
    user_id = await get_user_id(header) if header else None
    req_data = await request.get_json()
    result = await _chat_service.create_chat(user_id, req_data)
    if result.get("error"):
        return jsonify(result), 400
    return jsonify(result), 200


@chat_bp.route('/<technical_id>', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_optional
async def get_chat(technical_id):
    header = request.headers.get('Authorization', '')
    result = await _chat_service.get_chat(header, technical_id)
    return jsonify({"chat_body": result})


@chat_bp.route('/<technical_id>', methods=['DELETE'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_required
async def delete_chat(technical_id):
    header = request.headers.get('Authorization')
    result = await _chat_service.delete_chat(header, technical_id)
    return jsonify(result), 200


@chat_bp.route('/<technical_id>/text-questions', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(days=1))
@auth_required
async def submit_text_question(technical_id):
    header = request.headers.get('Authorization')
    data = await request.get_json()
    return await _chat_service.submit_text_question(header, technical_id, data.get('question'))


@chat_bp.route('/<technical_id>/questions', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(days=1))
@auth_required
async def submit_question(technical_id):
    header = request.headers.get('Authorization')
    form = (await request.form).to_dict()
    files = await request.files
    user_file = files.get('file')
    return await _chat_service.submit_question(header, technical_id, form.get('question'), user_file)


@chat_bp.route('/<technical_id>/text-answers', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_required
async def submit_text_answer(technical_id):
    header = request.headers.get('Authorization')
    data = await request.get_json()
    return await _chat_service.submit_text_answer(header, technical_id, data.get('answer'))


@chat_bp.route('/<technical_id>/answers', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_required
async def submit_answer(technical_id):
    header = request.headers.get('Authorization')
    form = (await request.form).to_dict()
    files = await request.files
    user_file = files.get('file')
    return await _chat_service.submit_answer(header, technical_id, form.get('answer'), user_file)


@chat_bp.route('/<technical_id>/approve', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_optional
async def approve(technical_id):
    header = request.headers.get('Authorization', '')
    return await _chat_service.approve(header, technical_id)


@chat_bp.route('/<technical_id>/rollback', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
@auth_optional
async def rollback(technical_id):
    header = request.headers.get('Authorization', '')
    result = await _chat_service.rollback(header, technical_id)
    return jsonify(result), 200


@chat_bp.route('/<technical_id>/push-notify', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
async def push_notify(technical_id):
    return jsonify({"error": const.OPERATION_NOT_SUPPORTED_WARNING}), 400
