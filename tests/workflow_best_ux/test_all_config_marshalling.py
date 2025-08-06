"""
Test All Configuration Marshalling

Comprehensive test suite that verifies all workflow_best_ux components
can be marshalled into their config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.agents.chat_assistant.agent import ChatAssistantAgent
from workflow_best_ux.tools.web_search.tool import WebSearchTool
from workflow_best_ux.tools.read_link.tool import ReadLinkTool
from workflow_best_ux.tools.get_cyoda_guidelines.tool import GetCyodaGuidelinesTool
from workflow_best_ux.tools.get_user_info.tool import GetUserInfoTool
from workflow_best_ux.messages.welcome_message.message import WelcomeMessage
from workflow_best_ux.prompts.assistant_prompt.prompt import AssistantPrompt
from workflow_best_ux.workflows.simple_chat_workflow.workflow import simple_chat_workflow


class TestAllConfigMarshalling:
    """Comprehensive test for all configuration marshalling"""
    
    def test_all_components_have_get_name_method(self):
        """Test that all components have static get_name method"""
        components = [
            ChatAssistantAgent,
            WebSearchTool,
            ReadLinkTool,
            GetCyodaGuidelinesTool,
            GetUserInfoTool,
            WelcomeMessage,
            AssistantPrompt
        ]
        
        for component_class in components:
            assert hasattr(component_class, 'get_name'), f"{component_class.__name__} must have get_name method"
            assert callable(component_class.get_name), f"{component_class.__name__} get_name must be callable"
            
            name = component_class.get_name()
            assert isinstance(name, str), f"{component_class.__name__} get_name must return string"
            assert len(name) > 0, f"{component_class.__name__} get_name must return non-empty string"
    
    def test_all_processors_have_get_config_method(self):
        """Test that all processors have get_config method"""
        processors = [
            ChatAssistantAgent(),
            WebSearchTool(),
            ReadLinkTool(),
            GetCyodaGuidelinesTool(),
            GetUserInfoTool(),
            WelcomeMessage()
        ]
        
        for processor in processors:
            assert hasattr(processor, 'get_config'), f"{processor.__class__.__name__} must have get_config method"
            assert callable(processor.get_config), f"{processor.__class__.__name__} get_config must be callable"
            
            config = processor.get_config()
            assert config is not None, f"{processor.__class__.__name__} get_config must return config"
    
    def test_all_configs_have_get_name_method(self):
        """Test that all configs have get_name method"""
        processors = [
            ChatAssistantAgent(),
            WebSearchTool(),
            ReadLinkTool(),
            GetCyodaGuidelinesTool(),
            GetUserInfoTool(),
            WelcomeMessage(),
            AssistantPrompt()
        ]
        
        for processor in processors:
            if hasattr(processor, 'get_config'):
                config = processor.get_config()
                assert hasattr(config, 'get_name'), f"{processor.__class__.__name__} config must have get_name method"
                assert callable(config.get_name), f"{processor.__class__.__name__} config get_name must be callable"
    
    def test_complete_system_marshalling(self):
        """Test complete system marshalling to JSON"""
        # Create complete system configuration
        system_config = {
            "agents": [],
            "tools": [],
            "messages": [],
            "prompts": [],
            "workflows": []
        }
        
        # Add agent
        agent = ChatAssistantAgent()
        agent_config = agent.get_config()
        system_config["agents"].append({
            "name": agent.get_name(),
            "type": "agent",
            "config": {
                "description": agent_config.description,
                "model": {
                    "model_name": agent_config.model_name,
                    "temperature": agent_config.temperature,
                    "max_tokens": agent_config.max_tokens
                },
                "tools": [tool.get_name() for tool in agent_config.get_tools()],
                "prompts": [prompt.get_name() for prompt in agent_config.get_prompts()]
            }
        })
        
        # Add tools
        tools = [WebSearchTool(), ReadLinkTool(), GetCyodaGuidelinesTool(), GetUserInfoTool()]
        for tool in tools:
            tool_config = tool.get_config()
            system_config["tools"].append({
                "name": tool.get_name(),
                "type": "tool",
                "config": {
                    "description": tool_config.description,
                    "parameters": tool_config.get_parameters()
                }
            })
        
        # Add message
        message = WelcomeMessage()
        message_config = message.get_config()
        system_config["messages"].append({
            "name": message.get_name(),
            "type": "message",
            "config": {
                "content": message_config.get_content(),
                "message_type": message_config.message_type
            }
        })
        
        # Add prompt
        prompt = AssistantPrompt()
        prompt_config = prompt.get_config()
        system_config["prompts"].append({
            "name": prompt.get_name(),
            "type": "prompt",
            "config": {
                "content": prompt_config.get_content(),
                "variables": prompt_config.variables
            }
        })
        
        # Add workflow
        workflow_config = simple_chat_workflow()
        system_config["workflows"].append({
            "name": workflow_config["name"],
            "type": "workflow",
            "config": workflow_config
        })
        
        # Convert to JSON
        json_str = json.dumps(system_config, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), "System JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == system_config, "System JSON round-trip must preserve data"
        
        print("✅ Complete system marshalling test passed!")
        print(f"System has {len(parsed['agents'])} agents, {len(parsed['tools'])} tools, {len(parsed['messages'])} messages, {len(parsed['prompts'])} prompts, {len(parsed['workflows'])} workflows")
    
    def test_component_name_consistency(self):
        """Test that component names are consistent between get_name() and configs"""
        # Test agent
        agent = ChatAssistantAgent()
        agent_config = agent.get_config()
        assert agent.get_name() == "chat_assistant", "Agent name must be consistent"
        
        # Test tools
        tools = [
            (WebSearchTool(), "web_search"),
            (ReadLinkTool(), "read_link"),
            (GetCyodaGuidelinesTool(), "get_cyoda_guidelines"),
            (GetUserInfoTool(), "get_user_info")
        ]
        
        for tool, expected_name in tools:
            tool_config = tool.get_config()
            assert tool.get_name() == expected_name, f"Tool {tool.__class__.__name__} name must be {expected_name}"
        
        # Test message
        message = WelcomeMessage()
        message_config = message.get_config()
        assert message.get_name() == "welcome_message", "Message name must be consistent"
        
        # Test prompt
        prompt = AssistantPrompt()
        prompt_config = prompt.get_config()
        assert prompt.get_name() == "assistant_prompt", "Prompt name must be consistent"
    
    def test_workflow_processor_references_valid(self):
        """Test that workflow processor references point to valid components"""
        workflow_config = simple_chat_workflow()
        
        # Get all processor names from workflow
        processor_names = []
        for state_name, state_config in workflow_config["states"].items():
            if "transitions" in state_config:
                for transition in state_config["transitions"]:
                    if "processors" in transition:
                        for processor in transition["processors"]:
                            processor_names.append(processor["name"])
        
        # Create mapping of available components
        available_components = {
            f"AgentProcessor.{ChatAssistantAgent.get_name()}": ChatAssistantAgent,
            f"MessageProcessor.{WelcomeMessage.get_name()}": WelcomeMessage,
            f"FunctionProcessor.{WebSearchTool.get_name()}": WebSearchTool,
            f"FunctionProcessor.{ReadLinkTool.get_name()}": ReadLinkTool,
            f"FunctionProcessor.{GetCyodaGuidelinesTool.get_name()}": GetCyodaGuidelinesTool,
            f"FunctionProcessor.{GetUserInfoTool.get_name()}": GetUserInfoTool
        }
        
        # Check that all processor references are valid
        for processor_name in processor_names:
            assert processor_name in available_components, f"Processor {processor_name} must reference valid component"
    
    def test_json_serialization_of_all_configs(self):
        """Test JSON serialization of all individual configs"""
        configs_to_test = []
        
        # Agent config
        agent = ChatAssistantAgent()
        configs_to_test.append(("agent", agent.get_config()))
        
        # Tool configs
        tools = [WebSearchTool(), ReadLinkTool(), GetCyodaGuidelinesTool(), GetUserInfoTool()]
        for tool in tools:
            configs_to_test.append(("tool", tool.get_config()))
        
        # Message config
        message = WelcomeMessage()
        configs_to_test.append(("message", message.get_config()))
        
        # Prompt config
        prompt = AssistantPrompt()
        configs_to_test.append(("prompt", prompt.get_config()))
        
        # Test each config
        for config_type, config in configs_to_test:
            # Create JSON representation based on type
            if config_type == "agent":
                config_dict = {
                    "description": config.description,
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "tools": [tool.get_name() for tool in config.get_tools()],
                    "prompts": [prompt.get_name() for prompt in config.get_prompts()]
                }
            elif config_type == "tool":
                config_dict = {
                    "description": config.description,
                    "parameters": config.get_parameters()
                }
            elif config_type == "message":
                config_dict = {
                    "content": config.get_content(),
                    "message_type": config.message_type
                }
            elif config_type == "prompt":
                config_dict = {
                    "content": config.get_content(),
                    "variables": config.variables
                }
            
            # Test JSON serialization
            json_str = json.dumps(config_dict, indent=2)
            parsed = json.loads(json_str)
            assert parsed == config_dict, f"{config_type} config JSON round-trip must preserve data"


def run_all_tests():
    """Run all marshalling tests"""
    test = TestAllConfigMarshalling()
    
    print("🧪 Running comprehensive config marshalling tests...")
    
    test.test_all_components_have_get_name_method()
    print("✅ All components have get_name method")
    
    test.test_all_processors_have_get_config_method()
    print("✅ All processors have get_config method")
    
    test.test_all_configs_have_get_name_method()
    print("✅ All configs have get_name method")
    
    test.test_component_name_consistency()
    print("✅ Component names are consistent")
    
    test.test_workflow_processor_references_valid()
    print("✅ Workflow processor references are valid")
    
    test.test_json_serialization_of_all_configs()
    print("✅ All configs can be JSON serialized")
    
    test.test_complete_system_marshalling()
    print("✅ Complete system marshalling works")
    
    print("🎉 All config marshalling tests passed!")


if __name__ == "__main__":
    run_all_tests()
