"""
CompileProjectF6g5PromptConfig Configuration

Configuration data for the compile project prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with compiling and building the Java project using GitHub Actions.

EXECUTION WORKFLOW - FOLLOW EXACTLY:

PHASE 1: INITIAL COMPILATION CHECK (CALL run_github_action EXACTLY ONCE)

2. Call run_github_action with the following parameters. Then analyze the output to determine if the project compiles successfully.

4. If fixes are needed, use available tools to:
   - Fix compilation errors in Java 21 Spring Boot 3 files
   
Once you fix the compilation errors, call run_github_action again to verify the fixes.

If the project compiles successfully, you are done.

CRITICAL CONSTRAINTS:
🚨 CALL run_github_action MAXIMUM 3 TIMES 

Your task is complete when you have:
1. ✅ Called run_github_action with successful compilation output
2. ✅ Applied any necessary fixes to Java files (if needed)
3. ✅ You run out of attempts to call run_github_action (max 3).

CRITICAL REQUIREMENTS:
- You CAN call run_github_action MAXIMUM 3 TIMES 
"""
