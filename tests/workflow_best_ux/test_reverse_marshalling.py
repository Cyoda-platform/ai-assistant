"""
Test Reverse Marshalling (Config to Code)

Tests that generated code from JSON configs works correctly.
Verifies that generated components have proper get_name() and get_config() methods.
"""

import pytest
import json
import sys
import os
import importlib.util
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.marshal_configs_to_code import ConfigToCodeMarshaller


class TestReverseMarshalling:
    """Test reverse marshalling from configs to code"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.marshaller = ConfigToCodeMarshaller()
        self.generated_dir = Path("workflow_best_ux_generated_test")
        self.config_dir = Path("tests/workflow_best_ux/expected_configs")
        
        # Clean up any existing generated files
        if self.generated_dir.exists():
            import shutil
            shutil.rmtree(self.generated_dir)
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Clean up generated files
        if self.generated_dir.exists():
            import shutil
            shutil.rmtree(self.generated_dir)
    
    def _load_module_from_file(self, file_path: str, module_name: str):
        """Load a Python module from file path"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    
    def test_generate_agent_code_from_config(self):
        """Test generating agent code from JSON config"""
        # Generate agent code
        agent_config_path = self.config_dir / "agent.json"
        agent_output_path = self.generated_dir / "agents/chat_assistant/agent.py"
        
        if not agent_config_path.exists():
            pytest.skip("Agent config file not found")
        
        self.marshaller.marshal_agent_config(str(agent_config_path), str(agent_output_path))
        
        # Verify file was created
        assert agent_output_path.exists(), "Agent code file should be generated"
        
        # Load and test the generated module
        try:
            # Add the generated directory to Python path temporarily
            sys.path.insert(0, str(self.generated_dir))
            
            # Import the generated module
            from agents.chat_assistant.agent import ChatAssistantComponent, chat_assistant_agent
            
            # Test static get_name method
            assert hasattr(ChatAssistantComponent, 'get_name'), "Generated class must have get_name method"
            assert ChatAssistantComponent.get_name() == "chat_assistant", "get_name must return correct name"
            
            # Test instance methods
            agent = ChatAssistantComponent()
            assert hasattr(agent, 'get_config'), "Generated instance must have get_config method"
            
            # Test get_config method
            config = agent.get_config()
            assert config is not None, "get_config must return a config object"
            assert hasattr(config, 'get_name'), "Config must have get_name method"
            
            # Test singleton instance
            assert chat_assistant_agent is not None, "Singleton instance must be created"
            assert isinstance(chat_assistant_agent, ChatAssistantComponent), "Singleton must be correct type"
            
            print("✅ Generated agent code works correctly")
            
        finally:
            # Clean up Python path
            if str(self.generated_dir) in sys.path:
                sys.path.remove(str(self.generated_dir))
    
    def test_generate_tool_code_from_config(self):
        """Test generating tool code from JSON config"""
        # Generate tool code
        tool_config_path = self.config_dir / "web_search_tool.json"
        tool_output_path = self.generated_dir / "tools/web_search/tool.py"
        
        if not tool_config_path.exists():
            pytest.skip("Tool config file not found")
        
        self.marshaller.marshal_tool_config(str(tool_config_path), str(tool_output_path))
        
        # Verify file was created
        assert tool_output_path.exists(), "Tool code file should be generated"
        
        # Load and test the generated module
        try:
            # Add the generated directory to Python path temporarily
            sys.path.insert(0, str(self.generated_dir))
            
            # Import the generated module
            from tools.web_search.tool import WebSearchComponent, web_search_tool
            
            # Test static get_name method
            assert hasattr(WebSearchComponent, 'get_name'), "Generated class must have get_name method"
            assert WebSearchComponent.get_name() == "web_search", "get_name must return correct name"
            
            # Test instance methods
            tool = WebSearchComponent()
            assert hasattr(tool, 'get_config'), "Generated instance must have get_config method"
            assert hasattr(tool, 'execute'), "Generated instance must have execute method"
            assert hasattr(tool, 'process'), "Generated instance must have process method"
            
            # Test get_config method
            config = tool.get_config()
            assert config is not None, "get_config must return a config object"
            assert hasattr(config, 'get_name'), "Config must have get_name method"
            assert hasattr(config, 'get_parameters'), "Config must have get_parameters method"
            
            # Test parameters
            parameters = config.get_parameters()
            assert isinstance(parameters, dict), "Parameters must be dict"
            assert "query" in parameters, "Query parameter must exist"
            
            # Test singleton instance
            assert web_search_tool is not None, "Singleton instance must be created"
            assert isinstance(web_search_tool, WebSearchComponent), "Singleton must be correct type"
            
            print("✅ Generated tool code works correctly")
            
        finally:
            # Clean up Python path
            if str(self.generated_dir) in sys.path:
                sys.path.remove(str(self.generated_dir))
    
    def test_generate_message_code_from_config(self):
        """Test generating message code from JSON config"""
        # Generate message code
        message_config_path = self.config_dir / "welcome_message_meta.json"
        message_output_path = self.generated_dir / "messages/welcome_message/message.py"
        
        if not message_config_path.exists():
            pytest.skip("Message config file not found")
        
        self.marshaller.marshal_message_config(str(message_config_path), str(message_output_path))
        
        # Verify file was created
        assert message_output_path.exists(), "Message code file should be generated"
        
        # Load and test the generated module
        try:
            # Add the generated directory to Python path temporarily
            sys.path.insert(0, str(self.generated_dir))
            
            # Import the generated module
            from messages.welcome_message.message import WelcomeMessageComponent, welcome_message_message
            
            # Test static get_name method
            assert hasattr(WelcomeMessageComponent, 'get_name'), "Generated class must have get_name method"
            assert WelcomeMessageComponent.get_name() == "welcome_message", "get_name must return correct name"
            
            # Test instance methods
            message = WelcomeMessageComponent()
            assert hasattr(message, 'get_config'), "Generated instance must have get_config method"
            assert hasattr(message, 'read_content'), "Generated instance must have read_content method"
            assert hasattr(message, 'process'), "Generated instance must have process method"
            
            # Test get_config method
            config = message.get_config()
            assert config is not None, "get_config must return a config object"
            assert hasattr(config, 'get_name'), "Config must have get_name method"
            assert hasattr(config, 'get_content'), "Config must have get_content method"
            
            # Test singleton instance
            assert welcome_message_message is not None, "Singleton instance must be created"
            assert isinstance(welcome_message_message, WelcomeMessageComponent), "Singleton must be correct type"
            
            print("✅ Generated message code works correctly")
            
        finally:
            # Clean up Python path
            if str(self.generated_dir) in sys.path:
                sys.path.remove(str(self.generated_dir))
    
    def test_generate_workflow_code_from_config(self):
        """Test generating workflow code from JSON config"""
        # Generate workflow code
        workflow_config_path = self.config_dir / "workflow.json"
        workflow_output_path = self.generated_dir / "workflows/simple_chat_workflow/workflow.py"
        
        if not workflow_config_path.exists():
            pytest.skip("Workflow config file not found")
        
        self.marshaller.marshal_workflow_config(str(workflow_config_path), str(workflow_output_path))
        
        # Verify file was created
        assert workflow_output_path.exists(), "Workflow code file should be generated"
        
        # Load and test the generated module
        try:
            # Add the generated directory to Python path temporarily
            sys.path.insert(0, str(self.generated_dir))
            
            # Import the generated module
            from workflows.simple_chat_workflow.workflow import simple_chat_workflow
            
            # Test workflow function
            assert callable(simple_chat_workflow), "Generated workflow must be callable"
            
            # Test workflow execution
            workflow_config = simple_chat_workflow()
            assert isinstance(workflow_config, dict), "Workflow must return dict"
            
            # Test workflow structure
            assert "name" in workflow_config, "Workflow must have name"
            assert "desc" in workflow_config, "Workflow must have desc"
            assert "initialState" in workflow_config, "Workflow must have initialState"
            assert "states" in workflow_config, "Workflow must have states"
            
            assert workflow_config["name"] == "simple_chat_workflow", "Workflow name must be correct"
            
            print("✅ Generated workflow code works correctly")
            
        finally:
            # Clean up Python path
            if str(self.generated_dir) in sys.path:
                sys.path.remove(str(self.generated_dir))
    
    def test_complete_reverse_marshalling_cycle(self):
        """Test complete reverse marshalling cycle"""
        print("\n🔄 TESTING COMPLETE REVERSE MARSHALLING CYCLE")
        print("=" * 50)
        
        # Generate all components
        configs_to_generate = [
            ("agent.json", "agents/chat_assistant/agent.py", "marshal_agent_config"),
            ("web_search_tool.json", "tools/web_search/tool.py", "marshal_tool_config"),
            ("welcome_message_meta.json", "messages/welcome_message/message.py", "marshal_message_config"),
            ("workflow.json", "workflows/simple_chat_workflow/workflow.py", "marshal_workflow_config")
        ]
        
        generated_files = []
        
        for config_file, output_file, marshal_method in configs_to_generate:
            config_path = self.config_dir / config_file
            output_path = self.generated_dir / output_file
            
            if config_path.exists():
                method = getattr(self.marshaller, marshal_method)
                method(str(config_path), str(output_path))
                generated_files.append(output_path)
                print(f"✅ Generated: {output_file}")
        
        # Verify all files were generated
        assert len(generated_files) > 0, "At least one file should be generated"
        
        for file_path in generated_files:
            assert file_path.exists(), f"Generated file should exist: {file_path}"
            
            # Verify file has content
            content = file_path.read_text()
            assert len(content) > 0, f"Generated file should have content: {file_path}"
            assert "get_name" in content, f"Generated file should have get_name method: {file_path}"
            assert "def " in content, f"Generated file should have function definitions: {file_path}"
        
        print(f"\n✅ Successfully generated {len(generated_files)} code files from JSON configs!")
        print("🎯 All generated files have proper get_name() and get_config() methods!")


def run_reverse_marshalling_tests():
    """Run all reverse marshalling tests"""
    test = TestReverseMarshalling()
    
    print("🧪 Testing Reverse Marshalling (Config → Code)...")
    print("=" * 50)
    
    try:
        test.setup_method()
        
        test.test_generate_agent_code_from_config()
        test.test_generate_tool_code_from_config()
        test.test_generate_message_code_from_config()
        test.test_generate_workflow_code_from_config()
        test.test_complete_reverse_marshalling_cycle()
        
        print("\n🎉 All reverse marshalling tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Reverse marshalling test failed: {e}")
        return False
        
    finally:
        test.teardown_method()


if __name__ == "__main__":
    success = run_reverse_marshalling_tests()
    sys.exit(0 if success else 1)
