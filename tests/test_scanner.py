"""
Tests for the file scanner module.
"""

import tempfile
from pathlib import Path

import pytest

from src.ai_doc_generator.config import Config
from src.ai_doc_generator.file_scanner import FileScanner


class TestFileScanner:
    """Test cases for the FileScanner class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test project structure
            root = Path(tmpdir)

            # Create directories
            (root / "src").mkdir()
            (root / "src" / "models").mkdir()
            (root / "tests").mkdir()
            (root / "__pycache__").mkdir()
            (root / ".git").mkdir()
            (root / "docs").mkdir()

            # Create Python files
            (root / "main.py").write_text("# Main file")
            (root / "setup.py").write_text("# Setup file")
            (root / "src" / "app.py").write_text("# App file")
            (root / "src" / "__init__.py").write_text("")
            (root / "src" / "models" / "user.py").write_text("class User: pass")
            (root / "src" / "models" / "__init__.py").write_text("from .user import User")

            # Create test files
            (root / "tests" / "test_app.py").write_text("# Test file")
            (root / "tests" / "__init__.py").write_text("")

            # Create non-Python files
            (root / "README.md").write_text("# README")
            (root / "requirements.txt").write_text("pytest")

            # Create files in excluded directories
            (root / "__pycache__" / "app.pyc").write_text("")
            (root / ".git" / "config").write_text("")

            yield root

    def test_scan_all_files_default(self, temp_project):
        """Test scanning all Python files with default configuration."""
        config = Config(project_root=temp_project)
        scanner = FileScanner(config)

        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        # Should include these files
        assert "main.py" in file_names
        assert "app.py" in file_names
        assert "user.py" in file_names

        # Should exclude these
        assert "setup.py" not in file_names  # in exclude_files
        assert "test_app.py" not in file_names  # test file
        assert "README.md" not in file_names  # not Python
        assert "app.pyc" not in file_names  # in __pycache__

    def test_scan_with_include_tests(self, temp_project):
        """Test scanning with test files included."""
        config = Config(project_root=temp_project, include_tests=True)
        scanner = FileScanner(config)

        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        assert "test_app.py" in file_names

    def test_scan_with_custom_patterns(self, temp_project):
        """Test scanning with custom include patterns."""
        # Create a .pyx file
        (temp_project / "src" / "extension.pyx").write_text("# Cython file")

        config = Config(
            project_root=temp_project,
            include_patterns=["*.py", "*.pyx"]
        )
        scanner = FileScanner(config)

        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        assert "extension.pyx" in file_names

    def test_exclude_directories(self, temp_project):
        """Test that excluded directories are properly skipped."""
        config = Config(project_root=temp_project)
        scanner = FileScanner(config)

        files = scanner.scan_all_files()

        # No files from excluded directories
        for f in files:
            assert "__pycache__" not in str(f)
            assert ".git" not in str(f)

    def test_exclude_custom_directories(self, temp_project):
        """Test custom directory exclusion."""
        (temp_project / "build").mkdir()
        (temp_project / "build" / "generated.py").write_text("# Generated")

        config = Config(
            project_root=temp_project,
            exclude_dirs=["build", "__pycache__", ".git"]
        )
        scanner = FileScanner(config)

        files = scanner.scan_all_files()

        for f in files:
            assert "build" not in str(f)

    def test_max_file_size(self, temp_project):
        """Test that files exceeding max size are excluded."""
        # Create a large file
        large_content = "x" * 200000  # 200KB
        (temp_project / "large_file.py").write_text(large_content)

        config = Config(
            project_root=temp_project,
            max_file_size=100000  # 100KB limit
        )
        scanner = FileScanner(config)

        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        assert "large_file.py" not in file_names

    def test_include_non_empty_init(self, temp_project):
        """Test that __init__.py files with content are included."""
        # Create __init__.py with substantial content
        init_content = """
'''Package initialization.'''

from .app import Application

__all__ = ['Application']

def initialize():
    '''Initialize the package.'''
    pass
"""
        (temp_project / "src" / "__init__.py").write_text(init_content)

        config = Config(project_root=temp_project)
        scanner = FileScanner(config)

        files = scanner.scan_all_files()

        # Find the specific __init__.py file
        init_files = [f for f in files if f.name == "__init__.py" and "src" in str(f)]
        assert len(init_files) == 1

    def test_get_project_structure(self, temp_project):
        """Test getting the project structure."""
        config = Config(project_root=temp_project)
        scanner = FileScanner(config)

        structure = scanner.get_project_structure()

        assert structure["name"] == temp_project.name
        assert structure["type"] == "directory"
        assert "children" in structure

        # Check that src directory is in structure
        assert "src" in structure["children"]
        assert structure["children"]["src"]["type"] == "directory"

        # Check that main.py is in structure
        assert "main.py" in structure["children"]
        assert structure["children"]["main.py"]["type"] == "file"

    def test_is_test_file(self, temp_project):
        """Test identification of test files."""
        test_files = [
            "test_something.py",
            "something_test.py",
            "test.py",
            "tests.py"
        ]

        for test_file in test_files:
            (temp_project / test_file).write_text("# Test")

        config = Config(project_root=temp_project, include_tests=False)
        scanner = FileScanner(config)

        # Private method test
        for test_file in test_files:
            assert scanner._is_test_file(temp_project / test_file)

        # Verify they're excluded from scan
        files = scanner.scan_all_files()
        file_names = [f.name for f in files]

        for test_file in test_files:
            assert test_file not in file_names

    def test_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(project_root=Path(tmpdir))
            scanner = FileScanner(config)

            files = scanner.scan_all_files()
            assert len(files) == 0

    def test_nested_structure(self, temp_project):
        """Test scanning deeply nested directory structure."""
        # Create deeply nested structure
        deep_path = temp_project / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        (deep_path / "deep_module.py").write_text("# Deep module")

        config = Config(project_root=temp_project)
        scanner = FileScanner(config)

        files = scanner.scan_all_files()
        file_paths = [str(f) for f in files]

        assert any("deep_module.py" in path for path in file_paths)