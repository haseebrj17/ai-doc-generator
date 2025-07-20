"""
Tests for the documentation builder module.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from ai_doc_generator.config import Config
from ai_doc_generator.doc_builder import DocumentationBuilder


class TestDocumentationBuilder:
    """Test cases for the DocumentationBuilder class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def builder(self, temp_output_dir):
        """Create a DocumentationBuilder instance."""
        config = Config(output_dir=temp_output_dir)
        return DocumentationBuilder(config)

    @pytest.fixture
    def sample_documentation(self):
        """Create sample documentation data."""
        return {
            "src/app.py": {
                "path": "src/app.py",
                "analysis": {
                    "module_docstring": "Main application module.",
                    "classes": [
                        {
                            "name": "Application",
                            "docstring": "Main application class.",
                            "methods": [
                                {
                                    "name": "__init__",
                                    "args": [{"name": "self"}, {"name": "config"}],
                                    "docstring": "Initialize application."
                                }
                            ]
                        }
                    ],
                    "functions": [
                        {
                            "name": "main",
                            "args": [],
                            "docstring": "Entry point.",
                            "decorators": []
                        }
                    ],
                    "imports": [
                        {"type": "import", "module": "os"},
                        {"type": "from", "module": "pathlib", "name": "Path"}
                    ],
                    "dependencies": ["external_lib"],
                    "loc": 100,
                    "complexity": 10
                },
                "documentation": "# Application Module\n\nThis is the main application module...",
                "timestamp": datetime.now().isoformat()
            },
            "src/utils/helpers.py": {
                "path": "src/utils/helpers.py",
                "analysis": {
                    "module_docstring": "Helper utilities.",
                    "classes": [],
                    "functions": [
                        {
                            "name": "format_date",
                            "args": [{"name": "date"}],
                            "returns": "str",
                            "docstring": "Format a date to string."
                        }
                    ],
                    "loc": 50,
                    "complexity": 3
                },
                "documentation": "# Helper Utilities\n\nUtility functions...",
                "timestamp": datetime.now().isoformat()
            }
        }

    def test_load_existing_documentation(self, builder, temp_output_dir):
        """Test loading existing documentation."""
        # Create existing documentation file
        existing_docs = {"existing.py": {"documentation": "Existing docs"}}
        doc_file = temp_output_dir / "documentation.json"
        doc_file.write_text(json.dumps(existing_docs))

        # Load it
        builder.load_existing_documentation()

        assert len(builder.documentation) == 1
        assert "existing.py" in builder.documentation

    def test_add_file_documentation(self, builder):
        """Test adding documentation for a single file."""
        file_path = builder.config.project_root / "test.py"
        doc_content = {
            "documentation": "Test documentation",
            "analysis": {"loc": 10}
        }

        builder.add_file_documentation(file_path, doc_content)

        assert "test.py" in builder.documentation
        assert builder.documentation["test.py"]["documentation"] == "Test documentation"

    def test_build_project_structure(self, builder, sample_documentation):
        """Test building project structure from documented files."""
        builder.documentation = sample_documentation
        builder._build_project_structure()

        structure = builder.project_structure
        assert structure["type"] == "directory"
        assert "src" in structure["children"]
        assert "app.py" in structure["children"]["src"]["children"]
        assert "utils" in structure["children"]["src"]["children"]
        assert "helpers.py" in structure["children"]["src"]["children"]["utils"]["children"]

    def test_generate_readme(self, builder, sample_documentation, temp_output_dir):
        """Test README generation."""
        builder.documentation = sample_documentation
        builder._build_project_structure()
        builder._generate_readme()

        readme_path = temp_output_dir / "README.md"
        assert readme_path.exists()

        content = readme_path.read_text()
        assert "# Project Documentation" in content
        assert "Table of Contents" in content
        assert "Documentation Statistics" in content
        assert "Total Files Documented: 2" in content

    def test_generate_module_docs(self, builder, sample_documentation, temp_output_dir):
        """Test module documentation generation."""
        builder.documentation = sample_documentation
        builder._generate_module_docs()

        modules_dir = temp_output_dir / "modules"
        assert modules_dir.exists()

        # Check that module directories were created
        src_module = modules_dir / "src"
        assert src_module.exists()

        # Check module index file
        index_file = src_module / "index.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "# Module: src" in content
        assert "app.py" in content

    def test_generate_api_reference(self, builder, sample_documentation, temp_output_dir):
        """Test API reference generation."""
        builder.documentation = sample_documentation
        builder._generate_api_reference()

        api_ref_path = temp_output_dir / "api-reference.md"
        assert api_ref_path.exists()

        content = api_ref_path.read_text()
        assert "# API Reference" in content
        assert "## Classes" in content
        assert "### class Application" in content
        assert "## Functions" in content
        assert "### main" in content
        assert "### format_date" in content

    def test_generate_project_overview(self, builder, sample_documentation, temp_output_dir):
        """Test project overview generation."""
        builder.documentation = sample_documentation
        builder._generate_project_overview()

        overview_path = temp_output_dir / "project-overview.md"
        assert overview_path.exists()

        content = overview_path.read_text()
        assert "# Project Overview" in content
        assert "## Architecture" in content
        assert "## Dependencies" in content
        assert "external_lib" in content

    def test_format_class_reference(self, builder):
        """Test formatting of class reference."""
        class_info = {
            "name": "TestClass",
            "file_path": "test.py",
            "docstring": "Test class docstring.",
            "bases": ["BaseClass"],
            "methods": [
                {
                    "name": "test_method",
                    "args": [{"name": "self"}, {"name": "arg1"}],
                    "docstring": "Test method."
                }
            ]
        }

        lines = builder._format_class_reference(class_info)

        assert "### class TestClass" in lines[0]
        assert "*File: test.py*" in lines[1]
        assert "Test class docstring." in lines
        assert "**Inherits from:** BaseClass" in "\n".join(lines)
        assert "**Methods:**" in lines
        assert "- `test_method(arg1)`" in "\n".join(lines)

    def test_format_function_reference(self, builder):
        """Test formatting of function reference."""
        func_info = {
            "name": "test_function",
            "file_path": "test.py",
            "docstring": "Test function docstring.",
            "args": [
                {"name": "arg1", "annotation": "str"},
                {"name": "arg2", "annotation": "int"}
            ],
            "returns": "bool",
            "decorators": ["@cached"],
            "raises": ["ValueError"]
        }

        lines = builder._format_function_reference(func_info)

        assert "### test_function" in lines[0]
        assert "*File: test.py*" in lines[1]
        assert "`test_function(arg1: str, arg2: int) -> bool`" in "\n".join(lines)
        assert "Test function docstring." in lines
        assert "**Decorators:** @cached" in "\n".join(lines)
        assert "**Raises:** ValueError" in "\n".join(lines)

    def test_count_statistics(self, builder, sample_documentation):
        """Test counting various statistics."""
        builder.documentation = sample_documentation

        assert builder._count_modules() == 2  # src and src/utils
        assert builder._count_classes() == 1
        assert builder._count_functions() == 2

    def test_analyze_architecture(self, builder):
        """Test architecture analysis."""
        builder.documentation = {
            "api/controller.py": {"analysis": {}},
            "application/service.py": {"analysis": {}},
            "domain/entity.py": {"analysis": {}},
            "infrastructure/repository.py": {"analysis": {}},
            "core/config.py": {"analysis": {}}
        }

        architecture = builder._analyze_architecture()

        assert "Api Layer: 1 files" in architecture
        assert "Application Layer: 1 files" in architecture
        assert "Domain Layer: 1 files" in architecture
        assert "Infrastructure Layer: 1 files" in architecture
        assert "Core Layer: 1 files" in architecture

    def test_identify_design_patterns(self, builder):
        """Test design pattern identification."""
        builder.documentation = {
            "test.py": {
                "analysis": {
                    "decorators_used": ["@property", "@classmethod", "@abstractmethod"],
                    "classes": [
                        {
                            "bases": ["ABC", "BaseHandler"]
                        }
                    ]
                }
            }
        }

        patterns = builder._identify_design_patterns()

        assert "Property decorators for encapsulation" in patterns
        assert "Class and static methods for alternative constructors" in patterns
        assert "Abstract base classes for interface definition" in patterns

    def test_build_documentation_full_flow(self, builder, sample_documentation, temp_output_dir):
        """Test the full documentation building flow."""
        builder.documentation = sample_documentation
        builder.build_documentation()

        # Check all expected files were created
        assert (temp_output_dir / "documentation.json").exists()
        assert (temp_output_dir / "README.md").exists()
        assert (temp_output_dir / "api-reference.md").exists()
        assert (temp_output_dir / "project-overview.md").exists()
        assert (temp_output_dir / "modules").exists()

    def test_generate_tree_view(self, builder):
        """Test tree view generation."""
        structure = {
            "src": {
                "type": "directory",
                "children": {
                    "app.py": {"type": "file"},
                    "utils": {
                        "type": "directory",
                        "children": {
                            "helpers.py": {"type": "file"}
                        }
                    }
                }
            },
            "tests": {
                "type": "directory",
                "children": {
                    "test_app.py": {"type": "file"}
                }
            }
        }

        tree = builder._generate_tree_view(structure)

        assert "├── src/" in tree
        assert "│   ├── app.py" in tree
        assert "│   └── utils/" in tree
        assert "│       └── helpers.py" in tree
        assert "└── tests/" in tree
        assert "    └── test_app.py" in tree

    def test_empty_documentation(self, builder, temp_output_dir):
        """Test building with no documentation."""
        builder.build_documentation()

        # Should still create basic structure
        assert (temp_output_dir / "README.md").exists()
        assert (temp_output_dir / "documentation.json").exists()

    def test_group_files_by_module(self, builder):
        """Test grouping files by module."""
        builder.documentation = {
            "main.py": {},
            "src/app.py": {},
            "src/models/user.py": {},
            "src/models/post.py": {},
            "tests/test_app.py": {}
        }

        modules = builder._group_files_by_module()

        assert "root" in modules
        assert "main.py" in modules["root"]
        assert "src" in modules
        assert "src/app.py" in modules["src"]
        assert "src/models" in modules
        assert len(modules["src/models"]) == 2