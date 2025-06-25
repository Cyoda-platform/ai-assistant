import logging
from quart import Blueprint, jsonify
from common.config.config import config
from services.factory import labels_config_service

labels_config_bp = Blueprint('labels_config', __name__, url_prefix=f"{config.API_PREFIX}/labels_config")
logger = logging.getLogger(__name__)


@labels_config_bp.route('', methods=['GET'])
async def labels_config_full_map():
    """Return the entire structured TEXT_MAP as JSON."""
    labels_config = await labels_config_service.get_all()
    return jsonify(labels_config)


@labels_config_bp.route('/<path:key>', methods=['GET'])
async def labels_config_item(key):
    """
    Return a single entry from TEXT_MAP.
    Key should be dot-separated, e.g.:
      /text_map/side_bar.links.home
    """
    # normalize URL segment into our key format
    identifier = key.replace('-', '_')
    value = await labels_config_service.get(identifier=identifier)
    if value is None:
        return jsonify({
            "error": f"Key '{key}' not found"
        }), 404
    return jsonify({key: value})


@labels_config_bp.route('/refresh', methods=['POST'])
async def refresh_labels_config():
    """
    POST /config/labels/refresh
    Force a reload of the labels configuration from the remote service.
    Rate-limited to avoid hammering the upstream, and requires authentication.
    """
    try:
        await labels_config_service.refresh()
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
