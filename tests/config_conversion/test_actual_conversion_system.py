"""
Test actual conversion system

Tests the actual conversion scripts with real workflow_configs data.
"""

import pytest
import json
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestActualConversionSystem:
    """Test the actual conversion system with real data"""
    
    @pytest.fixture
    def backup_dirs(self):
        """Backup and restore actual directories"""
        project_root = Path(__file__).parent.parent.parent
        
        # Backup existing directories if they exist
        code_dir = project_root / "workflow_config_code"
        generated_dir = project_root / "workflow_config_generated"
        
        code_backup = None
        generated_backup = None
        
        if code_dir.exists():
            code_backup = tempfile.mkdtemp(prefix="code_backup_")
            shutil.copytree(code_dir, Path(code_backup) / "workflow_config_code")
        
        if generated_dir.exists():
            generated_backup = tempfile.mkdtemp(prefix="generated_backup_")
            shutil.copytree(generated_dir, Path(generated_backup) / "workflow_config_generated")
        
        yield project_root
        
        # Restore backups
        if code_backup and code_dir.exists():
            shutil.rmtree(code_dir)
            shutil.copytree(Path(code_backup) / "workflow_config_code", code_dir)
            shutil.rmtree(code_backup)
        
        if generated_backup and generated_dir.exists():
            shutil.rmtree(generated_dir)
            shutil.copytree(Path(generated_backup) / "workflow_config_generated", generated_dir)
            shutil.rmtree(generated_backup)
    
    def test_json_to_code_conversion_script(self, backup_dirs):
        """Test the actual JSON to code conversion script"""
        project_root = backup_dirs
        
        # Ensure we have original configs
        original_configs_dir = project_root / "workflow_configs"
        if not original_configs_dir.exists():
            pytest.skip("No workflow_configs directory found")
        
        # Run the conversion script
        result = subprocess.run(
            [sys.executable, "convert_configs_to_code.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        
        # Verify output directory was created
        code_dir = project_root / "workflow_config_code"
        assert code_dir.exists(), "workflow_config_code directory not created"
        
        # Verify basic structure
        assert (code_dir / "__init__.py").exists(), "Main __init__.py not created"
        
        # Check for expected subdirectories
        expected_dirs = ["agents", "messages", "tools", "prompts", "workflows"]
        for dir_name in expected_dirs:
            if (original_configs_dir / dir_name).exists():
                assert (code_dir / dir_name).exists(), f"{dir_name} directory not created"
                assert (code_dir / dir_name / "__init__.py").exists(), f"{dir_name}/__init__.py not created"
    
    def test_code_to_json_conversion_script(self, backup_dirs):
        """Test the actual code to JSON conversion script"""
        project_root = backup_dirs
        
        # First ensure we have Python code to convert
        code_dir = project_root / "workflow_config_code"
        if not code_dir.exists():
            # Run JSON to code conversion first
            result = subprocess.run(
                [sys.executable, "convert_configs_to_code.py"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Initial conversion failed: {result.stderr}"
        
        # Run the reverse conversion script
        result = subprocess.run(
            [sys.executable, "convert_code_to_configs.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Reverse conversion failed: {result.stderr}"
        
        # Verify output directory was created
        generated_dir = project_root / "workflow_config_generated"
        assert generated_dir.exists(), "workflow_config_generated directory not created"
        
        # Check for expected subdirectories
        expected_dirs = ["agents", "messages", "tools", "prompts", "workflows"]
        for dir_name in expected_dirs:
            if (code_dir / dir_name).exists():
                assert (generated_dir / dir_name).exists(), f"{dir_name} directory not created"
    
    def test_complete_roundtrip_with_scripts(self, backup_dirs):
        """Test complete round-trip using actual scripts"""
        project_root = backup_dirs
        
        # Ensure we have original configs
        original_configs_dir = project_root / "workflow_configs"
        if not original_configs_dir.exists():
            pytest.skip("No workflow_configs directory found")
        
        # Step 1: JSON to Python
        result1 = subprocess.run(
            [sys.executable, "convert_configs_to_code.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        assert result1.returncode == 0, f"JSON to Python failed: {result1.stderr}"
        
        # Step 2: Python to JSON
        result2 = subprocess.run(
            [sys.executable, "convert_code_to_configs.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        assert result2.returncode == 0, f"Python to JSON failed: {result2.stderr}"
        
        # Step 3: Compare key files
        generated_dir = project_root / "workflow_config_generated"
        
        # Check that we have the same structure
        self.compare_directory_structures(original_configs_dir, generated_dir)
        
        # Check specific file types
        self.compare_agent_files(original_configs_dir, generated_dir)
        self.compare_message_files(original_configs_dir, generated_dir)
        self.compare_tool_files(original_configs_dir, generated_dir)
        self.compare_prompt_files(original_configs_dir, generated_dir)
        self.compare_workflow_files(original_configs_dir, generated_dir)
    
    def compare_directory_structures(self, original_dir: Path, generated_dir: Path):
        """Compare directory structures"""
        original_subdirs = {d.name for d in original_dir.iterdir() if d.is_dir()}
        generated_subdirs = {d.name for d in generated_dir.iterdir() if d.is_dir()}
        
        # Generated can have more directories, but not fewer
        missing_dirs = original_subdirs - generated_subdirs
        assert not missing_dirs, f"Missing directories in generated: {missing_dirs}"
    
    def compare_agent_files(self, original_dir: Path, generated_dir: Path):
        """Compare agent configuration files"""
        original_agents_dir = original_dir / "agents"
        generated_agents_dir = generated_dir / "agents"
        
        if not original_agents_dir.exists():
            return
        
        assert generated_agents_dir.exists(), "Generated agents directory missing"
        
        for agent_dir in original_agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                original_file = agent_dir / "agent.json"
                generated_file = generated_agents_dir / agent_name / "agent.json"
                
                if original_file.exists():
                    assert generated_file.exists(), f"Generated agent file missing: {agent_name}"
                    
                    # Load and compare essential fields
                    with open(original_file, 'r') as f:
                        original_config = json.load(f)
                    
                    with open(generated_file, 'r') as f:
                        generated_config = json.load(f)
                    
                    # Check essential fields exist
                    if "type" in original_config:
                        assert "type" in generated_config
                        assert original_config["type"] == generated_config["type"]
    
    def compare_message_files(self, original_dir: Path, generated_dir: Path):
        """Compare message configuration files"""
        original_messages_dir = original_dir / "messages"
        generated_messages_dir = generated_dir / "messages"
        
        if not original_messages_dir.exists():
            return
        
        assert generated_messages_dir.exists(), "Generated messages directory missing"
        
        for message_dir in original_messages_dir.iterdir():
            if message_dir.is_dir():
                message_name = message_dir.name
                original_file = message_dir / "message.md"
                generated_file = generated_messages_dir / message_name / "message.md"
                
                if original_file.exists():
                    assert generated_file.exists(), f"Generated message file missing: {message_name}"
                    
                    # Compare content (allowing for minor formatting differences)
                    with open(original_file, 'r', encoding='utf-8') as f:
                        original_content = f.read().strip()
                    
                    with open(generated_file, 'r', encoding='utf-8') as f:
                        generated_content = f.read().strip()
                    
                    assert original_content == generated_content, f"Message content differs: {message_name}"
    
    def compare_tool_files(self, original_dir: Path, generated_dir: Path):
        """Compare tool configuration files"""
        original_tools_dir = original_dir / "tools"
        generated_tools_dir = generated_dir / "tools"
        
        if not original_tools_dir.exists():
            return
        
        assert generated_tools_dir.exists(), "Generated tools directory missing"
        
        for tool_dir in original_tools_dir.iterdir():
            if tool_dir.is_dir():
                tool_name = tool_dir.name
                original_file = tool_dir / "tool.json"
                generated_file = generated_tools_dir / tool_name / "tool.json"
                
                if original_file.exists():
                    assert generated_file.exists(), f"Generated tool file missing: {tool_name}"
                    
                    # Load and compare essential fields
                    with open(original_file, 'r') as f:
                        original_config = json.load(f)
                    
                    with open(generated_file, 'r') as f:
                        generated_config = json.load(f)
                    
                    # Check essential fields exist
                    if "type" in original_config:
                        assert "type" in generated_config
                        assert original_config["type"] == generated_config["type"]
    
    def compare_prompt_files(self, original_dir: Path, generated_dir: Path):
        """Compare prompt configuration files"""
        original_prompts_dir = original_dir / "prompts"
        generated_prompts_dir = generated_dir / "prompts"
        
        if not original_prompts_dir.exists():
            return
        
        assert generated_prompts_dir.exists(), "Generated prompts directory missing"
        
        for prompt_dir in original_prompts_dir.iterdir():
            if prompt_dir.is_dir():
                prompt_name = prompt_dir.name
                original_file = prompt_dir / "message_0.md"
                generated_file = generated_prompts_dir / prompt_name / "message_0.md"
                
                if original_file.exists():
                    assert generated_file.exists(), f"Generated prompt file missing: {prompt_name}"
                    
                    # Compare content
                    with open(original_file, 'r', encoding='utf-8') as f:
                        original_content = f.read().strip()
                    
                    with open(generated_file, 'r', encoding='utf-8') as f:
                        generated_content = f.read().strip()
                    
                    assert original_content == generated_content, f"Prompt content differs: {prompt_name}"
    
    def compare_workflow_files(self, original_dir: Path, generated_dir: Path):
        """Compare workflow configuration files"""
        original_workflows_dir = original_dir / "workflows"
        generated_workflows_dir = generated_dir / "workflows"
        
        if not original_workflows_dir.exists():
            return
        
        assert generated_workflows_dir.exists(), "Generated workflows directory missing"
        
        for workflow_file in original_workflows_dir.glob("*.json"):
            workflow_name = workflow_file.stem
            generated_file = generated_workflows_dir / f"{workflow_name}.json"
            
            assert generated_file.exists(), f"Generated workflow file missing: {workflow_name}"
            
            # Load and compare essential fields
            with open(workflow_file, 'r') as f:
                original_config = json.load(f)
            
            with open(generated_file, 'r') as f:
                generated_config = json.load(f)
            
            # Check essential fields exist
            if "name" in original_config:
                assert "name" in generated_config
                assert original_config["name"] == generated_config["name"]
    
    def test_convenience_script(self, backup_dirs):
        """Test the convenience script for running both conversions"""
        project_root = backup_dirs
        
        # Ensure we have original configs
        original_configs_dir = project_root / "workflow_configs"
        if not original_configs_dir.exists():
            pytest.skip("No workflow_configs directory found")
        
        # Run the convenience script
        result = subprocess.run(
            [sys.executable, "run_conversions.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Convenience script failed: {result.stderr}"
        
        # Verify both directories were created
        code_dir = project_root / "workflow_config_code"
        generated_dir = project_root / "workflow_config_generated"
        
        assert code_dir.exists(), "workflow_config_code directory not created"
        assert generated_dir.exists(), "workflow_config_generated directory not created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
