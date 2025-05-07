from common.utils.utils import send_get_request
import common.config.config as config
from common.exception.exceptions import InvalidTokenException

def extract_bearer_token(auth_header: str) -> str:
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise InvalidTokenException('Invalid Authorization header')
    return parts[1]

async def validate_with_cyoda(token: str):
    resp = await send_get_request(token, config.CYODA_API_URL, 'v1')
    if not resp or resp.get('status') == 401:
        raise InvalidTokenException('Invalid token')
