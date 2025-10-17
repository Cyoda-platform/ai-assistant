"""
Repository resolver using Strategy pattern to determine repository names
based on programming language and entity context.

DEPRECATED: This module is kept for backward compatibility.
New code should use: from services.github.repository import resolver
"""

import warnings
from typing import Optional

from entity.model import WorkflowEntity

# Import from new location
from services.github.repository.resolver import (
    RepositoryResolver,
    DefaultRepositoryResolver,
    ParameterBasedRepositoryResolver,
    RepositoryResolverFactory,
    resolve_repository_name as _new_resolve_repository_name,
    resolve_repository_name_with_language_param as _new_resolve_repository_name_with_language_param,
)

# Re-export for backward compatibility
__all__ = [
    "RepositoryResolver",
    "DefaultRepositoryResolver",
    "ParameterBasedRepositoryResolver",
    "RepositoryResolverFactory",
    "resolve_repository_name",
    "resolve_repository_name_with_language_param",
]


def resolve_repository_name(entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
    """Resolve repository name using default resolution strategy.

    DEPRECATED: Use services.github.repository.resolver.resolve_repository_name instead.

    Args:
        entity: Workflow entity containing context
        programming_language: Optional programming language override

    Returns:
        Repository name for the entity
    """
    warnings.warn(
        "functions.repository_resolver is deprecated. Use services.github.repository.resolver instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _new_resolve_repository_name(entity, programming_language)


def resolve_repository_name_with_language_param(entity: WorkflowEntity, programming_language: Optional[str] = None) -> str:
    """Resolve repository name with priority on programming_language parameter.

    DEPRECATED: Use services.github.repository.resolver.resolve_repository_name_with_language_param instead.

    Args:
        entity: Workflow entity containing context
        programming_language: Programming language parameter with high priority

    Returns:
        Repository name based on parameter-prioritized resolution
    """
    warnings.warn(
        "functions.repository_resolver is deprecated. Use services.github.repository.resolver instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _new_resolve_repository_name_with_language_param(entity, programming_language)
