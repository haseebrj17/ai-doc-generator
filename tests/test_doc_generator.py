"""
Tests for the main documentation generator module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from scripts.documentation import conftest

from scripts.documentation.config import Config
from scripts.documentation.doc_generator import DocumentationGenerator


class TestDocumentationGenerator:
    """Test cases for the DocumentationGenerator class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create project structure
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text('''
"""Application module."""

class App:
    """Main application class."""
    def run(self):
        """Run the application."""
        pass
''')
            (root / "src" / "utils.py").write_text('''
"""Utility functions."""

def helper():
    """Helper function."""
    return True
''')

            yield root

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        mock_client = Mock()

        # Mock the response structure
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Generated documentation content"))
        ]

        # Set up the mock to return our response
        mock_client.chat.completions.create.return_value = mock_response

        return mock_client

    @pytest.fixture
    def generator(self, temp_project, mock_openai_client):
        """Create a DocumentationGenerator instance with mocked OpenAI."""
        config = Config(
            project_root=temp_project,
            output_dir=temp_project / "docs",
            openai_api_key="test-key"
        )

        with patch('scripts.documentation.doc_generator.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            generator = DocumentationGenerator(config)

        return generator

    def test_initialization(self, generator):
        """Test generator initialization."""
        assert generator.config is not None
        assert generator.client is not None
        assert generator.file_scanner is not None
        assert generator.code_analyzer is not None
        assert generator.change_tracker is not None
        assert generator.doc_builder is not None

    def test_generate_documentation_full_run(self, generator, temp_project, mock_openai_client):
        """Test full documentation generation."""
        # Run documentation generation
        generator.generate_documentation(force_full=True)

        # Check that OpenAI was called for each Python file
        assert mock_openai_client.chat.completions.create.call_count == 2

        # Check that documentation was generated
        docs_dir = temp_project / "docs"
        assert docs_dir.exists()
        assert (docs_dir / "README.md").exists()
        assert (docs_dir / "documentation.json").exists()

    def test_generate_documentation_incremental(self, generator, temp_project, mock_openai_client):
        """Test incremental documentation generation."""
        # First run - document all files
        generator.generate_documentation()
        initial_call_count = mock_openai_client.chat.completions.create.call_count

        # Reset mock
        mock_openai_client.reset_mock()

        # Second run - no changes, should not call OpenAI
        generator.generate_documentation()
        assert mock_openai_client.chat.completions.create.call_count == 0

        # Modify a file
        (temp_project / "src" / "app.py").write_text('''
"""Modified application module."""

class App:
    """Modified application class."""
    def run(self):
        """Run the application with new features."""
        pass

    def new_method(self):
        """New method added."""
        pass
''')

        # Third run - should only document the changed file
        generator.generate_documentation()
        assert mock_openai_client.chat.completions.create.call_count == 1

    def test_document_file_success(self, generator, temp_project, mock_openai_client):
        """Test successful documentation of a single file."""
        file_path = temp_project / "src" / "app.py"

        # Mock response
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = """
## Application Module

This module contains the main application class.

### Class: App

The `App` class is the main entry point for the application.

**Methods:**
- `run()`: Executes the main application logic.
"""

        result = generator._document_file(file_path)

        assert result is not None
        assert result["path"] == str(file_path)
        assert "analysis" in result
        assert "documentation" in result
        assert "timestamp" in result
        assert "Application Module" in result["documentation"]

    def test_document_file_read_error(self, generator, temp_project):
        """Test handling of file read errors."""
        non_existent = temp_project / "non_existent.py"

        result = generator._document_file(non_existent)

        assert result is None

    def test_document_file_api_error(self, generator, temp_project, mock_openai_client):
        """Test handling of OpenAI API errors."""
        file_path = temp_project / "src" / "app.py"

        # Mock API error
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        result = generator._document_file(file_path)

        assert result is None

    def test_create_documentation_prompt(self, generator, temp_project):
        """Test prompt creation for documentation."""
        file_path = temp_project / "src" / "app.py"
        content = file_path.read_text()
        analysis = {
            "classes": [{"name": "App"}],
            "functions": [],
            "imports": [],
            "loc": 8
        }

        prompt = generator._create_documentation_prompt(file_path, content, analysis)

        assert "src/app.py" in prompt
        assert "Classes: 1" in prompt
        assert "Functions: 0" in prompt
        assert "class App:" in prompt
        assert "brief overview" in prompt
        assert "Markdown" in prompt

    def test_prompt_truncation_for_large_files(self, generator, temp_project):
        """Test that large files are truncated in prompts."""
        file_path = temp_project / "large.py"

        # Create a large file
        large_content = "x = 1\n" * 5000  # Very large file
        file_path.write_text(large_content)

        analysis = {"classes": [], "functions": [], "imports": [], "loc": 5000}

        prompt = generator._create_documentation_prompt(file_path, large_content, analysis)

        assert "... (truncated)" in prompt
        assert len(prompt) < len(large_content)

    def test_no_files_to_document(self, generator, temp_project):
        """Test handling when no files need documentation."""
        # Document all files first
        generator.generate_documentation()

        # Clear the mock
        generator.client.chat.completions.create.reset_mock()

        # Run again - should find no changes
        generator.generate_documentation()

        # Should not call OpenAI
        assert generator.client.chat.completions.create.call_count == 0

    def test_state_persistence_between_runs(self, temp_project):
        """Test that state persists between generator instances."""
        config = Config(
            project_root=temp_project,
            output_dir=temp_project / "docs",
            openai_api_key="test-key"
        )

        # First generator
        with patch('scripts.documentation.doc_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content="Documentation"))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            gen1 = DocumentationGenerator(config)
            gen1.generate_documentation()

        # Second generator should recognize previous run
        with patch('scripts.documentation.doc_generator.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            gen2 = DocumentationGenerator(config)

            assert gen2.change_tracker.has_previous_run()

    @patch('scripts.documentation.doc_generator.logger')
    def test_error_handling_during_generation(self, mock_logger, generator, temp_project):
        """Test error handling during documentation generation."""
        # Create a file that will cause an error
        bad_file = temp_project / "src" / "bad.py"
        bad_file.write_text("Valid Python content")

        # Mock the document_file method to raise an exception for this file
        original_method = generator._document_file

        def mock_document_file(path):
            if path.name == "bad.py":
                raise Exception("Test error")
            return original_method(path)

        generator._document_file = mock_document_file

        # Should continue despite error
        generator.generate_documentation()

        # Check that error was logged
        mock_logger.error.assert_called()

    def test_configuration_validation(self, temp_project):
        """Test that configuration is validated."""
        # Test with missing API key
        config = Config(
            project_root=temp_project,
            openai_api_key=None
        )

        with pytest.raises(SystemExit):
            # The main() function should exit if no API key
            from scripts.documentation.doc_generator import main
            import sys

            # Mock command line args
            with patch.object(sys, 'argv', ['doc_generator.py']):
                with patch('scripts.documentation.doc_generator.Config') as mock_config:
                    mock_config.return_value = config
                    main()

    def test_progress_bar_integration(self, generator, temp_project):
        """Test that progress bar is used during generation."""
        with patch('scripts.documentation.doc_generator.tqdm') as mock_tqdm:
            # Create a mock progress bar
            mock_pbar = MagicMock()
            mock_tqdm.return_value.__enter__.return_value = mock_pbar

            generator.generate_documentation(force_full=True)

            # Check that tqdm was called
            mock_tqdm.assert_called_once()

            # Check that progress bar was updated
            assert mock_pbar.update.call_count == 2  # Two files in our test project