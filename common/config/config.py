import os
import base64
from enum import Enum
from dotenv import load_dotenv


class EnvError(Exception):
    pass


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    """Fetch an env var, enforcing ‘required’ if needed."""
    val = os.getenv(key, default)
    if required and val is None:
        raise EnvError(f"Missing required environment variable: {key}")
    return val  # always a str if required, else may be None


def _get_b64_env(key: str, required: bool = False) -> str:
    """Fetch a base64-encoded env var and decode it."""
    raw = _get_env(key, required=required)
    if raw is None:
        raise EnvError(f"Missing required environment variable: {key}")
    try:
        return base64.b64decode(raw).decode("utf-8")
    except Exception as e:
        raise EnvError(f"Could not decode {key} from base64: {e}")


def _get_int_env(key: str, default: int | None = None, required: bool = False) -> int:
    """Fetch an integer env var, with optional default or required enforcement."""
    default_str = None if default is None else str(default)
    val = _get_env(key, default=default_str, required=required)
    if val is None:
        raise EnvError(f"Missing required environment variable: {key}")
    try:
        return int(val)
    except ValueError:
        raise EnvError(f"Invalid integer for {key}: {val!r}")


class Config:
    def __init__(self) -> None:
        # Load .env from cwd
        load_dotenv()

        # — required strings —
        self.CYODA_HOST = _get_env("CYODA_HOST", required=True)
        self.DEEPSEEK_API_KEY = _get_env("DEEPSEEK_API_KEY", required=True)
        self.API_KEY = _get_b64_env("CYODA_API_KEY", required=True)
        self.API_SECRET = _get_b64_env("CYODA_API_SECRET", required=True)
        self.CLONE_REPO = _get_env("CLONE_REPO", required=True)
        self.MOCK_AI = _get_env("MOCK_AI", required=True)
        self.PROJECT_DIR = _get_env("PROJECT_DIR", required=True)
        self.REPOSITORY_URL = _get_env("REPOSITORY_URL", required=True)
        self.CYODA_AI_API = _get_env("CYODA_AI_API", required=True)
        self.WORKFLOW_AI_API = _get_env("WORKFLOW_AI_API", required=True)
        self.CONNECTION_AI_API = _get_env("CONNECTION_AI_API", required=True)
        self.RANDOM_AI_API = _get_env("RANDOM_AI_API", required=True)
        self.NUM_MOCK_ARR_ITEMS = _get_int_env("NUM_MOCK_ARR_ITEMS", required=True)
        self.RAW_REPOSITORY_URL = _get_env("RAW_REPOSITORY_URL", required=True)
        self.PYTHON_REPOSITORY_NAME = _get_env("PYTHON_REPOSITORY_NAME", required=True)
        self.JAVA_REPOSITORY_NAME = _get_env("JAVA_REPOSITORY_NAME", required=True)
        self.DATA_REPOSITORY_URL = _get_env("DATA_REPOSITORY_URL", required=True)
        self.GOOGLE_SEARCH_KEY = _get_env("GOOGLE_SEARCH_KEY", required=True)
        self.GOOGLE_SEARCH_CX = _get_env("GOOGLE_SEARCH_CX", required=True)
        self.AUTH_SECRET_KEY = _get_env("AUTH_SECRET_KEY", required=True)
        self.CLOUD_MANAGER_HOST = _get_env("CLOUD_MANAGER_HOST", required=True)
        self.CLIENT_HOST = _get_env("CLIENT_HOST", required=True)

        # — optional strings with defaults —
        self.API_PREFIX = _get_env("API_PREFIX", default="/api/v1")
        self.ENTITY_VERSION = _get_env("ENTITY_VERSION", default="1001")
        self.CHAT_ID = _get_env("CHAT_ID", default=None)
        self.GRPC_PROCESSOR_TAG = _get_env("GRPC_PROCESSOR_TAG", default="ai_assistant")
        self.CHAT_REPOSITORY = _get_env("CHAT_REPOSITORY", default="local")

        # — optional ints with defaults —
        self.MAX_ITERATION = _get_int_env("MAX_ITERATION", default=30)
        self.MAX_AI_AGENT_ITERATIONS = _get_int_env("MAX_AI_AGENT_ITERATIONS", default=4)
        self.MAX_AI_AGENT_VALIDATION_RETRIES = _get_int_env("MAX_AI_AGENT_ITERATIONS", default=4)
        self.MAX_GUEST_CHATS = _get_int_env("MAX_GUEST_CHATS", default=2)
        self.CHECK_DEPLOY_INTERVAL = _get_int_env("CHECK_DEPLOY_INTERVAL", default=30)
        self.MAX_IPS_PER_DEVICE_BEFORE_BLOCK = _get_int_env(
            "MAX_IPS_PER_DEVICE_BEFORE_BLOCK", default=300
        )
        self.MAX_IPS_PER_DEVICE_BEFORE_ALARM = _get_int_env(
            "MAX_IPS_PER_DEVICE_BEFORE_ALARM", default=100
        )
        self.MAX_SESSIONS_PER_IP = _get_int_env("MAX_SESSIONS_PER_IP", default=100)
        self.GUEST_TOKEN_LIMIT = _get_int_env("GUEST_TOKEN_LIMIT", default=10)

        # — optional bool —
        self.ENABLE_AUTH = _get_env("ENABLE_AUTH", default="true").lower() == "true"

        # — hard-coded constants —
        self.MAX_TEXT_SIZE = 50 * 1024
        self.MAX_FILE_SIZE = 500 * 1024
        self.USER_FILES_DIR_NAME = "entity/user_files"
        self.GENERAL_MEMORY_TAG = "general_memory_tag"
        self.CYODA_ENTITY_TYPE_TREE = "TREE"
        self.CYODA_ENTITY_TYPE_EDGE_MESSAGE = "EDGE_MESSAGE"
        self.UI_LABELS_CONFIG_FILE_NAME = "labels_config.json"
        self.CONFIG_URL = _get_env(
            "CONFIG_URL",
            default="https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/main/ai-assistant/config"
        )

        # — derived fields —
        self.CYODA_AI_URL = _get_env("CYODA_AI_URL", default=f"https://{self.CYODA_HOST}/ai")
        self.CYODA_API_URL = _get_env("CYODA_API_URL", default=f"https://{self.CYODA_HOST}/api")
        self.GRPC_ADDRESS = _get_env("GRPC_ADDRESS", default=f"grpc-{self.CYODA_HOST}")

        cm = self.CLOUD_MANAGER_HOST
        self.DEPLOY_CYODA_ENV = _get_env("DEPLOY_CYODA_ENV", default=f"https://{cm}/deploy/cyoda-env")
        self.DEPLOY_USER_APP = _get_env("DEPLOY_USER_APP", default=f"https://{cm}/deploy/user-app")
        self.BUILD_USER_APP = _get_env("BUILD_USER_APP", default=f"https://{cm}/build/user-app")
        self.DEPLOY_CYODA_ENV_STATUS = _get_env(
            "DEPLOY_CYODA_ENV_STATUS", default=f"https://{cm}/deploy/cyoda-env/status"
        )
        self.DEPLOY_USER_APP_STATUS = _get_env(
            "DEPLOY_USER_APP_STATUS", default=f"https://{cm}/deploy/user-app/status"
        )

        # — action mappings (instance-level) —
        self.ACTION_URL_MAP = {
            Config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: self.DEPLOY_CYODA_ENV,
            Config.ScheduledAction.SCHEDULE_USER_APP_BUILD: self.BUILD_USER_APP,
            Config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY: self.DEPLOY_USER_APP,
        }
        self.ACTION_SUCCESS_TRANSITIONS = {
            Config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: "finish_deployment_success",
            Config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY: "finish_deployment_success",
            Config.ScheduledAction.SCHEDULE_USER_APP_BUILD: "finish_build_success",
        }
        self.ACTION_FAILURE_TRANSITIONS = {
            Config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: "finish_deployment_failure",
            Config.ScheduledAction.SCHEDULE_USER_APP_DEPLOY: "finish_deployment_failure",
            Config.ScheduledAction.SCHEDULE_USER_APP_BUILD: "finish_build_failure",
        }

    class ScheduledAction(str, Enum):
        SCHEDULE_ENTITIES_FLOW = "schedule_entities_flow"
        SCHEDULE_CYODA_ENV_DEPLOY = "schedule_cyoda_env_deploy"
        SCHEDULE_USER_APP_DEPLOY = "schedule_user_app_deploy"
        SCHEDULE_USER_APP_BUILD = "schedule_user_app_build"


# instantiate once for module-wide use
config = Config()
