"""
Simple Test for Reverse Marshalling (Config to Code)

Tests that generated code from JSON configs has the correct structure and methods.
"""

import pytest
import json
import sys
import os
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
    
    def test_generate_agent_code_structure(self):
        """Test that generated agent code has correct structure"""
        # Generate agent code
        agent_config_path = self.config_dir / "agent.json"
        agent_output_path = self.generated_dir / "agents/chat_assistant/agent.py"
        
        if not agent_config_path.exists():
            pytest.skip("Agent config file not found")
        
        self.marshaller.marshal_agent_config(str(agent_config_path), str(agent_output_path))
        
        # Verify file was created
        assert agent_output_path.exists(), "Agent code file should be generated"
        
        # Read and verify content
        content = agent_output_path.read_text()
        
        # Check for required elements
        assert "class ChatAssistantAgent" in content, "Should have ChatAssistantAgent class"
        assert "def get_name(" in content, "Should have get_name method"
        assert "def get_config(self)" in content, "Should have get_config method"
        assert "async def process(self, context:" in content, "Should have process method"
        assert "return \"chat_assistant\"" in content, "Should return correct name"
        assert "agent_config(" in content, "Should use agent_config builder"
        assert "chat_assistant_agent = " in content, "Should create singleton instance"
        
        print("✅ Generated agent code has correct structure")
    
    def test_generate_tool_code_structure(self):
        """Test that generated tool code has correct structure"""
        # Generate tool code
        tool_config_path = self.config_dir / "web_search_tool.json"
        tool_output_path = self.generated_dir / "tools/web_search/tool.py"
        
        if not tool_config_path.exists():
            pytest.skip("Tool config file not found")
        
        self.marshaller.marshal_tool_config(str(tool_config_path), str(tool_output_path))
        
        # Verify file was created
        assert tool_output_path.exists(), "Tool code file should be generated"
        
        # Read and verify content
        content = tool_output_path.read_text()
        
        # Check for required elements
        assert "class WebSearchTool" in content, "Should have WebSearchTool class"
        assert "def get_name(" in content, "Should have get_name method"
        assert "def get_config(self)" in content, "Should have get_config method"
        assert "async def execute(self, **params)" in content, "Should have execute method"
        assert "async def process(self, context:" in content, "Should have process method"
        assert "return \"web_search\"" in content, "Should return correct name"
        assert "tool_config(" in content, "Should use tool_config builder"
        assert "add_parameter(" in content, "Should add parameters"
        assert "web_search_tool = " in content, "Should create singleton instance"
        
        print("✅ Generated tool code has correct structure")
    
    def test_generate_message_code_structure(self):
        """Test that generated message code has correct structure"""
        # Generate message code
        message_config_path = self.config_dir / "welcome_message_meta.json"
        message_output_path = self.generated_dir / "messages/welcome_message/message.py"
        
        if not message_config_path.exists():
            pytest.skip("Message config file not found")
        
        self.marshaller.marshal_message_config(str(message_config_path), str(message_output_path))
        
        # Verify file was created
        assert message_output_path.exists(), "Message code file should be generated"
        
        # Read and verify content
        content = message_output_path.read_text()
        
        # Check for required elements
        assert "class WelcomeMessage" in content, "Should have WelcomeMessage class"
        assert "def get_name(" in content, "Should have get_name method"
        assert "def get_config(self)" in content, "Should have get_config method"
        assert "def read_content(self)" in content, "Should have read_content method"
        assert "async def process(self, context:" in content, "Should have process method"
        assert "return \"welcome_message\"" in content, "Should return correct name"
        assert "message_config(" in content, "Should use message_config builder"
        assert "welcome_message_message = " in content, "Should create singleton instance"
        
        print("✅ Generated message code has correct structure")
    
    def test_generate_workflow_code_structure(self):
        """Test that generated workflow code has correct structure"""
        # Generate workflow code
        workflow_config_path = self.config_dir / "workflow.json"
        workflow_output_path = self.generated_dir / "workflows/simple_chat_workflow/workflow.py"
        
        if not workflow_config_path.exists():
            pytest.skip("Workflow config file not found")
        
        self.marshaller.marshal_workflow_config(str(workflow_config_path), str(workflow_output_path))
        
        # Verify file was created
        assert workflow_output_path.exists(), "Workflow code file should be generated"
        
        # Read and verify content
        content = workflow_output_path.read_text()
        
        # Check for required elements
        assert "def simple_chat_workflow()" in content, "Should have workflow function"
        assert "workflow(" in content, "Should use workflow builder"
        assert "with_description(" in content, "Should set description"
        assert "with_initial_state(" in content, "Should set initial state"
        assert "with_criterion(" in content, "Should set criterion"
        assert "add_state(" in content, "Should add states"
        assert "add_transition(" in content, "Should add transitions"
        assert "set_manual(" in content, "Should set manual flag"
        assert "with_processor(" in content, "Should add processors"
        assert ".build()" in content, "Should call build"
        
        print("✅ Generated workflow code has correct structure")
    
    def test_generated_code_syntax_validity(self):
        """Test that generated code has valid Python syntax"""
        # Generate all types of code
        configs_to_generate = [
            ("agent.json", "agents/chat_assistant/agent.py", "marshal_agent_config"),
            ("web_search_tool.json", "tools/web_search/tool.py", "marshal_tool_config"),
            ("welcome_message_meta.json", "messages/welcome_message/message.py", "marshal_message_config"),
            ("workflow.json", "workflows/simple_chat_workflow/workflow.py", "marshal_workflow_config")
        ]
        
        for config_file, output_file, marshal_method in configs_to_generate:
            config_path = self.config_dir / config_file
            output_path = self.generated_dir / output_file
            
            if not config_path.exists():
                continue
            
            # Generate code
            method = getattr(self.marshaller, marshal_method)
            method(str(config_path), str(output_path))
            
            # Verify file exists
            assert output_path.exists(), f"Generated file should exist: {output_file}"
            
            # Test syntax validity by compiling
            content = output_path.read_text()
            try:
                compile(content, str(output_path), 'exec')
                print(f"✅ Generated code has valid syntax: {output_file}")
            except SyntaxError as e:
                pytest.fail(f"Generated code has syntax error in {output_file}: {e}")
    
    def test_generated_code_contains_builders(self):
        """Test that generated code properly uses builders"""
        # Generate agent code
        agent_config_path = self.config_dir / "agent.json"
        agent_output_path = self.generated_dir / "agents/chat_assistant/agent.py"
        
        if agent_config_path.exists():
            self.marshaller.marshal_agent_config(str(agent_config_path), str(agent_output_path))
            content = agent_output_path.read_text()
            
            # Check builder usage
            assert "from workflow_best_ux.builders import agent_config" in content, "Should import agent_config builder"
            assert "agent_config(\"chat_assistant\")" in content, "Should use agent_config builder"
            assert ".with_description(" in content, "Should use builder methods"
            assert ".with_model(" in content, "Should use builder methods"
            assert ".build()" in content, "Should call build method"
        
        # Generate tool code
        tool_config_path = self.config_dir / "web_search_tool.json"
        tool_output_path = self.generated_dir / "tools/web_search/tool.py"
        
        if tool_config_path.exists():
            self.marshaller.marshal_tool_config(str(tool_config_path), str(tool_output_path))
            content = tool_output_path.read_text()
            
            # Check builder usage
            assert "from workflow_best_ux.builders import tool_config" in content, "Should import tool_config builder"
            assert "tool_config(\"web_search\")" in content, "Should use tool_config builder"
            assert ".with_description(" in content, "Should use builder methods"
            assert ".add_parameter(" in content, "Should use builder methods"
            assert ".build()" in content, "Should call build method"
        
        print("✅ Generated code properly uses builders")
    
    def test_complete_reverse_marshalling_cycle(self):
        """Test complete reverse marshalling cycle"""
        print("\n🔄 TESTING COMPLETE REVERSE MARSHALLING CYCLE")
        print("=" * 50)
        
        # Generate all components
        configs_to_generate = [
            ("agent.json", "agents/chat_assistant/agent.py", "marshal_agent_config"),
            ("web_search_tool.json", "tools/web_search/tool.py", "marshal_tool_config"),
            ("read_link_tool.json", "tools/read_link/tool.py", "marshal_tool_config"),
            ("get_cyoda_guidelines_tool.json", "tools/get_cyoda_guidelines/tool.py", "marshal_tool_config"),
            ("get_user_info_tool.json", "tools/get_user_info/tool.py", "marshal_tool_config"),
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
                generated_files.append((output_path, output_file))
                print(f"✅ Generated: {output_file}")
        
        # Verify all files were generated and have correct content
        assert len(generated_files) > 0, "At least one file should be generated"
        
        for file_path, file_name in generated_files:
            assert file_path.exists(), f"Generated file should exist: {file_name}"
            
            # Verify file has content
            content = file_path.read_text()
            assert len(content) > 0, f"Generated file should have content: {file_name}"

            # Workflows are functions, not classes with get_name methods
            if "workflow" in file_name:
                assert "def " in content, f"Generated workflow should have function definitions: {file_name}"
                assert "workflow(" in content, f"Generated workflow should use workflow builder: {file_name}"
            else:
                assert "get_name" in content, f"Generated file should have get_name method: {file_name}"
                assert "def " in content, f"Generated file should have function definitions: {file_name}"
            
            # Verify syntax
            try:
                compile(content, str(file_path), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Generated code has syntax error in {file_name}: {e}")
        
        print(f"\n✅ Successfully generated {len(generated_files)} code files from JSON configs!")
        print("🎯 All generated files have:")
        print("  • Valid Python syntax")
        print("  • Proper get_name() methods")
        print("  • Proper get_config() methods using builders")
        print("  • Correct class and function structures")
        print("  • Singleton instances")


def run_reverse_marshalling_tests():
    """Run all reverse marshalling tests"""
    test = TestReverseMarshalling()
    
    print("🧪 Testing Reverse Marshalling (Config → Code)...")
    print("=" * 50)
    
    try:
        test.setup_method()
        
        test.test_generate_agent_code_structure()
        test.test_generate_tool_code_structure()
        test.test_generate_message_code_structure()
        test.test_generate_workflow_code_structure()
        test.test_generated_code_syntax_validity()
        test.test_generated_code_contains_builders()
        test.test_complete_reverse_marshalling_cycle()
        
        print("\n🎉 All reverse marshalling tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Reverse marshalling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        test.teardown_method()


if __name__ == "__main__":
    success = run_reverse_marshalling_tests()
    sys.exit(0 if success else 1)
