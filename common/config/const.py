from enum import Enum

CAN_PROCEED = "can_proceed"
PROMPT = "prompt"
ANSWER = "answer"
FUNCTION = "function"
QUESTION = "question"
NOTIFICATION = "notification"
INFO = "info"
PROCESSORS_STACK = "PROCESSORS"
ENTITY_STACK = "ENTITY"
WORKFLOW_STACK = "WORKFLOW"
EXTERNAL_SOURCES_PULL_BASED_RAW_DATA = "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA"
WEB_SCRAPING_PULL_BASED_RAW_DATA = "WEB_SCRAPING_PULL_BASED_RAW_DATA"
TRANSACTIONAL_PULL_BASED_RAW_DATA = "TRANSACTIONAL_PULL_BASED_RAW_DATA"
API_REQUEST_STACK = "API_REQUEST"
SCHEDULED_STACK = "SCHEDULED"
EMPTY_PROMPT = "Thank you!"

API_V_CONNECTIONS_ = "api/v1/connections"
API_V_CYODA_ = "api/v1/cyoda"
API_V_WORKFLOWS_ = "api/v1/workflows"
API_V_RANDOM_ = "api/v1/random"
DEEPSEEK_CHAT = "deepseek-chat"
REQUIREMENT_AGENT = "requirement_agent"
EDITING_AGENT = "editing_agent"
APP_BUILDER_MODE = "app_builder"
DEPLOY_STATUS = "deploy_status"
FSM_CYODA = "cyoda"
FSM_LOCAL = "local"
EDGE_MESSAGE_CLASS = "net.cyoda.saas.message.model.EdgeMessage"
TREE_NODE_ENTITY_CLASS = "com.cyoda.tdb.model.treenode.TreeNodeEntity"
UPDATE_TRANSITION = "update_transition"
QUESTIONS_QUEUE_MODEL_NAME = "questions_queue"
MEMORY_MODEL_NAME = "chat_memory"
FLOW_EDGE_MESSAGE_MODEL_NAME = "flow_edge_message"
AI_MEMORY_EDGE_MESSAGE_MODEL_NAME = "ai_memory_edge_message"
EDGE_MESSAGE_STORE_MODEL_NAME = "edge_message_store"
CHAT_MODEL_NAME = "chat_entity"
AGENTIC_FLOW_ENTITY = "agentic_flow_entity"
GEN_APP_ENTITY = "build_general_application_python"
GENERATING_GEN_APP_WORKFLOW = "generating_gen_app_workflow"
SCHEDULER_ENTITY = "scheduler_entity"
ADD_NEW_FEATURE = "edit_existing_app_design_additional_feature"
ADD_NEW_ENTITY = "add_new_entity_for_existing_app"
ADD_NEW_WORKFLOW = "add_new_workflow"
EDIT_API_EXISTING_APP = "edit_api_existing_app"
EDIT_EXISTING_WORKFLOW = "edit_existing_workflow"
EDIT_EXISTING_PROCESSORS = "edit_existing_processors"
TRANSFER_CHATS_ENTITY = "transfer_chats_entity"
DEPLOY_CYODA_ENV_FLOW = "deploy_cyoda_env"
DEPLOY_USER_APP_FLOW = "deploy_user_application"
GIT_BRANCH_PARAM = "git_branch"
LOCKED_CHAT = "locked_chat"
FINISH_WORKFLOW = "finish_workflow"

PUSH_NOTIFICATION = "push_notification"
APPROVE = "I'm happy with the current result. Let's proceed to the next iteration—please call set_additional_question_flag(False) to conclude this discussion."
RATE_LIMIT = 300
SCHEDULER_CHECK_INTERVAL=60
CYODA_PAGE_SIZE=100
MAX_SCHEDULER_POLLS=120
PROCESS_USER_INPUT_TRANSITION = "process_user_input"
MANUAL_RETRY_TRANSITION = "retry"
UNLOCK_CHAT_TRANSITION = "unlock_chat"
FAIL_TRANSITION = "fail"
ROLLBACK_TRANSITION = "rollback"
MAX_GUEST_CHAT_MESSAGES = 300
MAX_CHAT_MESSAGES = 1500
FAILED_WORKFLOW_NOTIFICATION = "⚠️ We encountered an error while processing the workflow **{technical_id}**. Our team will look into it shortly.\n\nTo continue, please start a new chat.\n\nWe’re sorry for the inconvenience and appreciate your understanding."

class GetCyodaGuidelinesData(str, Enum):
    GENERATE_WORKFLOW = "generate_workflow"
    GENERATE_PROCESSORS = "generate_processors"
    CONFIGURE_TRINO = "configure_trino"
    GENERATE_ENTITY = "generate_entity"
    START_APP = "start_app"
    CYODA_BEST_PRACTICE = "cyoda_best_practice"

class AiErrorCodes(str, Enum):
    WRONG_GENERATED_CONTENT = "wrong_generated_content"



PUSHED_CHANGES_NOTIFICATION = """

🎉 **Changes have been pushed!** 🎉

I’ve submitted changes to the file: `{file_name}` in your branch. You can check it out by either:

1. **Pulling or fetching** the changes from the remote repository, or  
2. **Opening the link** to view the file directly: [View changes here]( {repository_url}/tree/{chat_id}/{file_name}) 🔗 (this will open in a new tab).

Feel free to **modify the file** as necessary

I will proceed with my work... I'll let you know when we can discuss the changes and make necessary update.
"""
APP_BUILDING_STACK_KEY = "app_building_stack"

DATA_INGESTION_STACK_KEY = "data_ingestion_stack"

ENTITY_STACK_KEY = "entity_stack"

WORKFLOW_STACK_KEY = "workflow_stack"

PROCESSORS_STACK_KEY = "processors_stack"

SCHEDULER_STACK_KEY = "scheduler_stack"

FORM_SUBMISSION_STACK_KEY = "form_submission_stack"

FILE_UPLOAD_STACK_KEY = "file_upload_stack"

API_REQUEST_STACK_KEY = "api_request_stack"
APPROVAL_NOTIFICATION = "Give a thumbs up 👍 if you'd like to proceed to the next question. If you'd like to discuss further, let's chat 💬"
DESIGN_PLEASE_WAIT = "Please give me a moment to think everything over 🤔⏳"
APPROVE_WARNING = "Sorry, you cannot skip this question. If you're unsure about anything, please refer to the example answers for guidance. If you need further help, just let us know! 😊 Apologies for the inconvenience!🙌"
OPERATION_FAILED_WARNING = "⚠️ Sorry, this action is not available right now. Please try again or wait for new questions ⚠️"
OPERATION_NOT_SUPPORTED_WARNING = "⚠️ Sorry, this operation is not supported ⚠️"
DESIGN_IN_PROGRESS_WARNING = "Sorry, you cannot submit answer right now. We are working on Cyoda workflow. Could you please wait a little or start a new chat"
DESIGN_IN_PROGRESS_ROLLBACK_WARNING = "Sorry, you cannot rollback right now. We are working on Cyoda design. Could you please wait a little"
ADDITIONAL_QUESTION_ROLLBACK_WARNING = "Sorry, this is an additional question, you cannot rollback to it. Please rollback to the earlier question"
BRANCH_READY_NOTIFICATION = """🎉 **Your branch is ready!** Please update the project and check it out when you get a chance. 😊

To get started:

1. **Clone the repository** using the following command:  
   `git clone https://github.com/Cyoda-platform/quart-client-template/` 🚀

2. **Checkout your branch** using:  
   `git checkout {chat_id}` 🔄

You can access your branch directly on GitHub here: [Cyoda Platform GitHub](https://github.com/Cyoda-platform/quart-client-template/tree/{chat_id}) 😄

This repository is a **starter template** for your app and has two main modules:

- **Common Module**: This is all about integration with Cyoda! You don’t need to edit it unless you want to – it’s all done for you! 🎉  
- **Entity Module**: This is where your business logic and custom files will go. We'll add your files here, and you can track your progress. 📈 Feel free to **add or edit** anything in the Entity module. I’ll be pulling changes now and then, so just push your updates to let me know! 🚀

You can ask **questions in the chat** or in your project files anytime. When I make changes, I’ll let you know, and you can simply **pull** to sync with me! 🔄💬
"""

FILES_NOTIFICATIONS = {
    "code": {
        "text": "🖌️💬",
        "file_name": "entity/{entity_name}/connections/connections.py"},
    "doc": {
        "text": "😊 Could you please provide more details for the connection documentation? It would be super helpful! Please provide raw data for each endpoint if the final entity structure is different. You can paste all your data right here. Thanks so much!",
        "file_name": "entity/{entity_name}/connections/connections_input.md"},
    "entity": {
        "text": "😊 Could you please provide an example of the entity JSON? It will help us map the raw data to the entity or save the raw data as is. You can paste all your data right here. Thanks a lot!",
        "file_name": "entity/{entity_name}/{entity_name}.json"}
}

LOGIC_CODE_DESIGN_STR = "Additional logic code design"

WORKFLOW_CODE_DESIGN_STR = "Workflow processors code design"

WORKFLOW_DESIGN_STR = "Workflow design"

ENTITIES_DESIGN_STR = "Entities design"

APPLICATION_DESIGN_STR = "Application design"

GATHERING_REQUIREMENTS_STR = "Gathering requirements"

QUESTION_OR_VALIDATE = "Could you please help me review my output and approve it you are happy with the result 😸"
