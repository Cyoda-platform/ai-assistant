# GitHub App Integration for Private Repositories - Implementation Tasks

## Overview
Enable users to use their private repositories with Cyoda AI Assistant by integrating GitHub App authentication, while maintaining full backward compatibility with existing public repository workflows. This allows the system to:
- **Continue working with public repositories** using existing personal access token (current behavior)
- **Support private repositories** using GitHub App installation tokens (new capability)

The system will automatically detect which authentication method to use based on provided parameters.

**GitHub App**: https://github.com/apps/cyoda-ai-assistant/installations/select_target

---

## Authentication Strategy

### Public Repositories (Existing - No Changes Required)
- Uses personal access token from `GITHUB_API_TOKEN` environment variable
- Works with `Cyoda-platform/quart-client-template` and `Cyoda-platform/java-client-template`
- No `installation_id` or custom `repository_url` provided
- **This flow remains completely unchanged**

### Private Repositories (New Capability)
- Uses GitHub App installation tokens (short-lived, auto-refreshing)
- Requires user to install GitHub App on their account/organization
- User provides required parameters:
  - `repository_url` - Full GitHub repository URL (e.g., `https://github.com/owner/repo`)
  - `installation_id` - GitHub App installation ID (obtained after installing the app)
- System workflow:
  1. Parse owner and repo name from `repository_url`
  2. Generate JWT using GitHub App credentials (App ID + private key)
  3. Request installation access token using `installation_id` and JWT
  4. Use installation token to authenticate git operations
  5. Token auto-refreshes before expiration
- Falls back to public repo flow if parameters not provided

---

## Dual-Mode Architecture Design

### Mode Detection Logic
The system will automatically detect which mode to use based on parameters:

```python
def determine_auth_mode(repository_url: Optional[str], installation_id: Optional[int]) -> str:
    """
    Determine authentication mode based on provided parameters.

    Returns:
        "public" - Use personal access token (existing behavior)
        "private" - Use GitHub App installation token (new capability)
    """
    if repository_url is not None and installation_id is not None:
        return "private"
    elif repository_url is None and installation_id is None:
        return "public"
    else:
        raise ValueError("Both repository_url and installation_id must be provided together, or neither")
```

### Public Repository Mode (Default)
**When**: No `repository_url` or `installation_id` provided
**Authentication**: Personal access token from `GITHUB_API_TOKEN`
**Repository**: Config-based (e.g., `Cyoda-platform/quart-client-template`)
**Behavior**: Exactly as current implementation - **zero changes**

### Private Repository Mode (New)
**When**: Both `repository_url` AND `installation_id` provided
**Authentication**: GitHub App installation token (auto-generated, auto-refreshed)
**Repository**: Custom URL provided by user
**Behavior**: New code path using installation tokens

### Implementation Principles
1. **No changes to existing code paths** - Public repo mode uses existing logic
2. **Additive only** - New functionality added alongside existing
3. **Clear separation** - Private repo logic in separate code branches
4. **Fail-safe defaults** - Missing params default to public mode
5. **Explicit validation** - Clear errors when params are inconsistent

---

## Phase 1: GitHub App Authentication Infrastructure

### Task 1.1: GitHub App Configuration & Credentials Management
**Priority**: High  
**Dependencies**: None

- [ ] Store GitHub App credentials securely
  - [ ] Add `.pem` file to secure location (not in git)
  - [ ] Add environment variables to `.env.template`:
    - `GITHUB_APP_ID` - The GitHub App ID
    - `GITHUB_APP_PRIVATE_KEY_PATH` - Path to .pem file
    - `GITHUB_APP_CLIENT_ID` - OAuth client ID (if needed)
    - `GITHUB_APP_CLIENT_SECRET` - OAuth client secret (if needed)
  - [ ] Update `common/config/config.py` to load these variables
  - [ ] Add validation for required GitHub App credentials on startup

**Files to modify**:
- `.env.template`
- `common/config/config.py`

---

### Task 1.2: GitHub App JWT Token Generation
**Priority**: High  
**Dependencies**: Task 1.1

- [ ] Create `services/github/auth/` directory structure
- [ ] Implement `services/github/auth/jwt_generator.py`
  - [ ] Create `GitHubAppJWTGenerator` class
  - [ ] Implement JWT token generation using RS256 algorithm
  - [ ] Use PyJWT library for token signing
  - [ ] Set proper expiration (max 10 minutes as per GitHub spec)
  - [ ] Include required claims: `iat`, `exp`, `iss` (app ID)
- [ ] Add comprehensive error handling for:
  - Missing/invalid private key
  - Token generation failures
  - Expiration handling
- [ ] Add unit tests for JWT generation

**Files to create**:
- `services/github/auth/__init__.py`
- `services/github/auth/jwt_generator.py`
- `tests/services/github/auth/test_jwt_generator.py`

**Dependencies to add**:
- `PyJWT[crypto]` (for RS256 signing)
- `cryptography` (for key handling)

---

### Task 1.3: Installation Access Token Management
**Priority**: High  
**Dependencies**: Task 1.2

- [ ] Implement `services/github/auth/installation_token_manager.py`
  - [ ] Create `InstallationTokenManager` class
  - [ ] Implement method to get installation access token from installation ID
  - [ ] Use GitHub API: `POST /app/installations/{installation_id}/access_tokens`
  - [ ] Authenticate with JWT from Task 1.2
  - [ ] Parse response to extract token and expiration
  - [ ] Handle token refresh logic
- [ ] Implement token caching with expiration awareness
  - [ ] Cache tokens per installation_id
  - [ ] Auto-refresh before expiration (e.g., 5 min buffer)
  - [ ] Thread-safe cache implementation
- [ ] Add comprehensive error handling:
  - Invalid installation ID
  - Expired JWT
  - API rate limits
  - Network errors
- [ ] Add unit tests with mocked GitHub API responses

**Files to create**:
- `services/github/auth/installation_token_manager.py`
- `tests/services/github/auth/test_installation_token_manager.py`

---

### Task 1.4: Update GitHub API Client for App Authentication
**Priority**: High
**Dependencies**: Task 1.3

- [ ] Modify `services/github/api/client.py`
  - [ ] Add optional `installation_id` parameter to `__init__`
  - [ ] Add `installation_token_manager` as optional dependency
  - [ ] Update `_get_headers()` to use installation token when available
  - [ ] **CRITICAL: Fallback to personal access token if no installation_id** (preserves existing behavior)
  - [ ] Add method `set_installation(installation_id)` for dynamic switching
  - [ ] Ensure existing code paths work without any changes
- [ ] Update all operation classes to support installation-based auth:
  - [ ] `WorkflowOperations` - support both auth methods
  - [ ] `RepositoryOperations` - support both auth methods
  - [ ] `CollaboratorOperations` - support both auth methods
  - [ ] All methods must work with `installation_id=None` (default)
- [ ] Add integration tests with **BOTH** auth methods:
  - [ ] Test public repos with personal token (existing flow)
  - [ ] Test private repos with installation token (new flow)
  - [ ] Test fallback behavior

**Files to modify**:
- `services/github/api/client.py`
- `services/github/api/workflows.py`
- `services/github/api/repositories.py`
- `services/github/api/collaborators.py`
- `tests/services/github/api/test_client.py`

**Backward Compatibility Requirements**:
- All existing code using `GitHubAPIClient()` without parameters must continue to work
- Default behavior (no installation_id) uses personal access token
- No breaking changes to method signatures

---

## Phase 2: Webhook Endpoint Implementation

### Task 2.1: Create GitHub Webhook Blueprint
**Priority**: High  
**Dependencies**: None

- [ ] Create `routes/github.py` with GitHub webhook blueprint
  - [ ] Define blueprint: `github_bp = Blueprint('github', __name__, url_prefix=f"{config.API_PREFIX}/github")`
  - [ ] Implement webhook endpoint: `POST /api/v1/github/webhook`
  - [ ] Add rate limiting (use existing pattern from other routes)
  - [ ] Add CORS support (already handled globally)
- [ ] Register blueprint in `app_factory.py`
  - [ ] Import `github_bp`
  - [ ] Add `app.register_blueprint(github_bp)` to blueprint registration section

**Files to create**:
- `routes/github.py`

**Files to modify**:
- `app_factory.py`

---

### Task 2.2: Webhook Signature Verification
**Priority**: Critical (Security)  
**Dependencies**: Task 2.1

- [ ] Implement webhook signature verification in `routes/github.py`
  - [ ] Extract `X-Hub-Signature-256` header
  - [ ] Compute HMAC-SHA256 of payload using webhook secret
  - [ ] Compare signatures using constant-time comparison
  - [ ] Reject requests with invalid signatures (401 Unauthorized)
  - [ ] Log security events (invalid signatures)
- [ ] Add webhook secret to configuration
  - [ ] Add `GITHUB_WEBHOOK_SECRET` to `.env.template`
  - [ ] Load in `common/config/config.py`
- [ ] Add unit tests for signature verification

**Files to modify**:
- `routes/github.py`
- `.env.template`
- `common/config/config.py`
- `tests/routes/test_github.py` (create)

---

### Task 2.3: Webhook Event Processing
**Priority**: High  
**Dependencies**: Task 2.2

- [ ] Implement webhook event handlers in `routes/github.py`
  - [ ] Parse `X-GitHub-Event` header to determine event type
  - [ ] Handle `installation` events:
    - [ ] `installation.created` - New installation
    - [ ] `installation.deleted` - Installation removed
    - [ ] `installation.suspend` - Installation suspended
    - [ ] `installation.unsuspend` - Installation unsuspended
  - [ ] Handle `installation_repositories` events:
    - [ ] `installation_repositories.added` - Repos added to installation
    - [ ] `installation_repositories.removed` - Repos removed
  - [ ] Extract relevant data: installation_id, repository info, user info
  - [ ] Return appropriate HTTP status codes (200, 204, 400, 401)
- [ ] Create service for webhook event processing
  - [ ] Create `services/github/webhook_handler.py`
  - [ ] Implement `GitHubWebhookHandler` class
  - [ ] Methods for each event type
  - [ ] Store installation data (see Task 2.4)
- [ ] Add comprehensive logging for all webhook events
- [ ] Add unit tests for each event type

**Files to create**:
- `services/github/webhook_handler.py`
- `tests/services/github/test_webhook_handler.py`

**Files to modify**:
- `routes/github.py`

---

### Task 2.4: Installation Data Storage
**Priority**: High  
**Dependencies**: Task 2.3

- [ ] Design installation data model
  - [ ] Create `services/github/models/installation.py`
  - [ ] Define `InstallationInfo` dataclass:
    - `installation_id: int`
    - `account_login: str` (GitHub username/org)
    - `account_type: str` (User/Organization)
    - `repositories: List[str]` (accessible repo names)
    - `created_at: str`
    - `updated_at: str`
    - `suspended: bool`
- [ ] Implement storage mechanism (choose one):
  - **Option A**: In-memory cache (simple, loses data on restart)
  - **Option B**: Cyoda entity storage (persistent, integrated)
  - **Option C**: Database (if available)
- [ ] Implement CRUD operations:
  - [ ] `save_installation(installation_info)`
  - [ ] `get_installation(installation_id)`
  - [ ] `get_installation_by_account(account_login)`
  - [ ] `delete_installation(installation_id)`
  - [ ] `update_installation_repositories(installation_id, repos)`
- [ ] Add unit tests for storage operations

**Files to create**:
- `services/github/models/installation.py`
- `services/github/installation_store.py`
- `tests/services/github/test_installation_store.py`

**Files to modify**:
- `services/github/models/__init__.py`

---

## Phase 3: Repository Operations with Private Repos

### Task 3.1: Update Repository Resolution for Custom URLs
**Priority**: High  
**Dependencies**: None

- [ ] Create new resolver strategy in `services/github/repository/resolver.py`
  - [ ] Implement `CustomRepositoryResolver` class
  - [ ] Accept custom repository URL from params
  - [ ] Parse repository owner and name from URL
  - [ ] Support various URL formats:
    - `https://github.com/owner/repo`
    - `https://github.com/owner/repo.git`
    - `git@github.com:owner/repo.git`
- [ ] Update `RepositoryResolverFactory`
  - [ ] Add `get_custom_resolver()` method
  - [ ] Add logic to choose resolver based on params
- [ ] Add helper function `parse_github_url(url: str) -> Tuple[str, str]`
  - [ ] Extract owner and repository name
  - [ ] Validate URL format
  - [ ] Handle edge cases
- [ ] Add unit tests for URL parsing and resolution

**Files to modify**:
- `services/github/repository/resolver.py`
- `tests/services/github/repository/test_resolver.py`

---

### Task 3.2: Update GitOperations for Installation Auth
**Priority**: High
**Dependencies**: Task 1.4, Task 3.1

- [ ] Modify `services/github/git/operations.py`
  - [ ] Add **optional** `installation_id` parameter to clone/pull/push methods (default: `None`)
  - [ ] Add **optional** `repository_url` parameter (default: `None` - uses existing config-based URL)
  - [ ] Update `clone_repository()`:
    - [ ] **If `repository_url` is None**: Use existing `config.REPOSITORY_URL.format(repository_name=repository_name)` (public repos)
    - [ ] **If `repository_url` provided**: Use custom URL (private repos)
    - [ ] **If `installation_id` provided**: Get installation token and construct authenticated URL: `https://x-access-token:{token}@github.com/owner/repo.git`
    - [ ] **If `installation_id` is None**: Use existing unauthenticated clone (public repos)
  - [ ] Update `pull()` and `push()`:
    - [ ] **If `installation_id` provided**: Use installation token for remote operations
    - [ ] **If `installation_id` is None**: Use existing git credential helper (public repos)
    - [ ] Handle authentication errors gracefully
  - [ ] **Ensure all existing calls work without changes** (all new params are optional)
- [ ] Update `GitHubService` facade
  - [ ] Add **optional** `installation_id` and `repository_url` params to methods
  - [ ] Pass through to underlying operations
  - [ ] Default values preserve existing behavior
- [ ] Add integration tests with mocked GitHub operations:
  - [ ] Test public repo flow (no installation_id, no custom URL)
  - [ ] Test private repo flow (with installation_id and custom URL)
  - [ ] Test mixed scenarios

**Files to modify**:
- `services/github/git/operations.py`
- `services/github/github_service.py`
- `tests/services/github/git/test_operations.py`

**Backward Compatibility Requirements**:
- All existing calls to `clone_repository(git_branch_id, repository_name)` must work unchanged
- All existing calls to `pull()` and `push()` must work unchanged
- New parameters are optional and only used when explicitly provided

---

### Task 3.3: Update ApplicationBuilderService for Private Repos
**Priority**: High
**Dependencies**: Task 3.2

- [ ] Modify `functions/application_builder_service.py`
  - [ ] Update `build_general_application()` to accept **optional** params from `**params`:
    - `repository_url: Optional[str] = None` - Custom repository URL (private repos)
    - `installation_id: Optional[int] = None` - GitHub App installation ID (private repos)
    - `repository_owner: Optional[str] = None` - Repository owner (parsed from URL)
  - [ ] Extract these params from `**params` with `.get()` (defaults to None)
  - [ ] **Determine authentication mode**:
    - **If `repository_url` and `installation_id` provided**: Use private repo mode
    - **If neither provided**: Use existing public repo mode (current behavior)
  - [ ] Store in `workflow_cache` **only if provided**:
    - `const.REPOSITORY_URL_PARAM = "repository_url"`
    - `const.INSTALLATION_ID_PARAM = "installation_id"`
    - `const.REPOSITORY_OWNER_PARAM = "repository_owner"`
  - [ ] Pass to repository resolution logic (only if provided)
  - [ ] Pass to clone operations (only if provided)
  - [ ] **Preserve existing logic when params not provided**
- [ ] Update `resume_build_general_application()` to:
  - [ ] Check workflow_cache for private repo params
  - [ ] Use cached values if present
  - [ ] Fall back to existing public repo logic if not present
- [ ] Update all downstream methods that perform git operations:
  - [ ] Pass `installation_id` and `repository_url` if available
  - [ ] Maintain existing behavior when not available
- [ ] Add validation:
  - [ ] If `repository_url` provided, `installation_id` **must** be provided (and vice versa)
  - [ ] Validate URL format (if provided)
  - [ ] Check installation has access to repository (if provided)
  - [ ] **Skip validation if params not provided** (public repo mode)
- [ ] Add unit tests for **both** scenarios:
  - [ ] Test public repo flow (existing behavior, no new params)
  - [ ] Test private repo flow (with repository_url and installation_id)
  - [ ] Test validation errors (one param without the other)

**Files to modify**:
- `functions/application_builder_service.py`
- `common/config/const.py` (add new param constants)
- `tests/functions/test_application_builder_service.py`

**Backward Compatibility Requirements**:
- All existing calls to `build_general_application()` without new params must work unchanged
- Public repository workflow (Cyoda-platform repos) continues to work exactly as before
- New parameters are completely optional
- No changes required to existing code that calls this service

---

## Phase 4: Integration & Testing

### Task 4.1: Update Tool Definitions for Private Repos
**Priority**: Medium  
**Dependencies**: Task 3.3

- [ ] Update `workflow_configs/agents/tools/build_general_application_f281/tool.json`
  - [ ] Add optional parameters to schema:
    ```json
    "repository_url": {
      "type": "string",
      "description": "Custom GitHub repository URL for private repositories"
    },
    "installation_id": {
      "type": "integer",
      "description": "GitHub App installation ID for authentication"
    }
    ```
  - [ ] Update description to mention private repository support
- [ ] Update any other tool definitions that interact with repositories

**Files to modify**:
- `workflow_configs/agents/tools/build_general_application_f281/tool.json`
- Other relevant tool definitions

---

### Task 4.2: End-to-End Integration Tests
**Priority**: High
**Dependencies**: All previous tasks

- [ ] Create integration test suite
  - [ ] **Test public repo flow (existing - must not break)**:
    - [ ] Build application without repository_url/installation_id
    - [ ] Verify uses personal access token
    - [ ] Verify clones from Cyoda-platform repos
    - [ ] Verify all existing functionality works
  - [ ] **Test private repo flow (new capability)**:
    - [ ] Build application with repository_url and installation_id
    - [ ] Verify uses installation token
    - [ ] Verify clones from custom repository
    - [ ] Test full flow: webhook → installation storage → token generation → repo operations
  - [ ] **Test mixed scenarios**:
    - [ ] Switch between public and private repos in same session
    - [ ] Multiple users with different repo types
  - [ ] **Test error scenarios**:
    - [ ] Invalid installation ID (should fail gracefully)
    - [ ] Expired tokens (should refresh automatically)
    - [ ] Insufficient permissions (should show clear error)
    - [ ] Invalid repository URLs (should validate and reject)
    - [ ] Missing installation_id when repository_url provided (should reject)
  - [ ] **Test fallback behavior**:
    - [ ] Verify fallback to public repos when no installation_id
    - [ ] Verify existing code paths unchanged
- [ ] Create test fixtures for webhook payloads
- [ ] Mock GitHub API responses appropriately for both auth methods
- [ ] Verify token refresh logic
- [ ] **Verify backward compatibility**: Run all existing tests to ensure nothing breaks

**Files to create**:
- `tests/integration/test_github_app_flow.py`
- `tests/integration/test_public_private_repo_compatibility.py`
- `tests/fixtures/github_webhooks.json`

**Critical Success Criteria**:
- All existing tests pass without modification
- Public repo workflow works exactly as before
- Private repo workflow works with new parameters
- Clear separation between the two modes

---

### Task 4.3: Documentation & Deployment
**Priority**: Medium  
**Dependencies**: Task 4.2

- [ ] Update documentation
  - [ ] Create user guide for installing GitHub App
  - [ ] Document how to provide repository_url and installation_id
  - [ ] Add troubleshooting section
  - [ ] Update API documentation
- [ ] Update deployment configuration
  - [ ] Ensure webhook endpoint is accessible
  - [ ] Configure webhook URL in GitHub App settings
  - [ ] Set up webhook secret
  - [ ] Verify SSL/TLS configuration
- [ ] Add monitoring and logging
  - [ ] Log all webhook events
  - [ ] Log token generation/refresh
  - [ ] Log repository operations with installation auth
  - [ ] Add metrics for GitHub App usage

**Files to create**:
- `docs/github_app_integration.md`
- `docs/user_guide_private_repos.md`

---

## Additional Considerations

### Security Checklist
- [ ] Private key stored securely (not in git, proper file permissions)
- [ ] Webhook signature verification implemented
- [ ] Constant-time signature comparison
- [ ] Rate limiting on webhook endpoint
- [ ] Input validation on all parameters
- [ ] Secure token storage (in-memory, encrypted if persisted)
- [ ] Token expiration handling
- [ ] Audit logging for security events

### Error Handling Checklist
- [ ] Invalid installation ID
- [ ] Expired/revoked installation
- [ ] Insufficient repository permissions
- [ ] Network failures
- [ ] GitHub API rate limits
- [ ] Invalid repository URLs
- [ ] Missing required parameters
- [ ] Webhook signature mismatch

### Backward Compatibility Checklist
- [ ] **Existing public repo flow works without ANY changes**
  - [ ] `build_general_application()` works with existing parameters only
  - [ ] Clone operations work with repository_name only
  - [ ] Git operations work without installation_id
  - [ ] GitHub API calls work with personal access token
- [ ] **All new parameters are optional**
  - [ ] `repository_url` defaults to None
  - [ ] `installation_id` defaults to None
  - [ ] `repository_owner` defaults to None
  - [ ] System detects mode based on parameter presence
- [ ] **Graceful fallback to personal access token**
  - [ ] When installation_id is None, use personal token
  - [ ] When repository_url is None, use config-based URL
  - [ ] No errors when new params not provided
- [ ] **No breaking changes to existing APIs**
  - [ ] All method signatures maintain backward compatibility
  - [ ] All existing calls work without modification
  - [ ] No required parameters added to existing methods
- [ ] **Existing tests still pass**
  - [ ] Run full test suite without modifications
  - [ ] All existing integration tests pass
  - [ ] No test failures due to new code
- [ ] **Clear separation of concerns**
  - [ ] Public repo logic isolated from private repo logic
  - [ ] Authentication mode determined by parameter presence
  - [ ] No mixing of authentication methods

---

## Questions for Clarification

1. **Installation ID Discovery**: How will users provide their installation_id? Options:
   - **Manual input in UI** - User copies installation ID from GitHub and pastes it
   - **Automatic discovery via OAuth flow** - User authorizes and we get installation ID automatically
   - **Lookup by repository URL** - We query GitHub API to find installation for a repo (requires user auth)
   - **From webhook** - Store installation IDs when users install the app, let them select from list

2. **Storage Preference**: Where should installation data be stored?
   - **In-memory** (simple, ephemeral) - Lost on restart, good for MVP
   - **Cyoda entities** (persistent, integrated) - Survives restarts, integrated with existing system
   - **External database** - If you have one available

3. **Webhook Secret**: Do you have the webhook secret, or should we generate one?
   - If you already configured the GitHub App, you should have set a webhook secret
   - We need this secret to verify webhook signatures

4. **Repository Permissions**: What permissions does the GitHub App need?
   - **Contents**: Read/Write (required for clone, push, pull)
   - **Metadata**: Read (required for repository info)
   - **Pull requests**: Read/Write (if you want to create PRs)
   - **Workflows**: Read/Write (if you want to trigger GitHub Actions)
   - **Other?**

5. **Multi-Repository Support**: Should one installation support multiple repositories simultaneously?
   - Yes - User can work with different repos in different chats
   - Need to validate installation has access to requested repo

6. **User Association**: How do we associate GitHub installations with Cyoda users?
   - **By GitHub username** - Match GitHub account to Cyoda user
   - **By email** - Match email addresses
   - **Manual linking in UI** - User explicitly links their installation
   - **No association** - Any user can use any installation_id (less secure)

7. **Additional Parameters Needed?**
   - Do we need `repository_owner` as a separate parameter, or parse from URL?
   - Do we need `repository_name` as a separate parameter, or parse from URL?
   - Should we support both HTTPS and SSH URLs?
   - Do we need to specify which repositories the installation token should have access to?

---

## Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Auth Infrastructure | 4 tasks | 2-3 days |
| Phase 2: Webhook Implementation | 4 tasks | 2-3 days |
| Phase 3: Repository Operations | 3 tasks | 2-3 days |
| Phase 4: Integration & Testing | 3 tasks | 2-3 days |
| **Total** | **14 tasks** | **8-12 days** |

---

## Success Criteria

### Public Repository Support (Existing - Must Not Break)
- [ ] **All existing public repository workflows work unchanged**
- [ ] Users can build applications with Python/Java without new parameters
- [ ] System clones from `Cyoda-platform/quart-client-template` and `Cyoda-platform/java-client-template`
- [ ] Git operations use personal access token (existing behavior)
- [ ] All existing tests pass without modification
- [ ] No performance degradation for public repo operations

### Private Repository Support (New Capability)
- [ ] Users can install Cyoda AI Assistant GitHub App on their account/org
- [ ] Webhook endpoint receives and processes installation events
- [ ] System generates valid installation access tokens
- [ ] Users can provide private repository URL and installation_id parameters
- [ ] System successfully clones private repositories using installation token
- [ ] System can push changes to private repositories
- [ ] System can pull changes from private repositories
- [ ] Token refresh works automatically before expiration

### Integration & Quality
- [ ] **Seamless switching between public and private repos**
- [ ] Clear error messages when private repo params are invalid
- [ ] Comprehensive test coverage (>80%) for both modes
- [ ] Documentation complete and accurate for both workflows
- [ ] Security review passed (webhook signatures, token storage, etc.)
- [ ] No breaking changes to any existing APIs or workflows
- [ ] Performance is acceptable for both authentication methods

