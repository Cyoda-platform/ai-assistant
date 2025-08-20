# gRPC Client Tests

This directory contains comprehensive tests for the gRPC client architecture.

## Test Coverage

- **57 tests total** with **83% code coverage**
- **100% coverage** on core components (GrpcClient, Factory, Router, etc.)
- **Unit tests** (29): Individual component testing
- **Integration tests** (22): End-to-end functionality
- **Backward compatibility tests** (6): API preservation

## Running Tests

### Option 1: Using the Test Script (Recommended)

From any directory in the project:

```bash
python run_grpc_tests.py
```

This script automatically:
- Finds the correct project directory
- Sets up the proper environment
- Runs all gRPC client tests
- Shows clear pass/fail results

### Option 2: Direct pytest (from project root)

From the project root directory (`/home/kseniia/IdeaProjects/ai-assistant-2`):

```bash
# Run all gRPC client tests
pytest tests/common/grpc_client/ -v

# Run with coverage
pytest tests/common/grpc_client/ --cov=common/grpc_client --cov-report=term-missing

# Run specific test file
pytest tests/common/grpc_client/test_grpc_client_integration.py -v

# Run specific test
pytest tests/common/grpc_client/test_grpc_client_integration.py::test_grpc_client_initialization -v
```

## Test Structure

```
tests/common/grpc_client/
├── test_grpc_client_app_integration.py    # App integration & backward compatibility
├── test_grpc_client_integration.py        # GrpcClient integration tests
└── test_router_handlers_builders.py       # Component unit tests
```

## Key Test Categories

### 1. Unit Tests (`test_router_handlers_builders.py`)
- **EventRouter**: Registration and routing logic
- **ResponseBuilders**: CloudEvent creation (Join, Ack, Calc, Criteria)
- **Handlers**: Business logic for each event type
- **Middleware**: Chain of responsibility pattern
- **Outbox**: Event generation and streaming
- **Factory**: Component creation and wiring

### 2. Integration Tests (`test_grpc_client_integration.py`)
- **Initialization**: Lazy facade creation
- **Authentication**: Token handling with retry
- **Event Processing**: End-to-end event flow
- **Delegation**: Method forwarding to facade
- **Exception Handling**: Error scenarios

### 3. Backward Compatibility (`test_grpc_client_app_integration.py`)
- **Constructor**: Signature unchanged
- **Public API**: All methods preserved
- **Constants**: Still importable
- **No Breaking Changes**: Verified

## Architecture Validation

The tests verify the clean architecture implementation:

```
CloudEventRequest → GrpcStreamingFacade → Middleware Chain:
  LoggingMiddleware → MetricsMiddleware → ErrorMiddleware → DispatchMiddleware:
    EventRouter → Handler → ResponseSpec → ResponseBuilder → CloudEventResponse → Outbox
```

## Critical Behaviors Tested

- ✅ **Calc responses always return success=True** (even on failure)
- ✅ **Greet events trigger rollback** via processor_loop
- ✅ **KeepAlive events generate ACK responses**
- ✅ **Error events are logged** without responses
- ✅ **Exception handling** with logger.exception calls
- ✅ **Join events sent first** in event generator
- ✅ **Auth token retry** on failure
- ✅ **Lazy facade initialization**

## Troubleshooting

### "async def functions are not natively supported"

This error occurs when pytest is run from the wrong directory. Solutions:

1. **Use the test script**: `python run_grpc_tests.py` (recommended)
2. **Run from project root**: Ensure you're in `/home/kseniia/IdeaProjects/ai-assistant-2`
3. **Check pytest config**: The `pytest.ini` file should be in the project root

### Import Errors

If you get import errors:
1. Ensure you're running from the project root directory
2. Check that the virtual environment is activated
3. Verify all dependencies are installed

## Configuration

The tests use:
- **pytest.ini**: Main pytest configuration
- **asyncio_mode = auto**: Automatic async test detection
- **Proper markers**: For test categorization
- **Warning filters**: To reduce noise in output

## Coverage Report

To generate an HTML coverage report:

```bash
pytest tests/common/grpc_client/ --cov=common/grpc_client --cov-report=html
```

Open `htmlcov/index.html` in a browser to view detailed coverage.
