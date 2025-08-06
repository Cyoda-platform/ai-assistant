"""
Test JSON to Python code conversion

Tests that verify the conversion from workflow_configs (JSON) to workflow_config_code (Python).
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


class TestJsonToCodeConversion:
    """Test conversion from JSON configs to Python code"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_source = tempfile.mkdtemp(prefix="test_source_")
        temp_target = tempfile.mkdtemp(prefix="test_target_")
        
        yield Path(temp_source), Path(temp_target)
        
        # Cleanup
        shutil.rmtree(temp_source, ignore_errors=True)
        shutil.rmtree(temp_target, ignore_errors=True)
    
    def create_sample_agent_config(self, source_dir: Path) -> Dict[str, Any]:
        """Create a sample agent configuration"""
        agent_dir = source_dir / "agents" / "test_agent_123"
        agent_dir.mkdir(parents=True)
        
        config = {
            "type": "agent",
            "tools": [
                {"name": "test_tool"}
            ],
            "messages": [
                {"content_from_file": "test_prompt"}
            ]
        }
        
        with open(agent_dir / "agent.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def create_sample_message_config(self, source_dir: Path) -> str:
        """Create a sample message configuration"""
        message_dir = source_dir / "messages" / "test_message_456"
        message_dir.mkdir(parents=True)
        
        content = """Welcome to the test application!
This is a multi-line message.

Please proceed with the next steps."""
        
        with open(message_dir / "message.md", 'w') as f:
            f.write(content)
        
        # Create meta.json
        meta = {"type": "message"}
        with open(message_dir / "meta.json", 'w') as f:
            json.dump(meta, f, indent=2)
        
        return content
    
    def create_sample_tool_config(self, source_dir: Path) -> Dict[str, Any]:
        """Create a sample tool configuration"""
        tool_dir = source_dir / "tools" / "test_tool_789"
        tool_dir.mkdir(parents=True)
        
        config = {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "A test function for validation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"}
                    },
                    "required": ["param1"]
                }
            }
        }
        
        with open(tool_dir / "tool.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def create_sample_prompt_config(self, source_dir: Path) -> str:
        """Create a sample prompt configuration"""
        prompt_dir = source_dir / "prompts" / "test_prompt_abc"
        prompt_dir.mkdir(parents=True)
        
        content = """You are a helpful assistant.
Please help the user with their request.
Be concise and accurate in your responses."""
        
        with open(prompt_dir / "message_0.md", 'w') as f:
            f.write(content)
        
        return content
    
    def create_sample_workflow_config(self, source_dir: Path) -> Dict[str, Any]:
        """Create a sample workflow configuration"""
        workflow_dir = source_dir / "workflows"
        workflow_dir.mkdir(parents=True)
        
        config = {
            "name": "test_workflow",
            "states": {
                "start": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.test_agent"}
                            ],
                            "criterion": {
                                "function": {
                                    "name": "FunctionProcessor.test_tool"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        with open(workflow_dir / "test_workflow.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def test_agent_conversion(self, temp_dirs):
        """Test agent configuration conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample agent config
        expected_config = self.create_sample_agent_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify generated files exist
        agent_dir = target_dir / "agents" / "test_agent_123"
        assert agent_dir.exists()
        assert (agent_dir / "__init__.py").exists()
        assert (agent_dir / "agent.py").exists()
        assert (agent_dir / "config.py").exists()
        
        # Verify agent.py structure
        agent_file = agent_dir / "agent.py"
        agent_content = agent_file.read_text()
        
        assert "class TestAgent123AgentConfig" in agent_content
        assert "AgentProcessor" in agent_content
        assert "get_type" in agent_content
        assert "get_name" in agent_content
        assert "get_config" in agent_content
        
        # Verify config.py structure
        config_file = agent_dir / "config.py"
        config_content = config_file.read_text()
        
        assert "def get_config()" in config_content
        assert "lambda params=None:" in config_content
        assert '"type": "agent"' in config_content
    
    def test_message_conversion(self, temp_dirs):
        """Test message configuration conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample message config
        expected_content = self.create_sample_message_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify generated files exist
        message_dir = target_dir / "messages" / "test_message_456"
        assert message_dir.exists()
        assert (message_dir / "__init__.py").exists()
        assert (message_dir / "message.py").exists()
        assert (message_dir / "config.py").exists()
        
        # Verify message.py structure
        message_file = message_dir / "message.py"
        message_content = message_file.read_text()
        
        assert "class TestMessage456MessageConfig" in message_content
        assert "MessageProcessor" in message_content
        assert "get_type" in message_content
        assert "get_name" in message_content
        assert "get_config" in message_content
        
        # Verify config.py contains the content
        config_file = message_dir / "config.py"
        config_content = config_file.read_text()

        assert "def get_config()" in config_content
        assert "def get_meta_config()" in config_content
        assert "lambda params=None:" in config_content
        assert "Welcome to the test application!" in config_content
        assert "multi-line message" in config_content
    
    def test_tool_conversion(self, temp_dirs):
        """Test tool configuration conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample tool config
        expected_config = self.create_sample_tool_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify generated files exist
        tool_dir = target_dir / "tools" / "test_tool_789"
        assert tool_dir.exists()
        assert (tool_dir / "__init__.py").exists()
        assert (tool_dir / "tool.py").exists()
        assert (tool_dir / "config.py").exists()
        
        # Verify tool.py structure
        tool_file = tool_dir / "tool.py"
        tool_content = tool_file.read_text()
        
        assert "class TestTool789ToolConfig" in tool_content
        assert "FunctionProcessor" in tool_content
        assert "get_type" in tool_content
        assert "get_name" in tool_content
        assert "get_tool_name" in tool_content
        assert "get_config" in tool_content
        
        # Verify config.py structure
        config_file = tool_dir / "config.py"
        config_content = config_file.read_text()
        
        assert "def get_config()" in config_content
        assert "lambda params=None:" in config_content
        assert '"type": "function"' in config_content
        assert '"name": "test_function"' in config_content
    
    def test_prompt_conversion(self, temp_dirs):
        """Test prompt configuration conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample prompt config
        expected_content = self.create_sample_prompt_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify generated files exist
        prompt_dir = target_dir / "prompts" / "test_prompt_abc"
        assert prompt_dir.exists()
        assert (prompt_dir / "__init__.py").exists()
        assert (prompt_dir / "prompt.py").exists()
        assert (prompt_dir / "config.py").exists()
        
        # Verify prompt.py structure
        prompt_file = prompt_dir / "prompt.py"
        prompt_content = prompt_file.read_text()
        
        assert "class TestPromptAbcPromptConfig" in prompt_content
        assert "get_name" in prompt_content
        assert "get_config" in prompt_content
        
        # Verify config.py contains the content
        config_file = prompt_dir / "config.py"
        config_content = config_file.read_text()
        
        assert "def get_config()" in config_content
        assert "lambda params=None:" in config_content
        assert "You are a helpful assistant" in config_content
        assert "Be concise and accurate" in config_content
    
    def test_workflow_conversion(self, temp_dirs):
        """Test workflow configuration conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample workflow config
        expected_config = self.create_sample_workflow_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify generated files exist
        workflow_dir = target_dir / "workflows" / "test_workflow"
        assert workflow_dir.exists()
        assert (workflow_dir / "__init__.py").exists()
        assert (workflow_dir / "workflow.py").exists()
        assert (workflow_dir / "config.py").exists()
        
        # Verify workflow.py structure
        workflow_file = workflow_dir / "workflow.py"
        workflow_content = workflow_file.read_text()
        
        assert "class TestWorkflowWorkflowConfig" in workflow_content
        assert "get_name" in workflow_content
        assert "get_config" in workflow_content
        
        # Verify config.py structure
        config_file = workflow_dir / "config.py"
        config_content = config_file.read_text()
        
        assert "def get_config()" in config_content
        assert "lambda params=None:" in config_content
        assert '"name": "test_workflow"' in config_content
        assert '"states"' in config_content
    
    def test_complete_conversion_pipeline(self, temp_dirs):
        """Test complete conversion pipeline with all config types"""
        source_dir, target_dir = temp_dirs
        
        # Create all sample configs
        self.create_sample_agent_config(source_dir)
        self.create_sample_message_config(source_dir)
        self.create_sample_tool_config(source_dir)
        self.create_sample_prompt_config(source_dir)
        self.create_sample_workflow_config(source_dir)
        
        # Run conversion
        converter = WorkflowConfigConverter(str(source_dir), str(target_dir))
        converter.convert_all()
        
        # Verify all directories were created
        assert (target_dir / "agents" / "test_agent_123").exists()
        assert (target_dir / "messages" / "test_message_456").exists()
        assert (target_dir / "tools" / "test_tool_789").exists()
        assert (target_dir / "prompts" / "test_prompt_abc").exists()
        assert (target_dir / "workflows" / "test_workflow").exists()
        
        # Verify main __init__.py was created
        assert (target_dir / "__init__.py").exists()
        
        # Verify each type has its __init__.py
        assert (target_dir / "agents" / "__init__.py").exists()
        assert (target_dir / "messages" / "__init__.py").exists()
        assert (target_dir / "tools" / "__init__.py").exists()
        assert (target_dir / "prompts" / "__init__.py").exists()
        assert (target_dir / "workflows" / "__init__.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
