import os
import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file automatically from the current working directory

class EnvError(Exception):
    pass


def _get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Fetch an env var, enforcing ‘required’ if needed."""
    val = os.getenv(key, default)
    if required and val is None:
        raise EnvError(f"Missing required environment variable: {key}")
    return val


def _get_b64_env(key: str, required: bool = False) -> str:
    """Fetch a base64-encoded env var and decode it."""
    raw = _get_env(key, required=required)
    if raw is None:
        raise EnvError(f"Missing required environment variable: {key}")
    try:
        return base64.b64decode(raw).decode("utf-8")
    except Exception as e:
        raise EnvError(f"Could not decode {key} from base64: {e}")


def _get_int_env(key: str, default: Optional[int] = None, required: bool = False) -> int:
    """Fetch an integer env var, with optional default or required enforcement."""
    val = _get_env(key, default=None if default is None else str(default), required=required)
    if val is None:
        raise EnvError(f"Missing required environment variable: {key}")
    try:
        return int(val)
    except ValueError:
        raise EnvError(f"Invalid integer for {key}: {val!r}")


@dataclass(frozen=True)
class Config:
    # Required strings
    CYODA_HOST:                   str = field(default_factory=lambda: _get_env("CYODA_HOST", required=True))
    DEEPSEEK_API_KEY:            str = field(default_factory=lambda: _get_env("DEEPSEEK_API_KEY", required=True))
    API_KEY:                     str = field(default_factory=lambda: _get_b64_env("CYODA_API_KEY", required=True))
    API_SECRET:                  str = field(default_factory=lambda: _get_b64_env("CYODA_API_SECRET", required=True))
    CLONE_REPO:                  str = field(default_factory=lambda: _get_env("CLONE_REPO", required=True))
    MOCK_AI:                     str = field(default_factory=lambda: _get_env("MOCK_AI", required=True))
    PROJECT_DIR:                 str = field(default_factory=lambda: _get_env("PROJECT_DIR", required=True))
    REPOSITORY_URL:              str = field(default_factory=lambda: _get_env("REPOSITORY_URL", required=True))
    CYODA_AI_API:                str = field(default_factory=lambda: _get_env("CYODA_AI_API", required=True))
    WORKFLOW_AI_API:             str = field(default_factory=lambda: _get_env("WORKFLOW_AI_API", required=True))
    CONNECTION_AI_API:           str = field(default_factory=lambda: _get_env("CONNECTION_AI_API", required=True))
    RANDOM_AI_API:               str = field(default_factory=lambda: _get_env("RANDOM_AI_API", required=True))
    NUM_MOCK_ARR_ITEMS:          int = field(default_factory=lambda: _get_int_env("NUM_MOCK_ARR_ITEMS", required=True))
    RAW_REPOSITORY_URL:          str = field(default_factory=lambda: _get_env("RAW_REPOSITORY_URL", required=True))
    DATA_REPOSITORY_URL:         str = field(default_factory=lambda: _get_env("DATA_REPOSITORY_URL", required=True))
    GOOGLE_SEARCH_KEY:           str = field(default_factory=lambda: _get_env("GOOGLE_SEARCH_KEY", required=True))
    GOOGLE_SEARCH_CX:            str = field(default_factory=lambda: _get_env("GOOGLE_SEARCH_CX", required=True))
    AUTH_SECRET_KEY:             str = field(default_factory=lambda: _get_env("AUTH_SECRET_KEY", required=True))
    CLOUD_MANAGER_HOST:          str = field(default_factory=lambda: _get_env("CLOUD_MANAGER_HOST", required=True))
    CLIENT_HOST:                 str = field(default_factory=lambda: _get_env("CLIENT_HOST", required=True))

    # Optional strings with defaults
    CYODA_AI_URL:                str = field(init=False)
    CYODA_API_URL:               str = field(init=False)
    GRPC_ADDRESS:                str = field(init=False)
    API_PREFIX:                  str = field(default_factory=lambda: _get_env("API_PREFIX", default="/api/v1"))
    ENTITY_VERSION:              str = field(default_factory=lambda: _get_env("ENTITY_VERSION", default="1001"))
    CHAT_ID:                     Optional[str] = field(default_factory=lambda: _get_env("CHAT_ID"))
    GRPC_PROCESSOR_TAG:          str = field(default_factory=lambda: _get_env("GRPC_PROCESSOR_TAG", default="ai_assistant"))
    MAX_ITERATION:               int = field(default_factory=lambda: _get_int_env("MAX_ITERATION", default=30))
    MAX_AI_AGENT_ITERATIONS:     int = field(default_factory=lambda: _get_int_env("MAX_AI_AGENT_ITERATIONS", default=20))
    MAX_GUEST_CHATS:             int = field(default_factory=lambda: _get_int_env("MAX_GUEST_CHATS", default=2))
    CHECK_DEPLOY_INTERVAL:       int = field(default_factory=lambda: _get_int_env("CHECK_DEPLOY_INTERVAL", default=30))
    REPOSITORY_NAME:             str = field(init=False)
    CHAT_REPOSITORY:             str = field(default_factory=lambda: _get_env("CHAT_REPOSITORY", default="local"))
    ENABLE_AUTH:                 bool = field(default_factory=lambda: _get_env("ENABLE_AUTH", default="true").lower() == "true")
    MAX_TEXT_SIZE:               int = field(default=50 * 1024)
    MAX_FILE_SIZE:               int = field(default=500 * 1024)
    USER_FILES_DIR_NAME:         str = field(default="entity/user_files")
    DEPLOY_CYODA_ENV:            str = field(init=False)
    DEPLOY_USER_APP:             str = field(init=False)
    BUILD_USER_APP:              str = field(init=False)
    DEPLOY_CYODA_ENV_STATUS:     str = field(init=False)
    DEPLOY_USER_APP_STATUS:      str = field(init=False)
    MAX_IPS_PER_DEVICE_BEFORE_BLOCK: int = field(default_factory=lambda: _get_int_env("MAX_IPS_PER_DEVICE_BEFORE_BLOCK", default=300))
    MAX_IPS_PER_DEVICE_BEFORE_ALARM: int = field(default_factory=lambda: _get_int_env("MAX_IPS_PER_DEVICE_BEFORE_ALARM", default=100))
    MAX_SESSIONS_PER_IP:         int = field(default_factory=lambda: _get_int_env("MAX_SESSIONS_PER_IP", default=100))
    GENERAL_MEMORY_TAG:          str = field(default="general_memory_tag")
    CYODA_ENTITY_TYPE_TREE:      str = field(default="TREE")
    CYODA_ENTITY_TYPE_EDGE_MESSAGE: str = field(default="EDGE_MESSAGE")
    GUEST_TOKEN_LIMIT:           int = field(default_factory=lambda: _get_int_env("GUEST_TOKEN_LIMIT", default=10))
    CLIENT_QUART_TEMPLATE_REPOSITORY_URL: str = field(default_factory=lambda: _get_env(
        "CLIENT_REPOSITORY_URL",
        default="https://github.com/Cyoda-platform/quart-client-template.git"
    ))

    def __post_init__(self):
        object.__setattr__(self, "CYODA_AI_URL",    _get_env("CYODA_AI_URL",    default=f"https://{self.CYODA_HOST}/ai"))
        object.__setattr__(self, "CYODA_API_URL",   _get_env("CYODA_API_URL",   default=f"https://{self.CYODA_HOST}/api"))
        object.__setattr__(self, "GRPC_ADDRESS",    _get_env("GRPC_ADDRESS",    default=f"grpc-{self.CYODA_HOST}"))
        object.__setattr__(self, "REPOSITORY_NAME", self.REPOSITORY_URL.rstrip("/").split("/")[-1].removesuffix(".git"))
        cm = self.CLOUD_MANAGER_HOST
        object.__setattr__(self, "DEPLOY_CYODA_ENV",        _get_env("DEPLOY_CYODA_ENV",        default=f"https://{cm}/deploy/cyoda-env"))
        object.__setattr__(self, "DEPLOY_USER_APP",         _get_env("DEPLOY_USER_APP",         default=f"https://{cm}/deploy/user-app"))
        object.__setattr__(self, "BUILD_USER_APP",          _get_env("BUILD_USER_APP",          default=f"https://{cm}/build/user-app"))
        object.__setattr__(self, "DEPLOY_CYODA_ENV_STATUS", _get_env("DEPLOY_CYODA_ENV_STATUS", default=f"https://{cm}/deploy/cyoda-env/status"))
        object.__setattr__(self, "DEPLOY_USER_APP_STATUS",  _get_env("DEPLOYUSER_APP_STATUS",   default=f"https://{cm}/deploy/user-app/status"))


    class ScheduledAction(str, Enum):
        SCHEDULE_ENTITIES_FLOW    = "schedule_entities_flow"
        SCHEDULE_CYODA_ENV_DEPLOY = "schedule_cyoda_env_deploy"
        SCHEDULE_USER_APP_DEPLOY  = "schedule_user_app_deploy"
        SCHEDULE_USER_APP_BUILD   = "schedule_user_app_build"


    ACTION_URL_MAP = {
        ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: DEPLOY_CYODA_ENV,
        ScheduledAction.SCHEDULE_USER_APP_BUILD:  BUILD_USER_APP,
        ScheduledAction.SCHEDULE_USER_APP_DEPLOY: DEPLOY_USER_APP,
    }

    ACTION_SUCCESS_TRANSITIONS = {
        ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: "finish_deployment_success",
        ScheduledAction.SCHEDULE_USER_APP_DEPLOY:  "finish_deployment_success",
        ScheduledAction.SCHEDULE_USER_APP_BUILD:   "finish_build_success",
    }

    ACTION_FAILURE_TRANSITIONS = {
        ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY: "finish_deployment_failure",
        ScheduledAction.SCHEDULE_USER_APP_DEPLOY:  "finish_deployment_failure",
        ScheduledAction.SCHEDULE_USER_APP_BUILD:   "finish_deployment_failure",
    }

config = Config()