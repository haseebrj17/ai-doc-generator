"""
Integration tests for the documentation generator.
Tests the complete workflow and integration between components.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from src.ai_doc_generator.config import Config
from src.ai_doc_generator.doc_generator import DocumentationGenerator
from src.ai_doc_generator.file_scanner import FileScanner
from src.ai_doc_generator.code_analyzer import CodeAnalyzer
from src.ai_doc_generator.change_tracker import ChangeTracker
from src.ai_doc_generator.doc_builder import DocumentationBuilder


@pytest.mark.integration
class TestDocumentationGeneratorIntegration:
    """Integration tests for the documentation generator workflow."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create project structure
            (project_root / "src").mkdir()
            (project_root / "src" / "models").mkdir()
            (project_root / "src" / "services").mkdir()
            (project_root / "tests").mkdir()
            (project_root / ".git").mkdir()  # Simulate git repo

            # Create sample Python files
            sample_files = {
                "src/main.py": '''"""Main application module."""
import os
from typing import List

def main():
    """Main entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''',
                "src/models/user.py": '''"""User model module."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User entity."""
    id: int
    name: str
    email: str
    age: Optional[int] = None

    def is_adult(self) -> bool:
        """Check if user is adult."""
        return self.age is not None and self.age >= 18
''',
                "src/services/user_service.py": '''"""User service module."""
from typing import List, Optional
from src.models.user import User

class UserService:
    """Service for managing users."""

    def __init__(self):
        self.users: List[User] = []

    def add_user(self, user: User) -> None:
        """Add a new user."""
        self.users.append(user)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_adults(self) -> List[User]:
        """Get all adult users."""
        return [user for user in self.users if user.is_adult()]
''',
                "tests/test_user.py": '''"""Tests for user module."""
import pytest
from src.models.user import User

def test_user_creation():
    """Test user creation."""
    user = User(1, "John Doe", "john@example.com", 25)
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.is_adult()

def test_minor_user():
    """Test minor user."""
    user = User(2, "Jane Doe", "jane@example.com", 16)
    assert not user.is_adult()
'''
            }

            # Write sample files
            for file_path, content in sample_files.items():
                full_path = project_root / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            yield project_root

    @pytest.fixture
    def config(self, temp_project):
        """Create test configuration."""
        return Config(
            openai_api_key="test-api-key",
            project_root=temp_project,
            output_dir=temp_project / "docs" / "generated",
            state_file=temp_project / ".doc_state.json",
            include_tests=True
        )

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        def create_mock_response(content):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = content
            return mock_response
        return create_mock_response

    @pytest.mark.integration
    def test_full_documentation_generation(self, config, mock_openai_response):
        """Test full documentation generation workflow."""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock
            mock_client = Mock()
            mock_openai.return_value = mock_client

            # Mock chat completions
            mock_client.chat.completions.create.return_value = mock_openai_response(
                """## Overview
This module provides the main entry point for the application.

## Functions

### main()
Main entry point function that prints a greeting message.

**Usage:**
```python
main()  # Prints "Hello, World!"
```
"""
            )

            # Create generator and run
            generator = DocumentationGenerator(config)
            generator.generate_documentation(force_full=True)

            # Verify output directory was created
            assert config.output_dir.exists()

            # Verify documentation files were created
            assert (config.output_dir / "README.md").exists()
            assert (config.output_dir / "api-reference.md").exists()
            assert (config.output_dir / "project-overview.md").exists()
            assert (config.output_dir / "documentation.json").exists()

            # Verify module documentation
            modules_dir = config.output_dir / "modules"
            assert modules_dir.exists()

            # Verify state file was created
            assert config.state_file.exists()

            # Load and verify state
            with open(config.state_file) as f:
                state = json.load(f)

            assert "files" in state
            assert "last_run" in state
            assert len(state["files"]) > 0

    @pytest.mark.integration
    def test_incremental_documentation_update(self, config, mock_openai_response):
        """Test incremental documentation updates."""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response(
                "Documentation content"
            )

            # First run - full documentation
            generator = DocumentationGenerator(config)
            generator.generate_documentation(force_full=True)

            initial_call_count = mock_client.chat.completions.create.call_count

            # Modify a file
            modified_file = config.project_root / "src" / "main.py"
            original_content = modified_file.read_text()
            modified_file.write_text(original_content + "\n# Modified")

            # Update file modification time to ensure it's detected
            import time
            time.sleep(0.1)
            modified_file.touch()

            # Second run - incremental
            generator.generate_documentation(force_full=False)

            # Should have made fewer API calls (only for modified file)
            final_call_count = mock_client.chat.completions.create.call_count
            assert final_call_count > initial_call_count
            assert final_call_count - initial_call_count < initial_call_count

    @pytest.mark.integration
    def test_change_detection_with_git(self, config, temp_project):
        """Test change detection using git."""
        import subprocess

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                       cwd=temp_project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                       cwd=temp_project, capture_output=True)

        # Add and commit initial files
        subprocess.run(["git", "add", "."], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                       cwd=temp_project, capture_output=True)

        # Create change tracker and get initial state
        tracker = ChangeTracker(config)
        tracker.update_state(list(temp_project.glob("**/*.py")))

        # Modify a file
        modified_file = temp_project / "src" / "main.py"
        modified_file.write_text(modified_file.read_text() + "\n# Git change")

        # Get changed files
        changed_files = tracker.get_changed_files()
        changed_paths = [str(f) for f in changed_files]

        assert any("main.py" in path for path in changed_paths)

    @pytest.mark.integration
    def test_documentation_builder_workflow(self, config, temp_project):
        """Test documentation builder workflow."""
        builder = DocumentationBuilder(config)

        # Add sample documentation
        sample_doc = {
            "analysis": {
                "classes": [{"name": "TestClass", "methods": []}],
                "functions": [{"name": "test_func", "args": []}],
                "loc": 100,
                "dependencies": ["pytest"]
            },
            "documentation": "Test documentation content",
            "timestamp": datetime.now().isoformat()
        }

        builder.add_file_documentation(
            temp_project / "src" / "test.py",
            sample_doc
        )

        # Build documentation
        builder.build_documentation()

        # Verify output
        assert config.output_dir.exists()
        assert (config.output_dir / "README.md").exists()

        # Check README content
        readme_content = (config.output_dir / "README.md").read_text()
        assert "Project Documentation" in readme_content
        assert "Total Files Documented: 1" in readme_content

    @pytest.mark.integration
    def test_code_analyzer_integration(self, temp_project):
        """Test code analyzer integration with real files."""
        analyzer = CodeAnalyzer()

        # Analyze user model
        user_file = temp_project / "src" / "models" / "user.py"
        content = user_file.read_text()
        analysis = analyzer.analyze_file(user_file, content)

        assert analysis["file_path"] == str(user_file)
        assert len(analysis["classes"]) == 1
        assert analysis["classes"][0]["name"] == "User"
        assert len(analysis["classes"][0]["methods"]) == 1
        assert analysis["classes"][0]["methods"][0]["name"] == "is_adult"
        assert "dataclasses" in analysis["dependencies"]

    @pytest.mark.integration
    def test_file_scanner_integration(self, config, temp_project):
        """Test file scanner integration."""
        scanner = FileScanner(config)

        # Scan all files
        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        assert "main.py" in file_names
        assert "user.py" in file_names
        assert "user_service.py" in file_names
        assert "test_user.py" in file_names  # Because include_tests=True

        # Test project structure
        structure = scanner.get_project_structure()
        assert structure["type"] == "directory"
        assert "src" in structure["children"]
        assert "models" in structure["children"]["src"]["children"]

    @pytest.mark.integration
    def test_error_handling_workflow(self, config):
        """Test error handling in the workflow."""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock to raise exception
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            # Create generator and run
            generator = DocumentationGenerator(config)

            # Should complete without raising exception
            generator.generate_documentation(force_full=True)

            # Documentation directory should still be created
            assert config.output_dir.exists()

    @pytest.mark.integration
    @pytest.mark.requires_git
    def test_git_integration_with_history(self, config, temp_project):
        """Test git integration with commit history."""
        import subprocess

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                       cwd=temp_project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                       cwd=temp_project, capture_output=True)

        # Create initial state
        tracker = ChangeTracker(config)

        # Add and commit initial files
        subprocess.run(["git", "add", "."], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                       cwd=temp_project, capture_output=True)

        # Update tracker state with timestamp before modification
        initial_files = list(temp_project.glob("**/*.py"))
        tracker.update_state(initial_files)

        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(1)

        # Modify a file and commit
        modified_file = temp_project / "src" / "main.py"
        modified_file.write_text(modified_file.read_text() + "\n# Historical change")
        subprocess.run(["git", "add", "src/main.py"], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Update main.py"],
                       cwd=temp_project, capture_output=True)

        # Check for changes
        changed_files = tracker.get_changed_files()
        changed_names = [f.name for f in changed_files]

        assert "main.py" in changed_names

    @pytest.mark.integration
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test invalid config
        invalid_config = Config(openai_api_key=None)
        errors = invalid_config.validate()
        assert len(errors) > 0
        assert any("API key" in error for error in errors)

        # Test valid config
        valid_config = Config(openai_api_key="test-key")
        errors = valid_config.validate()
        assert len(errors) == 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_project_handling(self, config, mock_openai_response):
        """Test handling of large projects with many files."""
        # Create many files
        for i in range(50):
            module_dir = config.project_root / f"module_{i}"
            module_dir.mkdir()
            for j in range(5):
                file_path = module_dir / f"file_{j}.py"
                file_path.write_text(f'''"""Module {i} File {j}"""
def function_{i}_{j}():
    """Function in module {i} file {j}"""
    pass
''')

        with patch('openai.OpenAI') as mock_openai:
            # Setup mock
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response(
                "Documentation for file"
            )

            # Generate documentation
            generator = DocumentationGenerator(config)
            generator.generate_documentation(force_full=True)

            # Verify all files were processed
            with open(config.state_file) as f:
                state = json.load(f)

            # Should have documented all Python files
            assert len(state["files"]) >= 250  # 50 modules * 5 files each

    @pytest.mark.integration
    def test_documentation_quality_check(self, config, temp_project):
        """Test documentation quality and completeness."""
        builder = DocumentationBuilder(config)

        # Add comprehensive documentation
        analysis = {
            "module_docstring": "Test module for quality check",
            "classes": [
                {
                    "name": "QualityClass",
                    "docstring": "A class for testing quality",
                    "methods": [
                        {
                            "name": "quality_method",
                            "docstring": "A quality method",
                            "args": [{"name": "param", "annotation": "str"}]
                        }
                    ],
                    "bases": ["BaseClass"]
                }
            ],
            "functions": [
                {
                    "name": "quality_function",
                    "docstring": "A quality function",
                    "args": [{"name": "x", "annotation": "int"}],
                    "returns": "bool"
                }
            ],
            "dependencies": ["typing", "dataclasses"],
            "loc": 150,
            "complexity": 10
        }

        doc_content = {
            "analysis": analysis,
            "documentation": """## Overview
This module provides quality testing functionality.

## Classes

### QualityClass
A comprehensive class for quality testing that inherits from BaseClass.

## Functions

### quality_function(x: int) -> bool
Tests the quality of an integer value.
""",
            "timestamp": datetime.now().isoformat()
        }

        builder.add_file_documentation(
            temp_project / "quality_test.py",
            doc_content
        )

        # Build documentation
        builder.build_documentation()

        # Check API reference
        api_ref = (config.output_dir / "api-reference.md").read_text()
        assert "QualityClass" in api_ref
        assert "quality_function" in api_ref
        assert "BaseClass" in api_ref

        # Check project overview
        overview = (config.output_dir / "project-overview.md").read_text()
        assert "Dependencies" in overview
        assert "typing" in overview