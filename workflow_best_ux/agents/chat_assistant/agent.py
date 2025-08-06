"""
Chat Assistant Agent

Implements AgentProcessor interface with get_config() method.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import AgentProcessor, AgentConfig
from workflow_best_ux.builders import agent_config


class ChatAssistantAgent(AgentProcessor):
    """Chat assistant agent processor"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this agent processor"""
        return "chat_assistant"

    def get_config(self) -> AgentConfig:
        """Get agent configuration"""
        from workflow_best_ux.tools.web_search.tool import WebSearchTool
        from workflow_best_ux.tools.read_link.tool import ReadLinkTool
        from workflow_best_ux.tools.get_cyoda_guidelines.tool import GetCyodaGuidelinesTool
        from workflow_best_ux.tools.get_user_info.tool import GetUserInfoTool
        from workflow_best_ux.prompts.assistant_prompt.prompt import AssistantPrompt

        return (agent_config("chat_assistant")
                .with_description("Helpful AI assistant for chat interactions")
                .with_model("gpt-4o", temperature=0.7, max_tokens=10000)
                .add_tool(WebSearchTool().get_config())
                .add_tool(ReadLinkTool().get_config())
                .add_tool(GetCyodaGuidelinesTool().get_config())
                .add_tool(GetUserInfoTool().get_config())
                .add_prompt(AssistantPrompt().get_config())
                .build())

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat request using AI agent"""
        try:
            user_input = context.get("user_input", "")
            session_id = context.get("session_id", "")

            response = {
                "agent_response": f"Processing: {user_input}",
                "session_id": session_id,
                "status": "completed"
            }

            return response

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


# Create singleton instance
chat_assistant_agent = ChatAssistantAgent()
