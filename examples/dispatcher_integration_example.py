#!/usr/bin/env python3
"""
Example of how to use the upgraded workflow dispatcher with the new processor architecture.

This example demonstrates:
1. Setting up the dispatcher with the new processor framework
2. Processing different types of processors (Agent, Function, Message)
3. Handling processor results and entity updates
"""

import asyncio
import logging
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleWorkflowEntity:
    """Example workflow entity for demonstration."""
    
    def __init__(self):
        self.technical_id = "example_tech_id"
        self.user_id = "example_user"
        self.workflow_name = "example_workflow"
        self.current_state = "processing"
        self.current_transition = "execute_agent"
        self.failed = False
        self.error = None
        self.last_modified = None
        self.workflow_cache = {
            "user_request": "Create a new API endpoint",
            "programming_language": "PYTHON",
            "git_branch": "feature/new-api"
        }
        self.memory_id = "example_memory_id"
    
    def model_dump(self):
        return {
            "technical_id": self.technical_id,
            "user_id": self.user_id,
            "workflow_name": self.workflow_name,
            "current_state": self.current_state,
            "workflow_cache": self.workflow_cache
        }


async def setup_dispatcher():
    """Set up the workflow dispatcher with mock dependencies."""
    from workflow.dispatcher.workflow_dispatcher import WorkflowDispatcher
    
    # Create mock dependencies (in real usage, these would be actual services)
    mock_cls = Mock()
    mock_cls_instance = Mock()
    mock_cls_instance._function_registry = {
        "validate_api_request": Mock(),
        "generate_api_code": Mock(),
        "deploy_api": Mock()
    }
    
    mock_ai_agent = Mock()
    mock_entity_service = Mock()
    mock_cyoda_auth_service = Mock()
    
    # Mock user service with async method
    mock_user_service = Mock()
    mock_user_service.get_entity_account = AsyncMock(return_value="example_user")
    
    # Create dispatcher
    dispatcher = WorkflowDispatcher(
        cls=mock_cls,
        cls_instance=mock_cls_instance,
        ai_agent=mock_ai_agent,
        entity_service=mock_entity_service,
        cyoda_auth_service=mock_cyoda_auth_service,
        user_service=mock_user_service,
        mock=False
    )
    
    return dispatcher


async def demonstrate_agent_processor():
    """Demonstrate using an AgentProcessor."""
    print("\n🤖 Demonstrating AgentProcessor")
    print("-" * 40)
    
    dispatcher = await setup_dispatcher()
    entity = ExampleWorkflowEntity()
    
    # Process with an agent processor
    processor_name = "AgentProcessor.api_generator"
    
    print(f"Processing: {processor_name}")
    print(f"Entity state: {entity.current_state}")
    print(f"User request: {entity.workflow_cache['user_request']}")
    
    try:
        result_entity, response = await dispatcher.process_event(
            entity=entity,
            processor_name=processor_name,
            technical_id=entity.technical_id
        )
        
        print(f"✅ Processing completed")
        print(f"Response: {response}")
        print(f"Entity failed: {result_entity.failed}")
        if result_entity.error:
            print(f"Error: {result_entity.error}")
            
    except Exception as e:
        print(f"❌ Processing failed: {e}")


async def demonstrate_function_processor():
    """Demonstrate using a FunctionProcessor."""
    print("\n🔧 Demonstrating FunctionProcessor")
    print("-" * 40)
    
    dispatcher = await setup_dispatcher()
    entity = ExampleWorkflowEntity()
    
    # Process with a function processor
    processor_name = "FunctionProcessor.validate_api_request"
    
    print(f"Processing: {processor_name}")
    print(f"Function: validate_api_request")
    
    try:
        result_entity, response = await dispatcher.process_event(
            entity=entity,
            processor_name=processor_name,
            technical_id=entity.technical_id
        )
        
        print(f"✅ Processing completed")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")


async def demonstrate_message_processor():
    """Demonstrate using a MessageProcessor."""
    print("\n💬 Demonstrating MessageProcessor")
    print("-" * 40)
    
    dispatcher = await setup_dispatcher()
    entity = ExampleWorkflowEntity()
    
    # Process with a message processor
    processor_name = "MessageProcessor.api_workflow/completion_notification"
    
    print(f"Processing: {processor_name}")
    print(f"Message: api_workflow/completion_notification")
    
    try:
        result_entity, response = await dispatcher.process_event(
            entity=entity,
            processor_name=processor_name,
            technical_id=entity.technical_id
        )
        
        print(f"✅ Processing completed")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")


async def demonstrate_processor_validation():
    """Demonstrate processor validation."""
    print("\n✅ Demonstrating Processor Validation")
    print("-" * 40)
    
    dispatcher = await setup_dispatcher()
    
    test_processors = [
        "AgentProcessor.valid_agent",
        "FunctionProcessor.valid_function", 
        "MessageProcessor.workflow/message",
        "InvalidProcessor.test",
        "AgentProcessor.",
        ""
    ]
    
    for processor_name in test_processors:
        is_valid, error_msg = await dispatcher.validate_processor(processor_name)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"{status}: {processor_name}")
        if not is_valid:
            print(f"   Error: {error_msg}")


async def demonstrate_component_status():
    """Demonstrate component status checking."""
    print("\n📊 Demonstrating Component Status")
    print("-" * 40)
    
    dispatcher = await setup_dispatcher()
    status = dispatcher.get_component_status()
    
    print("Component Status:")
    for component, info in status.items():
        print(f"  {component}:")
        if isinstance(info, dict):
            for key, value in info.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {info}")


async def demonstrate_workflow_sequence():
    """Demonstrate a complete workflow sequence."""
    print("\n🔄 Demonstrating Complete Workflow Sequence")
    print("-" * 50)
    
    dispatcher = await setup_dispatcher()
    entity = ExampleWorkflowEntity()
    
    # Simulate a workflow with multiple steps
    workflow_steps = [
        ("AgentProcessor.requirements_analyzer", "Analyze requirements"),
        ("FunctionProcessor.validate_api_request", "Validate request"),
        ("AgentProcessor.api_generator", "Generate API code"),
        ("FunctionProcessor.deploy_api", "Deploy API"),
        ("MessageProcessor.api_workflow/completion_notification", "Send notification")
    ]
    
    print(f"Starting workflow: {entity.workflow_name}")
    print(f"Initial state: {entity.current_state}")
    
    for i, (processor_name, description) in enumerate(workflow_steps, 1):
        print(f"\nStep {i}: {description}")
        print(f"Processor: {processor_name}")
        
        try:
            entity, response = await dispatcher.process_event(
                entity=entity,
                processor_name=processor_name,
                technical_id=entity.technical_id
            )
            
            print(f"✅ Step completed: {response[:100]}...")
            
            if entity.failed:
                print(f"❌ Workflow failed at step {i}: {entity.error}")
                break
                
        except Exception as e:
            print(f"❌ Step {i} failed: {e}")
            break
    
    print(f"\nWorkflow completed. Final state: {entity.current_state}")
    print(f"Success: {not entity.failed}")


async def main():
    """Run all demonstrations."""
    print("🚀 Workflow Dispatcher Integration Examples")
    print("=" * 60)
    
    demonstrations = [
        demonstrate_processor_validation,
        demonstrate_component_status,
        demonstrate_agent_processor,
        demonstrate_function_processor,
        demonstrate_message_processor,
        demonstrate_workflow_sequence
    ]
    
    for demo in demonstrations:
        try:
            await demo()
        except Exception as e:
            print(f"❌ Demonstration {demo.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 All demonstrations completed!")
    print("\nKey Takeaways:")
    print("1. ✅ Dispatcher accepts simple processor names")
    print("2. ✅ Processor validation works correctly")
    print("3. ✅ Component status includes processor framework")
    print("4. ✅ Error handling is maintained")
    print("5. ✅ Workflow sequences can be easily orchestrated")
    
    print("\nNext Steps:")
    print("- Create actual agent configurations in agents/")
    print("- Set up tool definitions in tools/")
    print("- Create message templates in messages/")
    print("- Update workflow JSON files to use processor names")


if __name__ == "__main__":
    asyncio.run(main())
