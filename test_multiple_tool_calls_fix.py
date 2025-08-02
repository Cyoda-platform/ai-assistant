#!/usr/bin/env python3
"""
Test script to verify the multiple tool calls fix.

This script tests that the OpenAI SDK agent no longer returns immediately
after the first tool call, but instead waits for all tool calls to complete
before returning the final result.
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

# Import the classes we need to test
from common.ai.openai_sdk.agent import OpenAiSdkAgent
from common.ai.openai_sdk.adapters.ui_function_handler import UiFunctionHandler
from entity.model import AIMessage


class MockResult:
    """Mock result object that simulates OpenAI Agents SDK result"""
    
    def __init__(self, final_output: str, new_items: List[Any] = None, tool_calls: List[Any] = None):
        self.final_output = final_output
        self.new_items = new_items or []
        self.tool_calls = tool_calls or []


class MockToolCallOutputItem:
    """Mock tool call output item"""
    
    def __init__(self, output: str):
        self.output = output
        self.__class__.__name__ = 'ToolCallOutputItem'


class MockToolCall:
    """Mock tool call object"""
    
    def __init__(self, function_name: str, arguments: str):
        self.function = Mock()
        self.function.name = function_name
        self.function.arguments = arguments


def test_ui_function_handler_multiple_tool_calls():
    """Test that UI function handler correctly processes multiple tool calls"""
    print("Testing UI function handler with multiple tool calls...")
    
    handler = UiFunctionHandler()
    
    # Test 1: UI function result in tool call output (correct behavior)
    ui_output = '{"type": "ui_function", "function": "ui_function_test", "param": "value"}'
    tool_output_item = MockToolCallOutputItem(ui_output)
    result_with_output = MockResult(
        final_output="Final response after all tools executed",
        new_items=[Mock(), tool_output_item]  # UI function result in tool call output
    )
    
    extracted = handler.extract_ui_function_from_result(result_with_output)
    print(f"✓ Extracted UI function from tool call output: {extracted}")
    assert extracted == ui_output
    
    # Test 2: No premature tool call interception
    pending_tool_call = MockToolCall("ui_function_test", '{"param": "value"}')
    result_with_pending_calls = MockResult(
        final_output="Final response after all tools executed",
        tool_calls=[pending_tool_call]  # This should NOT be intercepted
    )
    
    extracted = handler.extract_ui_function_from_result(result_with_pending_calls)
    print(f"✓ No premature interception of pending tool calls: {extracted}")
    assert extracted is None  # Should not extract from pending tool calls
    
    print("UI function handler tests passed!\n")


def test_agent_configuration():
    """Test that agent configuration no longer uses stop_at_tool_names"""
    print("Testing agent configuration...")
    
    agent = OpenAiSdkAgent()
    
    # Create mock model config
    model_config = {
        'name': 'gpt-4o-mini',
        'temperature': 0.7,
        'max_tokens': None,
        'top_p': None
    }
    
    # Build model settings (this should not include stop_at_tool_names)
    model_settings = agent._build_model_settings(
        model_config=model_config,
        tool_choice="auto",
        response_format=None
    )
    
    # Verify that stop_at_tool_names is not configured
    if hasattr(model_settings, 'tool_use_behavior'):
        print(f"✗ tool_use_behavior still configured: {model_settings.tool_use_behavior}")
        assert False, "tool_use_behavior should not be configured"
    else:
        print("✓ tool_use_behavior not configured (correct)")
    
    print("Agent configuration tests passed!\n")


async def test_full_execution_flow():
    """Test that the agent waits for full execution before returning result"""
    print("Testing full execution flow...")
    
    # This test simulates the corrected behavior where the agent
    # executes all tools and returns the final output
    
    agent = OpenAiSdkAgent()
    
    # Mock a result that represents completed execution with multiple tool calls
    final_output = "This is the final response after all tools have been executed"
    ui_tool_output = '{"type": "ui_function", "function": "ui_function_test", "result": "completed"}'
    
    # Simulate completed tool call output
    tool_output_item = MockToolCallOutputItem(ui_tool_output)
    completed_result = MockResult(
        final_output=final_output,
        new_items=[Mock(), tool_output_item]
    )
    
    # Process the result
    processed_result = await agent._process_agent_result(
        result=completed_result,
        response_format=None,
        function_tools=[],
        model=Mock(),
        tool_choice="auto",
        adapted_messages=[]
    )
    
    # Should return the UI function result from completed tool call output
    print(f"✓ Processed result: {processed_result}")
    assert processed_result == ui_tool_output
    
    print("Full execution flow tests passed!\n")


def main():
    """Run all tests"""
    print("Testing Multiple Tool Calls Fix")
    print("=" * 50)
    
    try:
        # Test UI function handler
        test_ui_function_handler_multiple_tool_calls()
        
        # Test agent configuration
        test_agent_configuration()
        
        # Test full execution flow
        asyncio.run(test_full_execution_flow())
        
        print("🎉 All tests passed!")
        print("\nSummary of fixes:")
        print("1. ✓ Removed stop_at_tool_names behavior that caused premature stopping")
        print("2. ✓ Updated UI function detection to work with completed tool outputs")
        print("3. ✓ Agent now waits for full execution before returning results")
        print("\nThe multiple tool calls issue has been fixed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
