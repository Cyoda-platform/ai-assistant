# Workflow Dispatcher - Modular Architecture

This directory contains the refactored workflow dispatcher with a modular architecture that follows the class diagram specifications. Each class is now organized in its own directory and file for better maintainability and separation of concerns.

## Directory Structure

```
workflow/dispatcher/
├── README.md                           # This documentation
├── event_processor.py                  # Backward compatibility wrapper
├── workflow_dispatcher.py              # Main dispatcher (unchanged)
├── events/                             # Event-related classes
│   ├── __init__.py
│   ├── workflow_event.py               # WorkflowEvent class
│   ├── processing_context.py           # ProcessingContext class
│   └── services.py                     # Services container
├── actions/                            # Action classes
│   ├── __init__.py
│   ├── action.py                       # Base Action class
│   ├── notification_action.py          # NotificationAction
│   ├── function_action.py              # FunctionAction
│   ├── agent_action.py                 # AgentAction
│   └── direct_method_action.py         # DirectMethodAction
├── processors/                         # Processor classes
│   ├── __init__.py
│   ├── processor.py                    # Base Processor class
│   ├── agent_processor.py              # AgentProcessor
│   ├── function_processor.py           # FunctionProcessor
│   ├── message_processor.py            # MessageProcessor
│   └── processor_selector.py           # ProcessorSelector
├── resolvers/                          # Resolver classes
│   ├── __init__.py
│   └── action_resolver.py              # ActionResolver
├── responders/                         # Responder classes
│   ├── __init__.py
│   ├── output_writer.py                # OutputWriter
│   ├── edge_message_appender.py        # EdgeMessageAppender
│   └── responder.py                    # Responder
└── dispatchers/                        # Dispatcher classes
    ├── __init__.py
    └── event_dispatcher.py             # EventDispatcher
```

## Class Relationships

The architecture follows the class diagram with clear separation of concerns:

1. **EventDispatcher** - Main coordinator that orchestrates all components
2. **WorkflowEvent** - Represents events to be processed
3. **ProcessingContext** - Context for event processing
4. **Services** - Container for all required services
5. **ActionResolver** - Resolves events into appropriate actions
6. **Action Classes** - Different types of actions (Notification, Function, Agent, DirectMethod)
7. **ProcessorSelector** - Selects appropriate processor for actions
8. **Processor Classes** - Execute specific processing logic
9. **Responder** - Coordinates response finalization
10. **OutputWriter** - Handles output writing
11. **EdgeMessageAppender** - Manages edge message creation

## Usage

### For New Code
```python
from workflow.dispatcher.events import WorkflowEvent
from workflow.dispatcher.dispatchers import EventDispatcher

# Create event dispatcher
dispatcher = EventDispatcher(...)

# Create and process event
event = WorkflowEvent(entity, processor_name, payload, technical_id)
result = await dispatcher.process(event)
```

### For Backward Compatibility
```python
from workflow.dispatcher.event_processor import EventProcessor

# Use exactly as before
processor = EventProcessor(...)
result = await processor.process_event(entity, processor_name, payload, technical_id)
```

## Benefits

1. **Modularity** - Each class has a single responsibility
2. **Testability** - Components can be tested in isolation
3. **Maintainability** - Clear structure makes code easier to understand and modify
4. **Extensibility** - New action types and processors can be easily added
5. **Backward Compatibility** - Existing code continues to work unchanged

## Migration Guide

No migration is required! The `EventProcessor` class maintains the exact same interface and delegates to the new modular architecture internally. All existing code will continue to work without any changes.
