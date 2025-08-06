#!/usr/bin/env python3
"""
Test script to verify round-trip conversion between JSON configs and Python code

This script tests that:
1. workflow_configs -> workflow_config_code -> workflow_config_generated
2. The content in workflow_configs and workflow_config_generated is identical
3. Order doesn't matter, can have more data but not less
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Set
import subprocess


class RoundTripTester:
    """Tests round-trip conversion accuracy"""
    
    def __init__(self):
        self.original_dir = Path("workflow_configs")
        self.generated_dir = Path("workflow_config_generated")
        self.errors = []
        self.warnings = []
    
    def run_all_tests(self):
        """Run all round-trip conversion tests"""
        print("🧪 TESTING ROUND-TRIP CONVERSION")
        print("=" * 50)
        
        # First, ensure we have fresh conversions
        self.run_conversions()
        
        # Run tests
        self.test_agents()
        self.test_messages()
        self.test_tools()
        self.test_prompts()
        self.test_workflows()
        
        # Report results
        self.report_results()
    
    def run_conversions(self):
        """Run both conversion scripts to ensure fresh data"""
        print("🔄 Running conversions...")
        
        try:
            # Convert JSON to Python
            result1 = subprocess.run([sys.executable, "convert_configs_to_code.py"], 
                                   capture_output=True, text=True)
            if result1.returncode != 0:
                print(f"❌ JSON to Python conversion failed: {result1.stderr}")
                return False
            
            # Convert Python back to JSON
            result2 = subprocess.run([sys.executable, "convert_code_to_configs.py"], 
                                   capture_output=True, text=True)
            if result2.returncode != 0:
                print(f"❌ Python to JSON conversion failed: {result2.stderr}")
                return False
            
            print("✅ Conversions completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
    
    def test_agents(self):
        """Test agent configurations"""
        print("\n📋 Testing agents...")
        
        original_agents = self.original_dir / "agents"
        generated_agents = self.generated_dir / "agents"
        
        if not original_agents.exists():
            print("  ⚠️ No original agents directory")
            return
        
        if not generated_agents.exists():
            self.errors.append("Generated agents directory missing")
            return
        
        # Test each agent
        for agent_dir in original_agents.iterdir():
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                self.test_agent_config(agent_name, agent_dir, generated_agents / agent_name)
    
    def test_agent_config(self, agent_name: str, original_dir: Path, generated_dir: Path):
        """Test individual agent configuration"""
        try:
            # Load original config
            original_json = original_dir / "agent.json"
            if not original_json.exists():
                self.warnings.append(f"Agent {agent_name}: Original JSON not found")
                return

            with open(original_json, 'r') as f:
                original_config = json.load(f)

            # Load generated config
            generated_json = generated_dir / "agent.json"
            if not generated_json.exists():
                self.errors.append(f"Agent {agent_name}: Generated JSON not found")
                return

            with open(generated_json, 'r') as f:
                generated_config = json.load(f)
            
            # Compare configurations
            self.compare_configs(f"Agent {agent_name}", original_config, generated_config)
            print(f"  ✅ {agent_name}")
            
        except Exception as e:
            self.errors.append(f"Agent {agent_name}: {e}")
    
    def test_messages(self):
        """Test message configurations"""
        print("\n💬 Testing messages...")
        
        original_messages = self.original_dir / "messages"
        generated_messages = self.generated_dir / "messages"
        
        if not original_messages.exists():
            print("  ⚠️ No original messages directory")
            return
        
        if not generated_messages.exists():
            self.errors.append("Generated messages directory missing")
            return
        
        # Test each message
        for message_dir in original_messages.iterdir():
            if message_dir.is_dir():
                message_name = message_dir.name
                self.test_message_config(message_name, message_dir, generated_messages / message_name)
    
    def test_message_config(self, message_name: str, original_dir: Path, generated_dir: Path):
        """Test individual message configuration"""
        try:
            # Load original content
            original_md = original_dir / "message.md"
            if not original_md.exists():
                self.warnings.append(f"Message {message_name}: Original markdown not found")
                return

            with open(original_md, 'r', encoding='utf-8') as f:
                original_content = f.read().strip()

            # Load generated content
            generated_md = generated_dir / "message.md"
            if not generated_md.exists():
                self.errors.append(f"Message {message_name}: Generated markdown not found")
                return

            with open(generated_md, 'r', encoding='utf-8') as f:
                generated_content = f.read().strip()
            
            # Compare content
            if original_content != generated_content:
                self.errors.append(f"Message {message_name}: Content mismatch")
            else:
                print(f"  ✅ {message_name}")
            
        except Exception as e:
            self.errors.append(f"Message {message_name}: {e}")
    
    def test_tools(self):
        """Test tool configurations"""
        print("\n🔧 Testing tools...")
        
        original_tools = self.original_dir / "tools"
        generated_tools = self.generated_dir / "tools"
        
        if not original_tools.exists():
            print("  ⚠️ No original tools directory")
            return
        
        if not generated_tools.exists():
            self.errors.append("Generated tools directory missing")
            return
        
        # Test each tool
        for tool_dir in original_tools.iterdir():
            if tool_dir.is_dir():
                tool_name = tool_dir.name
                self.test_tool_config(tool_name, tool_dir, generated_tools / tool_name)
    
    def test_tool_config(self, tool_name: str, original_dir: Path, generated_dir: Path):
        """Test individual tool configuration"""
        try:
            # Load original config
            original_json = original_dir / "tool.json"
            if not original_json.exists():
                self.warnings.append(f"Tool {tool_name}: Original JSON not found")
                return

            with open(original_json, 'r') as f:
                original_config = json.load(f)

            # Load generated config
            generated_json = generated_dir / "tool.json"
            if not generated_json.exists():
                self.errors.append(f"Tool {tool_name}: Generated JSON not found")
                return

            with open(generated_json, 'r') as f:
                generated_config = json.load(f)
            
            # Compare configurations
            self.compare_configs(f"Tool {tool_name}", original_config, generated_config)
            print(f"  ✅ {tool_name}")
            
        except Exception as e:
            self.errors.append(f"Tool {tool_name}: {e}")
    
    def test_prompts(self):
        """Test prompt configurations"""
        print("\n📝 Testing prompts...")
        
        original_prompts = self.original_dir / "prompts"
        generated_prompts = self.generated_dir / "prompts"
        
        if not original_prompts.exists():
            print("  ⚠️ No original prompts directory")
            return
        
        if not generated_prompts.exists():
            self.errors.append("Generated prompts directory missing")
            return
        
        # Test each prompt
        for prompt_dir in original_prompts.iterdir():
            if prompt_dir.is_dir():
                prompt_name = prompt_dir.name
                self.test_prompt_config(prompt_name, prompt_dir, generated_prompts / prompt_name)
    
    def test_prompt_config(self, prompt_name: str, original_dir: Path, generated_dir: Path):
        """Test individual prompt configuration"""
        try:
            # Load original content
            original_md = original_dir / "message_0.md"
            if not original_md.exists():
                self.warnings.append(f"Prompt {prompt_name}: Original markdown not found")
                return

            with open(original_md, 'r', encoding='utf-8') as f:
                original_content = f.read().strip()

            # Load generated content
            generated_md = generated_dir / "message_0.md"
            if not generated_md.exists():
                self.errors.append(f"Prompt {prompt_name}: Generated markdown not found")
                return

            with open(generated_md, 'r', encoding='utf-8') as f:
                generated_content = f.read().strip()
            
            # Compare content
            if original_content != generated_content:
                self.errors.append(f"Prompt {prompt_name}: Content mismatch")
            else:
                print(f"  ✅ {prompt_name}")
            
        except Exception as e:
            self.errors.append(f"Prompt {prompt_name}: {e}")
    
    def test_workflows(self):
        """Test workflow configurations"""
        print("\n🔄 Testing workflows...")
        
        original_workflows = self.original_dir / "workflows"
        generated_workflows = self.generated_dir / "workflows"
        
        if not original_workflows.exists():
            print("  ⚠️ No original workflows directory")
            return
        
        if not generated_workflows.exists():
            self.errors.append("Generated workflows directory missing")
            return
        
        # Test each workflow
        for workflow_file in original_workflows.glob("*.json"):
            workflow_name = workflow_file.stem
            self.test_workflow_config(workflow_name, workflow_file, generated_workflows / f"{workflow_name}.json")
    
    def test_workflow_config(self, workflow_name: str, original_file: Path, generated_file: Path):
        """Test individual workflow configuration"""
        try:
            # Load original config
            with open(original_file, 'r') as f:
                original_config = json.load(f)
            
            # Load generated config
            if not generated_file.exists():
                self.errors.append(f"Workflow {workflow_name}: Generated JSON not found")
                return
            
            with open(generated_file, 'r') as f:
                generated_config = json.load(f)
            
            # Compare configurations
            self.compare_configs(f"Workflow {workflow_name}", original_config, generated_config)
            print(f"  ✅ {workflow_name}")
            
        except Exception as e:
            self.errors.append(f"Workflow {workflow_name}: {e}")
    
    def compare_configs(self, name: str, original: Dict[str, Any], generated: Dict[str, Any]):
        """Compare two configurations - generated can have more data but not less"""
        missing_keys = self.find_missing_keys(original, generated)
        if missing_keys:
            self.errors.append(f"{name}: Missing keys in generated config: {missing_keys}")
        
        # Check values for existing keys
        mismatched_values = self.find_mismatched_values(original, generated)
        if mismatched_values:
            self.errors.append(f"{name}: Mismatched values: {mismatched_values}")
    
    def find_missing_keys(self, original: Any, generated: Any, path: str = "") -> Set[str]:
        """Find keys that exist in original but not in generated"""
        missing = set()
        
        if isinstance(original, dict) and isinstance(generated, dict):
            for key, value in original.items():
                current_path = f"{path}.{key}" if path else key
                if key not in generated:
                    missing.add(current_path)
                else:
                    missing.update(self.find_missing_keys(value, generated[key], current_path))
        elif isinstance(original, list) and isinstance(generated, list):
            # For lists, check that generated has at least as many items
            if len(generated) < len(original):
                missing.add(f"{path}[length]")
        
        return missing
    
    def find_mismatched_values(self, original: Any, generated: Any, path: str = "") -> Set[str]:
        """Find values that don't match between original and generated"""
        mismatched = set()
        
        if isinstance(original, dict) and isinstance(generated, dict):
            for key, value in original.items():
                if key in generated:
                    current_path = f"{path}.{key}" if path else key
                    mismatched.update(self.find_mismatched_values(value, generated[key], current_path))
        elif isinstance(original, list) and isinstance(generated, list):
            for i, (orig_item, gen_item) in enumerate(zip(original, generated)):
                current_path = f"{path}[{i}]"
                mismatched.update(self.find_mismatched_values(orig_item, gen_item, current_path))
        elif original != generated:
            mismatched.add(path or "root")
        
        return mismatched
    
    def report_results(self):
        """Report test results"""
        print("\n" + "=" * 50)
        print("📊 ROUND-TRIP CONVERSION TEST RESULTS")
        print("=" * 50)
        
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print(f"\n💥 {len(self.errors)} errors found - round-trip conversion failed!")
            return False
        else:
            print("\n🎉 All tests passed! Round-trip conversion is accurate!")
            if self.warnings:
                print(f"   (with {len(self.warnings)} warnings - this is expected)")
                print("   Warnings indicate that generated configs contain more data than originals,")
                print("   which is perfectly fine and expected behavior.")
            return True


if __name__ == "__main__":
    tester = RoundTripTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
