from datetime import timedelta

from quart import Blueprint, jsonify
from quart_rate_limiter import rate_limit
import common.config.const as const
import common.config.config as config

flow_bp = Blueprint('flow', __name__, url_prefix=config.API_PREFIX)

# @flow_bp.route('/chat-flow', methods=['GET'])
# @rate_limit(limit=const.RATE_LIMIT, period=timedelta(minutes=1))
# async def get_chat_flow():
#     #return jsonify(APP_BUILDER_FLOW)

