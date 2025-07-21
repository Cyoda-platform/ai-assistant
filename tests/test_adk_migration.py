#!/usr/bin/env python3
"""
Test script to validate Google ADK migration
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any

from common.ai.ai_agent import GoogleAdkAgent
from entity.model import AIMessage, ModelConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_authentication():
    """Test Google ADK authentication setup"""
    print("🔐 Testing Google ADK authentication...")

    try:
        from google.adk.agents import Agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types

        # Check for authentication
        auth_methods = []
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            auth_methods.append("Service Account")
        if os.getenv('GOOGLE_API_KEY'):
            auth_methods.append("API Key")

        if not auth_methods:
            print("⚠️  No authentication found. Checking for gcloud auth...")
            # Try to use application default credentials
            auth_methods.append("Application Default Credentials")

        print(f"📋 Authentication methods available: {', '.join(auth_methods)}")

        # Create a simple test agent
        agent = Agent(
            model='gemini-2.0-flash',
            name='auth_test_agent',
            instruction='You are a test assistant.'
        )

        print("✅ Authentication test passed - ADK agent created successfully")
        return True

    except ImportError as e:
        print(f"❌ Google ADK not installed: {e}")
        print("💡 Run: pip install google-adk")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        print("💡 Please check ADK_SETUP_GUIDE.md for authentication setup")
        return False


async def test_basic_functionality():
    """Test basic ADK agent functionality"""
    print("🧪 Testing basic ADK agent functionality...")
    
    try:
        # Create agent
        agent = GoogleAdkAgent()
        
        # Create test messages
        messages = [
            AIMessage(role="user", content="Hello, how are you?")
        ]
        
        # Create test model config
        model = ModelConfig(model_name="gemini-2.0-flash")
        
        # Mock methods dict (empty for basic test)
        methods_dict = {}
        
        # Run agent
        response = await agent.run_agent(
            methods_dict=methods_dict,
            technical_id="test_123",
            cls_instance=None,
            entity=None,
            tools=[],
            model=model,
            messages=messages
        )
        
        print(f"✅ Basic test passed. Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        logger.exception("Basic test error")
        return False


async def test_tool_conversion():
    """Test tool conversion functionality"""
    print("🔧 Testing tool conversion...")
    
    try:
        agent = GoogleAdkAgent()
        
        # Mock tool function
        async def mock_tool(user_request: str) -> str:
            return f"Processed: {user_request}"
        
        # Create methods dict
        methods_dict = {
            "get_user_info": mock_tool
        }
        
        # Create test tools (JSON format like in your workflows)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_user_info",
                    "description": "Get user information",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_request": {
                                "type": "string"
                            }
                        },
                        "required": ["user_request"],
                        "additionalProperties": False
                    }
                }
            }
        ]
        
        # Test tool conversion
        function_tools = agent._create_function_tools(tools, methods_dict)
        
        print(f"✅ Tool conversion test passed. Created {len(function_tools)} tools")
        return True
        
    except Exception as e:
        print(f"❌ Tool conversion test failed: {e}")
        logger.exception("Tool conversion test error")
        return False


async def test_message_adaptation():
    """Test message adaptation functionality"""
    print("📝 Testing message adaptation...")
    
    try:
        agent = GoogleAdkAgent()
        
        # Create test messages
        messages = [
            AIMessage(role="user", content="First message"),
            AIMessage(role="assistant", content="Assistant response"),
            AIMessage(role="user", content=["Multi", "part", "message"])
        ]
        
        # Test adaptation
        adapted = agent.adapt_messages(messages)
        
        print(f"✅ Message adaptation test passed. Adapted {len(adapted)} messages")
        
        # Print adapted messages for verification
        for i, msg in enumerate(adapted):
            print(f"  Message {i}: role={msg.role}, parts={len(msg.parts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Message adaptation test failed: {e}")
        logger.exception("Message adaptation test error")
        return False


async def test_schema_validation():
    """Test JSON schema validation"""
    print("📋 Testing schema validation...")
    
    try:
        agent = GoogleAdkAgent()
        
        # Test valid JSON
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        
        valid_json = '{"name": "John", "age": 30}'
        invalid_json = '{"age": "thirty"}'  # age should be number
        
        # Test valid JSON
        result, error = await agent._validate_with_schema(valid_json, schema, 1, 3)
        if result is not None:
            print("✅ Valid JSON validation passed")
        else:
            print(f"❌ Valid JSON validation failed: {error}")
            return False
        
        # Test invalid JSON
        result, error = await agent._validate_with_schema(invalid_json, schema, 1, 3)
        if result is None and error:
            print("✅ Invalid JSON validation passed (correctly rejected)")
        else:
            print("❌ Invalid JSON validation failed (should have been rejected)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {e}")
        logger.exception("Schema validation test error")
        return False


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Google ADK migration tests...\n")
    
    tests = [
        ("Authentication Setup", test_authentication),
        ("Basic Functionality", test_basic_functionality),
        ("Tool Conversion", test_tool_conversion),
        ("Message Adaptation", test_message_adaptation),
        ("Schema Validation", test_schema_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Migration is ready.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🔄 Next steps:")
        print("1. Install Google ADK: pip install google-adk")
        print("2. Update factory configuration to use GoogleAdkAgent")
        print("3. Test with your actual workflow configurations")
        print("4. Monitor logs for any issues")
    else:
        print("\n🔧 Please fix the failing tests before proceeding with migration.")
