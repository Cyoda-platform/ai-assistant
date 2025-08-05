import logging
from datetime import timedelta

from quart import Quart, send_from_directory
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
import common.config.const as const
from common.exception.errors import init_error_handlers
from common.utils.event_loop import BackgroundEventLoop
from routes.chat import chat_bp
from routes.labels_config import labels_config_bp
from routes.token import token_bp
from routes.workflow import workflow_bp
from services.factory import grpc_client

logger = logging.getLogger(__name__)

def create_app():
    # --- Core app ---
    app = Quart(__name__, static_folder='static', static_url_path='')
    app = cors(app, allow_origin='*')
    RateLimiter(app)  # attaches rate_limit decorator

    # --- Error handlers ---
    init_error_handlers(app)

    # --- CORS + OPTIONS hooks ---
    @app.before_serving
    async def configure_cors_and_start_grpc():
        @app.after_request
        async def _apply_cors(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'

            # Cache Control
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers["Vary"] = "Authorization, Accept-Encoding"

            # Security
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

            return response

        @app.route('/<path:path>', methods=['OPTIONS'])
        @app.route('/', methods=['OPTIONS'])
        async def _options(path=None):
            return '', 204

        # start gRPC stream in background
        grpc_client_loop = BackgroundEventLoop()
        grpc_client_loop.run_coroutine(grpc_client.grpc_stream())
        logger.info("Started gRPC background stream.")


    @app.after_serving
    async def shutdown_grpc():
        if hasattr(app, 'background_task'):
            app.background_task.cancel()
            await app.background_task
        logger.info("Stopped gRPC background stream.")

    # --- Static index route ---
    @app.route('/')
    @rate_limit(const.RATE_LIMIT, timedelta(minutes=1))
    async def index():
        return await send_from_directory(app.static_folder, 'index.html')

    # --- Register blueprints ---
    app.register_blueprint(token_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(labels_config_bp)
    app.register_blueprint(workflow_bp)

    return app
