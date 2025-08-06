# Workflow Configuration Conversion Scripts

This directory contains scripts for converting between JSON workflow configurations and Python code representations.

## Scripts Overview

### 1. `convert_configs_to_code.py`
Converts JSON configurations to Python code.

**Input**: `workflow_configs/` directory  
**Output**: `workflow_config_code/` directory

```bash
python convert_configs_to_code.py
```

### 2. `convert_code_to_configs.py`
Converts Python code back to JSON configurations.

**Input**: `workflow_config_code/` directory  
**Output**: `workflow_config_generated/` directory

```bash
python convert_code_to_configs.py
```

### 3. `test_roundtrip_conversion.py`
Tests that round-trip conversion preserves all data.

```bash
python test_roundtrip_conversion.py
```

### 4. `run_conversions.py`
Convenience script to run conversions and tests.

```bash
# Run both conversions
python run_conversions.py

# Run conversions + tests
python run_conversions.py --test

# Run only JSON to code
python run_conversions.py --json-to-code

# Run only code to JSON
python run_conversions.py --code-to-json
```

## Directory Structure

```
workflow_configs/           # Original JSON configs
├── agents/
├── messages/
├── tools/
├── prompts/
└── workflows/

workflow_config_code/       # Generated Python code
├── agents/
│   └── agent_name/
│       ├── __init__.py
│       ├── agent.py        # Class definition
│       └── config.py       # Configuration data
├── messages/
├── tools/
├── prompts/
└── workflows/

workflow_config_generated/  # Generated JSON configs
├── agents/
├── messages/
├── tools/
├── prompts/
└── workflows/
```

## Features

### Python Code Generation
- **Single Responsibility**: Each file has one clear purpose
- **Interface Inheritance**: Classes inherit from proper processor interfaces
- **Lambda Configuration**: All configs support parameterization
- **Type Safety**: Full type hints and IDE support
- **Natural Multi-line Strings**: Messages and prompts use clean triple quotes

### Round-trip Conversion
- **Data Preservation**: All original data is preserved
- **Additional Data**: Generated configs can contain more data than originals
- **Validation**: Comprehensive tests ensure accuracy
- **Warnings vs Errors**: Warnings for extra data, errors for missing data

### Code Structure
```python
# Agent Example
class ProcessUserInputAgentConfig(AgentProcessor):
    @staticmethod
    def get_type() -> str:
        return AgentProcessor.get_type()
    
    @staticmethod
    def get_name() -> str:
        return f"{ProcessUserInputAgentConfig.get_type()}.process_user_input"
    
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        config_factory = get_config()
        return config_factory(params or {})

# Tool Example
class WebSearchToolConfig(FunctionProcessor):
    @staticmethod
    def get_tool_name() -> str:
        return "web_search"
    
    @staticmethod
    def get_name() -> str:
        return f"{WebSearchToolConfig.get_type()}.web_search"

# Message Example
class WelcomeMessageConfig(MessageProcessor):
    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        config_factory = get_config()
        return config_factory(params or {})
```

## Testing

The test suite verifies:
- ✅ All configurations are converted correctly
- ✅ Round-trip conversion preserves data
- ✅ Generated configs contain at least the original data
- ✅ No data is lost in conversion
- ⚠️ Warnings for additional data (expected behavior)

## Usage Examples

```bash
# Full workflow with testing
python run_conversions.py --test

# Quick conversion check
python convert_configs_to_code.py
python convert_code_to_configs.py

# Verify round-trip accuracy
python test_roundtrip_conversion.py
```

## Notes

- **Warnings are expected**: The Python code contains many more configurations than the original JSON configs
- **Order doesn't matter**: Configurations can have additional fields
- **Type safety**: All generated code is fully type-safe with proper interfaces
- **IDE support**: Complete auto-completion and navigation support
