"""
Configuration management for the documentation generator.
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Config:
    """Configuration settings for the documentation generator."""

    # OpenAI settings
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    model: str = "gpt-4-turbo-preview"

    # Project settings
    project_root: Path = field(default_factory=lambda: Path.cwd())
    output_dir: Path = field(default_factory=lambda: Path("docs/generated"))
    state_file: Path = field(default_factory=lambda: Path(".doc_state.json"))

    # File scanning settings
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    exclude_dirs: List[str] = field(default_factory=lambda: [
        "__pycache__", ".git", ".venv", "venv", "env", ".env",
        "node_modules", ".pytest_cache", ".mypy_cache", "build",
        "dist", "*.egg-info", ".tox", "htmlcov", ".coverage"
    ])
    exclude_files: List[str] = field(default_factory=lambda: [
        "setup.py", "conftest.py", "__init__.py"
    ])

    # Documentation settings
    max_file_size: int = 100000  # Maximum file size in bytes to process
    include_tests: bool = False
    include_examples: bool = True

    # LLM prompt settings
    system_prompt: str = """You are an expert technical documentation writer specializing in Python projects. 
Your task is to create clear, comprehensive, and well-structured documentation that helps developers 
understand and use the code effectively. Focus on:
- Clear explanations of purpose and functionality
- Detailed parameter and return value descriptions
- Usage examples where helpful
- Important notes about design decisions or limitations
- Relationships between components
Format everything in clean, readable Markdown."""

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from a JSON file."""
        with open(config_path, 'r') as f:
            data = json.load(f)

        # Convert paths from strings
        if 'project_root' in data:
            data['project_root'] = Path(data['project_root'])
        if 'output_dir' in data:
            data['output_dir'] = Path(data['output_dir'])
        if 'state_file' in data:
            data['state_file'] = Path(data['state_file'])

        return cls(**data)

    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        data = asdict(self)

        # Convert paths to strings for JSON serialization
        data['project_root'] = str(data['project_root'])
        data['output_dir'] = str(data['output_dir'])
        data['state_file'] = str(data['state_file'])

        # Don't save the API key
        data.pop('openai_api_key', None)

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def validate(self) -> List[str]:
        """Validate the configuration and return any errors."""
        errors = []

        if not self.openai_api_key:
            errors.append("OpenAI API key is required")

        if not self.project_root.exists():
            errors.append(f"Project root does not exist: {self.project_root}")

        return errors