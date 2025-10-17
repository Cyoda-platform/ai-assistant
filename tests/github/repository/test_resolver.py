"""
Tests for repository resolver.
"""

import pytest
from unittest.mock import MagicMock, patch
from services.github.repository.resolver import (
    RepositoryResolver,
    DefaultRepositoryResolver,
    ParameterBasedRepositoryResolver,
    RepositoryResolverFactory,
    resolve_repository_name,
    resolve_repository_name_with_language_param,
)
from entity.model import WorkflowEntity


class TestDefaultRepositoryResolver:
    """Test DefaultRepositoryResolver."""
    
    def test_resolve_with_explicit_parameter_python(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity, "python")
            assert result == "python-repo"
    
    def test_resolve_with_explicit_parameter_java(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java-repo"
            result = resolver.resolve_repository_name(entity, "java")
            assert result == "java-repo"
    
    def test_resolve_from_workflow_cache(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {"programming_language": "python"}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity)
            assert result == "python-repo"
    
    def test_resolve_from_workflow_name_java(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "build_application_java"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java-repo"
            result = resolver.resolve_repository_name(entity)
            assert result == "java-repo"
    
    def test_resolve_defaults_to_python(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity)
            assert result == "python-repo"
    
    def test_resolve_unknown_language_defaults_to_python(self):
        resolver = DefaultRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity, "rust")
            assert result == "python-repo"


class TestParameterBasedRepositoryResolver:
    """Test ParameterBasedRepositoryResolver."""
    
    def test_resolve_with_parameter_python(self):
        resolver = ParameterBasedRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity, "python")
            assert result == "python-repo"
    
    def test_resolve_with_parameter_java(self):
        resolver = ParameterBasedRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java-repo"
            result = resolver.resolve_repository_name(entity, "JAVA")
            assert result == "java-repo"
    
    def test_resolve_falls_back_to_default(self):
        resolver = ParameterBasedRepositoryResolver()
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolver.resolve_repository_name(entity)
            assert result == "python-repo"


class TestRepositoryResolverFactory:
    """Test RepositoryResolverFactory."""
    
    def test_get_default_resolver(self):
        resolver = RepositoryResolverFactory.get_default_resolver()
        assert isinstance(resolver, DefaultRepositoryResolver)
    
    def test_get_parameter_based_resolver(self):
        resolver = RepositoryResolverFactory.get_parameter_based_resolver()
        assert isinstance(resolver, ParameterBasedRepositoryResolver)
    
    def test_get_resolver_for_context_with_param(self):
        resolver = RepositoryResolverFactory.get_resolver_for_context(
            has_programming_language_param=True
        )
        assert isinstance(resolver, ParameterBasedRepositoryResolver)
    
    def test_get_resolver_for_context_without_param(self):
        resolver = RepositoryResolverFactory.get_resolver_for_context(
            has_programming_language_param=False
        )
        assert isinstance(resolver, DefaultRepositoryResolver)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_resolve_repository_name(self):
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolve_repository_name(entity)
            assert result == "python-repo"
    
    def test_resolve_repository_name_with_language(self):
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java-repo"
            result = resolve_repository_name(entity, "java")
            assert result == "java-repo"
    
    def test_resolve_repository_name_with_language_param(self):
        entity = MagicMock(spec=WorkflowEntity)
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.repository.resolver.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            result = resolve_repository_name_with_language_param(entity, "python")
            assert result == "python-repo"

