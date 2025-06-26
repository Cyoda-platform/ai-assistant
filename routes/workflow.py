from datetime import timedelta
from quart import Blueprint, jsonify, request
from quart_rate_limiter import rate_limit

import common.config.const as const
from common.config.config import config
from common.utils.auth_utils import auth_required
from routes.chat_utils import extract_auth_info
from routes.rl_key_functions import token_key_function
from services.factory import workflow_converter_service
workflow_bp = Blueprint('workflow', __name__, url_prefix=f"{config.API_PREFIX}/workflows")


@workflow_bp.route('/<technical_id>/<entity_name>/<entity_version>', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def create_chat(technical_id, entity_name, entity_version):
    _, user_id = await extract_auth_info()
    workflow = await request.get_json()
    result = await workflow_converter_service.convert_workflow(
        workflow_contents=workflow,
        entity_name=entity_name,
        entity_version=entity_version,
        technical_id=technical_id,
    )
    return jsonify(result), 400 if result.get("error") else 2000