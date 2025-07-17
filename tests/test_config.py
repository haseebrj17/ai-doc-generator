"""
Tests for the config module.
"""

import os
import json
import tempfile
from pathlib import Path

from src.ai_doc_generator.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_default_config(self):
        """Test that default configuration values are set correctly."""
        config = Config()

        assert config.model == "gpt-4-turbo-preview"
        assert config.project_root == Path.cwd()
        assert config.output_dir == Path("docs/generated")
        assert config.state_file == Path(".doc_state.json")
        assert config.include_patterns == ["*.py"]
        assert "__pycache__" in config.exclude_dirs
        assert ".git" in config.exclude_dirs
        assert "setup.py" in config.exclude_files
        assert config.max_file_size == 100000
        assert config.include_tests is False
        assert config.include_examples is True

    def test_config_from_env(self):
        """Test that API key is loaded from environment variable."""
        test_key = "test-api-key-123"
        os.environ["OPENAI_API_KEY"] = test_key

        config = Config()
        assert config.openai_api_key == test_key

        # Clean up
        del os.environ["OPENAI_API_KEY"]

    def test_config_from_file(self):
        """Test loading configuration from a JSON file."""
        config_data = {
            "model": "gpt-4",
            "project_root": "/test/path",
            "output_dir": "custom/docs",
            "state_file": ".custom_state.json",
            "include_patterns": ["*.py", "*.pyx"],
            "exclude_dirs": ["custom_exclude"],
            "max_file_size": 50000,
            "include_tests": True
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = Config.from_file(temp_path)

            assert config.model == "gpt-4"
            assert config.project_root == Path("/test/path")
            assert config.output_dir == Path("custom/docs")
            assert config.state_file == Path(".custom_state.json")
            assert config.include_patterns == ["*.py", "*.pyx"]
            assert config.exclude_dirs == ["custom_exclude"]
            assert config.max_file_size == 50000
            assert config.include_tests is True
        finally:
            os.unlink(temp_path)

    def test_config_to_file(self):
        """Test saving configuration to a JSON file."""
        config = Config(
            model="gpt-3.5-turbo",
            project_root=Path("/test"),
            output_dir=Path("output"),
            openai_api_key="secret-key"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            config.to_file(temp_path)

            with open(temp_path, 'r') as f:
                saved_data = json.load(f)

            assert saved_data["model"] == "gpt-3.5-turbo"
            assert saved_data["project_root"] == "/test"
            assert saved_data["output_dir"] == "output"
            # API key should not be saved
            assert "openai_api_key" not in saved_data
        finally:
            os.unlink(temp_path)

    def test_config_validation_missing_api_key(self):
        """Test validation when API key is missing."""
        config = Config(openai_api_key=None)
        errors = config.validate()

        assert len(errors) == 1
        assert "OpenAI API key is required" in errors[0]

    def test_config_validation_invalid_project_root(self):
        """Test validation when project root doesn't exist."""
        config = Config(
            openai_api_key="test-key",
            project_root=Path("/nonexistent/path")
        )
        errors = config.validate()

        assert len(errors) == 1
        assert "Project root does not exist" in errors[0]

    def test_config_validation_success(self):
        """Test validation with valid configuration."""
        config = Config(
            openai_api_key="test-key",
            project_root=Path.cwd()
        )
        errors = config.validate()

        assert len(errors) == 0