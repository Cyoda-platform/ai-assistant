import hashlib

from quart import request


async def ua_key_function() -> str:
    ua_raw = request.headers.get("User-Agent", "unknown")
    ua: str = str(ua_raw)
    ua_bytes: bytes = ua.encode("utf-8")
    return hashlib.sha256(ua_bytes).hexdigest()


async def token_key_function() -> str:
    token = request.headers.get("Authorization", "").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token or "unauthenticated"
