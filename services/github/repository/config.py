"""
Repository configuration management.
"""

from dataclasses import dataclass
from typing import Optional

from common.config.config import config


@dataclass
class RepositoryConfig:
    """Configuration for a repository."""
    
    name: str
    owner: str
    default_branch: str = "main"
    url_template: Optional[str] = None
    raw_url_template: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get repository URL."""
        template = self.url_template or config.REPOSITORY_URL
        return template.format(owner=self.owner, repository_name=self.name)
    
    @property
    def raw_url(self) -> str:
        """Get raw repository URL."""
        template = self.raw_url_template or config.RAW_REPOSITORY_URL
        return template.format(owner=self.owner, repository_name=self.name)
    
    @classmethod
    def from_name(cls, repository_name: str, owner: Optional[str] = None) -> "RepositoryConfig":
        """Create repository config from name.
        
        Args:
            repository_name: Name of the repository
            owner: Repository owner (defaults to config owner)
            
        Returns:
            RepositoryConfig instance
        """
        return cls(
            name=repository_name,
            owner=owner or config.GH_DEFAULT_OWNER,
            default_branch=config.CLIENT_GIT_BRANCH,
        )
    
    @classmethod
    def python_repository(cls) -> "RepositoryConfig":
        """Get Python repository configuration."""
        return cls.from_name(config.PYTHON_REPOSITORY_NAME)
    
    @classmethod
    def java_repository(cls) -> "RepositoryConfig":
        """Get Java repository configuration."""
        return cls.from_name(config.JAVA_REPOSITORY_NAME)

