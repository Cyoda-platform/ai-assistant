import asyncio
import logging
import threading
from datetime import timedelta

from quart import Quart, send_from_directory
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
import common.config.const as const
from common.exception.errors import init_error_handlers
from routes.chat import chat_bp
from routes.labels_config import labels_config_bp
from routes.token import token_bp
from services.factory import grpc_client
from services.factory import scheduler

logger = logging.getLogger(__name__)

def create_app():
    # --- Core app ---
    app = Quart(__name__, static_folder='static', static_url_path='')
    app = cors(app, allow_origin='*')
    RateLimiter(app)  # attaches rate_limit decorator

    # --- Error handlers ---
    init_error_handlers(app)

    def start_scheduler_background():
        loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        # Start loop in background thread
        threading.Thread(target=run_loop, daemon=True).start()
        # Schedule the coroutine
        future = asyncio.run_coroutine_threadsafe(scheduler.start(), loop)
        logger.info("Started Scheduler background thread.")
        return loop, future

    # --- CORS + OPTIONS hooks ---
    @app.before_serving
    async def configure_cors_and_start_grpc():
        @app.after_request
        async def _apply_cors(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

        @app.route('/<path:path>', methods=['OPTIONS'])
        @app.route('/', methods=['OPTIONS'])
        async def _options(path=None):
            return '', 204

        # start gRPC stream in background
        loop = asyncio.new_event_loop()
        threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_forever()), daemon=True).start()
        app.background_task = asyncio.run_coroutine_threadsafe(grpc_client.grpc_stream(), loop)
        logger.info("Started gRPC background stream.")
        loop, future = start_scheduler_background()



    @app.after_serving
    async def shutdown_grpc():
        if hasattr(app, 'background_task'):
            app.background_task.cancel()
            await app.background_task
        grpc_client.stop()  # you can wrap loop.stop()/thread.join() inside grpc_client
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

    return app
