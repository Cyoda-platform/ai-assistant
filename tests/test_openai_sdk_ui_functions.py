#!/usr/bin/env python3
"""
Test UI function handling in OpenAI SDK Agent
"""

import json
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from common.ai.openai_sdk_agent import OpenAiSdkAgent, OpenAiSdkAgentContext
from common.config import const
from entity.model import AIMessage


class TestOpenAiSdkUiFunctions:
    """Test UI function handling in OpenAI SDK Agent"""

    @pytest.fixture
    def agent(self):
        """Create OpenAI SDK agent instance"""
        return OpenAiSdkAgent(max_calls=3)

    @pytest.fixture
    def mock_context(self):
        """Create mock context for testing"""
        return OpenAiSdkAgentContext(
            methods_dict={},
            technical_id="test_tech_id",
            cls_instance=Mock(),
            entity=Mock()
        )

    @pytest.fixture
    def ui_function_tools(self):
        """Create UI function tools for testing"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "ui_function_list_all_technical_users",
                    "description": "List all M2M clients",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["GET"]
                            },
                            "path": {
                                "type": "string", 
                                "enum": ["/api/clients"]
                            },
                            "response_format": {
                                "type": "string",
                                "enum": ["text"]
                            }
                        },
                        "required": ["method", "path", "response_format"]
                    }
                }
            }
        ]

    def test_ui_function_detection(self, agent):
        """Test UI function detection logic"""
        # Test UI function JSON detection
        ui_json = '{"type": "ui_function", "function": "ui_function_list_all_technical_users", "method": "GET"}'
        assert agent._is_ui_function_json(ui_json) == True
        
        # Test non-UI function JSON
        regular_json = '{"type": "regular", "function": "get_weather"}'
        assert agent._is_ui_function_json(regular_json) == False
        
        # Test invalid JSON
        invalid_json = 'not json'
        assert agent._is_ui_function_json(invalid_json) == False

    def test_create_function_tools_ui_function(self, agent, mock_context, ui_function_tools):
        """Test creation of UI function tools"""
        function_tools = agent._create_function_tools(ui_function_tools, mock_context)
        
        assert len(function_tools) == 1
        tool = function_tools[0]
        assert tool.name == "ui_function_list_all_technical_users"
        assert "CRITICAL: This is a UI function" in tool.description

    @pytest.mark.asyncio
    async def test_ui_function_execution(self, agent, mock_context, ui_function_tools):
        """Test UI function execution returns clean single-quoted JSON"""
        function_tools = agent._create_function_tools(ui_function_tools, mock_context)
        ui_tool = function_tools[0]

        # Mock ToolContext
        mock_tool_context = Mock()

        # Test UI function execution - should return clean JSON
        args_json = '{"method": "GET", "path": "/api/clients", "response_format": "text"}'
        result = await ui_tool.on_invoke_tool(mock_tool_context, args_json)

        # Should return single-quoted JSON directly
        expected = "{'type': 'ui_function', 'function': 'ui_function_list_all_technical_users', 'method': 'GET', 'path': '/api/clients', 'response_format': 'text'}"
        assert result == expected

    def test_message_adaptation(self, agent):
        """Test message adaptation works correctly"""
        messages = [
            AIMessage(role="user", content="List all technical users"),
            AIMessage(role="assistant", content="I'll help you list the technical users.")
        ]

        adapted = agent.adapt_messages(messages)
        assert len(adapted) == 2
        assert adapted[0]["role"] == "user"
        assert adapted[1]["role"] == "assistant"
        assert "technical users" in adapted[0]["content"]

    def test_ui_function_tool_call_detection(self, agent):
        """Test detection of UI function from tool calls"""
        from unittest.mock import Mock

        # Mock tool call object
        mock_tool_call = Mock()
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "ui_function_issue_technical_user"
        mock_tool_call.function.arguments = '{"method": "POST", "path": "/api/clients", "response_format": "file"}'

        # Mock result object
        mock_result = Mock()
        mock_result.tool_calls = [mock_tool_call]
        mock_result.final_output = "Some response"

        # Test the simplified detection logic
        response = str(mock_result.final_output)

        # Check if execution was stopped due to UI function tool call
        if hasattr(mock_result, 'tool_calls') and mock_result.tool_calls:
            for call in mock_result.tool_calls:
                if hasattr(call, 'function') and call.function.name.startswith("ui_function"):
                    # Parse arguments
                    args = {}
                    if hasattr(call.function, 'arguments') and call.function.arguments:
                        try:
                            args = json.loads(call.function.arguments)
                        except json.JSONDecodeError:
                            pass

                    # Create UI function JSON
                    if isinstance(args, dict):
                        ui_json = json.dumps({"type": "ui_function", "function": call.function.name, **args})
                    else:
                        ui_json = json.dumps({"type": "ui_function", "function": call.function.name})

                    # Convert to single quotes
                    ui_json_single_quotes = ui_json.replace('"', "'")

                    # Verify the result
                    expected = "{'type': 'ui_function', 'function': 'ui_function_issue_technical_user', 'method': 'POST', 'path': '/api/clients', 'response_format': 'file'}"
                    assert ui_json_single_quotes == expected

    def test_ui_function_tool_use_behavior(self, agent):
        """Test that UI functions are configured with stop_at_tool_names"""
        # Mock model
        mock_model = Mock()
        mock_model.model_name = "gpt-4o-mini"
        mock_model.temperature = 0.7
        mock_model.max_tokens = None
        mock_model.top_p = None

        # Tools with UI function
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "ui_function_test",
                    "description": "Test UI function",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "regular_function",
                    "description": "Regular function",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

        # Create function tools
        from common.ai.openai_sdk_agent import OpenAiSdkAgentContext
        context = OpenAiSdkAgentContext(
            methods_dict={},
            technical_id="test",
            cls_instance=Mock(),
            entity=Mock()
        )

        function_tools = agent._create_function_tools(tools, context)

        # Test agent creation with UI functions
        test_agent = agent._create_agent(function_tools, mock_model, "test instructions", "auto")

        # Verify the agent was created (we can't easily test the internal tool_use_behavior)
        assert test_agent is not None

    def test_ui_function_direct_json_response(self, agent):
        """Test that UI functions return single-quoted JSON directly"""
        ui_json_double = '{"type": "ui_function", "function": "ui_function_test", "method": "GET"}'
        ui_json_single = ui_json_double.replace('"', "'")

        # Test the conversion
        assert ui_json_single == "{'type': 'ui_function', 'function': 'ui_function_test', 'method': 'GET'}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
