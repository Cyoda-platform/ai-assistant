#!/usr/bin/env python3
"""
Integration test for OpenAI SDK Agent UI functions
"""

import json
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from common.ai.openai_sdk_agent import OpenAiSdkAgent
from common.config import const
from entity.model import AIMessage


class MockModel:
    """Mock model for testing"""
    def __init__(self):
        self.model_name = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = None
        self.top_p = None


class MockAgent:
    """Mock OpenAI Agents SDK Agent"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'test_agent')
        self.tools = kwargs.get('tools', [])
        self.instructions = kwargs.get('instruction', '')


class MockRunner:
    """Mock OpenAI Agents SDK Runner"""
    
    @staticmethod
    async def run(starting_agent, input, session=None, run_config=None, max_turns=3):
        """Mock run method that simulates UI function call"""
        # Simulate the agent calling the UI function and returning clean JSON
        mock_result = Mock()
        mock_result.final_output = json.dumps({
            "type": "ui_function",
            "function": "ui_function_list_all_technical_users",
            "method": "GET",
            "path": "/api/clients",
            "response_format": "text"
        })
        return mock_result


class TestOpenAiSdkIntegration:
    """Integration tests for OpenAI SDK Agent"""

    @pytest.fixture
    def agent(self):
        """Create OpenAI SDK agent instance"""
        return OpenAiSdkAgent(max_calls=3)

    @pytest.fixture
    def mock_model(self):
        """Create mock model"""
        return MockModel()

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

    @pytest.fixture
    def messages(self):
        """Create test messages"""
        return [
            AIMessage(role="user", content="Give me all technical/m2m users")
        ]

    @pytest.mark.asyncio
    @patch('common.ai.openai_sdk_agent.Agent', MockAgent)
    @patch('common.ai.openai_sdk_agent.Runner', MockRunner)
    async def test_ui_function_integration(self, agent, mock_model, ui_function_tools, messages):
        """Test complete UI function integration"""
        
        # Mock context
        methods_dict = {}
        technical_id = "test_tech_id"
        cls_instance = Mock()
        entity = Mock()
        
        # Run the agent
        result = await agent.run_agent(
            methods_dict=methods_dict,
            technical_id=technical_id,
            cls_instance=cls_instance,
            entity=entity,
            tools=ui_function_tools,
            model=mock_model,
            messages=messages,
            tool_choice="auto"
        )
        
        # Verify the result is clean JSON (not wrapped with error messages)
        assert result != "I'm unable to provide the list of M2M users at the moment. Please try again later or contact your system administrator for further assistance."
        
        # Verify it's valid JSON
        parsed_result = json.loads(result)
        assert parsed_result["type"] == "ui_function"
        assert parsed_result["function"] == "ui_function_list_all_technical_users"
        assert parsed_result["method"] == "GET"
        assert parsed_result["path"] == "/api/clients"
        assert parsed_result["response_format"] == "text"

    @pytest.mark.asyncio
    async def test_ui_function_detection_in_response(self, agent):
        """Test UI function detection in various response formats"""
        
        # Test clean JSON response (what we want)
        clean_json = '{"type": "ui_function", "function": "ui_function_list_all_technical_users", "method": "GET", "path": "/api/clients", "response_format": "text"}'
        
        # Test if it's detected as UI function JSON
        assert agent._is_ui_function_json(clean_json) == True
        
        # Test extraction
        extracted = agent._extract_ui_function_result(clean_json)
        assert extracted is not None
        
        parsed = json.loads(extracted)
        assert parsed["type"] == "ui_function"
        assert parsed["function"] == "ui_function_list_all_technical_users"

    def test_ui_function_prefix_constant(self):
        """Test that UI function prefix is correctly defined"""
        assert const.UI_FUNCTION_PREFIX == "ui_function"

    @pytest.mark.asyncio
    async def test_error_handling_for_non_ui_functions(self, agent, mock_model):
        """Test that regular functions still work correctly"""
        
        regular_tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        
        # Mock methods dict with a regular function
        methods_dict = {
            "get_weather": AsyncMock(return_value="Sunny, 25°C")
        }
        
        messages = [AIMessage(role="user", content="What's the weather in London?")]
        
        # This should not break even though we're not mocking the full SDK
        # The function creation should work correctly
        from common.ai.openai_sdk_agent import OpenAiSdkAgentContext
        context = OpenAiSdkAgentContext(
            methods_dict=methods_dict,
            technical_id="test_tech_id",
            cls_instance=Mock(),
            entity=Mock()
        )
        
        function_tools = agent._create_function_tools(regular_tools, context)
        assert len(function_tools) == 1
        assert function_tools[0].name == "get_weather"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
