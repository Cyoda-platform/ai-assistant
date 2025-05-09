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
    UPDATE = "update_transition"
    PROCESS_USER_INPUT = "process_user_input"
    MANUAL_RETRY = "retry"
    LOCKED_CHAT = "locked_chat"
    UNLOCK_CHAT = "unlock_chat"
    FAIL = "fail"
    ROLLBACK = "rollback"


# === Model names ===
@unique
class ModelName(str, Enum):
    QUESTIONS_QUEUE = "questions_queue"
    CHAT_MEMORY = "chat_memory"
    FLOW_EDGE_MESSAGE = "flow_edge_message"
    AI_MEMORY_EDGE_MESSAGE = "ai_memory_edge_message"
    EDGE_MESSAGE_STORE = "edge_message_store"
    CHAT_ENTITY = "chat_entity"
    AGENTIC_FLOW_ENTITY = "agentic_flow_entity"
    GEN_APP_ENTITY = "build_general_application_python"
    GENERATING_GEN_APP_WORKFLOW = "generating_gen_app_workflow"
    SCHEDULER_ENTITY = "scheduler_entity"
    TRANSFER_CHATS_ENTITY = "transfer_chats_entity"
    ADD_NEW_FEATURE = "edit_existing_app_design_additional_feature"
    ADD_NEW_ENTITY = "add_new_entity_for_existing_app"
    ADD_NEW_WORKFLOW = "add_new_workflow"
    EDIT_API_EXISTING_APP = "edit_api_existing_app"
    EDIT_EXISTING_WORKFLOW = "edit_existing_workflow"
    EDIT_EXISTING_PROCESSORS = "edit_existing_processors"

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
        "iteration—please call set_additional_question_flag(False) to conclude this discussion."
    )
    OPERATION_FAILED = (
        "⚠️ Sorry, this action is not available right now. Please try again or wait for new questions ⚠️"
    )
    OPERATION_NOT_SUPPORTED = "⚠️ Sorry, this operation is not supported ⚠️"
    DESIGN_PLEASE_WAIT = "Please give me a moment to think everything over 🤔⏳"
    FAILED_WORKFLOW = (
        "⚠️ We encountered an error while processing the workflow **{technical_id}**. "
        "Our team will look into it shortly.\n\nTo continue, please start a new chat.\n\n"
        "We’re sorry for the inconvenience and appreciate your understanding."
    )
    APPROVAL_NOTIFICATION = (
        "Give a thumbs up 👍 if you'd like to proceed to the next question. "
        "If you'd like to discuss further, let's chat 💬"
    )
    APPROVE_WARNING = (
        "Sorry, you cannot skip this question. If you're unsure about anything, "
        "please refer to the example answers for guidance."
    )


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

BRANCH_READY_NOTIFICATION = """🎉 **Your branch is ready!** Please update the project and check it out when you get a chance. 😊

To get started:

1. **Clone the repository** using the following command:  
   git clone https://github.com/Cyoda-platform/quart-client-template/ 🚀

2. **Checkout your branch** using:  
   git checkout {chat_id} 🔄

You can access your branch directly on GitHub here: [Cyoda Platform GitHub](https://github.com/Cyoda-platform/quart-client-template/tree/{chat_id}) 😄

This repository is a **starter template** for your app and has two main modules:

- **Common Module**: This is all about integration with Cyoda! You don’t need to edit it unless you want to – it’s all done for you! 🎉  
- **Entity Module**: This is where your business logic and custom files will go. We'll add your files here, and you can track your progress. 📈 Feel free to **add or edit** anything in the Entity module. I’ll be pulling changes now and then, so just push your updates to let me know! 🚀

You can ask **questions in the chat** or in your project files anytime. When I make changes, I’ll let you know, and you can simply **pull** to sync with me! 🔄💬
"""

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
