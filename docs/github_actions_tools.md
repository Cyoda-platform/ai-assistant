# GitHub Actions Tools

This document describes the GitHub Actions workflow tools available in the AI assistant system.

## Overview

The GitHub Actions tools allow AI agents to trigger, monitor, and manage GitHub Actions workflows programmatically. These tools are particularly useful for CI/CD automation, build processes, and deployment workflows.

## Available Tools

### 1. `run_github_action` (Recommended)

**High-level tool that triggers a workflow and waits for completion with timeout.**

```python
await run_github_action(
    technical_id, entity,
    repo="java-client-template",
    workflow_id="build.yml",
    ref="main",
    inputs={
        "branch": "main",
        "build_type": "compile-only"
    },
    timeout_minutes=2
)
```

**Parameters:**
- `repo` (required): Repository name
- `workflow_id` (required): Workflow file name (e.g., "build.yml")
- `owner` (optional): Repository owner (defaults to config value)
- `ref` (optional): Git branch/tag (defaults to "main")
- `inputs` (optional): Workflow input parameters
- `timeout_minutes` (optional): Timeout in minutes (defaults to 2)

**Returns:**
```json
{
  "status": "completed",
  "conclusion": "success",
  "success": true,
  "run_id": "12345",
  "tracker_id": "tracker_abc123",
  "elapsed_time_seconds": 45,
  "html_url": "https://github.com/owner/repo/actions/runs/12345",
  "workflow_name": "Build",
  "repository": "owner/repo",
  "head_branch": "main",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:05:00Z"
}
```

**Timeout Response:**
```json
{
  "status": "timeout",
  "message": "Workflow did not complete within 2 minutes",
  "run_id": "12345",
  "tracker_id": "tracker_abc123",
  "elapsed_time_seconds": 120,
  "timeout_seconds": 120
}
```

### 2. `trigger_github_workflow`

**Low-level tool to trigger a workflow and get run ID.**

```python
await trigger_github_workflow(
    technical_id, entity,
    repo="java-client-template",
    workflow_id="build.yml",
    ref="main",
    inputs={"build_type": "compile-only"}
)
```

**Returns:**
```json
{
  "status": "success",
  "message": "Workflow 'build.yml' triggered successfully",
  "run_id": "12345",
  "tracker_id": "tracker_abc123",
  "repository": "owner/repo",
  "ref": "main"
}
```

### 3. `monitor_workflow_run`

**Get detailed status information about a workflow run.**

```python
await monitor_workflow_run(
    technical_id, entity,
    repo="java-client-template",
    run_id="12345"
)
```

### 4. `get_workflow_run_status`

**Get simple status string for a workflow run.**

```python
await get_workflow_run_status(
    technical_id, entity,
    repo="java-client-template",
    run_id="12345"
)
```

**Returns:** `"completed - success"` or `"in_progress"` etc.

## Configuration

### Environment Variables

- `GH_TOKEN`: GitHub personal access token (required)
- `GH_DEFAULT_OWNER`: Default repository owner (defaults to "Cyoda-platform")
- `GH_DEFAULT_REPOS`: Comma-separated list of default repositories

### GitHub Token Setup

1. Create a GitHub personal access token with appropriate permissions:
   - `repo` scope for private repositories
   - `public_repo` scope for public repositories
   - `actions:write` permission for triggering workflows

2. Set the environment variable:
   ```bash
   export GH_TOKEN="your_github_token_here"
   ```

## Usage Examples

### Example 1: Simple Build Trigger

```python
# Trigger a build and wait for completion
result = await run_github_action(
    technical_id, entity,
    repo="java-client-template",
    workflow_id="build.yml",
    inputs={"build_type": "compile-only"}
)

# Check if successful
result_data = json.loads(result)
if result_data.get("success"):
    print("Build completed successfully!")
else:
    print(f"Build failed: {result_data.get('conclusion')}")
```

### Example 2: Deployment with Custom Timeout

```python
# Deploy with longer timeout
result = await run_github_action(
    technical_id, entity,
    repo="my-app",
    workflow_id="deploy.yml",
    ref="production",
    inputs={
        "environment": "prod",
        "version": "v1.2.3"
    },
    timeout_minutes=10
)
```

### Example 3: Manual Control

```python
# Trigger workflow
trigger_result = await trigger_github_workflow(
    technical_id, entity,
    repo="java-client-template",
    workflow_id="build.yml"
)

# Get run ID
trigger_data = json.loads(trigger_result)
run_id = trigger_data.get("run_id")

# Monitor manually
while True:
    status = await get_workflow_run_status(
        technical_id, entity,
        repo="java-client-template",
        run_id=run_id
    )
    
    if "completed" in status:
        break
    
    await asyncio.sleep(30)  # Wait 30 seconds
```

## Error Handling

All tools return error messages as strings when something goes wrong:

- `"Error: GH_TOKEN not configured in environment variables"`
- `"Missing required parameters: workflow_id"`
- `"Failed to trigger workflow: <details>"`
- `"Error: Failed to get status for run ID 'xyz'"`

## Best Practices

1. **Use `run_github_action` for most cases** - it handles the complete workflow lifecycle
2. **Set appropriate timeouts** - default 2 minutes may not be enough for complex builds
3. **Handle timeouts gracefully** - workflows may continue running even after timeout
4. **Check the `success` field** in results to determine if the workflow passed
5. **Use the `html_url`** to provide users with links to view detailed logs
6. **Include meaningful `tracker_id`** values for easier debugging

## Tool Configurations

The tools are available in workflow configurations:

- `trigger_github_workflow_nw3v`
- `monitor_workflow_run_0hve` 
- `run_github_action_ozv1`

Add them to your agent configurations as needed.


https://www.google-analytics.com/g/collect?v=2&tid=G-Q5X63SWG2Y&gtm=45je5861h1v9108329830za200zb9226798631zd9226798631&_p=1754670045412&gcd=13l3l3l3l1l1&npa=0&dma=0&tag_exp=101509157~103116026~103200004~103233427~104527907~104528501~104684208~104684211~104948813~105103161~105103163~105135708~105135710&cid=1955764247.1754603976&ul=en-us&sr=1920x1080&uaa=x86&uab=64&uafvl=Not)A%253BBrand%3B8.0.0.0%7CChromium%3B138.0.7204.183&uamb=0&uam=&uap=Linux&uapv=6.14.0&uaw=0&are=1&frm=0&pscdl=noapi&_eu=AEAAAAQ&sid=1754670045&sct=2&seg=0&dl=https%3A%2F%2Fai.cyoda.net%2F&dt=Cyoda%20AI%20Assistant&_s=2&tfd=5482