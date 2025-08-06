"""
Test round-trip conversion

Tests that verify the complete round-trip conversion:
workflow_configs -> workflow_config_code -> workflow_config_generated
"""

import pytest
import json
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from convert_configs_to_code import WorkflowConfigConverter
from convert_code_to_configs import CodeToConfigConverter


class TestRoundTripConversion:
    """Test complete round-trip conversion"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_original = tempfile.mkdtemp(prefix="test_original_")
        temp_code = tempfile.mkdtemp(prefix="test_code_")
        temp_generated = tempfile.mkdtemp(prefix="test_generated_")
        
        yield Path(temp_original), Path(temp_code), Path(temp_generated)
        
        # Cleanup
        shutil.rmtree(temp_original, ignore_errors=True)
        shutil.rmtree(temp_code, ignore_errors=True)
        shutil.rmtree(temp_generated, ignore_errors=True)
    
    def create_complete_test_configs(self, original_dir: Path) -> Dict[str, Any]:
        """Create a complete set of test configurations"""
        configs = {}
        
        # Create agent config
        agent_dir = original_dir / "agents" / "test_agent_123"
        agent_dir.mkdir(parents=True)
        
        agent_config = {
            "type": "agent",
            "tools": [
                {"name": "test_tool_789"}
            ],
            "messages": [
                {"content_from_file": "test_prompt_abc"}
            ]
        }
        
        with open(agent_dir / "agent.json", 'w') as f:
            json.dump(agent_config, f, indent=2)
        
        configs["agent"] = agent_config
        
        # Create message config
        message_dir = original_dir / "messages" / "test_message_456"
        message_dir.mkdir(parents=True)
        
        message_content = """Welcome to the test application!
This is a multi-line message.

Please proceed with the next steps."""
        
        with open(message_dir / "message.md", 'w') as f:
            f.write(message_content)
        
        meta_config = {"type": "message"}
        with open(message_dir / "meta.json", 'w') as f:
            json.dump(meta_config, f, indent=2)
        
        configs["message"] = message_content
        
        # Create tool config
        tool_dir = original_dir / "tools" / "test_tool_789"
        tool_dir.mkdir(parents=True)
        
        tool_config = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function for validation",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"}
                    },
                    "required": ["param1"],
                    "additionalProperties": False
                }
            }
        }
        
        with open(tool_dir / "tool.json", 'w') as f:
            json.dump(tool_config, f, indent=2)
        
        configs["tool"] = tool_config
        
        # Create prompt config
        prompt_dir = original_dir / "prompts" / "test_prompt_abc"
        prompt_dir.mkdir(parents=True)
        
        prompt_content = """You are a helpful assistant.
Please help the user with their request.
Be concise and accurate in your responses."""
        
        with open(prompt_dir / "message_0.md", 'w') as f:
            f.write(prompt_content)
        
        configs["prompt"] = prompt_content
        
        # Create workflow config
        workflow_dir = original_dir / "workflows"
        workflow_dir.mkdir(parents=True)
        
        workflow_config = {
            "name": "test_workflow",
            "states": {
                "start": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.test_agent_123"}
                            ],
                            "criterion": {
                                "function": {
                                    "name": "FunctionProcessor.test_tool_789"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        with open(workflow_dir / "test_workflow.json", 'w') as f:
            json.dump(workflow_config, f, indent=2)
        
        configs["workflow"] = workflow_config
        
        return configs
    
    def test_complete_roundtrip_conversion(self, temp_dirs):
        """Test complete round-trip conversion preserves all data"""
        original_dir, code_dir, generated_dir = temp_dirs
        
        # Create original configs
        original_configs = self.create_complete_test_configs(original_dir)
        
        # Step 1: Convert JSON to Python code
        json_to_code_converter = WorkflowConfigConverter(str(original_dir), str(code_dir))
        json_to_code_converter.convert_all()
        
        # Verify Python code was generated
        assert (code_dir / "agents" / "test_agent_123" / "agent.py").exists()
        assert (code_dir / "messages" / "test_message_456" / "message.py").exists()
        assert (code_dir / "tools" / "test_tool_789" / "tool.py").exists()
        assert (code_dir / "prompts" / "test_prompt_abc" / "prompt.py").exists()
        assert (code_dir / "workflows" / "test_workflow" / "workflow.py").exists()
        
        # Step 2: Convert Python code back to JSON
        code_to_json_converter = CodeToConfigConverter(str(code_dir), str(generated_dir))
        code_to_json_converter.convert_all()
        
        # Verify JSON was regenerated
        assert (generated_dir / "agents" / "test_agent_123" / "agent.json").exists()
        assert (generated_dir / "messages" / "test_message_456" / "message.md").exists()
        assert (generated_dir / "tools" / "test_tool_789" / "tool.json").exists()
        assert (generated_dir / "prompts" / "test_prompt_abc" / "message_0.md").exists()
        assert (generated_dir / "workflows" / "test_workflow.json").exists()
        
        # Step 3: Compare original and generated configs
        self.compare_agent_configs(original_dir, generated_dir, "test_agent_123")
        self.compare_message_configs(original_dir, generated_dir, "test_message_456")
        self.compare_tool_configs(original_dir, generated_dir, "test_tool_789")
        self.compare_prompt_configs(original_dir, generated_dir, "test_prompt_abc")
        self.compare_workflow_configs(original_dir, generated_dir, "test_workflow")
    
    def compare_agent_configs(self, original_dir: Path, generated_dir: Path, agent_name: str):
        """Compare original and generated agent configurations"""
        # Load original
        with open(original_dir / "agents" / agent_name / "agent.json", 'r') as f:
            original = json.load(f)
        
        # Load generated
        with open(generated_dir / "agents" / agent_name / "agent.json", 'r') as f:
            generated = json.load(f)
        
        # Compare essential fields
        assert original["type"] == generated["type"]
        assert original["tools"] == generated["tools"]
        assert original["messages"] == generated["messages"]
    
    def compare_message_configs(self, original_dir: Path, generated_dir: Path, message_name: str):
        """Compare original and generated message configurations"""
        # Load original content
        with open(original_dir / "messages" / message_name / "message.md", 'r') as f:
            original_content = f.read().strip()
        
        # Load generated content
        with open(generated_dir / "messages" / message_name / "message.md", 'r') as f:
            generated_content = f.read().strip()
        
        # Compare content
        assert original_content == generated_content
        
        # Verify meta.json exists
        assert (generated_dir / "messages" / message_name / "meta.json").exists()
    
    def compare_tool_configs(self, original_dir: Path, generated_dir: Path, tool_name: str):
        """Compare original and generated tool configurations"""
        # Load original
        with open(original_dir / "tools" / tool_name / "tool.json", 'r') as f:
            original = json.load(f)
        
        # Load generated
        with open(generated_dir / "tools" / tool_name / "tool.json", 'r') as f:
            generated = json.load(f)
        
        # Compare essential fields
        assert original["type"] == generated["type"]
        assert original["function"]["name"] == generated["function"]["name"]
        assert original["function"]["description"] == generated["function"]["description"]
        assert original["function"]["parameters"] == generated["function"]["parameters"]
    
    def compare_prompt_configs(self, original_dir: Path, generated_dir: Path, prompt_name: str):
        """Compare original and generated prompt configurations"""
        # Load original content
        with open(original_dir / "prompts" / prompt_name / "message_0.md", 'r') as f:
            original_content = f.read().strip()
        
        # Load generated content
        with open(generated_dir / "prompts" / prompt_name / "message_0.md", 'r') as f:
            generated_content = f.read().strip()
        
        # Compare content
        assert original_content == generated_content
    
    def compare_workflow_configs(self, original_dir: Path, generated_dir: Path, workflow_name: str):
        """Compare original and generated workflow configurations"""
        # Load original
        with open(original_dir / "workflows" / f"{workflow_name}.json", 'r') as f:
            original = json.load(f)
        
        # Load generated
        with open(generated_dir / "workflows" / f"{workflow_name}.json", 'r') as f:
            generated = json.load(f)
        
        # Compare essential fields
        assert original["name"] == generated["name"]
        assert original["states"] == generated["states"]
    
    def test_data_preservation(self, temp_dirs):
        """Test that no data is lost during round-trip conversion"""
        original_dir, code_dir, generated_dir = temp_dirs
        
        # Create configs with special characters and formatting
        agent_dir = original_dir / "agents" / "special_agent_test"
        agent_dir.mkdir(parents=True)
        
        special_config = {
            "type": "agent",
            "tools": [
                {"name": "tool_with_special_chars_!@#$%"}
            ],
            "messages": [
                {"content_from_file": "prompt_with_unicode_🚀"}
            ],
            "custom_field": "This should be preserved",
            "nested": {
                "deep": {
                    "value": 42,
                    "list": [1, 2, 3, "string"]
                }
            }
        }
        
        with open(agent_dir / "agent.json", 'w') as f:
            json.dump(special_config, f, indent=2)
        
        # Run round-trip conversion
        json_to_code_converter = WorkflowConfigConverter(str(original_dir), str(code_dir))
        json_to_code_converter.convert_all()
        
        code_to_json_converter = CodeToConfigConverter(str(code_dir), str(generated_dir))
        code_to_json_converter.convert_all()
        
        # Load generated config
        with open(generated_dir / "agents" / "special_agent_test" / "agent.json", 'r') as f:
            generated_config = json.load(f)
        
        # Verify all data is preserved
        assert generated_config["type"] == special_config["type"]
        assert generated_config["tools"] == special_config["tools"]
        assert generated_config["messages"] == special_config["messages"]
        assert generated_config["custom_field"] == special_config["custom_field"]
        assert generated_config["nested"] == special_config["nested"]
    
    def test_unicode_and_special_characters(self, temp_dirs):
        """Test handling of unicode and special characters"""
        original_dir, code_dir, generated_dir = temp_dirs
        
        # Create message with unicode content
        message_dir = original_dir / "messages" / "unicode_message_test"
        message_dir.mkdir(parents=True)
        
        unicode_content = """Welcome! 🎉
This message contains unicode: αβγδε
And special characters: !@#$%^&*()
And emojis: 🚀🎯✅❌🔧💬📝🔄"""
        
        with open(message_dir / "message.md", 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        meta_config = {"type": "message"}
        with open(message_dir / "meta.json", 'w') as f:
            json.dump(meta_config, f, indent=2)
        
        # Run round-trip conversion
        json_to_code_converter = WorkflowConfigConverter(str(original_dir), str(code_dir))
        json_to_code_converter.convert_all()
        
        code_to_json_converter = CodeToConfigConverter(str(code_dir), str(generated_dir))
        code_to_json_converter.convert_all()
        
        # Load generated content
        with open(generated_dir / "messages" / "unicode_message_test" / "message.md", 'r', encoding='utf-8') as f:
            generated_content = f.read().strip()
        
        # Verify unicode content is preserved
        assert generated_content == unicode_content.strip()
        assert "🎉" in generated_content
        assert "αβγδε" in generated_content
        assert "🚀🎯✅❌🔧💬📝🔄" in generated_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
