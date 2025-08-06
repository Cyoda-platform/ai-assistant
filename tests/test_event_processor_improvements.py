#!/usr/bin/env python3
"""
Test script for event processor improvements.
"""

import asyncio
import sys
import threading
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.config_builder import ConfigBuilder
from workflow.dispatcher.event_processor import EventProcessor
from entity.model import WorkflowEntity


class TestEventProcessorImprovements:
    """Test the improved event processor functionality."""
    
    def setup_mocks(self):
        """Set up mock objects for testing."""
        self.method_registry = MagicMock()
        self.ai_agent_handler = AsyncMock()
        self.memory_manager = AsyncMock()
        self.file_handler = AsyncMock()
        self.message_processor = AsyncMock()
        self.user_service = AsyncMock()
        self.entity_service = AsyncMock()
        self.cyoda_auth_service = AsyncMock()
        self.config_builder = MagicMock()
        
        # Mock user service to return the same user_id
        self.user_service.get_entity_account.return_value = "test_user_123"
        
        # Mock method registry
        self.method_registry.has_method.return_value = True
        self.method_registry.dispatch_method = AsyncMock(return_value="Direct method executed successfully")
        
        # Create event processor
        self.event_processor = EventProcessor(
            method_registry=self.method_registry,
            ai_agent_handler=self.ai_agent_handler,
            memory_manager=self.memory_manager,
            file_handler=self.file_handler,
            message_processor=self.message_processor,
            user_service=self.user_service,
            entity_service=self.entity_service,
            cyoda_auth_service=self.cyoda_auth_service,
            config_builder=self.config_builder
        )
    
    async def test_direct_method_execution(self):
        """Test that methods without 'Processor.' prefix execute directly."""
        print("Testing direct method execution...")
        
        self.setup_mocks()
        
        # Create test entity
        entity = WorkflowEntity(
            user_id="test_user",
            technical_id="test_tech_id"
        )
        
        # Test direct method call (no "Processor." prefix)
        processor_name = "test_method"
        technical_id = "test_tech_123"
        
        result_entity, response = await self.event_processor.process_event(
            entity=entity,
            processor_name=processor_name,
            technical_id=technical_id
        )
        
        # Verify direct method was called
        self.method_registry.dispatch_method.assert_called_once_with(
            method_name="test_method",
            technical_id=technical_id,
            entity=entity
        )
        
        # Verify config builder was NOT called
        self.config_builder.build_config.assert_not_called()
        
        print("✅ Direct method execution test passed")
        return True
    
    async def test_processor_method_execution(self):
        """Test that methods with 'Processor.' prefix use config building."""
        print("Testing processor method execution...")
        
        self.setup_mocks()
        
        # Mock config builder to return a valid config
        self.config_builder.build_config.return_value = {
            "type": "function",
            "function": {
                "name": "test_function",
                "parameters": {}
            }
        }
        
        # Create test entity
        entity = WorkflowEntity(
            user_id="test_user",
            technical_id="test_tech_id"
        )
        
        # Test processor method call
        processor_name = "FunctionProcessor.test_method"
        technical_id = "test_tech_123"
        
        result_entity, response = await self.event_processor.process_event(
            entity=entity,
            processor_name=processor_name,
            technical_id=technical_id
        )
        
        # Verify config builder was called
        self.config_builder.build_config.assert_called_once_with("FunctionProcessor.test_method")
        
        print("✅ Processor method execution test passed")
        return True
    
    def test_config_builder_caching(self):
        """Test that config builder caching works correctly."""
        print("Testing config builder caching...")
        
        # Create a test config builder with a temporary directory
        test_configs_path = Path(__file__).parent / "temp_test_configs"
        test_configs_path.mkdir(exist_ok=True)
        
        # Create a simple tools directory structure for testing
        tools_path = test_configs_path / "tools" / "test_tool"
        tools_path.mkdir(parents=True, exist_ok=True)
        
        tool_config = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool"
            }
        }
        
        with open(tools_path / "tool.json", "w") as f:
            import json
            json.dump(tool_config, f)
        
        try:
            config_builder = ConfigBuilder(str(test_configs_path))
            
            # First call - should build and cache
            config1 = config_builder.build_config("FunctionProcessor.test_tool")
            cache_size_after_first = config_builder.get_cache_size()
            
            # Second call - should use cache
            config2 = config_builder.build_config("FunctionProcessor.test_tool")
            cache_size_after_second = config_builder.get_cache_size()
            
            # Verify caching worked
            assert cache_size_after_first == 1, f"Expected cache size 1, got {cache_size_after_first}"
            assert cache_size_after_second == 1, f"Expected cache size 1, got {cache_size_after_second}"
            assert config1 == config2, "Configs should be identical"
            
            # Test cache clearing
            config_builder.clear_cache()
            assert config_builder.get_cache_size() == 0, "Cache should be empty after clearing"
            
            print("✅ Config builder caching test passed")
            return True
            
        finally:
            # Clean up test directory
            import shutil
            if test_configs_path.exists():
                shutil.rmtree(test_configs_path)
    
    def test_concurrent_config_access(self):
        """Test that concurrent config access is thread-safe."""
        print("Testing concurrent config access...")
        
        # Create a test config builder
        test_configs_path = Path(__file__).parent / "temp_concurrent_test"
        test_configs_path.mkdir(exist_ok=True)
        
        tools_path = test_configs_path / "tools" / "concurrent_tool"
        tools_path.mkdir(parents=True, exist_ok=True)
        
        tool_config = {
            "type": "function",
            "function": {
                "name": "concurrent_tool",
                "description": "A concurrent test tool"
            }
        }
        
        with open(tools_path / "tool.json", "w") as f:
            import json
            json.dump(tool_config, f)
        
        try:
            config_builder = ConfigBuilder(str(test_configs_path))
            results = []
            errors = []
            
            def worker():
                try:
                    for i in range(10):
                        config = config_builder.build_config("FunctionProcessor.concurrent_tool")
                        results.append(config)
                        time.sleep(0.001)  # Small delay to increase chance of race conditions
                except Exception as e:
                    errors.append(e)
            
            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify no errors occurred
            assert len(errors) == 0, f"Errors occurred during concurrent access: {errors}"
            assert len(results) == 50, f"Expected 50 results, got {len(results)}"
            
            # Verify all results are identical
            first_result = results[0]
            for result in results[1:]:
                assert result == first_result, "All results should be identical"
            
            print("✅ Concurrent config access test passed")
            return True
            
        finally:
            # Clean up test directory
            import shutil
            if test_configs_path.exists():
                shutil.rmtree(test_configs_path)


async def run_tests():
    """Run all tests."""
    print("Running Event Processor Improvement Tests")
    print("=" * 50)
    
    test_suite = TestEventProcessorImprovements()
    
    try:
        # Run async tests
        await test_suite.test_direct_method_execution()
        await test_suite.test_processor_method_execution()
        
        # Run sync tests
        test_suite.test_config_builder_caching()
        test_suite.test_concurrent_config_access()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(run_tests())
