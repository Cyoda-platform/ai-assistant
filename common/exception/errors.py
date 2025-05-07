import logging
from quart import jsonify
from common.exception.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    ChatNotFoundException,
    GuestChatsLimitExceededException,
    RequestLimitExceededException
)
from quart_rate_limiter import RateLimitExceeded

logger = logging.getLogger(__name__)

async def handle_401(error):
    logger.exception(error)
    return jsonify({'error': str(error)}), 401

async def handle_404(error):
    logger.exception(error)
    return jsonify({'error': str(error)}), 404

async def handle_403(error):
    logger.exception(error)
    return jsonify({'error': str(error)}), 403

async def handle_429(error):
    logger.exception(error)
    return jsonify({'error': str(error)}), 429

async def handle_500(error):
    logger.exception(error)
    return jsonify({'error': 'Internal server error'}), 500

def init_error_handlers(app):
    app.errorhandler(InvalidTokenException)(handle_401)
    app.errorhandler(TokenExpiredException)(handle_401)
    app.errorhandler(ChatNotFoundException)(handle_404)
    app.errorhandler(GuestChatsLimitExceededException)(handle_403)
    app.errorhandler(RequestLimitExceededException)(handle_429)
    app.errorhandler(RateLimitExceeded)(handle_429)
    app.errorhandler(Exception)(handle_500)
