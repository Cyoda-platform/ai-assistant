import uuid
import datetime

from quart import Blueprint, request, jsonify
from quart_rate_limiter import rate_limit
import jwt

from common.config.config import config

token_bp = Blueprint('token', __name__, url_prefix=config.API_PREFIX)

@token_bp.route('/get_guest_token', methods=['OPTIONS'])
async def get_guest_token_preflight():
    return jsonify({})

@token_bp.route('/get_guest_token', methods=['GET'])
@rate_limit(limit=config.GUEST_TOKEN_LIMIT, period=datetime.timedelta(weeks=50))
async def get_guest_token():
    session_id = uuid.uuid4()
    now = datetime.datetime.utcnow()
    payload = {
        'sub': f'guest.{session_id}',
        'caas_org_id': f'guest.{session_id}',
        'iat': now,
        'exp': now + datetime.timedelta(weeks=50)
    }
    token = jwt.encode(payload, config.AUTH_SECRET_KEY, algorithm='HS256')
    return jsonify({'access_token': token})
