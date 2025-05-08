import functools
import jwt
from quart import request, jsonify

from common.config.config import config
from common.utils.request_utils import extract_bearer_token, validate_with_cyoda
from common.exception.exceptions import InvalidTokenException, TokenExpiredException
from common.utils.utils import validate_token


async def get_user_id(auth_header: str) -> str:
    token = extract_bearer_token(auth_header)
    try:
        # Decode the JWT without verifying the signature
        # The verify=False option ensures that we do not verify the signature
        # This is useful for extracting the payload only.
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("caas_org_id")
        if not user_id:
            raise InvalidTokenException()
        if user_id.startswith('guest.'):
            validate_token(token)
        return user_id
    except jwt.InvalidTokenError:
        raise InvalidTokenException()

def auth_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if config.ENABLE_AUTH:
            header = request.headers.get('Authorization')
            if not header:
                raise InvalidTokenException('Missing token')
            user_id = await get_user_id(header)
            if user_id.startswith('guest.'):
                return jsonify({'error': 'Please sign in to proceed'}), 403
            await validate_with_cyoda(extract_bearer_token(header))
        return await func(*args, **kwargs)
    return wrapper

def auth_optional(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if config.ENABLE_AUTH:
            header = request.headers.get('Authorization')
            if header:
                await validate_with_cyoda(extract_bearer_token(header))
        return await func(*args, **kwargs)
    return wrapper
