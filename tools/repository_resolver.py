"""
Repository resolver using Strategy pattern to determine repository names
based on programming language and entity context.
"""

from abc import ABC, abstractmethod
from typing import Optional

from common.config.config import config
from entity.model import WorkflowEntity


class RepositoryResolver(ABC):
    """Abstract base class for repository resolution strategies."""
    
    @abstractmethod
    def resolve_repository_name(self, entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
        """
        Resolve repository name based on entity and programming language.
        
        Args:
            entity: Workflow entity
            programming_language: Optional programming language override
            
        Returns:
            Repository name
        """
        pass


class DefaultRepositoryResolver(RepositoryResolver):
    """
    Default repository resolver that follows the existing logic from utils.get_repository_name.
    This maintains backward compatibility with the current system.
    """
    
    def resolve_repository_name(self, entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
        """Resolve repository name using explicit priority order.

        Resolution priority:
        1. Explicit programming_language parameter
        2. Entity workflow_cache programming_language
        3. Entity workflow_name suffix (java/python)
        4. Default to Python

        Args:
            entity: Workflow entity containing context
            programming_language: Optional programming language override

        Returns:
            Repository name for the determined language
        """
        # Explicit parameter takes highest priority
        if programming_language:
            return self._get_repository_for_language(programming_language)

        # Check entity workflow cache
        if "programming_language" in entity.workflow_cache:
            cached_language = entity.workflow_cache["programming_language"]
            return self._get_repository_for_language(cached_language)

        # Fall back to workflow name suffix
        if entity.workflow_name.endswith("java"):
            return config.JAVA_REPOSITORY_NAME

        # Default to Python repository
        return config.PYTHON_REPOSITORY_NAME
    
    def _get_repository_for_language(self, programming_language: str) -> str:
        """Get repository name for a specific programming language.

        Args:
            programming_language: Programming language (case-insensitive)

        Returns:
            Repository name for the language, defaults to Python for unknown languages
        """
        language_upper = programming_language.upper()

        if language_upper == "JAVA":
            return config.JAVA_REPOSITORY_NAME

        if language_upper == "PYTHON":
            return config.PYTHON_REPOSITORY_NAME

        # Default to Python for unknown languages
        return config.PYTHON_REPOSITORY_NAME


class ParameterBasedRepositoryResolver(RepositoryResolver):
    """
    Repository resolver that prioritizes explicit programming_language parameter.
    Useful for functions that receive programming_language as a parameter.
    """
    
    def resolve_repository_name(self, entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
        """
        Resolve repository name with priority on programming_language parameter.
        
        Args:
            entity: Workflow entity
            programming_language: Programming language parameter
            
        Returns:
            Repository name
        """
        if programming_language:
            language_upper = programming_language.upper()
            if language_upper == "JAVA":
                return config.JAVA_REPOSITORY_NAME
            elif language_upper == "PYTHON":
                return config.PYTHON_REPOSITORY_NAME
        
        # Fall back to default resolver logic
        default_resolver = DefaultRepositoryResolver()
        return default_resolver.resolve_repository_name(entity, programming_language)


class RepositoryResolverFactory:
    """
    Factory for creating repository resolvers.
    Provides a centralized way to get the appropriate resolver.
    """
    
    @staticmethod
    def get_default_resolver() -> RepositoryResolver:
        """Get the default repository resolver."""
        return DefaultRepositoryResolver()
    
    @staticmethod
    def get_parameter_based_resolver() -> RepositoryResolver:
        """Get parameter-based repository resolver."""
        return ParameterBasedRepositoryResolver()
    
    @staticmethod
    def get_resolver_for_context(has_programming_language_param: bool = False) -> RepositoryResolver:
        """
        Get appropriate resolver based on context.
        
        Args:
            has_programming_language_param: Whether the calling function has programming_language parameter
            
        Returns:
            Appropriate repository resolver
        """
        if has_programming_language_param:
            return ParameterBasedRepositoryResolver()
        else:
            return DefaultRepositoryResolver()


# Convenience functions for backward compatibility
def resolve_repository_name(entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
    """Resolve repository name using default resolution strategy.

    Args:
        entity: Workflow entity containing context
        programming_language: Optional programming language override

    Returns:
        Repository name for the entity
    """
    resolver = RepositoryResolverFactory.get_default_resolver()
    return resolver.resolve_repository_name(entity, programming_language)


def resolve_repository_name_with_language_param(entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
    """Resolve repository name with priority on programming_language parameter.

    Args:
        entity: Workflow entity containing context
        programming_language: Programming language parameter with high priority

    Returns:
        Repository name based on parameter-prioritized resolution
    """
    resolver = RepositoryResolverFactory.get_parameter_based_resolver()
    return resolver.resolve_repository_name(entity, programming_language)
