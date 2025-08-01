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

    def test_ui_function_extraction(self, agent):
        """Test UI function result extraction"""
        # Test direct UI function JSON
        response_with_ui = 'Here is the result: {"type": "ui_function", "function": "ui_function_list_all_technical_users", "method": "GET", "path": "/api/clients"}'
        extracted = agent._extract_ui_function_result(response_with_ui)
        assert extracted is not None

        parsed = json.loads(extracted)
        assert parsed["type"] == "ui_function"
        assert parsed["function"] == "ui_function_list_all_technical_users"

        # Test the problematic case from user report
        problematic_response = 'Here\'s the M2M user information you requested. Please let me know if there\'s anything else you need! {"type": "ui_function", "function": "ui_function_list_all_technical_users", "method": "GET", "path": "/api/clients", "response_format": "text"}'
        extracted = agent._extract_ui_function_result(problematic_response)
        assert extracted is not None

        parsed = json.loads(extracted)
        assert parsed["type"] == "ui_function"
        assert parsed["function"] == "ui_function_list_all_technical_users"
        assert parsed["method"] == "GET"
        assert parsed["path"] == "/api/clients"
        assert parsed["response_format"] == "text"

        # Test response without UI function
        regular_response = "This is a regular response without UI functions"
        extracted = agent._extract_ui_function_result(regular_response)
        assert extracted is None

    def test_create_function_tools_ui_function(self, agent, mock_context, ui_function_tools):
        """Test creation of UI function tools"""
        function_tools = agent._create_function_tools(ui_function_tools, mock_context)
        
        assert len(function_tools) == 1
        tool = function_tools[0]
        assert tool.name == "ui_function_list_all_technical_users"
        assert "CRITICAL: This is a UI function" in tool.description

    @pytest.mark.asyncio
    async def test_ui_function_execution(self, agent, mock_context, ui_function_tools):
        """Test UI function execution returns clean JSON"""
        function_tools = agent._create_function_tools(ui_function_tools, mock_context)
        ui_tool = function_tools[0]
        
        # Mock ToolContext
        mock_tool_context = Mock()
        
        # Test UI function execution
        args_json = '{"method": "GET", "path": "/api/clients", "response_format": "text"}'
        result = await ui_tool.on_invoke_tool(mock_tool_context, args_json)
        
        # Verify result is clean JSON (no wrapper markers)
        assert not result.startswith("UI_FUNCTION_RESULT:")
        assert not result.endswith(":END_UI_FUNCTION")
        
        # Verify it's valid JSON with correct structure
        parsed_result = json.loads(result)
        assert parsed_result["type"] == const.UI_FUNCTION_PREFIX
        assert parsed_result["function"] == "ui_function_list_all_technical_users"
        assert parsed_result["method"] == "GET"
        assert parsed_result["path"] == "/api/clients"
        assert parsed_result["response_format"] == "text"

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
