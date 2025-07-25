"""
Tests for repository resolver classes and functions.
"""

import pytest
from unittest.mock import Mock, patch

from tools.repository_resolver import (
    DefaultRepositoryResolver,
    ParameterBasedRepositoryResolver,
    RepositoryResolverFactory,
    resolve_repository_name,
    resolve_repository_name_with_language_param
)
from entity.model import WorkflowEntity


class TestDefaultRepositoryResolver:
    """Test cases for DefaultRepositoryResolver."""
    
    @pytest.fixture
    def resolver(self):
        """Create DefaultRepositoryResolver instance."""
        return DefaultRepositoryResolver()
    
    @pytest.fixture
    def mock_entity(self):
        """Create mock WorkflowEntity."""
        entity = Mock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        return entity
    
    def test_resolve_with_explicit_programming_language(self, resolver, mock_entity):
        """Test resolution with explicit programming language parameter."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Test JAVA
            result = resolver.resolve_repository_name(mock_entity, "JAVA")
            assert result == "java_repo"
            
            # Test java (lowercase)
            result = resolver.resolve_repository_name(mock_entity, "java")
            assert result == "java_repo"
            
            # Test PYTHON
            result = resolver.resolve_repository_name(mock_entity, "PYTHON")
            assert result == "python_repo"
            
            # Test python (lowercase)
            result = resolver.resolve_repository_name(mock_entity, "python")
            assert result == "python_repo"
    
    def test_resolve_with_cached_programming_language(self, resolver, mock_entity):
        """Test resolution with programming language in entity cache."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Test with JAVA in cache
            mock_entity.workflow_cache = {"programming_language": "JAVA"}
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "java_repo"
            
            # Test with PYTHON in cache
            mock_entity.workflow_cache = {"programming_language": "PYTHON"}
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "python_repo"
    
    def test_resolve_with_workflow_name_suffix(self, resolver, mock_entity):
        """Test resolution based on workflow name suffix."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Test java suffix
            mock_entity.workflow_name = "test_workflow_java"
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "java_repo"
            
            # Test python suffix (default)
            mock_entity.workflow_name = "test_workflow_python"
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "python_repo"
            
            # Test no specific suffix (defaults to python)
            mock_entity.workflow_name = "test_workflow"
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "python_repo"
    
    def test_priority_order(self, resolver, mock_entity):
        """Test that explicit parameter takes priority over cache and workflow name."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Set up entity with JAVA in cache and java workflow name
            mock_entity.workflow_cache = {"programming_language": "JAVA"}
            mock_entity.workflow_name = "test_workflow_java"
            
            # Explicit PYTHON parameter should override everything
            result = resolver.resolve_repository_name(mock_entity, "PYTHON")
            assert result == "python_repo"
    
    def test_unknown_language_defaults_to_python(self, resolver, mock_entity):
        """Test that unknown languages default to Python repository."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            result = resolver.resolve_repository_name(mock_entity, "UNKNOWN")
            assert result == "python_repo"


class TestParameterBasedRepositoryResolver:
    """Test cases for ParameterBasedRepositoryResolver."""
    
    @pytest.fixture
    def resolver(self):
        """Create ParameterBasedRepositoryResolver instance."""
        return ParameterBasedRepositoryResolver()
    
    @pytest.fixture
    def mock_entity(self):
        """Create mock WorkflowEntity."""
        entity = Mock(spec=WorkflowEntity)
        entity.workflow_cache = {"programming_language": "JAVA"}
        entity.workflow_name = "test_workflow_java"
        return entity
    
    def test_parameter_takes_priority(self, resolver, mock_entity):
        """Test that programming_language parameter takes priority."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Even though entity has JAVA, PYTHON parameter should win
            result = resolver.resolve_repository_name(mock_entity, "PYTHON")
            assert result == "python_repo"
    
    def test_fallback_to_default_logic(self, resolver, mock_entity):
        """Test fallback to default resolver logic when no parameter."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            
            # Should use entity cache when no parameter
            result = resolver.resolve_repository_name(mock_entity)
            assert result == "java_repo"


class TestRepositoryResolverFactory:
    """Test cases for RepositoryResolverFactory."""
    
    def test_get_default_resolver(self):
        """Test getting default resolver."""
        resolver = RepositoryResolverFactory.get_default_resolver()
        assert isinstance(resolver, DefaultRepositoryResolver)
    
    def test_get_parameter_based_resolver(self):
        """Test getting parameter-based resolver."""
        resolver = RepositoryResolverFactory.get_parameter_based_resolver()
        assert isinstance(resolver, ParameterBasedRepositoryResolver)
    
    def test_get_resolver_for_context(self):
        """Test getting resolver based on context."""
        # Without programming language parameter
        resolver = RepositoryResolverFactory.get_resolver_for_context(has_programming_language_param=False)
        assert isinstance(resolver, DefaultRepositoryResolver)
        
        # With programming language parameter
        resolver = RepositoryResolverFactory.get_resolver_for_context(has_programming_language_param=True)
        assert isinstance(resolver, ParameterBasedRepositoryResolver)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @pytest.fixture
    def mock_entity(self):
        """Create mock WorkflowEntity."""
        entity = Mock(spec=WorkflowEntity)
        entity.workflow_cache = {"programming_language": "PYTHON"}
        entity.workflow_name = "test_workflow"
        return entity
    
    def test_resolve_repository_name(self, mock_entity):
        """Test resolve_repository_name convenience function."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            result = resolve_repository_name(mock_entity)
            assert result == "python_repo"
    
    def test_resolve_repository_name_with_language_param(self, mock_entity):
        """Test resolve_repository_name_with_language_param convenience function."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            
            # Parameter should override entity cache
            result = resolve_repository_name_with_language_param(mock_entity, "JAVA")
            assert result == "java_repo"
    
    def test_backward_compatibility_with_utils(self, mock_entity):
        """Test that convenience function behaves like utils.get_repository_name."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python_repo"
            mock_config.JAVA_REPOSITORY_NAME = "java_repo"
            
            # Test same scenarios as utils.get_repository_name
            
            # 1. With programming_language in cache
            mock_entity.workflow_cache = {"programming_language": "PYTHON"}
            result = resolve_repository_name(mock_entity)
            assert result == "python_repo"
            
            # 2. Without programming_language, with java workflow name
            mock_entity.workflow_cache = {}
            mock_entity.workflow_name = "test_workflow_java"
            result = resolve_repository_name(mock_entity)
            assert result == "java_repo"
            
            # 3. Without programming_language, with python workflow name
            mock_entity.workflow_name = "test_workflow_python"
            result = resolve_repository_name(mock_entity)
            assert result == "python_repo"
            
            # 4. Default case
            mock_entity.workflow_name = "test_workflow"
            result = resolve_repository_name(mock_entity)
            assert result == "python_repo"


class TestIntegrationWithExistingCode:
    """Test integration with existing codebase patterns."""
    
    @pytest.fixture
    def mock_entity(self):
        """Create mock entity similar to real usage."""
        entity = Mock(spec=WorkflowEntity)
        entity.workflow_cache = {
            "programming_language": "JAVA",
            "git_branch": "feature_branch"
        }
        entity.workflow_name = "build_general_application_java"
        return entity
    
    def test_application_builder_pattern(self, mock_entity):
        """Test pattern used in application_builder_service.py."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_template"
            mock_config.PYTHON_REPOSITORY_NAME = "python_template"
            
            # Simulate application_builder_service pattern
            programming_language = "JAVA"
            resolver = RepositoryResolverFactory.get_parameter_based_resolver()
            repository_name = resolver.resolve_repository_name(mock_entity, programming_language)
            
            assert repository_name == "java_template"
    
    def test_file_operations_pattern(self, mock_entity):
        """Test pattern used in file_operations_service.py."""
        with patch('tools.repository_resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java_template"
            
            # Simulate file_operations_service pattern (no explicit programming_language)
            resolver = RepositoryResolverFactory.get_default_resolver()
            repository_name = resolver.resolve_repository_name(mock_entity)
            
            assert repository_name == "java_template"
