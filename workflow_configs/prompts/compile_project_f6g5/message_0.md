
You are tasked with compiling and building the Java project using GitHub Actions.

EXECUTION WORKFLOW - FOLLOW EXACTLY:

PHASE 1: INITIAL COMPILATION CHECK (CALL run_github_action EXACTLY ONCE)
1. Use run_github_action tool to trigger the compilation workflow:
   - repository_name: "java-client-template"
   - workflow_id: "build.yml"
   - owner: "Cyoda-platform"
   - git_branch: Use the current branch from workflow cache
   - option: "compile-only"

2. Wait for the GitHub Actions workflow to complete and analyze the results

PHASE 2: ANALYSIS AND FIXES (NO MORE run_github_action CALLS)
3. Based on the compilation results from Phase 1:
   - If compilation succeeded: Note the success
   - If compilation failed: Identify specific issues from the GitHub Actions logs

4. If fixes are needed, use add_application_resource to:
   - Fix compilation errors in Java files
   - Address missing imports and dependencies
   - Correct syntax issues
   - Fix package declarations

PHASE 3: FINAL REPORT (SINGLE add_application_resource CALL)
5. Create a comprehensive compilation report using add_application_resource:
   - resource_path: "compilation_report.md"
   - file_contents: Include all details below

COMPILATION REPORT MUST INCLUDE:
- GitHub Actions workflow execution details (run ID, status, duration)
- Compilation status (SUCCESS/FAILURE)
- List of all generated files that were compiled
- If failures occurred: Detailed error analysis and fixes applied
- If successful: Confirmation of successful compilation
- Summary of any code modifications made

CRITICAL CONSTRAINTS:
🚨 CALL run_github_action EXACTLY ONCE - Never call it again after the initial check
🚨 CALL add_application_resource EXACTLY ONCE - Only for the final compilation report
🚨 DO NOT attempt to re-run compilation after fixes - just document the fixes in the report
🚨 If compilation fails, fix the issues but DO NOT verify fixes by calling run_github_action again

Your task is complete when you have:
1. ✅ Called run_github_action once for initial compilation check
2. ✅ Applied any necessary fixes to Java files (if needed)
3. ✅ Generated the final compilation report with add_application_resource
