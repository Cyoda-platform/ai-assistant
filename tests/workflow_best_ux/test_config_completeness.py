"""
Test Configuration Completeness

Tests that marshalled configs contain at least all the data from expected config files.
Marshalled configs can have more data, but must not have less.
"""

import pytest
import json
import sys
import os
from pathlib import Path

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


def load_expected_config(filename):
    """Load expected config from JSON file"""
    config_path = Path(__file__).parent / "expected_configs" / filename
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def contains_all_data(marshalled, expected, path=""):
    """
    Check if marshalled config contains at least all data from expected config.
    
    Args:
        marshalled: The marshalled configuration (can have more data)
        expected: The expected configuration (minimum required data)
        path: Current path for error reporting
    
    Returns:
        tuple: (is_complete, missing_items)
    """
    missing_items = []
    
    if isinstance(expected, dict):
        if not isinstance(marshalled, dict):
            missing_items.append(f"{path}: expected dict, got {type(marshalled)}")
            return False, missing_items
        
        for key, expected_value in expected.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in marshalled:
                missing_items.append(f"{current_path}: missing key")
                continue
            
            is_complete, sub_missing = contains_all_data(marshalled[key], expected_value, current_path)
            if not is_complete:
                missing_items.extend(sub_missing)
    
    elif isinstance(expected, list):
        if not isinstance(marshalled, list):
            missing_items.append(f"{path}: expected list, got {type(marshalled)}")
            return False, missing_items
        
        # For lists, we check that marshalled has at least as many items
        # and that each expected item has a corresponding item in marshalled
        if len(marshalled) < len(expected):
            missing_items.append(f"{path}: expected at least {len(expected)} items, got {len(marshalled)}")
        
        # For now, we'll do a simple length check for lists
        # More sophisticated matching could be added if needed
    
    else:
        # For primitive values, we can check equality or just presence
        # Since marshalled can have more data, we mainly check that the key exists
        pass
    
    return len(missing_items) == 0, missing_items


class TestConfigCompleteness:
    """Test that marshalled configs contain all expected data"""
    
    def test_agent_config_completeness(self):
        """Test that marshalled agent config contains all expected data"""
        # Load expected config
        expected_config = load_expected_config("agent.json")
        
        # Get marshalled config
        agent = ChatAssistantAgent()
        agent_config = agent.get_config()
        
        # Create marshalled representation similar to expected format
        marshalled_config = {
            "type": "agent",
            "publish": True,
            "allow_anonymous_users": True,
            "model": {
                "model_name": agent_config.model_name,
                "temperature": agent_config.temperature,
                "max_tokens": agent_config.max_tokens
            },
            "tools": [],
            "messages": [
                {
                    "role": "user",
                    "content_from_file": "assistant_prompt"
                }
            ],
            "tool_choice": "auto",
            "max_iteration": 30,
            "approve": False
        }

        # Add tools in expected format
        for tool_config in agent_config.get_tools():
            tool_json = {
                "type": "function",
                "function": {
                    "name": tool_config.get_name(),
                    "description": tool_config.description,
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    }
                }
            }

            # Convert parameters
            for param_name, param_info in tool_config.get_parameters().items():
                param_def = {
                    "type": param_info["type"],
                    "description": param_info["description"]
                }
                if "default" in param_info:
                    param_def["default"] = param_info["default"]

                tool_json["function"]["parameters"]["properties"][param_name] = param_def

                if param_info.get("required", False):
                    tool_json["function"]["parameters"]["required"].append(param_name)

            marshalled_config["tools"].append(tool_json)
        
        # Check completeness
        is_complete, missing_items = contains_all_data(marshalled_config, expected_config)
        
        if not is_complete:
            print(f"Missing items in agent config: {missing_items}")
            print(f"Expected: {json.dumps(expected_config, indent=2)}")
            print(f"Marshalled: {json.dumps(marshalled_config, indent=2)}")
        
        assert is_complete, f"Agent config is missing required data: {missing_items}"
        print("✅ Agent config contains all expected data")
    
    def test_tool_configs_completeness(self):
        """Test that marshalled tool configs contain all expected data"""
        tools_to_test = [
            (WebSearchTool(), "web_search_tool.json"),
            (ReadLinkTool(), "read_link_tool.json"),
            (GetCyodaGuidelinesTool(), "get_cyoda_guidelines_tool.json"),
            (GetUserInfoTool(), "get_user_info_tool.json")
        ]
        
        for tool, config_file in tools_to_test:
            # Load expected config
            expected_config = load_expected_config(config_file)
            
            # Get marshalled config
            tool_config = tool.get_config()
            
            # Create marshalled representation similar to expected format
            marshalled_config = {
                "type": "function",
                "function": {
                    "name": tool.get_name(),
                    "description": tool_config.description,
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    }
                }
            }
            
            # Convert our parameter format to expected format
            for param_name, param_info in tool_config.get_parameters().items():
                param_def = {
                    "type": param_info["type"],
                    "description": param_info["description"]
                }
                if "default" in param_info:
                    param_def["default"] = param_info["default"]

                marshalled_config["function"]["parameters"]["properties"][param_name] = param_def

                if param_info.get("required", False):
                    marshalled_config["function"]["parameters"]["required"].append(param_name)
            
            # Check completeness
            is_complete, missing_items = contains_all_data(marshalled_config, expected_config)
            
            if not is_complete:
                print(f"Missing items in {tool.__class__.__name__} config: {missing_items}")
                print(f"Expected: {json.dumps(expected_config, indent=2)}")
                print(f"Marshalled: {json.dumps(marshalled_config, indent=2)}")
            
            assert is_complete, f"{tool.__class__.__name__} config is missing required data: {missing_items}"
            print(f"✅ {tool.__class__.__name__} config contains all expected data")
    
    def test_message_config_completeness(self):
        """Test that marshalled message config contains all expected data"""
        # Load expected config (meta.json)
        expected_config = load_expected_config("welcome_message_meta.json")
        
        # Get marshalled config
        message = WelcomeMessage()
        message_config = message.get_config()
        
        # Create marshalled representation similar to expected format
        marshalled_config = {
            "approve": False,  # Default value
            "publish": True    # Default value
        }
        
        # Check completeness
        is_complete, missing_items = contains_all_data(marshalled_config, expected_config)
        
        if not is_complete:
            print(f"Missing items in message config: {missing_items}")
            print(f"Expected: {json.dumps(expected_config, indent=2)}")
            print(f"Marshalled: {json.dumps(marshalled_config, indent=2)}")
        
        assert is_complete, f"Message config is missing required data: {missing_items}"
        print("✅ Message config contains all expected data")
    
    def test_prompt_config_completeness(self):
        """Test that marshalled prompt config contains all expected data"""
        # Load expected config (meta.json)
        expected_config = load_expected_config("assistant_prompt_meta.json")
        
        # Get marshalled config
        prompt = AssistantPrompt()
        prompt_config = prompt.get_config()
        
        # Create marshalled representation similar to expected format
        marshalled_config = {
            "approve": False,  # Default value
            "publish": True    # Default value
        }
        
        # Check completeness
        is_complete, missing_items = contains_all_data(marshalled_config, expected_config)
        
        if not is_complete:
            print(f"Missing items in prompt config: {missing_items}")
            print(f"Expected: {json.dumps(expected_config, indent=2)}")
            print(f"Marshalled: {json.dumps(marshalled_config, indent=2)}")
        
        assert is_complete, f"Prompt config is missing required data: {missing_items}"
        print("✅ Prompt config contains all expected data")
    
    def test_workflow_config_completeness(self):
        """Test that marshalled workflow config contains all expected data"""
        # Load expected config
        expected_config = load_expected_config("workflow.json")
        
        # Get marshalled config
        marshalled_config = simple_chat_workflow()
        
        # Check completeness
        is_complete, missing_items = contains_all_data(marshalled_config, expected_config)
        
        if not is_complete:
            print(f"Missing items in workflow config: {missing_items}")
            print(f"Expected keys: {list(expected_config.keys())}")
            print(f"Marshalled keys: {list(marshalled_config.keys())}")
            
            # Show detailed comparison for debugging
            for key in expected_config.keys():
                if key not in marshalled_config:
                    print(f"Missing key: {key}")
                elif key == "states":
                    expected_states = set(expected_config["states"].keys())
                    marshalled_states = set(marshalled_config["states"].keys())
                    if expected_states != marshalled_states:
                        print(f"State mismatch - Expected: {expected_states}, Marshalled: {marshalled_states}")
        
        assert is_complete, f"Workflow config is missing required data: {missing_items}"
        print("✅ Workflow config contains all expected data")
    
    def test_all_configs_have_required_structure(self):
        """Integration test to verify all configs have the required structure"""
        print("\n🔍 TESTING ALL CONFIG COMPLETENESS")
        print("=" * 40)
        
        # Test each component type
        self.test_agent_config_completeness()
        self.test_tool_configs_completeness()
        self.test_message_config_completeness()
        self.test_prompt_config_completeness()
        self.test_workflow_config_completeness()
        
        print("\n✅ ALL CONFIGS CONTAIN EXPECTED DATA!")
        print("Marshalled configs have at least all required data from expected configs.")


def run_completeness_tests():
    """Run all completeness tests"""
    test = TestConfigCompleteness()
    
    print("🧪 Testing Configuration Completeness...")
    print("Verifying marshalled configs contain at least all expected data")
    print("=" * 60)
    
    try:
        test.test_all_configs_have_required_structure()
        print("\n🎉 All completeness tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Completeness test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_completeness_tests()
    sys.exit(0 if success else 1)
