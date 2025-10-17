"""
WelcomeUserOptimizedMessageConfig Configuration

Generated from config: workflow_configs/messages/welcome_user_optimized/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """👋 Welcome to Cyoda Application Builder (Optimized flow)!

I will go through the following steps on my own. 

This will take from 10 to 30 minutes depending on the complexity of the application.

**Please make sure you've logged in to your account so that we could prepare your environment.**

Once the application is ready, I will start launch assistant, so that we can start your application together.

🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
