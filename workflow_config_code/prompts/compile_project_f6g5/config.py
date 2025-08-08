"""
CompileProjectF6g5PromptConfig Configuration

Configuration data for the compile project prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with compiling and building the Java project using GitHub Actions.

Based on the generated application code, perform the following tasks:

1. Trigger GitHub Actions compilation workflow with "compile-only" option
2. Monitor the compilation process and wait for completion
3. Analyze compilation results and fix any issues found
4. Generate a comprehensive compilation report

Your primary workflow:
1. Use run_github_action to trigger the compilation workflow:
   - repository_name: "java-client-template"
   - workflow_id: "build.yml"
   - owner: "Cyoda-platform"
   - git_branch: "main" (or specify the target branch)
   - option: "compile-only"

2. Wait for the GitHub Actions workflow to complete and analyze results

3. If compilation fails, use add_application_resource to:
   - Fix any compilation issues in Java files
   - Update build configuration files (build.gradle or pom.xml) if needed
   - Address missing imports and dependencies
   - Ensure controllers have proper annotations
   - Validate that processors implement required interfaces

4. Create a compilation report using add_application_resource at 'compilation_report.md'

The compilation report should include:
- GitHub Actions workflow execution details
- Compilation status (success/failure)
- List of all generated files that were compiled
- Any issues found during compilation and how they were resolved
- Build configuration validation results
- Performance metrics from the compilation process
- Build instructions for the user
- Next steps for deployment

Key advantages of using GitHub Actions for compilation:
- Consistent build environment
- Automated dependency resolution
- Parallel compilation capabilities
- Integration with CI/CD pipeline
- Detailed build logs and artifacts

Ensure the project is ready for building with standard Java build tools (Gradle or Maven) and passes all compilation checks in the GitHub Actions environment.
"""
