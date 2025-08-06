"""
Welcome Message

Implements MessageProcessor interface with get_config() method.
"""

from pathlib import Path
from typing import Any, Dict
from workflow_best_ux.interfaces import MessageProcessor, MessageConfig
from workflow_best_ux.builders import message_config


class WelcomeMessage(MessageProcessor):
    """Welcome message processor"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this message processor"""
        return "welcome_message"

    def __init__(self):
        self.base_path = Path(__file__).parent

    def get_config(self) -> MessageConfig:
        """Get message configuration"""
        content = self.read_content()
        return (message_config("welcome_message")
                .with_content(content)
                .with_type("welcome")
                .build())

    def read_content(self) -> str:
        """Read the markdown content"""
        md_path = self.base_path / "message.md"
        if md_path.exists():
            return md_path.read_text(encoding='utf-8')
        return "Welcome to the chat assistant!"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process welcome message"""
        try:
            content = self.read_content()
            user_name = context.get("user_name", "there")
            platform_name = context.get("platform_name", "Cyoda")

            formatted_content = content.replace("{user_name}", user_name)
            formatted_content = formatted_content.replace("{platform_name}", platform_name)

            return {
                "message": formatted_content,
                "message_type": "welcome",
                "status": "completed"
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


# Create singleton instance
welcome_message = WelcomeMessage()

