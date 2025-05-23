import logging

from common.utils.utils import send_get_request
from common.config.config import config
from common.exception.exceptions import InvalidTokenException


logger = logging.getLogger(__name__)

def extract_bearer_token(auth_header: str) -> str:
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise InvalidTokenException('Invalid Authorization header')
    return parts[1]

async def validate_with_cyoda(token: str):
    resp = await send_get_request(token, config.CYODA_API_URL, 'v1')
    if not resp or resp.get('status') == 401:
        if not config.ENABLE_AUTH:
            logger.info("token invalid, but auth is disabled")
            return
        raise InvalidTokenException('Invalid token')
