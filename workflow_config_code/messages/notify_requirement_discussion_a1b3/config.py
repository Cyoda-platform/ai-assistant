"""
NotifyRequirementDiscussionA1b3MessageConfig Configuration

Configuration data for the requirement discussion message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
💬 Let’s review your initial requirement.
I’ll share my understanding (my “vision”) and a few clarifying questions.

You can answer as many as you like—I’ll use good judgment to fill any gaps.

If everything looks right, just click Approve. We’ll move to the next step, where I’ll provide formal functional requirements for us to edit together here—or you can work on them in your IDE.

"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
