# GitHub Interactions - Complete Findings

## Overview
This document catalogs ALL GitHub and Git interactions found across the entire project codebase.

---

## 1. GitHub API Operations

### Location: `functions/github_operations_service.py`
**Purpose:** Service for GitHub API interactions

#### Methods:
1. **`add_collaborator`** (lines 23-82)
   - Adds collaborators to GitHub repositories
   - Uses GitHub API PUT request to `/repos/{owner}/{repo}/collaborators/{username}`
   - Supports multiple repositories via config
   - Parameters: username (required), owner, repo, permission

2. **`get_repository_info`** (lines 84-119)
   - Gets repository information (placeholder implementation)
   - Parameters: owner, repository_name

3. **`trigger_github_workflow`** (lines 178-269)
   - Triggers GitHub Actions workflows
   - Uses POST to `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`
   - Returns run_id and tracker_id
   - Parameters: repository_name, workflow_id, ref, git_branch, inputs, tracker_id

4. **`monitor_workflow_run`** (lines 271-340)
   - Monitors GitHub Actions workflow runs
   - Parameters: repository_name, run_id

5. **`get_workflow_run_status`** (lines 341-380)
   - Gets status of a GitHub Actions run
   - Uses GET to `/repos/{owner}/{repo}/actions/runs/{run_id}`
   - Parameters: repository_name, run_id

6. **`run_github_action`** (lines 382-470)
   - High-level method: triggers workflow, monitors, and waits for completion
   - Includes timeout handling
   - Parameters: workflow_id, repository_name, git_branch, inputs, timeout_minutes

7. **`get_workflow_logs`** (lines 472-550)
   - Retrieves logs from GitHub Actions workflow runs
   - Downloads and extracts log zip files

8. **`get_enhanced_workflow_logs`** (lines 552-630)
   - Enhanced log retrieval with filtering and formatting

9. **`get_workflow_enhancement_suggestions`** (lines 632-700)
   - Analyzes workflow logs and provides suggestions

10. **`_make_github_api_request`** (lines 121-176)
    - Core GitHub API request handler
    - Supports GET, POST, PUT, DELETE methods
    - Uses httpx.AsyncClient
    - Headers: Authorization (Bearer token), Accept, X-GitHub-Api-Version, Content-Type

11. **`_wait_for_run_to_appear`** (helper method)
    - Waits for workflow run to appear in GitHub

12. **`_find_run_by_tracker_id`** (helper method)
    - Finds workflow run by tracker ID

---

## 2. Git Operations (Local Repository Management)

### Location: `common/utils/utils.py`

#### Core Git Functions:

1. **`clone_repo`** (lines 711-775)
   - Clones GitHub repository to local directory
   - Creates new branch from base branch
   - Uses: `git clone`, `git checkout`, `git checkout -b`
   - Calls: `set_upstream_tracking`, `run_git_config_command`, `_git_pull_internal`
   - Parameters: git_branch_id, repository_name

2. **`_git_pull_internal`** (lines 1042-1116)
   - Internal git pull without locks
   - Operations: checkout, fetch, diff, pull
   - Uses merge strategy: `--strategy recursive --strategy-option=theirs`
   - Commands: `git checkout`, `git fetch origin`, `git diff`, `git pull`

3. **`git_pull`** (lines 1118-1121)
   - Public git pull with lock protection
   - Wraps `_git_pull_internal` with `_git_operations_lock`

4. **`_git_push`** (lines 1125-1185)
   - Pushes changes to remote repository
   - Operations: pull, checkout, add files, commit, push
   - Commands: `git checkout`, `git add`, `git commit -m`, `git push -u origin`
   - Uses `_git_operations_lock` for thread safety

5. **`set_upstream_tracking`** (lines 1205-1219)
   - Sets upstream tracking for branch
   - Command: `git branch --set-upstream-to origin/{branch} {branch}`

6. **`run_git_config_command`** (lines 1193-1202)
   - Configures git pull behavior
   - Command: `git config pull.rebase false --global`

7. **`repo_exists`** (lines 1188-1190)
   - Checks if repository directory exists

#### File Operations with Git Integration:

8. **`_save_file`** (lines 898-975)
   - Saves file and commits to git
   - Creates `__init__.py` for Python repositories
   - Calls `_git_push` if CLONE_REPO is enabled

9. **`save_all`** (lines 792-896)
   - Saves multiple files and performs single git push
   - Generates commit messages
   - Handles both text and binary files

10. **`delete_file`** (lines 978-1010)
    - Deletes file and pushes deletion to git
    - Uses relative paths for git operations

11. **`delete_directory`** (lines 1013-1039)
    - Deletes directory and pushes to git
    - Uses `shutil.rmtree` for directory removal

12. **`read_file_util`** (lines 1272-1280)
    - Reads file from repository
    - Calls `git_pull` before reading

#### Helper Functions:

13. **`get_project_file_name`** (lines 777-783)
    - Constructs file path and ensures repo is cloned

14. **`get_project_file_name_path`** (lines 786-790)
    - Gets file path after cloning repo

15. **`get_repository_name`** (lines 1377-1386)
    - Determines repository name based on programming language
    - Legacy function (replaced by repository_resolver.py)

---

## 3. Repository Name Resolution

### Location: `functions/repository_resolver.py`

#### Classes:

1. **`RepositoryResolver`** (abstract base class)
   - Abstract method: `resolve_repository_name`

2. **`DefaultRepositoryResolver`** (lines 32-88)
   - Resolution priority:
     1. Explicit programming_language parameter
     2. Entity workflow_cache programming_language
     3. Entity workflow_name suffix (java/python)
     4. Default to Python

3. **`ParameterBasedRepositoryResolver`** (lines 90-117)
   - Prioritizes programming_language parameter
   - Falls back to DefaultRepositoryResolver

4. **`RepositoryResolverFactory`** (lines 120-150)
   - Factory methods:
     - `get_default_resolver()`
     - `get_parameter_based_resolver()`
     - `get_resolver_for_context(has_programming_language_param)`

#### Convenience Functions:

5. **`resolve_repository_name`** (lines 154-165)
   - Uses default resolution strategy

6. **`resolve_repository_name_with_language_param`** (lines 168-179)
   - Uses parameter-based resolution strategy

---

## 4. Git Operations in Auggie Processor

### Location: `workflow/dispatcher/auggie_processor.py`

#### Method:

1. **`_commit_all_changes`** (lines 473-560)
   - Commits and pushes Auggie CLI generated code
   - Operations:
     - `git add .`
     - `git diff --cached --quiet` (check for changes)
     - `git diff --cached --stat` (get diff stats)
     - `git commit -m`
     - `git push`
   - Returns: success status, had_changes flag, git diff

---

## 5. Configuration and Environment

### Location: `common/config/config.py`

#### GitHub-Related Configuration:

1. **`GITHUB_API_TOKEN`** (line 79)
   - GitHub personal access token for API authentication

2. **`GH_DEFAULT_OWNER`** (line 88)
   - Default: "Cyoda-platform"

3. **`GH_DEFAULT_REPOS`** (line 89)
   - Default: "mcp-cyoda-quart-app,java-client-template"
   - Split into list

4. **`GH_DEFAULT_USERNAME`** (line 90)
   - Default: "target-username"

5. **`GH_DEFAULT_PERMISSION`** (line 91)
   - Default: "push"

6. **`CLIENT_GIT_BRANCH`** (line 94)
   - Default: "main"

7. **`PYTHON_REPOSITORY_NAME`** (line 62)
   - From env: PYTHON_REPOSITORY_NAME

8. **`JAVA_REPOSITORY_NAME`** (line 63)
   - From env: JAVA_REPOSITORY_NAME

9. **`REPOSITORY_URL`** (line 61)
   - Template: "https://github.com/{owner}/{repository_name}"

10. **`RAW_REPOSITORY_URL`** (line 61)
    - Template for raw GitHub content

11. **`CONFIG_URL`** (lines 122-125)
    - Default: GitHub raw URL for config files

12. **`CLONE_REPO`** (not shown but referenced)
    - Controls whether to actually clone repos or just create directories

---

## 6. Docker Configuration

### Location: `Dockerfile`

#### Git Configuration (lines 104-127):

1. **Build Arguments:**
   - `GITHUB_API_TOKEN`
   - `GITHUB_USERNAME`

2. **Environment Variables:**
   - `GITHUB_API_TOKEN=${GITHUB_API_TOKEN}`
   - `GITHUB_USERNAME=${GITHUB_USERNAME}`

3. **Git Credential Setup:**
   - `git config --global credential.helper store`
   - Creates `~/.git-credentials` with token
   - Sets git user.email and user.name
   - Configured for both root and appuser

---

## 7. Function Registry Integration

### Location: `entity/chat/workflow.py`

#### Registered GitHub Functions (lines 315-323):

1. `add_collaborator`
2. `trigger_github_workflow`
3. `monitor_workflow_run`
4. `get_workflow_run_status`
5. `run_github_action`
6. `get_workflow_logs`
7. `get_enhanced_workflow_logs`
8. `get_workflow_enhancement_suggestions`

---

## 8. Service Usage Across Codebase

### `functions/file_operations_service.py`
- **`clone_repo`** method (lines 388-428)
  - Wraps `clone_repo` utility
  - Updates entity workflow_cache with git_branch and repository_name
  - Returns branch ready notification

### `functions/application_builder_service.py`
- Uses `resolve_repository_name_with_language_param`
- Validates branch (no modifications to main)
- Calls `clone_repo` before operations

### `functions/workflow_orchestrator_service.py`
- **`_get_repository_name`** (lines 246-248)
  - Gets repository from entity or defaults to "java-client-template"
- **`_get_git_branch_id`** (lines 250-252)
  - Gets git branch from entity or uses technical_id

### `functions/utility_service.py`
- Uses `_save_file` to save user-submitted files
- Constructs file paths using PROJECT_DIR, branch_id, repository_name

---

## 9. Constants and Parameters

### Location: `common/config/const.py`

1. **`GIT_BRANCH_PARAM`** (line 252)
   - Value: "git_branch"

2. **`REPOSITORY_NAME_PARAM`** (line 253)
   - Value: "repository_name"

3. **`PROGRAMMING_LANGUAGE_PARAM`** (line 254)
   - Value: "programming_language"

4. **`BRANCH_READY_NOTIFICATION`** (line 240)
   - Template message for branch creation

5. **`GITHUB_ACTION_COMPILED`** (referenced in code)
   - Tracks GitHub Action compilation status

---

## 10. Concurrency and Thread Safety

### Location: `common/utils/utils.py`

#### Global Locks (lines 27-29):

1. **`_file_operations_lock`**
   - asyncio.Lock for file operations

2. **`_git_operations_lock`**
   - asyncio.Lock for git operations
   - Used in: `clone_repo`, `_git_pull_internal`, `_git_push`, `git_pull`

---

## 11. Workflow Configuration References

### Locations:
- `workflow_config_code/workflows/configs/build_general_application_python/config.py`
- `workflow_config_code/workflows/configs/build_general_application_java/config.py`

#### Imports:
- `CloneRepoB60aFunctionConfig` - Function config for clone_repo

---

## 12. Environment Template

### Location: `.env.template`

#### Git/GitHub Related Variables (lines 27-31):

1. `PYTHON_REPOSITORY_NAME="quart-client-template"`
2. `JAVA_REPOSITORY_NAME="java-client-template"`
3. `REPOSITORY_URL="https://github.com/Cyoda-platform/{repository_name}"`
4. `RAW_REPOSITORY_URL="https://raw.githubusercontent.com/Cyoda-platform/{repository_name}/refs/heads"`
5. `CLONE_REPO="true"` (line 18)

---

## Summary Statistics

### Total GitHub/Git Interaction Points:
- **GitHub API Operations:** 10 methods
- **Git Command Operations:** 15+ functions
- **Repository Resolution:** 6 classes/functions
- **Configuration Variables:** 12+ settings
- **Registered Functions:** 8 in workflow registry
- **Service Integrations:** 5+ services

### Git Commands Used:
1. `git clone`
2. `git checkout`
3. `git checkout -b`
4. `git fetch origin`
5. `git diff`
6. `git pull`
7. `git add`
8. `git commit -m`
9. `git push -u origin`
10. `git branch --set-upstream-to`
11. `git config`

### GitHub API Endpoints:
1. `/repos/{owner}/{repo}/collaborators/{username}` (PUT)
2. `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` (POST)
3. `/repos/{owner}/{repo}/actions/runs/{run_id}` (GET)
4. `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` (GET)

---

## Next Steps for GitHub Service Refactoring

Based on these findings, the new GitHub service should consolidate:

1. **GitHub API operations** (from github_operations_service.py)
2. **Local git operations** (from utils.py)
3. **Repository name resolution** (from repository_resolver.py)
4. **Configuration management** (GitHub-related config)
5. **Credential management** (tokens, authentication)
6. **Branch management** (creation, tracking, switching)
7. **File operations with git integration** (save, delete with auto-commit)
8. **Workflow integration** (GitHub Actions triggering and monitoring)

All these should be unified under a single, well-organized GitHub service architecture.

