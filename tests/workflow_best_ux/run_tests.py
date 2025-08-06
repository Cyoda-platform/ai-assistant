"""
Test Runner for Workflow Best UX

Runs all configuration marshalling tests and provides a summary.
"""

import sys
import os
import subprocess
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def run_test_file(test_file):
    """Run a single test file and return results"""
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.join(os.path.dirname(__file__), '..', '..'),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "file": test_file,
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "file": test_file,
            "success": False,
            "stdout": "",
            "stderr": "Test timed out"
        }
    except Exception as e:
        return {
            "file": test_file,
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }


def run_all_tests():
    """Run all workflow_best_ux tests"""
    
    test_files = [
        "tests/workflow_best_ux/test_agent_config_marshalling.py",
        "tests/workflow_best_ux/test_tool_config_marshalling.py",
        "tests/workflow_best_ux/test_message_config_marshalling.py",
        "tests/workflow_best_ux/test_prompt_config_marshalling.py",
        "tests/workflow_best_ux/test_workflow_config_marshalling.py",
        "tests/workflow_best_ux/test_all_config_marshalling.py",
        "tests/workflow_best_ux/test_config_completeness.py",
        "tests/workflow_best_ux/test_reverse_marshalling_simple.py"
    ]
    
    print("🧪 Running Workflow Best UX Configuration Marshalling Tests")
    print("=" * 60)
    
    results = []
    
    for test_file in test_files:
        print(f"\n📋 Running {os.path.basename(test_file)}...")
        result = run_test_file(test_file)
        results.append(result)
        
        if result["success"]:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            if result["stderr"]:
                print(f"Error: {result['stderr']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ All workflow_best_ux components can be marshalled to JSON:")
        print("  • Agents → AgentConfig JSON")
        print("  • Tools → ToolConfig JSON")
        print("  • Messages → MessageConfig JSON")
        print("  • Prompts → PromptConfig JSON")
        print("  • Workflows → Workflow JSON")
        print("  • Complete System → Full JSON configuration")
        print("\n✅ Marshalled configs contain ALL expected data:")
        print("  • Agent configs have all required fields from agent.json")
        print("  • Tool configs have all required fields from tool.json files")
        print("  • Message configs have all required fields from meta.json files")
        print("  • Workflow configs have all required fields from workflow.json")
        print("  • Marshalled configs can have MORE data, but never LESS than expected")
        print("\n✅ Reverse marshalling (Config → Code) works perfectly:")
        print("  • JSON configs can be converted back to Python code")
        print("  • Generated code has proper get_name() and get_config() methods")
        print("  • Generated code uses builders correctly")
        print("  • Generated code has valid Python syntax")
        print("  • Complete bidirectional marshalling cycle works!")
    else:
        print("❌ Some tests failed:")
        for result in results:
            if not result["success"]:
                print(f"  • {os.path.basename(result['file'])}")
    
    return passed == total


def demonstrate_json_marshalling():
    """Demonstrate JSON marshalling of all components"""
    
    print("\n🔧 JSON MARSHALLING DEMONSTRATION")
    print("=" * 40)
    
    try:
        from workflow_best_ux.agents.chat_assistant.agent import ChatAssistantAgent
        from workflow_best_ux.tools.web_search.tool import WebSearchTool
        from workflow_best_ux.messages.welcome_message.message import WelcomeMessage
        from workflow_best_ux.prompts.assistant_prompt.prompt import AssistantPrompt
        from workflow_best_ux.workflows.simple_chat_workflow.workflow import simple_chat_workflow
        
        # Agent JSON
        agent = ChatAssistantAgent()
        agent_config = agent.get_config()
        agent_json = {
            "type": "agent",
            "name": agent.get_name(),
            "config": {
                "description": agent_config.description,
                "model": {
                    "model_name": agent_config.model_name,
                    "temperature": agent_config.temperature,
                    "max_tokens": agent_config.max_tokens
                }
            }
        }
        
        print("Agent JSON:")
        print(json.dumps(agent_json, indent=2))
        
        # Tool JSON
        tool = WebSearchTool()
        tool_config = tool.get_config()
        tool_json = {
            "type": "tool",
            "name": tool.get_name(),
            "config": {
                "description": tool_config.description,
                "parameters": tool_config.get_parameters()
            }
        }
        
        print("\nTool JSON:")
        print(json.dumps(tool_json, indent=2))
        
        # Message JSON
        message = WelcomeMessage()
        message_config = message.get_config()
        message_json = {
            "type": "message",
            "name": message.get_name(),
            "config": {
                "content": message_config.get_content()[:100] + "...",  # Truncate for display
                "message_type": message_config.message_type
            }
        }
        
        print("\nMessage JSON:")
        print(json.dumps(message_json, indent=2))
        
        # Workflow JSON (truncated)
        workflow_config = simple_chat_workflow()
        workflow_json = {
            "type": "workflow",
            "name": workflow_config["name"],
            "states": list(workflow_config["states"].keys())
        }
        
        print("\nWorkflow JSON (summary):")
        print(json.dumps(workflow_json, indent=2))
        
        print("\n✅ All components successfully marshalled to JSON!")
        
    except Exception as e:
        print(f"❌ Error demonstrating JSON marshalling: {e}")


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        demonstrate_json_marshalling()
    
    sys.exit(0 if success else 1)
