#!/usr/bin/env python3
"""
Example usage of the ConfigBuilder for different processor types.
"""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.config_builder import build_processor_config


def example_agent_processor():
    """Example: Building AgentProcessor configuration."""
    print("=== AgentProcessor Example ===")
    
    # Build config for AgentProcessor.submit_answer_5607
    config = build_processor_config("AgentProcessor.submit_answer_5607")
    
    print(f"Agent Type: {config['type']}")
    print(f"Model: {config['model']['model_name']}")
    print(f"Temperature: {config['model']['temperature']}")
    print(f"Max Tokens: {config['model']['max_tokens']}")
    print(f"Number of Tools: {len(config['tools'])}")
    
    # Show first tool as example
    if config['tools']:
        first_tool = config['tools'][0]
        print(f"First Tool: {first_tool['function']['name']}")
        print(f"Tool Description: {first_tool['function']['description'][:50]}...")
    
    # Show message content
    if config['messages']:
        first_message = config['messages'][0]
        print(f"Message Role: {first_message['role']}")
        print(f"Message Content: {first_message['content'][:100]}...")
    
    print()


def example_function_processor():
    """Example: Building FunctionProcessor configuration."""
    print("=== FunctionProcessor Example ===")
    
    # Build config for FunctionProcessor.add_new_workflow
    config = build_processor_config("FunctionProcessor.add_new_workflow")
    
    print(f"Type: {config['type']}")
    print(f"Function Name: {config['function']['name']}")
    print(f"Description: {config['function']['description'][:100]}...")
    print(f"Strict Mode: {config['function']['strict']}")
    
    # Show parameters
    params = config['function']['parameters']
    print(f"Parameter Type: {params['type']}")
    print(f"Required Fields: {params['required']}")
    print(f"Properties: {list(params['properties'].keys())}")
    
    print()


def example_message_processor():
    """Example: Building MessageProcessor configuration."""
    print("=== MessageProcessor Example ===")
    
    # Build config for MessageProcessor.submit_answer_5607
    config = build_processor_config("MessageProcessor.submit_answer_5607")
    
    print(f"Type: {config['type']}")
    print(f"Notification: {config['notification']}")
    print(f"Publish: {config['publish']}")
    print(f"Allow Anonymous Users: {config['allow_anonymous_users']}")
    
    print()


def example_batch_processing():
    """Example: Processing multiple processor names."""
    print("=== Batch Processing Example ===")
    
    processor_names = [
        "AgentProcessor.submit_answer_5607",
        "FunctionProcessor.add_new_workflow",
        "MessageProcessor.submit_answer_5607"
    ]
    
    configs = {}
    
    for processor_name in processor_names:
        try:
            config = build_processor_config(processor_name)
            configs[processor_name] = config
            print(f"✓ Successfully built config for: {processor_name}")
        except Exception as e:
            print(f"✗ Failed to build config for {processor_name}: {e}")
    
    print(f"\nTotal configs built: {len(configs)}")
    print()


def example_workflow_integration():
    """Example: How to integrate with workflow processing."""
    print("=== Workflow Integration Example ===")
    
    # Simulate workflow processor names from a workflow definition
    workflow_processors = [
        "AgentProcessor.submit_answer_5607",
        "FunctionProcessor.add_new_workflow", 
        "MessageProcessor.submit_answer_5607"
    ]
    
    print("Processing workflow with processors:")
    
    for processor_name in workflow_processors:
        print(f"\n--- Processing {processor_name} ---")
        
        try:
            config = build_processor_config(processor_name)
            
            # Different handling based on processor type
            processor_type = processor_name.split(".")[0]
            
            if processor_type == "AgentProcessor":
                print(f"  Agent with {len(config.get('tools', []))} tools")
                print(f"  Model: {config.get('model', {}).get('model_name', 'unknown')}")
                
            elif processor_type == "FunctionProcessor":
                func_name = config.get('function', {}).get('name', 'unknown')
                print(f"  Function: {func_name}")
                
            elif processor_type == "MessageProcessor":
                msg_type = config.get('type', 'unknown')
                print(f"  Message type: {msg_type}")
                print(f"  Content: {config.get('notification', '')[:50]}...")
            
            print("  ✓ Config built successfully")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")


def main():
    """Run all examples."""
    print("ConfigBuilder Usage Examples")
    print("=" * 50)
    print()
    
    example_agent_processor()
    example_function_processor()
    example_message_processor()
    example_batch_processing()
    example_workflow_integration()
    
    print("=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
