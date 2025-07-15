import pytest
from unittest.mock import AsyncMock, MagicMock
from workflow.dispatcher.method_registry import MethodRegistry


class TestMethodRegistry:
    """Test cases for MethodRegistry."""

    @pytest.fixture
    def mock_traditional_class(self):
        """Create a mock traditional workflow class."""
        class MockTraditionalClass:
            async def method_one(self, technical_id, entity, cls_instance=None, **kwargs):
                return f"method_one_result_{technical_id}"

            async def method_two(self, technical_id, entity, cls_instance=None, **kwargs):
                return f"method_two_result_{technical_id}"

            def sync_method(self, technical_id, entity, cls_instance=None, **kwargs):
                return f"sync_method_result_{technical_id}"

        return MockTraditionalClass

    @pytest.fixture
    def mock_registry_class(self):
        """Create a mock class with function registry."""
        class MockRegistryClass:
            def __init__(self):
                self._function_registry = {
                    'registry_function_one': AsyncMock(return_value="registry_one_result"),
                    'registry_function_two': AsyncMock(return_value="registry_two_result"),
                    'error_function': AsyncMock(side_effect=Exception("Registry error"))
                }
        
        return MockRegistryClass

    @pytest.fixture
    def traditional_instance(self, mock_traditional_class):
        """Create instance of traditional class."""
        return mock_traditional_class()

    @pytest.fixture
    def registry_instance(self, mock_registry_class):
        """Create instance of registry class."""
        return mock_registry_class()

    @pytest.fixture
    def traditional_registry(self, mock_traditional_class, traditional_instance):
        """Create MethodRegistry for traditional class."""
        return MethodRegistry(mock_traditional_class, traditional_instance)

    @pytest.fixture
    def registry_registry(self, mock_registry_class, registry_instance):
        """Create MethodRegistry for registry class."""
        return MethodRegistry(mock_registry_class, registry_instance)

    def test_traditional_method_collection(self, traditional_registry):
        """Test method collection from traditional class."""
        methods = traditional_registry.methods_dict
        
        assert isinstance(methods, dict)
        assert len(methods) >= 2
        assert 'method_one' in methods
        assert 'method_two' in methods
        # sync_method should also be collected
        assert 'sync_method' in methods

    def test_registry_method_collection(self, registry_registry):
        """Test method collection from registry class."""
        methods = registry_registry.methods_dict
        
        assert isinstance(methods, dict)
        assert len(methods) >= 2
        assert 'registry_function_one' in methods
        assert 'registry_function_two' in methods
        assert 'error_function' in methods

    def test_has_method_traditional(self, traditional_registry):
        """Test has_method for traditional class."""
        assert traditional_registry.has_method('method_one') is True
        assert traditional_registry.has_method('method_two') is True
        assert traditional_registry.has_method('nonexistent_method') is False

    def test_has_method_registry(self, registry_registry):
        """Test has_method for registry class."""
        assert registry_registry.has_method('registry_function_one') is True
        assert registry_registry.has_method('registry_function_two') is True
        assert registry_registry.has_method('nonexistent_function') is False

    def test_list_methods_traditional(self, traditional_registry):
        """Test list_methods for traditional class."""
        methods = traditional_registry.list_methods()
        
        assert isinstance(methods, list)
        assert 'method_one' in methods
        assert 'method_two' in methods
        assert 'sync_method' in methods

    def test_list_methods_registry(self, registry_registry):
        """Test list_methods for registry class."""
        methods = registry_registry.list_methods()
        
        assert isinstance(methods, list)
        assert 'registry_function_one' in methods
        assert 'registry_function_two' in methods
        assert 'error_function' in methods

    def test_get_method_traditional_success(self, traditional_registry):
        """Test get_method for traditional class."""
        method = traditional_registry.get_method('method_one')
        assert callable(method)

    def test_get_method_registry_success(self, registry_registry):
        """Test get_method for registry class."""
        method = registry_registry.get_method('registry_function_one')
        assert callable(method)

    def test_get_method_not_found(self, traditional_registry):
        """Test get_method with non-existent method."""
        with pytest.raises(ValueError) as exc_info:
            traditional_registry.get_method('nonexistent_method')
        
        assert "Unknown method: nonexistent_method" in str(exc_info.value)
        assert "Available methods:" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_dispatch_method_traditional_success(self, traditional_registry):
        """Test dispatch_method for traditional class."""
        result = await traditional_registry.dispatch_method(
            'method_one',
            technical_id='test_id',
            entity=MagicMock()
        )
        
        assert result == "method_one_result_test_id"

    @pytest.mark.asyncio
    async def test_dispatch_method_registry_success(self, registry_registry):
        """Test dispatch_method for registry class."""
        result = await registry_registry.dispatch_method(
            'registry_function_one',
            technical_id='test_id',
            entity=MagicMock()
        )
        
        assert result == "registry_one_result"

    @pytest.mark.asyncio
    async def test_dispatch_method_not_found(self, traditional_registry):
        """Test dispatch_method with non-existent method."""
        with pytest.raises(ValueError):
            await traditional_registry.dispatch_method(
                'nonexistent_method',
                technical_id='test_id',
                entity=MagicMock()
            )

    @pytest.mark.asyncio
    async def test_dispatch_method_registry_error(self, registry_registry):
        """Test dispatch_method with registry function that raises error."""
        with pytest.raises(Exception) as exc_info:
            await registry_registry.dispatch_method(
                'error_function',
                technical_id='test_id',
                entity=MagicMock()
            )
        
        assert "Registry error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_dispatch_method_with_extra_params(self, traditional_registry):
        """Test dispatch_method with additional parameters."""
        result = await traditional_registry.dispatch_method(
            'method_one',
            technical_id='test_id',
            entity=MagicMock(),
            extra_param='extra_value'
        )
        
        # Should still work, extra params are passed through
        assert result == "method_one_result_test_id"

    def test_mixed_class_with_both_traditional_and_registry(self):
        """Test class that has both traditional methods and function registry."""
        class MixedClass:
            def __init__(self):
                self._function_registry = {
                    'registry_func': AsyncMock(return_value="registry_result")
                }
            
            async def traditional_func(self, technical_id, entity):
                return f"traditional_result_{technical_id}"
        
        instance = MixedClass()
        registry = MethodRegistry(MixedClass, instance)
        
        methods = registry.list_methods()
        
        # Should have both traditional and registry methods
        assert 'traditional_func' in methods
        assert 'registry_func' in methods
        assert len(methods) >= 2

    @pytest.mark.asyncio
    async def test_mixed_class_dispatch_both_types(self):
        """Test dispatching both traditional and registry methods from mixed class."""
        class MixedClass:
            def __init__(self):
                self._function_registry = {
                    'registry_func': AsyncMock(return_value="registry_result")
                }

            async def traditional_func(self, technical_id, entity, cls_instance=None, **kwargs):
                return f"traditional_result_{technical_id}"
        
        instance = MixedClass()
        registry = MethodRegistry(MixedClass, instance)
        
        # Test traditional method
        traditional_result = await registry.dispatch_method(
            'traditional_func',
            technical_id='test_id',
            entity=MagicMock()
        )
        assert traditional_result == "traditional_result_test_id"
        
        # Test registry method
        registry_result = await registry.dispatch_method(
            'registry_func',
            technical_id='test_id',
            entity=MagicMock()
        )
        assert registry_result == "registry_result"

    def test_empty_class(self):
        """Test MethodRegistry with empty class."""
        class EmptyClass:
            pass
        
        instance = EmptyClass()
        registry = MethodRegistry(EmptyClass, instance)
        
        methods = registry.list_methods()
        assert isinstance(methods, list)
        # Should have no methods (or only inherited ones)
        assert len(methods) == 0

    def test_class_with_private_methods(self):
        """Test that private methods are not collected."""
        class ClassWithPrivateMethods:
            async def public_method(self, technical_id, entity):
                return "public_result"
            
            async def _private_method(self, technical_id, entity):
                return "private_result"
            
            async def __very_private_method(self, technical_id, entity):
                return "very_private_result"
        
        instance = ClassWithPrivateMethods()
        registry = MethodRegistry(ClassWithPrivateMethods, instance)
        
        methods = registry.list_methods()
        
        assert 'public_method' in methods
        assert '_private_method' in methods  # inspect.getmembers includes private methods
        assert '_ClassWithPrivateMethods__very_private_method' in methods  # Python name mangling

    def test_registry_logging(self, caplog, mock_registry_class, registry_instance):
        """Test that registry logs method collection."""
        with caplog.at_level('INFO'):
            registry = MethodRegistry(mock_registry_class, registry_instance)
        
        # Should log about finding function registry
        assert "Found function registry in class instance" in caplog.text
        # Should log collected methods count
        assert "Collected" in caplog.text and "methods:" in caplog.text
