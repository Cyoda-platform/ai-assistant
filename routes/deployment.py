import logging
from datetime import timedelta
from quart import Blueprint, request, jsonify
from quart_rate_limiter import rate_limit

import common.config.const as const
from common.config.config import config
from common.utils.auth_utils import auth_required, auth_optional
from routes.chat_utils import extract_auth_info
from routes.rl_key_functions import token_key_function
from services.factory import deployment_http_service

deployment_bp = Blueprint('deployment', __name__, url_prefix=f"{config.API_PREFIX}/deployment")
logger = logging.getLogger(__name__)


@deployment_bp.route('/schedule/env', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def schedule_deploy_env():
    """Schedule environment deployment."""
    try:
        header, user_id = await extract_auth_info()
        req_data = await request.get_json()

        if not req_data:
            return jsonify({"error": "Request body is required"}), 400

        technical_id = req_data.get('technical_id')
        if not technical_id:
            return jsonify({"error": "technical_id is required"}), 400

        result = await deployment_http_service.schedule_deploy_env(
            technical_id=technical_id,
            user_id=user_id,
            entity_data=req_data.get('entity', {})
        )

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error in schedule_deploy_env: {e}")
        return jsonify({"error": str(e)}), 500


@deployment_bp.route('/schedule/user-app/build', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def schedule_build_user_application():
    """Schedule user application build."""
    try:
        header, user_id = await extract_auth_info()
        req_data = await request.get_json()

        if not req_data:
            return jsonify({"error": "Request body is required"}), 400

        technical_id = req_data.get('technical_id')
        if not technical_id:
            return jsonify({"error": "technical_id is required"}), 400

        result = await deployment_http_service.schedule_build_user_application(
            technical_id=technical_id,
            user_id=user_id,
            entity_data=req_data.get('entity', {})
        )

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error in schedule_build_user_application: {e}")
        return jsonify({"error": str(e)}), 500


@deployment_bp.route('/schedule/user-app/deploy', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_required
async def schedule_deploy_user_application():
    """Schedule user application deployment."""
    try:
        header, user_id = await extract_auth_info()
        req_data = await request.get_json()

        if not req_data:
            return jsonify({"error": "Request body is required"}), 400

        technical_id = req_data.get('technical_id')
        if not technical_id:
            return jsonify({"error": "technical_id is required"}), 400

        result = await deployment_http_service.schedule_deploy_user_application(
            technical_id=technical_id,
            user_id=user_id,
            entity_data=req_data.get('entity', {})
        )

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error in schedule_deploy_user_application: {e}")
        return jsonify({"error": str(e)}), 500


@deployment_bp.route('/status/<build_id>', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def get_env_deploy_status(build_id):
    """Get deployment status for a specific build."""
    try:
        header, user_id = await extract_auth_info()

        result = await deployment_http_service.get_env_deploy_status(
            build_id=build_id,
            user_id=user_id
        )

        return jsonify(result)

    except ValueError as ve:
        logger.warning(f"Validation error in get_env_deploy_status: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.exception(f"Error in get_env_deploy_status: {e}")
        return jsonify({"error": str(e)}), 500


@deployment_bp.route('/methods', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=1), key_function=token_key_function)
@auth_optional
async def list_deployment_methods():
    """List all available deployment methods."""
    try:
        result = deployment_http_service.get_available_methods()
        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error in list_deployment_methods: {e}")
        return jsonify({"error": str(e)}), 500
