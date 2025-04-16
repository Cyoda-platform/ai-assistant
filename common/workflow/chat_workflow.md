stateDiagram-v2
    [*] --> none
    none --> initialized_chat : initialize_chat
    initialized_chat --> submitted_workflow_question : submit_chat_question
    submitted_workflow_question --> processed_question : process_question (manual) /function
    processed_question --> submitted_workflow_question : submit_agent_question
    processed_question --> end : finish_chat
    end --> [*]