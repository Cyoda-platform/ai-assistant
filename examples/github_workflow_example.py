#!/usr/bin/env python3
"""
Example script demonstrating how to use the GitHub Actions workflow trigger tool.

This script shows how to:
1. Trigger a GitHub Actions workflow
2. Monitor the workflow run status
3. Handle the complete workflow lifecycle

Prerequisites:
- Set GH_TOKEN environment variable with a GitHub personal access token
- Configure GH_DEFAULT_OWNER in environment (defaults to "Cyoda-platform")
- Ensure the target repository has the specified workflow file

Usage:
    python examples/github_workflow_example.py
"""

import asyncio
import json
import os
import time
from tools.github_operations_service import GitHubOperationsService
from entity.chat.chat import ChatEntity
from unittest.mock import AsyncMock


async def main():
    """Main example function"""
    
    # Check if GitHub token is configured
    if not os.getenv('GH_TOKEN'):
        print("❌ Error: GH_TOKEN environment variable not set")
        print("Please set your GitHub personal access token:")
        print("export GH_TOKEN='your_github_token_here'")
        return
    
    print("🚀 GitHub Actions Workflow Tools Example")
    print("=" * 50)
    
    # Create the GitHub operations service
    github_service = GitHubOperationsService(
        workflow_helper_service=AsyncMock(),
        entity_service=AsyncMock(),
        cyoda_auth_service=AsyncMock(),
        workflow_converter_service=AsyncMock(),
        scheduler_service=AsyncMock(),
        data_service=AsyncMock(),
        dataset=None,
        mock=False  # Set to False for real GitHub API calls
    )
    
    # Create a mock chat entity
    entity = ChatEntity(
        memory_id="example_memory_id",
        technical_id="example_tech_id",
        user_id="example_user_id"
    )
    
    # Configure your workflow parameters here
    workflow_params = {
        "repo": "java-client-template",  # Repository name
        "workflow_id": "build.yml",      # Workflow file name
        "ref": "main",                   # Branch to run on
        "inputs": {                      # Workflow inputs
            "branch": "main",
            "build_type": "compile-only"
        }
    }

    # Example 1: High-level run_github_action (recommended)
    print("\n🎯 Method 1: Using run_github_action (High-level, waits for completion)")
    print("-" * 70)

    try:
        # Run the workflow and wait for completion (2 minute timeout by default)
        run_result = await github_service.run_github_action(
            "example_tech_id", entity,
            timeout_minutes=2,  # Wait up to 2 minutes
            **workflow_params
        )

        print(f"🏁 Final result: {run_result}")

        # Parse the result
        if run_result.startswith('{"status":'):
            result_data = json.loads(run_result)

            if result_data.get("status") == "completed":
                if result_data.get("success"):
                    print(f"✅ Workflow completed successfully!")
                    print(f"🔗 View at: {result_data.get('html_url')}")
                else:
                    print(f"❌ Workflow failed with conclusion: {result_data.get('conclusion')}")
                    print(f"🔗 View at: {result_data.get('html_url')}")
            elif result_data.get("status") == "timeout":
                print(f"⏰ Workflow timed out after {result_data.get('timeout_seconds')} seconds")
                print(f"🔗 Check status at GitHub for run ID: {result_data.get('run_id')}")
        else:
            print(f"❌ Error: {run_result}")

    except Exception as e:
        print(f"❌ Error with run_github_action: {e}")

    print("\n" + "=" * 70)
    print("🔧 Method 2: Using individual tools (Low-level, manual control)")
    print("-" * 70)

    # Example 2: Manual workflow using individual tools
    print("\n📋 Step 1: Triggering GitHub Actions workflow...")
    
    try:
        # Trigger the workflow
        trigger_result = await github_service.trigger_github_workflow(
            "example_tech_id", entity, **workflow_params
        )
        
        print(f"✅ Workflow trigger result: {trigger_result}")
        
        # Parse the result to get run_id and tracker_id
        if trigger_result.startswith('{"status": "success"'):
            result_data = json.loads(trigger_result)
            run_id = result_data.get("run_id")
            tracker_id = result_data.get("tracker_id")
            
            print(f"🔍 Run ID: {run_id}")
            print(f"🏷️  Tracker ID: {tracker_id}")
            
            # Example 3: Monitor the workflow run
            print(f"\n📊 Step 2: Monitoring workflow run {run_id}...")
            
            # Monitor the workflow run
            monitor_result = await github_service.monitor_workflow_run(
                "example_tech_id", entity,
                repo="java-client-template",
                run_id=run_id
            )
            
            print(f"📈 Workflow status: {monitor_result}")
            
            # Example 4: Get simple status
            print(f"\n🎯 Step 3: Getting simple workflow status...")

            status_result = await github_service.get_workflow_run_status(
                "example_tech_id", entity,
                repo="java-client-template",
                run_id=run_id
            )

            print(f"📊 Current status: {status_result}")

            # Example 5: Poll for completion (optional)
            print(f"\n⏳ Step 4: Polling for workflow completion...")
            
            max_polls = 10
            poll_interval = 30  # seconds
            
            for i in range(max_polls):
                status = await github_service.get_workflow_run_status(
                    "example_tech_id", entity,
                    repo="java-client-template",
                    run_id=run_id
                )
                
                print(f"Poll {i+1}/{max_polls}: {status}")
                
                if "completed" in status.lower():
                    print("🎉 Workflow completed!")
                    
                    # Get final detailed status
                    final_result = await github_service.monitor_workflow_run(
                        "example_tech_id", entity,
                        repo="java-client-template",
                        run_id=run_id
                    )
                    
                    final_data = json.loads(final_result)
                    conclusion = final_data.get("conclusion", "unknown")
                    html_url = final_data.get("html_url", "")
                    
                    if conclusion == "success":
                        print(f"✅ Workflow succeeded! View at: {html_url}")
                    elif conclusion == "failure":
                        print(f"❌ Workflow failed! View at: {html_url}")
                    else:
                        print(f"⚠️  Workflow completed with status: {conclusion}")
                        print(f"🔗 View at: {html_url}")
                    
                    break
                
                if i < max_polls - 1:  # Don't sleep on the last iteration
                    print(f"⏱️  Waiting {poll_interval} seconds before next poll...")
                    await asyncio.sleep(poll_interval)
            else:
                print("⏰ Polling timeout reached. Workflow may still be running.")
        
        else:
            print(f"❌ Failed to trigger workflow: {trigger_result}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🏁 Example completed!")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
