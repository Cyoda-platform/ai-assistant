"""
ProcessCompilationResultsI9j0PromptConfig Configuration

Configuration data for the process compilation results prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with analyzing GitHub Actions compilation results and applying fixes if needed.

USE:
- add_application_resource tool to save fixes to Java files:
  - resource_path: Full path to the Java file to be fixed
  - file_contents: Corrected content of the Java file
  
Useful file paths:
- Entity POJOs: 'src/main/java/com/java_template/application/entity/**'
- Processor classes: 'src/main/java/com/java_template/application/processor/**'
- Criterion classes: 'src/main/java/com/java_template/application/criterion/**'
- Controller: 'src/main/java/com/java_template/application/controller/Controller.java'

EXECUTION WORKFLOW - FOLLOW EXACTLY:

PHASE 1: ANALYZE COMPILATION RESULTS
1. Review the GitHub Actions workflow execution results from the previous step
2. Check the compilation status from the workflow memory/context
3. Identify any compilation errors, warnings, or issues from the GitHub Actions logs

PHASE 2: APPLY FIXES (IF NEEDED)
4. If compilation failed, use add_application_resource to fix issues:
   - Fix compilation errors in Java files
   - Address missing imports and dependencies  
   - Correct syntax issues
   - Fix package declarations
   - Resolve any other build-related problems
   
PHASE 3: GENERATE FINAL REPORT
6. Create a comprehensive compilation report using add_application_resource:
   - resource_path: "compilation_report.md"
   - file_contents: Include all details below

COMPILATION REPORT MUST INCLUDE:
- GitHub Actions workflow execution details (run ID, status, duration)
- Compilation status (SUCCESS/FAILURE)
- List of all generated files that were compiled
- If failures occurred: Detailed error analysis and fixes applied
- If successful: Confirmation of successful compilation
- Summary of any code modifications made
- Next steps or recommendations

CRITICAL CONSTRAINTS:
🚨 DO NOT call run_github_action - compilation was already triggered in the previous step
🚨 Only use add_application_resource for fixes and the final report
🚨 Focus on fixing issues based on the compilation results from memory/context
🚨 Be thorough in analyzing errors and applying appropriate fixes
🚨 Generate the final report as the last step

Your task is complete when you have:
1. ✅ Analyzed the compilation results from the previous step
2. ✅ Applied any necessary fixes to Java files (if compilation failed)
3. ✅ Generated the final comprehensive compilation report
"""
