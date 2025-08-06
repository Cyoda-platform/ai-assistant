# Configuration Conversion Tests

This directory contains comprehensive tests for the workflow configuration conversion system.

## Test Files

### `test_json_to_code_conversion.py`
Tests the conversion from JSON configurations to Python code.

**What it tests:**
- Agent JSON → Python class generation
- Message markdown → Python string configuration
- Tool JSON → Python class with `get_tool_name()` method
- Prompt markdown → Python string configuration
- Workflow JSON → Python class generation
- Complete conversion pipeline
- File structure and naming conventions
- Class inheritance and interface compliance

**Expected Input:** JSON configurations in `workflow_configs/` format
**Expected Output:** Python code in `workflow_config_code/` format

### `test_code_to_json_conversion.py`
Tests the reverse conversion from Python code to JSON configurations.

**What it tests:**
- Python agent classes → JSON configuration
- Python message classes → Markdown files
- Python tool classes → JSON configuration
- Python prompt classes → Markdown files
- Proper filename conventions (agent.json, message.md, tool.json, message_0.md)
- Configuration extraction from lambda functions
- Content preservation during conversion

**Expected Input:** Python code in `workflow_config_code/` format
**Expected Output:** JSON configurations in `workflow_config_generated/` format

### `test_actual_conversion_system.py`
Tests the actual conversion scripts with real workflow_configs data.

**What it tests:**
- Real conversion scripts execution
- Complete pipeline: JSON → Python → JSON using actual scripts
- Directory structure preservation
- File naming conventions
- Content preservation across conversions
- Convenience script functionality
- Integration with actual project structure

**Expected Input:** Real `workflow_configs/` directory
**Expected Output:** Identical structure in `workflow_config_generated/`

## Running Tests

### Run All Tests
```bash
# From project root
python tests/config_conversion/run_conversion_tests.py

# Or using pytest directly
pytest tests/config_conversion/ -v
```

### Run Individual Tests
```bash
# JSON to Code conversion
pytest tests/config_conversion/test_json_to_code_conversion.py -v

# Code to JSON conversion
pytest tests/config_conversion/test_code_to_json_conversion.py -v

# Actual conversion system
pytest tests/config_conversion/test_actual_conversion_system.py -v
```

## Test Structure

Each test uses temporary directories to avoid conflicts with actual configuration files:

```
temp_source/          # Temporary input directory
├── agents/
├── messages/
├── tools/
├── prompts/
└── workflows/

temp_target/          # Temporary output directory
├── agents/
├── messages/
├── tools/
├── prompts/
└── workflows/
```

## Expected Behaviors

### ✅ What Should Pass
- All configuration types convert correctly
- File structures match expected patterns
- Content is preserved exactly
- Unicode and special characters work
- Class inheritance is correct
- Interface methods are implemented
- Lambda configuration factories work
- Round-trip conversion preserves all data

### ❌ What Should Fail
- Missing required files
- Invalid Python syntax in generated code
- Incorrect class inheritance
- Missing interface methods
- Data loss during conversion
- Incorrect filename conventions

## Test Data Examples

### Sample Agent Configuration
```json
{
  "type": "agent",
  "tools": [
    {"name": "test_tool"}
  ],
  "messages": [
    {"content_from_file": "test_prompt"}
  ]
}
```

### Sample Generated Python Class
```python
class TestAgentAgentConfig(AgentProcessor):
    @staticmethod
    def get_type() -> str:
        return AgentProcessor.get_type()
    
    @staticmethod
    def get_name() -> str:
        return f"{TestAgentAgentConfig.get_type()}.test_agent"
    
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        config_factory = get_config()
        return config_factory(params or {})
```

### Sample Message Content
```markdown
Welcome to the test application!
This is a multi-line message.

Please proceed with the next steps.
```

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Configuration Conversion Tests
  run: |
    python tests/config_conversion/run_conversion_tests.py
```

## Debugging Failed Tests

### Common Issues
1. **Import Errors**: Ensure project root is in Python path
2. **File Not Found**: Check temporary directory creation
3. **Class Not Found**: Verify class naming conventions
4. **Content Mismatch**: Check encoding and line ending handling

### Debug Commands
```bash
# Run with verbose output
pytest tests/config_conversion/ -v -s

# Run specific test method
pytest tests/config_conversion/test_json_to_code_conversion.py::TestJsonToCodeConversion::test_agent_conversion -v

# Show test output
pytest tests/config_conversion/ --capture=no
```

## Coverage

The tests cover:
- ✅ All configuration types (agents, messages, tools, prompts, workflows)
- ✅ Forward conversion (JSON → Python)
- ✅ Reverse conversion (Python → JSON)
- ✅ Round-trip conversion (JSON → Python → JSON)
- ✅ Data preservation and integrity
- ✅ Unicode and special character handling
- ✅ File structure and naming conventions
- ✅ Class inheritance and interface compliance
- ✅ Configuration factory functions
- ✅ Error handling and edge cases
