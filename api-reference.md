# API Reference

Complete API documentation for all classes and functions.

## Classes

### class ASTAnalyzer
*File: src/ai_doc_generator/code_analyzer.py*

AST visitor for extracting information from Python code.

**Inherits from:** ast.NodeVisitor

**Methods:**

- `__init__()`
- `visit_Module(node)` - Visit module node to extract module docstring.
- `visit_Import(node)` - Visit import statements.
- `visit_ImportFrom(node)` - Visit from-import statements.
- `visit_ClassDef(node)` - Visit class definitions.
- `visit_FunctionDef(node)` - Visit function definitions.
- `visit_AsyncFunctionDef(node)` - Visit async function definitions.
- `_process_function(node, is_async)` - Process function or async function definition.
- `visit_If(node)` - Visit if statements to check for main guard.
- `visit_AnnAssign(node)` - Visit annotated assignments (type hints).
- `visit_Assign(node)` - Visit assignments to find constants.
- `_is_main_guard(node)` - Check if an if statement is a main guard.
- `_get_name(node)` - Get the name from various node types.
- `_get_decorator_name(node)` - Get decorator name as a string.
- `_extract_arguments(args)` - Extract function arguments.
- `_get_annotation(node)` - Get type annotation as a string.
- `_get_return_annotation(node)` - Get return type annotation.
- `_is_generator(node)` - Check if a function is a generator.
- `_extract_exceptions(node)` - Extract exceptions that might be raised.
- `_is_exception_class(node)` - Check if a class is an exception class.
- `_get_metaclass(node)` - Extract metaclass if specified.
- `_is_stdlib_module(module_name)` - Check if a module is part of the standard library.

---

### class ChangeTracker
*File: src/ai_doc_generator/change_tracker.py*

Tracks changes to files between documentation runs.

**Methods:**

- `__init__(config)`
- `has_previous_run()` - Check if there's a previous documentation run.
- `get_changed_files()` - Get list of files that have changed since last run.
- `_has_file_changed(file_path, previous_info)` - Check if a file has changed since last run.
- `_calculate_file_hash(file_path)` - Calculate SHA256 hash of file content.
- `_get_git_changed_files()` - Get files changed according to git.
- `update_state(documented_files)` - Update the state with newly documented files.
- `_load_state()` - Load state from file.
- `_save_state()` - Save state to file.
- `clear_state()` - Clear the state (useful for forcing full regeneration).
- `get_documentation_stats()` - Get statistics about the documentation state.

---

### class CodeAnalyzer
*File: src/ai_doc_generator/code_analyzer.py*

Analyzes Python code to extract structural information.

**Methods:**

- `analyze_file(file_path, content)` - Analyze a Python file and extract its structure.
- `_calculate_complexity(analyzer)` - Calculate a simple complexity score for the file.

---

### class Config
*File: src/ai_doc_generator/config.py*

Configuration settings for the documentation generator.

**Methods:**

- `from_file(cls, config_path)` - Load configuration from a JSON file.
- `to_file(config_path)` - Save configuration to a JSON file.
- `validate()` - Validate the configuration and return any errors.

---

### class DocumentationBuilder
*File: src/ai_doc_generator/doc_builder.py*

Builds and organizes the final documentation structure.

**Methods:**

- `__init__(config)`
- `load_existing_documentation()` - Load existing documentation for incremental updates.
- `add_file_documentation(file_path, doc_content)` - Add documentation for a single file.
- `build_documentation()` - Build the final documentation structure.
- `_save_documentation_json()` - Save the raw documentation data as JSON.
- `_build_project_structure()` - Build a hierarchical project structure from documented files.
- `_generate_readme()` - Generate the main README.md file.
- `_generate_module_docs()` - Generate documentation for each module.
- `_generate_module_doc(module_path, files, output_dir)` - Generate documentation for a single module.
- `_generate_api_reference()` - Generate comprehensive API reference.
- `_generate_project_overview()` - Generate project overview documentation.
- `_generate_tree_view(structure, prefix, is_last)` - Generate a tree view of the project structure.
- `_group_files_by_module()` - Group files by their module (directory).
- `_generate_module_overview(module_path, files)` - Generate an overview for a module based on its files.
- `_format_analysis(analysis)` - Format code analysis results.
- `_format_class_reference(cls)` - Format class information for API reference.
- `_format_function_reference(func)` - Format function information for API reference.
- `_count_modules()` - Count the number of modules in the project.
- `_count_classes()` - Count total number of classes.
- `_count_functions()` - Count total number of functions.
- `_analyze_architecture()` - Analyze and describe the project architecture.
- `_analyze_dependencies()` - Analyze project dependencies.
- `_identify_key_components()` - Identify and describe key components.
- `_identify_design_patterns()` - Identify design patterns used in the codebase.

---

### class DocumentationGenerator
*File: src/ai_doc_generator/doc_generator.py*

Main class for generating project documentation using LLM.

**Methods:**

- `__init__(config)`
- `generate_documentation(force_full)` - Generate documentation for the project.
- `_document_file(file_path)` - Generate documentation for a single file.
- `_create_documentation_prompt(file_path, content, analysis)` - Create a prompt for the LLM to generate documentation.

---

### class FileScanner
*File: src/ai_doc_generator/file_scanner.py*

Scans the project directory for files to document.

**Methods:**

- `__init__(config)`
- `scan_all_files()` - Scan the entire project for files matching the include patterns.
- `_find_files(pattern)` - Find all files matching the given pattern.
- `_should_exclude_dir(dir_path)` - Check if a directory should be excluded.
- `_should_include_file(file_path)` - Check if a file should be included in documentation.
- `_is_test_directory(dir_path)` - Check if a directory is a test directory.
- `_is_test_file(file_path)` - Check if a file is a test file.
- `get_project_structure()` - Get the project structure as a nested dictionary.

---


## Functions

### main
*File: src/ai_doc_generator/cli.py*

`main() -> None`

Main CLI entry point.

---

### main
*File: src/ai_doc_generator/doc_generator.py*

`main() -> None`

Main entry point for the documentation generator.

---

### setup_logging
*File: src/ai_doc_generator/cli.py*

`setup_logging(verbose: bool) -> None`

Configure logging based on verbosity.

---
