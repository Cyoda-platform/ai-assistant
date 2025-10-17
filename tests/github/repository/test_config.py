"""
Tests for repository configuration.
"""

import pytest
from unittest.mock import patch
from services.github.repository.config import RepositoryConfig


class TestRepositoryConfig:
    """Test RepositoryConfig dataclass."""
    
    def test_repository_config_creation(self):
        config = RepositoryConfig(
            name="test-repo",
            owner="test-owner"
        )
        assert config.name == "test-repo"
        assert config.owner == "test-owner"
    
    def test_repository_config_url(self):
        with patch('services.github.repository.config.config') as mock_config:
            mock_config.REPOSITORY_URL = "https://github.com/{owner}/{repository_name}.git"

            config = RepositoryConfig(
                name="test-repo",
                owner="test-owner"
            )
            assert config.url == "https://github.com/test-owner/test-repo.git"
    
    def test_repository_config_raw_url(self):
        with patch('services.github.repository.config.config') as mock_config:
            mock_config.RAW_REPOSITORY_URL = "https://raw.githubusercontent.com/{owner}/{repository_name}/main"

            config = RepositoryConfig(
                name="test-repo",
                owner="test-owner"
            )
            raw_url = config.raw_url
            assert raw_url == "https://raw.githubusercontent.com/test-owner/test-repo/main"
    
    def test_from_name_class_method(self):
        with patch('services.github.repository.config.config') as mock_config:
            mock_config.GH_DEFAULT_OWNER = "default-owner"
            
            config = RepositoryConfig.from_name("my-repo")
            assert config.name == "my-repo"
            assert config.owner == "default-owner"
    
    def test_python_repository_class_method(self):
        with patch('services.github.repository.config.config') as mock_config:
            mock_config.PYTHON_REPOSITORY_NAME = "python-repo"
            mock_config.GH_DEFAULT_OWNER = "default-owner"
            
            config = RepositoryConfig.python_repository()
            assert config.name == "python-repo"
            assert config.owner == "default-owner"
    
    def test_java_repository_class_method(self):
        with patch('services.github.repository.config.config') as mock_config:
            mock_config.JAVA_REPOSITORY_NAME = "java-repo"
            mock_config.GH_DEFAULT_OWNER = "default-owner"
            
            config = RepositoryConfig.java_repository()
            assert config.name == "java-repo"
            assert config.owner == "default-owner"

