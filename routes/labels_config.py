import logging
from datetime import timedelta
from quart import Blueprint, jsonify
from quart_rate_limiter import rate_limit

import common.config.const as const
from common.config.config import config
from services.labels_config_service import LabelsConfigService

labels_config_bp = Blueprint('labels_config', __name__, url_prefix=f"{config.API_PREFIX}/labels_config")
logger = logging.getLogger(__name__)

_labels_config_service = LabelsConfigService()

@labels_config_bp.route('', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(seconds=15))
async def labels_config_full_map():
    """Return the entire structured TEXT_MAP as JSON."""
    labels_config = await _labels_config_service.get_all()
    return jsonify(labels_config)


@labels_config_bp.route('/<path:key>', methods=['GET'])
@rate_limit(const.RATE_LIMIT, timedelta(seconds=15))
async def labels_config_item(key):
    """
    Return a single entry from TEXT_MAP.
    Key should be dot-separated, e.g.:
      /text_map/side_bar.links.home
    """
    # normalize URL segment into our key format
    identifier = key.replace('-', '_')
    value = await _labels_config_service.get(identifier=identifier)
    if value is None:
        return jsonify({
            "error": f"Key '{key}' not found"
        }), 404
    return jsonify({key: value})

@labels_config_bp.route('/refresh', methods=['POST'])
@rate_limit(const.RATE_LIMIT, timedelta(minutes=15))
async def refresh_labels_config():
    """
    POST /config/labels/refresh
    Force a reload of the labels configuration from the remote service.
    Rate-limited to avoid hammering the upstream, and requires authentication.
    """
    try:
        await _labels_config_service.refresh()
        return jsonify({
            "success": True,
            "message": "Labels configuration refreshed successfully."
        }), 200

    except Exception as e:
        logger.exception("Failed to refresh labels config")
        return jsonify({
            "success": False,
            "message": "Unable to refresh labels configuration at this time."
        }), 502
