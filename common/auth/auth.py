import json
import logging
import requests

from common.config import config
from common.config.config import CYODA_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_and_get_refresh_token():
    login_endpoint = f"{CYODA_API_URL}/auth/login"
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }

    credentials = {"username": config.API_KEY, "password": config.API_SECRET}
    payload = json.dumps(credentials)
    logger.info(f"Attempting to authenticate with Cyoda API., login url: {login_endpoint}")
    response = requests.post(login_endpoint, headers=headers, data=payload)

    if response.status_code == 200:
        # Assuming the refresh token is returned in the 'refresh_token' field
        refresh_token = response.json().get('refreshToken')
        return refresh_token
    else:
        raise Exception(f"Login failed: {response.status_code} {response.text}")


def get_access_token(refresh_token):
    token_endpoint = f"{CYODA_API_URL}/auth/token"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {refresh_token}'
    }
    response = requests.get(token_endpoint, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('token')
        # token_expiry = token_data.get('tokenExpiry')
        return access_token
    else:
        raise Exception(f"Token refresh failed: {response.status_code} {response.text}")