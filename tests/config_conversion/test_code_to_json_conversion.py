"""
Test Python code to JSON conversion

Tests that verify the conversion from workflow_config_code (Python) to workflow_config_generated (JSON).
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

from convert_code_to_configs import CodeToConfigConverter


class TestCodeToJsonConversion:
    """Test conversion from Python code to JSON configs"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_source = tempfile.mkdtemp(prefix="test_code_source_")
        temp_target = tempfile.mkdtemp(prefix="test_json_target_")
        
        yield Path(temp_source), Path(temp_target)
        
        # Cleanup
        shutil.rmtree(temp_source, ignore_errors=True)
        shutil.rmtree(temp_target, ignore_errors=True)
    
    def create_sample_agent_code(self, source_dir: Path) -> Dict[str, Any]:
        """Create sample agent Python code"""
        # Create agents directory and __init__.py
        agents_dir = source_dir / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "__init__.py").write_text('"""Agents package"""')

        agent_dir = agents_dir / "test_agent_123"
        agent_dir.mkdir(parents=True)

        # Create __init__.py
        (agent_dir / "__init__.py").write_text('"""Test agent package"""')
        
        # Create config.py
        config_code = '''"""
TestAgent123AgentConfig Configuration
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "tools": [
            {"name": "test_tool"}
        ],
        "messages": [
            {"content_from_file": "test_prompt"}
        ]
    }
'''
        (agent_dir / "config.py").write_text(config_code)
        
        # Create agent.py
        agent_code = '''"""
TestAgent123AgentConfig Agent
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class TestAgent123AgentConfig(AgentProcessor):
    """Agent configuration for test_agent_123"""
    
    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()
    
    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{TestAgent123AgentConfig.get_type()}.test_agent_123"
    
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
test_agent_123_agent = TestAgent123AgentConfig()
'''
        (agent_dir / "agent.py").write_text(agent_code)
        
        return {
            "type": "agent",
            "tools": [{"name": "test_tool"}],
            "messages": [{"content_from_file": "test_prompt"}]
        }
    
    def create_sample_message_code(self, source_dir: Path) -> str:
        """Create sample message Python code"""
        # Create messages directory and __init__.py
        messages_dir = source_dir / "messages"
        messages_dir.mkdir(parents=True)
        (messages_dir / "__init__.py").write_text('"""Messages package"""')

        message_dir = messages_dir / "test_message_456"
        message_dir.mkdir(parents=True)

        # Create __init__.py
        (message_dir / "__init__.py").write_text('"""Test message package"""')
        
        content = """Welcome to the test application!
This is a multi-line message.

Please proceed with the next steps."""
        
        # Create config.py
        config_code = f'''"""
TestMessage456MessageConfig Configuration
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """{content}"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {{'type': 'message'}}
'''
        (message_dir / "config.py").write_text(config_code)
        
        # Create message.py
        message_code = '''"""
TestMessage456MessageConfig Message
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config


class TestMessage456MessageConfig(MessageProcessor):
    """Message configuration for test_message_456"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{TestMessage456MessageConfig.get_type()}.test_message_456"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get message configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_meta_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get message meta configuration"""
        meta_factory = get_meta_config()
        return meta_factory(params or {})


# Create singleton instance
test_message_456_message = TestMessage456MessageConfig()
'''
        (message_dir / "message.py").write_text(message_code)
        
        return content
    
    def create_sample_tool_code(self, source_dir: Path) -> Dict[str, Any]:
        """Create sample tool Python code"""
        # Create tools directory and __init__.py
        tools_dir = source_dir / "tools"
        tools_dir.mkdir(parents=True)
        (tools_dir / "__init__.py").write_text('"""Tools package"""')

        tool_dir = tools_dir / "test_tool_789"
        tool_dir.mkdir(parents=True)

        # Create __init__.py
        (tool_dir / "__init__.py").write_text('"""Test tool package"""')
        
        # Create config.py
        config_code = '''"""
TestTool789ToolConfig Configuration
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
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
'''
        (tool_dir / "config.py").write_text(config_code)
        
        # Create tool.py
        tool_code = '''"""
TestTool789ToolConfig Tool
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class TestTool789ToolConfig(FunctionProcessor):
    """Tool configuration for test_tool_789"""
    
    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()
    
    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{TestTool789ToolConfig.get_type()}.test_tool_789"
    
    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "test_tool_789"
    
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
test_tool_789_tool = TestTool789ToolConfig()
'''
        (tool_dir / "tool.py").write_text(tool_code)
        
        return {
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
    
    def create_sample_prompt_code(self, source_dir: Path) -> str:
        """Create sample prompt Python code"""
        # Create prompts directory and __init__.py
        prompts_dir = source_dir / "prompts"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "__init__.py").write_text('"""Prompts package"""')

        prompt_dir = prompts_dir / "test_prompt_abc"
        prompt_dir.mkdir(parents=True)

        # Create __init__.py
        (prompt_dir / "__init__.py").write_text('"""Test prompt package"""')
        
        content = """You are a helpful assistant.
Please help the user with their request.
Be concise and accurate in your responses."""
        
        # Create config.py
        config_code = f'''"""
TestPromptAbcPromptConfig Configuration
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """{content}"""
'''
        (prompt_dir / "config.py").write_text(config_code)
        
        # Create prompt.py
        prompt_code = '''"""
TestPromptAbcPromptConfig Prompt
"""

from .config import get_config
from typing import Any, Dict


class TestPromptAbcPromptConfig:
    """Prompt configuration for test_prompt_abc"""
    
    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "test_prompt_abc"
    
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
test_prompt_abc_prompt = TestPromptAbcPromptConfig()
'''
        (prompt_dir / "prompt.py").write_text(prompt_code)
        
        return content
    
    def test_agent_reverse_conversion(self, temp_dirs):
        """Test agent code to JSON conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample agent code
        expected_config = self.create_sample_agent_code(source_dir)
        
        # Add source to Python path
        sys.path.insert(0, str(source_dir))
        
        try:
            # Run conversion
            converter = CodeToConfigConverter(str(source_dir), str(target_dir))
            converter.convert_agents()
            
            # Verify generated files exist
            agent_dir = target_dir / "agents" / "test_agent_123"
            assert agent_dir.exists()
            assert (agent_dir / "agent.json").exists()
            
            # Verify JSON content
            with open(agent_dir / "agent.json", 'r') as f:
                generated_config = json.load(f)
            
            assert generated_config["type"] == expected_config["type"]
            assert generated_config["tools"] == expected_config["tools"]
            assert generated_config["messages"] == expected_config["messages"]
            
        finally:
            # Remove from path
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))
    
    def test_message_reverse_conversion(self, temp_dirs):
        """Test message code to JSON conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample message code
        expected_content = self.create_sample_message_code(source_dir)
        
        # Add source to Python path
        sys.path.insert(0, str(source_dir))
        
        try:
            # Run conversion
            converter = CodeToConfigConverter(str(source_dir), str(target_dir))
            converter.convert_messages()
            
            # Verify generated files exist
            message_dir = target_dir / "messages" / "test_message_456"
            assert message_dir.exists()
            assert (message_dir / "message.md").exists()
            assert (message_dir / "meta.json").exists()
            
            # Verify content
            with open(message_dir / "message.md", 'r') as f:
                generated_content = f.read()
            
            assert generated_content.strip() == expected_content.strip()
            
            # Verify meta.json
            with open(message_dir / "meta.json", 'r') as f:
                meta_config = json.load(f)

            assert meta_config["type"] == "message"
            
        finally:
            # Remove from path
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))
    
    def test_tool_reverse_conversion(self, temp_dirs):
        """Test tool code to JSON conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample tool code
        expected_config = self.create_sample_tool_code(source_dir)
        
        # Add source to Python path
        sys.path.insert(0, str(source_dir))
        
        try:
            # Run conversion
            converter = CodeToConfigConverter(str(source_dir), str(target_dir))
            converter.convert_tools()
            
            # Verify generated files exist
            tool_dir = target_dir / "tools" / "test_tool_789"
            assert tool_dir.exists()
            assert (tool_dir / "tool.json").exists()
            
            # Verify JSON content
            with open(tool_dir / "tool.json", 'r') as f:
                generated_config = json.load(f)
            
            assert generated_config["type"] == expected_config["type"]
            assert generated_config["function"]["name"] == expected_config["function"]["name"]
            assert generated_config["function"]["description"] == expected_config["function"]["description"]
            
        finally:
            # Remove from path
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))
    
    def test_prompt_reverse_conversion(self, temp_dirs):
        """Test prompt code to JSON conversion"""
        source_dir, target_dir = temp_dirs
        
        # Create sample prompt code
        expected_content = self.create_sample_prompt_code(source_dir)
        
        # Add source to Python path
        sys.path.insert(0, str(source_dir))
        
        try:
            # Run conversion
            converter = CodeToConfigConverter(str(source_dir), str(target_dir))
            converter.convert_prompts()
            
            # Verify generated files exist
            prompt_dir = target_dir / "prompts" / "test_prompt_abc"
            assert prompt_dir.exists()
            assert (prompt_dir / "message_0.md").exists()
            
            # Verify content
            with open(prompt_dir / "message_0.md", 'r') as f:
                generated_content = f.read()
            
            assert generated_content.strip() == expected_content.strip()
            
        finally:
            # Remove from path
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
