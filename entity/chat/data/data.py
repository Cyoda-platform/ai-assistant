import copy

from common.config.config import MAX_ITERATION

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
DESIGN_IN_PROGRESS_WARNING = "Sorry, you cannot submit answer right now. We are working on Cyoda design. Could you please wait a little"
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

Happy coding! 😄🎉"""

PUSHED_CHANGES_NOTIFICATION = """

🎉 **Changes have been pushed!** 🎉

I’ve submitted changes to the file: `{file_name}` in your branch. You can check it out by either:

1. **Pulling or fetching** the changes from the remote repository, or  
2. **Opening the link** to view the file directly: [View changes here]( {repository_url}/tree/{chat_id}/{file_name}) 🔗 (this will open in a new tab).

Feel free to **modify the file** as necessary

I will proceed with my work... I'll let you know when we can discuss the changes and make necessary update.
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

APP_BUILDER_FLOW = [
    {GATHERING_REQUIREMENTS_STR: "Let's collect all the necessary details."},
    {
        APPLICATION_DESIGN_STR: "Let's design the application using diagrams and chat. You'll receive a text document with the PRD as the output. Output documents: entity/app_design.json"},
    {ENTITIES_DESIGN_STR: "Let's define the JSON data structure for each entity."},
    {WORKFLOW_DESIGN_STR: "Let's ensure our entity workflow is correctly defined."},
    {WORKFLOW_CODE_DESIGN_STR: "Let's implement the workflow processors."},
    {LOGIC_CODE_DESIGN_STR: "Let's develop any additional business logic."}
]

ENTITY_WORKFLOW = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "class_name": {
            "type": "string",
            "enum": ["com.cyoda.tdb.model.treenode.TreeNodeEntity"]
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "start_state": {
                        "type": "string"
                    },
                    "start_state_description": {
                        "type": "string"
                    },
                    "end_state": {
                        "type": "string"
                    },
                    "end_state_description": {
                        "type": "string"
                    },
                    # "criteria": {
                    #     "type": "object",
                    #     "properties": {
                    #         "name": {
                    #             "type": "string"
                    #         },
                    #         "description": {
                    #             "type": "string"
                    #         }
                    #     },
                    #     "required": [
                    #         "name",
                    #         "description"
                    #     ]
                    # },
                    "process": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "adds_new_entites": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "name",
                            "description",
                            "adds_new_entites"
                        ]
                    }
                },
                "required": [
                    "name",
                    "start_state",
                    "end_state",
                    "process"
                ]
            }
        }
    },
    "required": [
        "name",
        "class_name",
        "transitions"
    ]
}

ENTITIES_DESIGN = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "entity_name": {
                "type": "string"
            },
            "entity_type": {
                "type": "string",
                "enum": ["JOB", "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA", "WEB_SCRAPING_PULL_BASED_RAW_DATA",
                         "TRANSACTIONAL_PULL_BASED_RAW_DATA", "EXTERNAL_SOURCES_PUSH_BASED_RAW_DATA",
                         "WEB_SCRAPING_PUSH_BASED_RAW_DATA", "TRANSACTIONAL_PUSH_BASED_RAW_DATA", "SECONDARY_DATA",
                         "UTIL", "CONFIG", "BUSINESS_ENTITY"]
            },
            "entity_source": {
                "type": "string",
                "enum": ["API_REQUEST", "SCHEDULED", "ENTITY_EVENT"]
            },
            "depends_on_entity": {
                "type": "string"
            },
            "entity_workflow": ENTITY_WORKFLOW
        },
        "required": [
            "entity_name",
            "entity_type",
            "entity_source",
            "depends_on_entity",
            "entity_workflow"
        ]
    }
}

# Finished
app_building_stack = [{"question": None,
                       "prompt": {
                           "text": "Hi! "
                       },

                       # "file_name": "entity/app_design.json",
                       "answer": None,
                       "approve": True,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": MAX_ITERATION,
                       "additional_questions": [
                           {
                               "question": "Feel free to ask any questions or discuss the design in the chat 💬💬",
                               "approve": True}],
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"question": "Your application is finished! Thank you for collaboration!",
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "index": 2,
                       "iteration": 0,
                       "file_name": "entity/chat.json",
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "remove_api_registration"},
                       "index": 2,
                       "iteration": 0,
                       "file_name": "app.py",
                       "notification_text": """
                       """,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "save_env_file"},
                       "index": 2,
                       "iteration": 0,
                       "file_name": ".env.template",
                       "notification_text": """
### Setup Instructions for Your Application

Your application is ready! Please follow the steps below to configure it:

1. **Move the `.env.template` to `.env`**:
    Rename the `.env.template` file to `.env`:
    ```bash
    mv .env.template .env
    ```

2. **Update the `.env` file**:
    Open the `.env` file and replace the placeholder values with your actual environment variables and credentials. For example, replace `CHAT_ID_VAR` with `$chat_id` and fill in other necessary values.

    You might need to specify the path to .env file in your IDE run configurations.

3. **Start Your Application**:
    Once you've updated the `.env` file, you can start your application by running:
    ```bash
    python app.py
    ```
    or just run the app.py in your IDE.
Please also update your api.py files to use cyoda_token until authentication featute is fully implemented. Sorry for inconvenience!
Your application should now be up and running! 🎉

You can check the api with http://localhost:5000/scalar

                       """,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "finish_flow"},
                       "index": 2,
                       "iteration": 0,
                       "file_name": "entity/chat.json",
                       "notification_text": """
🎉 **Chat flow has been saved!** 🎉

The chat flow has been successfully saved to `entity/chat.json`. Now you can run `app.py` to start the application. 🚀

Once you run it, both the **workflow** and **entities** will be imported to the Cyoda environment automatically. 🌟

Any updates or changes to the entities will trigger the workflow, so you’re all set to go! 🔄

We are available in the **Google Tech Channel** to support you. If you spot any bugs or need additional features, feel free to submit tickets at [GitHub Issues](https://github.com/Cyoda-platform/ai-assistant). You’re also most welcome to contribute to the project! 💻 

For any direct inquiries, reach out to **ksenia.lukonina@cyoda.com**. We’re here to help! 😊
                       """,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},

                      {
                          "question": APPROVAL_NOTIFICATION,
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          # "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "approve": True,
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True},
                      # add_design_stack
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "add_design_stack"},
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "iteration": 0,
                       "fills_stack": True,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY},
                      {"question": None,
                       "prompt": {
                           "text": "Generate Cyoda design json, based on the complete prd. Use only lowercase underscore for namings. If the entity is saved in the workflow of another entity then its source will be ENTITY_EVENT. The JOB entity_source defaults to API_REQUEST. Prefer entity source/type mentioned in the prd, if it is unclear default to API_REQUEST or ENTITY_EVENT for secondary data. Avoid scheduler unless specified explicitly. You should not change entities or their workflows. You should not omit or add entities which are not listed in the prd. You should follow the complete prd 100% as it was confirmed.",
                           "schema": {
                               "$schema": "http://json-schema.org/draft-07/schema#",
                               "title": "Cyoda design",
                               "type": "object",
                               "properties": {
                                   "entities": ENTITIES_DESIGN
                               },
                               "required": [
                                   "entities"
                               ]
                           }
                       },
                       "answer": None,
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "function": None,
                       "iteration": 0,
                       "ui_config": {
                           "format": "json",
                       },
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY},
                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True
                       },
                      {"question": None,
                       "prompt": {
                           "text": "Please, return a complete prd."
                       },
                       "file_name": "entity/app_design_prd.md",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True
                       },
                      {
                          "notification": """
Awesome! Let's dive into generating your application code! 🚀 

I'll keep you updated with notifications on my progress, and let you know when it's time to discuss any changes.
 
Feel free to grab a coffee ☕ while I work—it's going to take about 2 minutes. 
 
Just relax and wait for the update!

In this process, we will walk through each stage of building an application, from gathering initial requirements to designing, coding, and implementing the final logic.

### The stages of the process are as follows:

1. **Application design**:  
   Let's design the application using diagrams and chat. You'll receive a text document with the PRD as the output.  
   *Output documents*: entity/app_design.md

2. **Entities design**:  
   Let's define the JSON data structure for each entity.
   *Output documents*: entity/*

3. **Workflow design**:  
   Let's ensure our entity workflow is correctly defined.
   *Output documents*: entity/*/workflow.json

4. **Workflow processors code design**:  
   Let's implement the workflow processors.
   *Output documents*: entity/*/workflow.py

5. **Additional logic code design**:  
   Let's develop any additional business logic.
   *Output documents*: entity/*/api.py or entity/*/logic.py

---

### Process Flow:

Gathering requirements --> **Application design** --> **Entities design** --> **Workflow design** --> **Workflow processors code design** --> **Additional logic code design**         
                          """,
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "info": True,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True},
                      {"question": None,
                       "prompt": {
                           "text": "Hi! "
                       },

                       # "file_name": "entity/app_design.json",
                       "answer": None,
                       "approve": True,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": MAX_ITERATION,
                       "additional_questions": [
                           {
                               "question": "We can discuss our ideas in the chat 💬💬, when you feel we are ready to start code generation - give me thumbs up 👍",
                               "approve": True}],
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {
                          "question": f"I'm ready with the design - we can discuss our ideas in the chat 💬💬, when you feel we are ready to start code generation - give me thumbs up 👍",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "approve": True,
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True},
                      {"question": None,
                       "prompt": {
                           "text": """Please outline entities for this requirement. Return entities diagram (mermaid or plantuml).
Please give me some json examples of data models for each entity, based on my requirement (you can use abridged json versions substituting excessive text with ...) . Provide only example data. If I provided entity schemas - just use them (abridged), if no - generate yours. 
For each entity specify how it should be saved - through the workflow of a different entity (ENTITY_EVENT, SECONDARY_DATA) or directly via an API call or maybe via scheduler.
For an orchestration entity (if there is any) consider adding a single workflow per app. If there is no orchestration entity - then add workflow to any entity where it makes sense.
***For each workflow let's provide a flowchart***
Example:
```mermaid
flowchart TD
  A[Start State] -->|transition: transition_name_1, processor: processor_name_1, processor attributes: sync_process=true/false, new_transaction_for_async=true/false, none_transactional_for_async=true/false| B[State 1]
  B -->|transition: transition_name_2, processor: processor_name_2, processor attributes: sync_process=true/false, new_transaction_for_async=true/false, none_transactional_for_async=true/false| C[State 2]
  C --> D[End State]
  %% Decision point for criteria (only if necessary!)
  B -->|criteria: criteria_name, entityModelName equals some_value| D1{Decision: Check Criteria}
  D1 -->|true| C
  D1 -->|false| E[Error: Criteria not met]
class A,B,C,D,D1 automated;
``` 
If I ask you a general question, just return an answer to this question.
If I ask you a general question, just return an answer to this question. 
I say: """
                       },
                       # "file_name": "entity/app_design.json",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True
                       },
                      {
                          "notification": """
Thanks for the go-ahead!
There are many ways to structure systems. We suggest using **event-driven design** with **entities** and **state machines**. This approach has proven to work exceptionally well for **high-availability** and **data-intensive** applications, ensuring scalability and simplicity.

### What are **Entities**? 🤔
Entities are **data units** that represent real-world objects. Each entity has a **lifecycle**, **states**, and **transitions** that define how it evolves over time.

### Our Approach: 💡
- **Entities** represent things like a **Light Bulb** 💡.
- **State Machines** visualize the **lifecycle** of entities (states + transitions) 🔄.
- **Event-Driven Architecture** triggers actions based on events, making systems responsive and scalable ⚡.

### Simple Light Bulb Example 💡:
- **States**:  
  - **OFF** 🚫  
  - **ON** ✅

- **Transitions**:  
  - **New** → OFF (initial state)  
  - **Flip Switch** → ON  
  - **Flip Switch Again** → OFF
---

### Light Bulb Flowchart:

```mermaid
stateDiagram-v2
    [*] --> OFF
    OFF --> ON : Flip Switch
    ON --> OFF : Flip Switch Again
```    
🎉 Let’s dive into creating your project’s **entities** and **workflow** to build a scalable and data-intensive system! 

For more on entity databases, check out this article by [Paul Schleger](https://medium.com/@paul_42036/whats-an-entity-database-11f8538b631a) 📚.
""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True
                      },
                      {"question": None,
                       "prompt": {
                           "text": "Hi! This is a general question, but remember we are building Cyoda app, and currently we are designing my journey and sequence diagram, so if the user requirement is sufficient it's a nice idea to return these mermaid diagrams. If my question is completely irrelevant - answer it as is , but remind that we are building app here. I say:"
                       },

                       # "file_name": "entity/app_design.json",
                       "answer": None,
                       "approve": True,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": MAX_ITERATION,
                       "additional_questions": [
                           {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {
                          "question": f"{APPROVAL_NOTIFICATION}",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "approve": True,
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True},
                      {"question": None,
                       "prompt": {
                           "text": "Please validate my requirement and return user requirement doc with user stories, journey diagram and sequence diagram. Use markdown with mermaid dialect (```mermaid). Explain your choice in simple words, but try to keep everything short and friendly. Talk to me like we are close friends. If I ask you a general question, just return an answer to this question. Start your answer with what you understood from my requirement. My requirement: "
                       },
                       "file_name": "entity/user_requirement.md",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0,
                       # "additional_questions": [
                       #    {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {"question": None,
                       "prompt": {
                           "text": "We are in the loop of requirement validation. Talk to me like we are close friends. If I ask you a general question, just return an answer to this question. Start your answer with what you understood from my requirement. Help me improve my requirement, i.e. if any information is missing help me understand why we need it and ask for it very friendly, like api docs, my expectations, if we need ha, persistence, what api will the future application provide. Speak in simple words and remember - we are in a chat loop - so you do not have to ask all questions at once. Guide slowly, suggest to attach relevant doc files and user requirement as files. My requirement: "
                       },
                       # "file_name": "entity/app_design.json",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": MAX_ITERATION,
                       "additional_questions": [
                           {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
                      {
                          "question": "💡 What kind of application would you like to build? I'd love to hear your ideas! Feel free to share them with me! 😊",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "approve": False,
                          "example_answers": [
                              """
                              Hello, I would like to download the following data: [London Houses Data](https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv), analyze it using **pandas**, and save a report. 📊""",
                              """
                              Hello! 👋
                              I would like to develop an application that:
                              1. Ingests data from a specified data source 📥
                              2. Aggregates the data 🧮
                              3. Saves the aggregated data to a report 📄
                              Once the report is generated, the application should send it to the admin's email 📧. 
                              Additionally, the data ingestion process should be scheduled to run **once a day** ⏰."""],
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True},

                      # add_instruction
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "add_instruction"},
                       "file_name": "instruction.txt",
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       },
                      # init_chats
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "init_chats"},
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "iteration": 0,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       },
                      # clone_repo
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "clone_repo"},
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True
                       },
                      {
                          "notification": """
👋 Welcome to Cyoda Application Builder! We’re excited to build something amazing with you! 😄  

We’re here to help with building and deploying on Cyoda Cloud! Reach out anytime! 🌟 Your branch will be ready soon, and I’ll notify you when I push changes. If you have suggestions, message me or use Canvas! 😊  

In Canvas, you can code, edit, and improve around the main app build flow! It’s a great way to collaborate and make changes! 💻  

If you’re happy with the progress or want me to pull your changes, just give me a thumbs up! 👍  (currently approve button in the top panel)

If something goes wrong, no worries—just roll back! 😬 Your app will be live on Cyoda Platform GitHub soon! 🚀 Let’s build your branch together! 🌿
""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "info": True,
                          "file_name": "instruction.txt",
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                          "publish": True

                      },
                      {
                          "notification": """
🌿🪷🏵️⚜️🌿
""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "info": True,
                          "file_name": "instruction.txt",
                          "max_iteration": 0,
                          "stack": APP_BUILDING_STACK_KEY,
                      }
                      ]

data_ingestion_stack = lambda entities: [
    # {
    #     "question": f"😊✨ Are you ready to move on to the next iteration? Give me thumbs up if you are ready to proceed 👍👍",
    #     "prompt": {},
    #     "answer": None,
    #     "function": None,
    #     "index": 0,
    #     "iteration": 0,
    #     "flow_step": ENTITIES_DESIGN_STR,
    #     "approve": True,
    #     "max_iteration": 0,
    #     "stack": DATA_INGESTION_STACK_KEY},
    {"question": None,
     "prompt": {
         "text": "Hi! "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": ENTITIES_DESIGN_STR,
     "max_iteration": MAX_ITERATION,
     "additional_questions": [
         {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
     "stack": DATA_INGESTION_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": "Hi! Could you please explain what you've done, why you wrote the code you wrote, what tests you added. Also please answer my questions if I have any.  Your answer should be well-structured with markdown and not exceed 100 words. I say: "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": ENTITIES_DESIGN_STR,
     "max_iteration": 0,
     "stack": DATA_INGESTION_STACK_KEY,
     "publish": True},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_data_ingestion_code",
                     "prompts": {
                         "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. ingest_data function takes request parameters as arguments if there are any. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything. **Tests should be in the same file with the code**",
                         },
                         "WEB_SCRAPING_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. ingest_data function takes request parameters as arguments if there are any. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything.  **Tests should be in the same file with the code**",
                         },
                         "TRANSACTIONAL_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. ingest_data function takes request parameters as arguments if there are any. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything.  **Tests should be in the same file with the code**",
                         }
                     }},
        "context": {
            "files": [],
        },
        "entities": entities,
        "files_notifications": FILES_NOTIFICATIONS,
        "notification_text": "🎉 The code for data ingestion has been generated successfully! Please check it out and click 'Approve' if you're ready to move on to the next iteration. Feel free to use Canvas QA to suggest any improvements! 😊",
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY
    },
    {
        "question": f"🚀 Are you ready to start the bulk generation? Give me thumbs up to let me know you're good to go!👍👍 😊",
        "prompt": {},
        "answer": None,
        "approve": True,
        "function": None,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "files_notifications": FILES_NOTIFICATIONS,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY,
        "publish": True},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "check_entity_definitions"},
        "notification_text": "Please consider updating the file contents for {file_name}",
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY,
        "publish": True},
    {"question": None,
     "prompt": {
         "text": "Hi! "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": GATHERING_REQUIREMENTS_STR,
     "max_iteration": MAX_ITERATION,
     "additional_questions": [
         {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
     "stack": APP_BUILDING_STACK_KEY,
     "publish": True},
    {
        "question": f"😊 Could you please update the files with the necessary information? Once you're done, just click 'Approve' 👍. Thanks so much!",
        "prompt": {},
        "answer": None,
        "function": None,
        "approve": True,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY,
        "publish": True},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_data_ingestion_entities_template"},
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY,
        "publish": True},
    # {
    #     "question": None,
    #     "prompt": {},
    #     "answer": None,
    #     "function": {"name": "refresh_context"},
    #     "context": {
    #         "files": ["entity/app_design.json", "entity/user_requirement.md", "entity/user_files/**"],
    #     },
    #     "iteration": 0,
    #     "flow_step": ENTITIES_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": DATA_INGESTION_STACK_KEY},
    {
        "notification": """
We are currently generating templates for your data ingestion entities! 🎉 Once I’m done, you’ll find each entity in a separate folder: `entity/{entity_name}/{entity_name}.json`. 🗂️
Also you’ll find connection folder for each entity where we'll configure code for the data ingestion: `entity/{entity_name}/connections/connection.py`. 🗂️

This file will represent the **entity model** as semi-structured data (think of it as an example). For data ingestion, this model should either be:
- **A golden JSON**: The raw data output from your data source, or
- **A transformed version**: In which case, we’ll automatically handle the mapping for you! 🔄

For now, we just need you to either:
- **Provide your own data example**, or
- **Approve our example** if it works for you! 👍 Once you’re happy with it, we can move forward!

If everything looks good, just give us a thumbs up! 👍  
If you want to make any changes, feel free to edit the file in your IDE and **push the changes** so I can fetch them. Or, you can edit the models directly here, and I’ll save them for you! ✏️

Also, feel free to use **Canvas** to collaborate and edit the models together! 🖌️😊

Looking forward to your feedback! 🌟
""",
        "prompt": {},
        "info": True,
        "answer": None,
        "function": None,
        "iteration": 0,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY
    },
    {
        "notification": f"""Proceeding to {ENTITIES_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> ***{ENTITIES_DESIGN_STR}*** --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": DATA_INGESTION_STACK_KEY,
        "publish": True},
]

entity_stack = lambda entities: [
    # {
    #     "question": f"😊✨ Are you ready to move on to the next iteration? Let me know when you're all set! Give me thumbs up 👍👍 if you are ready to proceed",
    #     "prompt": {},
    #     "answer": None,
    #     "function": None,
    #     "approve": True,
    #     "index": 0,
    #     "iteration": 0,
    #     "flow_step": ENTITIES_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": ENTITY_STACK_KEY},
    {"question": None,
     "prompt": {
         "text": "Hi! "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": ENTITIES_DESIGN_STR,
     "max_iteration": MAX_ITERATION,
     "additional_questions": [
         {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
     "stack": ENTITY_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": "Hi! Could you please shortly explain what you've done. Also please answer my questions if I have any.  Your answer should be well-structured with markdown and not exceed 100 words. I say: "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": ENTITIES_DESIGN_STR,
     "max_iteration": 0,
     "stack": ENTITY_STACK_KEY,
     "publish": True},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_entities_template",
                     "prompts": {
                         "ai_question": "Based on the data you have in the context and your understanding of the users requirement please generate json data example for entity {entity_name}. This json data should reflect business logic of the entity - it is not related to entity design schema!!!! it should not have any relevance to Cyoda. {user_data}. If there is any data ingestion in the application flow, make sure you add request parameters at least to the orchestration entity. Return json with markdown."
                     }},
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "notification_text": f"😊 Could you please take a look at the generated entity examples? If you have a specific structure in mind, feel free to adjust my suggestions and click 'Approve' 👍. You can also use Canvas to edit the entities together. Thanks so much!",
        "max_iteration": 0,
        "stack": ENTITY_STACK_KEY},
    {
        "notification": """
We are currently generating templates for your entities! 🎉 Once I’m done, you’ll find each entity in a separate folder: `entity/{entity_name}/{entity_name}.json`. 🗂️

This file will represent the **entity model** as semi-structured data (think of it as an example). Later, we’ll automatically generate the dynamic entity schema based on this JSON data. 🔄

For now, we just need you to either:
- **Provide your own data example**, or
- **Approve our example** if it works for you! 👍 Once you’re happy with it, we’re good to move forward!

If everything looks good, just give us a thumbs up! 👍  
If you want to make any changes, feel free to edit the file in your IDE and **push the changes** so I can fetch them. Or, you can edit the models directly here, and I’ll save them for you! ✏️

Also, feel free to use **Canvas** to collaborate and edit the models together! 🖌️😊

Looking forward to your feedback! 🌟
""",
        "prompt": {},
        "info": True,
        "answer": None,
        "function": None,
        "iteration": 0,
        "file_name": "entity/app_design.json",
        "flow_step": APPLICATION_DESIGN_STR,
        "max_iteration": 0,
        "stack": ENTITY_STACK_KEY
    },
    # {
    #     "question": f"🚀 We’re all set to start generating the entities! If you have any additional details you'd like me to include, feel free to share. No worries if anything goes wrong – we can always fix it later! 😊 If you are ready to proceed give me a thumbs up! 👍 (currently: approve button)",
    #     "prompt": {},
    #     "answer": None,
    #     "function": None,
    #     "index": 0,
    #     "iteration": 0,
    #     "approve": True,
    #     "flow_step": ENTITIES_DESIGN_STR,
    #     "files_notifications": FILES_NOTIFICATIONS,
    #     "max_iteration": 0,
    #     "stack": ENTITY_STACK_KEY},
    # {
    #     "question": None,
    #     "prompt": {},
    #     "answer": None,
    #     "function": {"name": "refresh_context"},
    #     "context": {
    #         "files": ["entity/**"],
    #         "excluded_files": ["entity/workflow.py", "entity/__init__.py"],
    #     },
    #     "notification_text": "",
    #     "iteration": 0,
    #     "flow_step": ENTITIES_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": ENTITY_STACK_KEY},
    {
        "notification": f"""Proceeding to {ENTITIES_DESIGN_STR}


{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> ***{ENTITIES_DESIGN_STR}*** --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "stack": ENTITY_STACK_KEY,
        "publish": True
    },
]

workflow_stack = lambda entity: [
    # ========================================================================================================
    # {"question": None,
    #  "prompt": {
    #      "text": f"Improve the workflow for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
    #      "schema": {
    #          "$schema": "http://json-schema.org/draft-07/schema#",
    #          "title": "Improved workflow design",
    #          "type": "object",
    #          "properties": {
    #              "can_proceed": {
    #                  "type": "boolean"
    #              },
    #              "entity_workflow": ENTITY_WORKFLOW
    #          },
    #          "required": [
    #              "can_proceed",
    #              "entity_workflow"
    #          ]
    #      }
    #
    #  },
    #  "answer": None,
    #  "function": None,
    #  "entity": entity,
    #  "index": 0,
    #  "iteration": 0,
    #  "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
    #  "flow_step": WORKFLOW_DESIGN_STR,
    #  "additional_questions": [{"question": "Would you like to improve the workflow?", "approve": True}],
    #  "max_iteration": MAX_ITERATION,
    #  "stack": WORKFLOW_STACK_KEY},
    # Would you like to add any changes to entity workflow
    # {
    #     "question": f"Would you like to add any changes to entity workflow: entity/{entity.get("entity_name")}/workflow/workflow.json . If not - you can just approve and proceed to the next step 👍",
    #     "prompt": {},
    #     "answer": None,
    #     "function": None,
    #     "approve": True,
    #     "index": 0,
    #     "iteration": 0,
    #     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
    #     "flow_step": WORKFLOW_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": WORKFLOW_STACK_KEY},
    {"question": None,
     "prompt": {},
     "answer": None,
     "function": {"name": "generate_cyoda_workflow"},
     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
     "entity": entity,
     "iteration": 0,
     "flow_step": WORKFLOW_DESIGN_STR,
     "max_iteration": 0,
     "stack": WORKFLOW_STACK_KEY},
    # {
    #     "question": None,
    #     "prompt": {},
    #     "answer": None,
    #     "function": {"name": "refresh_context"},
    #     "context": {
    #         "files": ["entity/app_design.json", "entity/user_requirement.md"],
    #     },
    #     "iteration": 0,
    #     "flow_step": WORKFLOW_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": WORKFLOW_STACK_KEY},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "refresh_context"},
        "context": {
            "files": ["common/service/entity_service_interface.py",
                      "common/service/trino_service.py",
                      "common/ai/ai_assistant_service.py",
                      "processor_instruction.txt", "entity/**"],
            "excluded_files": ["entity/workflow.py", "entity/__init__.py"],
        },
        "iteration": 0,
        "flow_step": WORKFLOW_CODE_DESIGN_STR,
        "max_iteration": 0,
        "stack": PROCESSORS_STACK_KEY},

    {
        "notification": f"""Proceeding to {WORKFLOW_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> ***{WORKFLOW_DESIGN_STR}*** --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": WORKFLOW_STACK_KEY,
        "publish": True},
]

processors_stack = lambda entity: [
    # Would you like to edit the model
    # Generate the processor functions
    # {"question": None,
    #  "prompt": {
    #      "text": "Hi! "
    #  },
    #
    #  # "file_name": "entity/app_design.json",
    #  "answer": None,
    #  "approve": True,
    #  "function": None,
    #  "iteration": 0,
    #  "flow_step": GATHERING_REQUIREMENTS_STR,
    #  "max_iteration": MAX_ITERATION,
    #  "additional_questions": [
    #      {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
    #  "stack": APP_BUILDING_STACK_KEY},
    {"question": None,
     "prompt": {
         "text": f"Hi! "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": WORKFLOW_CODE_DESIGN_STR,
     "max_iteration": MAX_ITERATION,
     "additional_questions": [
         {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
     "stack": PROCESSORS_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": f"Hi! Could you please explain what processors functions you wrote. Explain that they are isolated functions in a faas way like aws lambda. They will be triggered by Cyoda grpc server when the {entity.get('entity_name')} entity state changes. Tell what tests you wrote and how you mocked Cyoda entity service (repository) so that i can test every function in an isolated fashion. Also please answer my questions if I have any.  Your answer should be well-structured with markdown and not exceed 100 words. I say: "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": WORKFLOW_CODE_DESIGN_STR,
     "max_iteration": 0,
     "stack": PROCESSORS_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": f"Please, generate the processor functions for {entity.get('entity_name')} "
                 f"call public functions by the name of each processor: "
                 f"{', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}. "
                 f" Reuse functions that are available in the code base, including logic.app_init import entity_service, connections.py (ingest_data public function) and any other existing function that is related to your purpose."
                 f" Make sure you include logic to save any dependant entities: {', '.join([transition.get('process', {}).get('adds_new_entites', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}."
                 f" Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code**"
                 f"{entity.get('entity_name')}. Based on the user suggestions if there are any. "
                 f" Please make sure you are re-using all raw_data_*/connections/connection.py ingest_data functions. This is very important not to re-implement ingest_data but reuse it. You should import and reuse all ingest_data functions, use 'as' to avoid names duplicates. Make sure the result of data ingestion is saved to the corresponding raw data entity."
                 f" Please also make sure that you understand that argument 'data' that you pass to each function corresponds to entity/{entity.get('entity_name')}/{entity.get('entity_name')}.json data and not to any other entity!"
                 f" User says: ",
     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py",
     "flow_step": WORKFLOW_CODE_DESIGN_STR,
     # "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": 0,
     "stack": PROCESSORS_STACK_KEY
     },
    # Would you like to specify any details for generating processors
    # {
    #     "question": f"Would you like to share any comments or suggestions for these functions: {', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}? 🤔 We’d love to hear your ideas to make it even better! 😄",
    #     "prompt": {},
    #     "answer": None,
    #     "function": None,
    #     "index": 0,
    #     "iteration": 0,
    #     "flow_step": WORKFLOW_CODE_DESIGN_STR,
    #     "approve": False,
    #     "example_answers": ["Could you please take into account ...",
    #                         "What would you recommend?",
    #                         "I've already provided all the necessary details in the session context"],
    #     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py",
    #     "max_iteration": 0,
    #     "stack": PROCESSORS_STACK_KEY},
    # {
    #     "question": None,
    #     "prompt": {},
    #     "answer": None,
    #     "function": {"name": "refresh_context"},
    #     "context": {
    #         "files": ["common/service/entity_service_interface.py",
    #                   "common/service/trino_service.py",
    #                   "common/ai/ai_assistant_service.py",
    #                   "processor_instruction.txt", "entity/**"],
    #         "excluded_files": ["entity/workflow.py", "entity/__init__.py"],
    #     },
    #     "iteration": 0,
    #     "flow_step": WORKFLOW_CODE_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": PROCESSORS_STACK_KEY},
    {
        "notification": f"""
Now it’s time to give life to {entity.get('entity_name')} workflow! 🎉

Our workflow will have a set of functions 🛠️ (think of them as isolated functions that will receive your entity as an argument). These functions can perform various actions on your entity. It’s a bit like AWS Lambda's **FaaS** (Function as a Service) in a way 💻⚡
""",
        "prompt": {},
        "answer": None,
        "function": None,
        "iteration": 0,
        "info": True,
        "file_name": "entity/app_design.json",
        "flow_step": APPLICATION_DESIGN_STR,
        "max_iteration": 0,
        "stack": PROCESSORS_STACK_KEY
    },
    {
        "notification": f"""Proceeding to {WORKFLOW_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> ***{WORKFLOW_CODE_DESIGN_STR}*** --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": PROCESSORS_STACK_KEY,
        "publish": True},
]

scheduler_stack = lambda entity: [
    # ========================================================================================================
    # {"question": None,
    #  "prompt": {
    #      "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
    #  },
    #  "answer": None,
    #  "function": None,
    #  "entity": entity,
    #  "index": 0,
    #  "iteration": 0,
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "additional_questions": [QUESTION_OR_VALIDATE],
    #  "max_iteration": MAX_ITERATION},
    # {"question": "Would you like to edit the code?",
    #  "prompt": {},
    #  "answer": None,
    #  "function": None,
    #  "index": 0,
    #  "iteration": 0,
    #  "example_answers": ["Yes, I'd like to change ...",
    #                      "No, I'd like to proceed with the current version"],
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "max_iteration": 0},
    # ========================================================================================================
    # Generate the processor functions
    {"question": None,
     "prompt": {
         "text": f"Generate the scheduler file for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. This function should save a job entity with data model $data to cyoda. Besides, it should not do any logic. Also generate main function with entry point so that the user can do end-to-end test. User says: ",
     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": 0,
     "stack": SCHEDULER_STACK_KEY,
     },
    {
        "question": f"Let's generate the logic to schedule saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
        "prompt": {},
        "approve": False,
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "example_answers": ["Could you please take into account ...",
                            "What would you recommend?",
                            "I've already provided all the necessary details in the session context"],
        "max_iteration": 0,
        "stack": SCHEDULER_STACK_KEY},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "refresh_context"},
        "context": {
            "files": ["common/service/entity_service_interface.py",
                      "common/service/trino_service.py",
                      "common/ai/ai_assistant_service.py",
                      "logic_instruction.txt",
                      "entity/app_design.json",
                      "entity/user_requirement.md",
                      f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
        },
        "iteration": 0,
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "max_iteration": 0,
        "stack": SCHEDULER_STACK_KEY},
    {
        "notification": f"""Proceeding to {LOGIC_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": SCHEDULER_STACK_KEY,
        "publish": True},
]

form_submission_stack = lambda entity: [
    # ========================================================================================================
    {"question": None,
     "prompt": {
         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",

     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION,
     "stack": FORM_SUBMISSION_STACK_KEY},
    # Would you like to edit the model
    # {"question": "Would you like to edit the code?",
    #  "prompt": {},
    #  "answer": None,
    #  "function": None,
    #  "index": 0,
    #  "iteration": 0,
    #  "example_answers": ["Yes, I'd like to change ...",
    #                      "No, I'd like to proceed with the current version"],
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "max_iteration": 0},
    # ========================================================================================================
    # Generate the processor functions
    {"question": None,
     "prompt": {
         "text": f"Generate the logic file to process the form application and saving the entity {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code** User says: ",

     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION,
     "stack": FORM_SUBMISSION_STACK_KEY
     },
    {
        "question": f"Let's generate the logic to process the form application and saving the entity {entity.get("entity_name")} with the form entity. Would you like to specify any details?",
        "prompt": {},
        "answer": None,
        "approve": False,
        "function": None,
        "index": 0,
        "iteration": 0,
        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "example_answers": ["Could you please take into account ...",
                            "What would you recommend?",
                            "I've already provided all the necessary details in the session context"],
        "max_iteration": 0,
        "stack": FORM_SUBMISSION_STACK_KEY},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "refresh_context"},
        "context": {
            "files": ["common/service/entity_service_interface.py",
                      "common/service/trino_service.py",
                      "common/ai/ai_assistant_service.py",
                      "logic_instruction.txt",
                      "entity/app_design.json",
                      "entity/user_requirement.md"
                      f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
        },
        "iteration": 0,
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "max_iteration": 0,
        "stack": FORM_SUBMISSION_STACK_KEY},
    {
        "notification": f"""Proceeding to {LOGIC_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": FORM_SUBMISSION_STACK_KEY},
]

file_upload_stack = lambda entity: [
    # ========================================================================================================
    {"question": None,
     "prompt": {
         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",

     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION,
     "stack": FILE_UPLOAD_STACK_KEY},
    # Would you like to edit the model
    # {"question": "Would you like to edit the code?",
    #  "prompt": {},
    #  "answer": None,
    #  "function": None,
    #  "index": 0,
    #  "iteration": 0,
    #  "example_answers": ["Yes, I'd like to change ...",
    #                      "No, I'd like to proceed with the current version"],
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "max_iteration": 0},
    # ========================================================================================================
    # Generate the processor functions
    {"question": None,
     "prompt": {
         "text": f"Generate the logic file to upload the file and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code** User says: ",

     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION,
     "stack": FILE_UPLOAD_STACK_KEY
     },
    {
        "question": f"Let's generate the logic to upload the file and saving the entity {entity.get("entity_name")} based on the file contents. Would you like to specify any details?",
        "prompt": {},
        "answer": None,
        "function": None,
        "approve": False,
        "index": 0,
        "iteration": 0,
        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "example_answers": ["Could you please take into account ...",
                            "What would you recommend?",
                            "I've already provided all the necessary details in the session context"],
        "max_iteration": 0,
        "stack": FILE_UPLOAD_STACK_KEY},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "refresh_context"},
        "context": {
            "files": ["common/service/entity_service_interface.py",
                      "common/service/trino_service.py",
                      "common/ai/ai_assistant_service.py",
                      "logic_instruction.txt",
                      "entity/app_design.json",
                      "entity/user_requirement.md"
                      f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
        },
        "iteration": 0,
        "flow_step": LOGIC_CODE_DESIGN_STR,
        "max_iteration": 0,
        "stack": FILE_UPLOAD_STACK_KEY},
    {
        "notification": f"""Proceeding to {LOGIC_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": FILE_UPLOAD_STACK_KEY},
]

api_request_stack = lambda entity: [
    # ========================================================================================================
    # {"question": None,
    #  "prompt": {
    #      "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
    #
    #  },
    #  "answer": None,
    #  "function": None,
    #  "entity": entity,
    #  "index": 0,
    #  "iteration": 0,
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
    #  "max_iteration": MAX_ITERATION,
    #  "stack": API_REQUEST_STACK_KEY},
    # Would you like to edit the model
    # {"question": "Would you like to edit the code?",
    #  "prompt": {},
    #  "answer": None,
    #  "function": None,
    #  "index": 0,
    #  "iteration": 0,
    #  "example_answers": ["Yes, I'd like to change ...",
    #                      "No, I'd like to proceed with the current version"],
    #  "flow_step": LOGIC_CODE_DESIGN_STR,
    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
    #  "max_iteration": 0},
    # ========================================================================================================
    # Generate the processor functions
    {"question": None,
     "prompt": {},
     "answer": None,
     "function": {"name": "register_api_with_app"},
     "index": 2,
     "iteration": 0,
     "file_name": "app.py",
     "entity": entity,
     "notification_text": """
### Setup Instructions for Your Application

Your application is ready! Please follow the steps below to configure it:

1. **Move the `.env.template` to `.env`**:
    Rename the `.env.template` file to `.env`:
    ```bash
    mv .env.template .env
    ```

2. **Update the `.env` file**:
    Open the `.env` file and replace the placeholder values with your actual environment variables and credentials. For example, replace `CHAT_ID_VAR` with `$chat_id` and fill in other necessary values.

    You might need to specify the path to .env file in your IDE run configurations.

3. **Start Your Application**:
    Once you've updated the `.env` file, you can start your application by running:
    ```bash
    python app.py
    ```
    or just run the app.py in your IDE.

Your application should now be up and running! 🎉

You can check the api with http://localhost:5000/scalar

                       """,
     "max_iteration": 0,
     "stack": APP_BUILDING_STACK_KEY,
     "publish": True},

    {"question": None,
     "prompt": {
         "text": "Hi! "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "max_iteration": MAX_ITERATION,
     "additional_questions": [
         {"question": f"{APPROVAL_NOTIFICATION}", "approve": True}],
     "stack": API_REQUEST_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": "Hi! Could you please explain what you've done what api you added and why. Also please answer my questions if I have any. Your answer should be well-structured with markdown and not exceed 100 words. I say: "
     },

     # "file_name": "entity/app_design.json",
     "answer": None,
     "approve": True,
     "function": None,
     "iteration": 0,
     "flow_step": LOGIC_CODE_DESIGN_STR,
     "max_iteration": 0,
     "stack": API_REQUEST_STACK_KEY,
     "publish": True},
    {"question": None,
     "prompt": {
         "text": f"Generate the quart additional api.py file to save the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Use blueprint api_bp_{entity.get("entity_name")} = Blueprint('api/{entity.get("entity_name")}', __name__) and @api_bp_{entity.get("entity_name")}.route respectively. Please use const ENTITY_VERSION for entity version and const cyoda_token for token. User says: ",
     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
     "file_name": f"entity/{entity.get("entity_name")}/api.py",
     "flow_step": LOGIC_CODE_DESIGN_STR,
     # "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": 0,
     "stack": API_REQUEST_STACK_KEY
     },
    {
        "notification": f"Let's generate the api for processing entity and saving the entity {entity.get("entity_name")}",
        "prompt": {},
        "answer": None,
        "approve": False,
        "function": None,
        "index": 0,
        "iteration": 0,
        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
        "flow_step": LOGIC_CODE_DESIGN_STR,
        # "example_answers": ["Could you please take into account ...",
        #                     "What would you recommend?",
        #                     "I've already provided all the necessary details in the session context"],
        "max_iteration": 0,
        "stack": API_REQUEST_STACK_KEY},
    # {
    #     "question": None,
    #     "prompt": {},
    #     "answer": None,
    #     "function": {"name": "refresh_context"},
    #     "context": {
    #         "files": ["common/service/entity_service_interface.py",
    #                   "common/service/trino_service.py",
    #                   "common/ai/ai_assistant_service.py",
    #                   "logic_instruction.txt",
    #                   "entity/app_design.json",
    #                   "entity/user_requirement.md"
    #                   f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
    #     },
    #     "iteration": 0,
    #     "flow_step": LOGIC_CODE_DESIGN_STR,
    #     "max_iteration": 0,
    #     "stack": API_REQUEST_STACK_KEY},
    {
        "notification": f"""Proceeding to {LOGIC_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0,
        "stack": API_REQUEST_STACK_KEY,
        "publish": True},
]


def get_stack_by_name(name: str):
    stacks = {
        FILE_UPLOAD_STACK_KEY: copy.deepcopy(file_upload_stack),
        API_REQUEST_STACK_KEY: copy.deepcopy(api_request_stack),
        FORM_SUBMISSION_STACK_KEY: copy.deepcopy(form_submission_stack),
        SCHEDULER_STACK_KEY: copy.deepcopy(scheduler_stack),
        PROCESSORS_STACK_KEY: copy.deepcopy(processors_stack),
        WORKFLOW_STACK_KEY: copy.deepcopy(workflow_stack),
        ENTITY_STACK_KEY: copy.deepcopy(entity_stack),
        DATA_INGESTION_STACK_KEY: copy.deepcopy(data_ingestion_stack),
        APP_BUILDING_STACK_KEY: copy.deepcopy(app_building_stack)
    }

    return stacks.get(name, None)
