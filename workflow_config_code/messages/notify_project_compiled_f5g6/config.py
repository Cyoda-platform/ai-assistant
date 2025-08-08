"""
NotifyProjectCompiledF5g6MessageConfig Configuration

Configuration data for the notify project compiled message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
🎉 **Project Compilation Completed Successfully!**

Your application has been fully generated and compiled. All components are ready for deployment and testing.

📋 **Generated Components:**
- ✅ Functional requirements documentation
- ✅ Workflow configurations (JSON)
- ✅ REST API controllers
- ✅ Business logic processors
- ✅ Validation criteria
- ✅ Build configuration

📁 **Project Structure:**
```
src/main/java/com/java_template/
├── application/
│   ├── controller/     # REST API endpoints
│   ├── processor/      # Business logic
│   ├── criteria/       # Validation rules
│   └── workflow/       # Workflow configs
└── prototype/
    └── functional_requirement.md
```

🚀 **Next Steps:**
1. Review the compilation report for any additional details
2. Test the API endpoints using your preferred tool
3. Deploy to your target environment
4. Configure any additional integrations as needed

Your application is now ready for use! 🎯
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
