from enum import Enum, unique


# === Message types ===
@unique
class MessageType(str, Enum):
    CAN_PROCEED = "can_proceed"
    PROMPT = "prompt"
    ANSWER = "answer"
    FUNCTION = "function"
    QUESTION = "question"
    NOTIFICATION = "notification"
    INFO = "info"


# === Workflow & processing stacks ===
@unique
class StackKey(str, Enum):
    PROCESSORS = "PROCESSORS"
    ENTITY = "ENTITY"
    WORKFLOW = "WORKFLOW"
    EXTERNAL_SOURCES_PULL_BASED_RAW_DATA = "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA"
    WEB_SCRAPING_PULL_BASED_RAW_DATA = "WEB_SCRAPING_PULL_BASED_RAW_DATA"
    TRANSACTIONAL_PULL_BASED_RAW_DATA = "TRANSACTIONAL_PULL_BASED_RAW_DATA"
    API_REQUEST = "API_REQUEST"
    SCHEDULED = "SCHEDULED"
    APP_BUILDING = "app_building_stack"
    DATA_INGESTION = "data_ingestion_stack"
    SCHEDULER = "scheduler_stack"
    FILE_UPLOAD = "file_upload_stack"
    FORM_SUBMISSION = "form_submission_stack"


# === Default prompts ===
EMPTY_PROMPT = "Thank you!"


# === API endpoints ===
@unique
class ApiV1Endpoint(str, Enum):
    CONNECTIONS = "api/v1/connections"
    CYODA = "api/v1/cyoda"
    WORKFLOWS = "api/v1/workflows"
    RANDOM = "api/v1/random"
    PROCESSOR_REMOTE_ADDRESS_PATH = "platform-processing/pm-cluster-stats-full.do"
    PROCESSOR_ENTITY_EVENTS_PATH = "platform-processing/transactions/view/entity-state-machine?node={processor_node_address}&type={entity_class}&id={entity_id}"


# === Agents & modes ===
@unique
class AgentType(str, Enum):
    DEEPSEEK_CHAT = "deepseek-chat"
    REQUIREMENT_AGENT = "requirement_agent"
    EDITING_AGENT = "editing_agent"
    APP_BUILDER_MODE = "app_builder"
    DEPLOY_STATUS = "deploy_status"


# === Finite State Machine targets ===
@unique
class FsmTarget(str, Enum):
    CYODA = "cyoda"
    LOCAL = "local"


# === Java class references ===
@unique
class JavaClasses(str, Enum):
    EDGE_MESSAGE = "net.cyoda.saas.message.model.EdgeMessage"
    TREE_NODE_ENTITY = "com.cyoda.tdb.model.treenode.TreeNodeEntity"


# === Transition keys ===
@unique
class TransitionKey(str, Enum):
    DELETE = "delete"
    UPDATE = "update_transition"
    PROCESS_USER_INPUT = "submit_answer"
    MANUAL_APPROVE = "manual_approve"
    MANUAL_RETRY = "retry"
    LOCKED_CHAT = "locked_chat"
    UNLOCK_CHAT = "unlock_chat"
    FAIL = "fail"
    ROLLBACK = "rollback"
    BUILD_NEW_APP = "build_new_app"
    DISCUSS_FUNCTIONAL_REQUIREMENTS = "discuss_functional_requirements"
    EDIT_FUNCTIONAL_REQUIREMENTS = "edit_functional_requirements"
    PROTOTYPE_DISCUSSION_REQUESTED = "prototype_discussion_requested"
    RESUME_MIGRATION = "resume_migration"
    RESUME_PROTOTYPE_CYODA_WORKFLOW = "resume_prototype_cyoda_workflow"
    RESUME_GEN_PROTOTYPE_CYODA_WORKFLOW_JSON = "resume_gen_prototype_cyoda_workflow_json"
    RESUME_GEN_ENTITIES = "resume_gen_entities"
    RESUME_POST_APP_BUILD_STEPS = "resume_post_app_build_steps"

# === Model names ===
@unique
class ModelName(str, Enum):
    QUESTIONS_QUEUE = "questions_queue"
    CHAT_BUSINESS_ENTITY = "chat_business_entity"
    CHAT_MEMORY = "chat_memory"
    FLOW_EDGE_MESSAGE = "flow_edge_message"
    AI_MEMORY_EDGE_MESSAGE = "ai_memory_edge_message"
    EDGE_MESSAGE_STORE = "edge_message_store"
    CHAT_ENTITY = "chat_entity"
    AGENTIC_FLOW_ENTITY = "agentic_flow_entity"
    GEN_APP_ENTITY_PYTHON = "build_general_application_python"
    GEN_APP_ENTITY_JAVA = "build_general_application_java"
    CYODA_ENV_DEPLOYMENT_CHAT = "cyoda_env_deploy_chat"
    GENERATING_GEN_APP_WORKFLOW_JAVA = "generating_gen_app_workflow_java"
    GENERATING_GEN_APP_WORKFLOW_PYTHON = "generating_gen_app_workflow_python"
    SCHEDULER_ENTITY = "scheduler_entity"
    TRANSFER_CHATS_ENTITY = "transfer_chats_entity"
    ADD_NEW_FEATURE = "edit_existing_app_design_additional_feature"
    ADD_NEW_ENTITY_PYTHON = "add_new_entity_for_existing_app_python"
    ADD_NEW_WORKFLOW_PYTHON = "add_new_workflow_python"
    EDIT_API_EXISTING_APP_PYTHON = "edit_api_existing_app_python"
    EDIT_EXISTING_WORKFLOW_PYTHON = "edit_existing_workflow_python"
    EDIT_EXISTING_PROCESSORS_PYTHON = "edit_existing_processors_python"
    INIT_SETUP_WORKFLOW_PYTHON = "init_setup_workflow_python"
    INIT_SETUP_WORKFLOW_JAVA = "init_setup_workflow_java"
    ADD_NEW_ENTITY_JAVA = "add_new_entity_for_existing_app_java"
    ADD_NEW_WORKFLOW_JAVA = "add_new_workflow_java"
    EDIT_API_EXISTING_APP_JAVA = "edit_api_existing_app_java"
    EDIT_EXISTING_WORKFLOW_JAVA = "edit_existing_workflow_java"
    EDIT_EXISTING_PROCESSORS_JAVA = "edit_existing_processors_java"

# === Deployment flows ===
@unique
class DeploymentFlow(str, Enum):
    DEPLOY_CYODA_ENV = "deploy_cyoda_env"
    BUILD_USER_APP = "build_user_application"
    DEPLOY_USER_APPLICATION = "deploy_user_application"


# === Error codes ===
@unique
class AiErrorCodes(str, Enum):
    WRONG_GENERATED_CONTENT = "wrong_generated_content"


# === Guidelines data types ===
@unique
class GetCyodaGuidelinesData(str, Enum):
    GENERATE_WORKFLOW = "generate_workflow"
    GENERATE_PROCESSORS = "generate_processors"
    CONFIGURE_TRINO = "configure_trino"
    GENERATE_ENTITY = "generate_entity"
    START_APP = "start_app"
    CYODA_BEST_PRACTICE = "cyoda_best_practice"


# === Notification templates ===
@unique
class Notifications(str, Enum):
    PUSH_NOTIFICATION = "push_notification"
    APPROVE = (
        "I'm happy with the current result. Let's proceed to the next "
        "iteration—please call finish_discussion to conclude this discussion."
    )
    OPERATION_FAILED = (
        "⚠️ Sorry, this action is not available right now. Please try again or wait for new questions ⚠️"
    )
    OPERATION_NOT_SUPPORTED = "⚠️ Sorry, this operation is not supported ⚠️"
    EXIT_LOOP_FUNCTION_NAME = "finish_discussion"
    PROCEED_TO_THE_NEXT_STEP = "Proceeded to the next step. You will see a notification soon!"
    DESIGN_PLEASE_WAIT = "Sorry, I haven't come up with an answer to the previous question yet. Please give me one more minute to think everything over 🤔⏳ Response taking too long? Please feel free to continue a new chat with your branch name or let us know at [Discord](https://discord.gg/95rdAyBZr2)"
    FAILED_WORKFLOW = (
        "⚠️ We ran into an error while processing the workflow **{technical_id}**. "
        "Our team will review the issue shortly.\n\n"
        "In the meantime, you can continue working on your branch or application in a new chat. \n\n"
        "Please start a new conversation and include your branch name along with what you'd like to do — \n\n"
        "We apologize for the inconvenience and appreciate your understanding."
        "Please let us know at [Discord](https://discord.gg/95rdAyBZr2). We're here to help!"
    )

    APPROVAL_NOTIFICATION = (
        "Give a thumbs up 👍 if you'd like to proceed to the next question. "
        "If you'd like to discuss further, let's chat 💬"
    )
    APPROVE_WARNING = (
        "Sorry, you cannot skip this question. If you're unsure about anything, "
        "please refer to the example answers for guidance."
    )
    APPROVE_INSTRUCTION_MESSAGE = "*Hit ✅ to approve or escape the 🔁 loop. 🙈 No turning back!*"


@unique
class ApproveAnswer(str, Enum):
    FINE_BY_ME = "Fine by me 👌"
    HAPPY_WITH_THAT = "Happy with that 😎"
    DONE_NEXT = "Done, next ➡️"
    SOLID_MOVE_ON = "Solid. move on ✅"
    SORTED = "Sorted👌"
    MOVE_ON = "Cool with the result 😎 Let’s move."


# === Push changes template ===
PUSHED_CHANGES_NOTIFICATION = """
🎉 **Changes have been pushed!** 🎉

I’ve submitted changes to the file: `{file_name}` in your branch. You can check it out by either:

1. **Pulling or fetching** the changes from the remote repository, or  
2. **Opening the link** to view the file directly: [View changes here]({repository_url}/tree/{chat_id}/{file_name}) 🔗

I will proceed with my work... I'll let you know when we can discuss the changes and make necessary updates.
"""


# === File-specific notifications ===
FILES_NOTIFICATIONS = {
    "code": {
        "text": "🖌️💬",
        "file_name": "entity/{entity_name}/connections/connections.py",
    },
    "doc": {
        "text": (
            "😊 Could you please provide more details for the connection "
            "documentation? Please provide raw data for each endpoint if the "
            "final entity structure is different."
        ),
        "file_name": "entity/{entity_name}/connections/connections_input.md",
    },
    "entity": {
        "text": (
            "😊 Could you please provide an example of the entity JSON? "
            "It will help us map the raw data to the entity."
        ),
        "file_name": "entity/{entity_name}/{entity_name}.json",
    },
}

BRANCH_READY_NOTIFICATION = "🎉 **Your branch `{git_branch}` is live!**\nI’ve added a GitHub branch in our public repository where I’ll be posting updates.\nYou can check it out now or come back to it anytime:\n🔗 [Cyoda GitHub](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch}) 👀 \n"

# === Miscellaneous design strings ===
LOGIC_CODE_DESIGN_STR = "Additional logic code design"
WORKFLOW_CODE_DESIGN_STR = "Workflow processors code design"
WORKFLOW_DESIGN_STR = "Workflow design"
ENTITIES_DESIGN_STR = "Entities design"
APPLICATION_DESIGN_STR = "Application design"
GATHERING_REQUIREMENTS_STR = "Gathering requirements"
QUESTION_OR_VALIDATE = (
    "Could you please help me review my output and approve it if you are happy with the result 😸"
)
GIT_BRANCH_PARAM="git_branch"

# === Numeric limits ===
RATE_LIMIT = 300
SCHEDULER_CHECK_INTERVAL = 60
CYODA_PAGE_SIZE = 100
MAX_SCHEDULER_POLLS = 120
MAX_GUEST_CHAT_MESSAGES = 300
MAX_CHAT_MESSAGES = 1500
SCHEDULER_STATUS_WAITING = "waiting"
UI_FUNCTION_PREFIX = "ui_function"

CYODA_WELCOME_MESSAGE = """\
Hi! I’m Cyoda 🧚 and I’ll be guiding you on your journey!

We’re currently in alpha, so you might run into a few bumps. No worries — if you need help, just reach out on [Discord](https://discord.gg/95rdAyBZr2)!

Cyoda is entity-based — each entity follows its own workflow.  
I'm also workflow-driven! To track progress, open the *Entities Data* window.

I’ll be kicking off new workflows for you — you’ll see them appear in that window. Once a flow reaches the **locked** state, it’s done and dusted ✅.

Curious about what I can do? Just ask: **"Show me your agent tools."**

Have fun exploring!
"""