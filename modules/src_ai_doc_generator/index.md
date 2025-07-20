# Module: src/ai_doc_generator

## Overview

This module contains 9 files with a total of:
- 7 classes
- 3 functions
- 1861 lines of code

## Files

### __init__.py

# Documentation for ai_doc_generator

The `ai_doc_generator` package is designed to automate the creation of documentation for Python projects by leveraging OpenAI's capabilities. This package scans Python files, analyzes the code, tracks changes, and builds comprehensive documentation. The package is structured to be modular, with each component focusing on a specific aspect of the documentation generation process.

## Overview

The `__init__.py` file serves as the entry point to the `ai_doc_generator` package. It imports and exposes the main components of the package, making them accessible for external use. Additionally, it specifies the package version.

## Key Components

### Config

- **Purpose**: The `Config` class is responsible for managing configuration settings for the documentation generation process. This may include settings such as the directory paths to scan, output formats, and OpenAI API keys.
- **Key Methods**:
  - Not detailed in the provided code snippet, but typically includes methods for loading, saving, and accessing various configuration parameters.
- **Relationships**: Used by other components to access configuration settings.

### DocumentationGenerator

- **Purpose**: This class acts as the orchestrator for the documentation generation process. It coordinates the activities between scanning files, analyzing code, tracking changes, and building the documentation.
- **Key Methods**:
  - Again, not specified in the snippet, but likely includes methods for initiating the documentation generation process and possibly for integrating with OpenAI's API.
- **Relationships**: Interacts with `FileScanner`, `CodeAnalyzer`, `ChangeTracker`, and `DocumentationBuilder` to generate documentation.

### FileScanner

- **Purpose**: Responsible for scanning the specified directories and files that need documentation. It identifies the files to be processed.
- **Key Methods**:
  - Methods would include functionality for listing files, filtering based on extensions, and possibly excluding certain directories or files.
- **Relationships**: Provides a list of files to `CodeAnalyzer` for further analysis.

### CodeAnalyzer

- **Purpose**: Analyzes the Python code to extract documentation-relevant information such as classes, functions, parameters, and docstrings.
- **Key Methods**:
  - Likely includes methods for parsing Python files, extracting and analyzing code elements, and possibly leveraging OpenAI for understanding complex code segments.
- **Relationships**: Feeds analyzed code data to `ChangeTracker` and `DocumentationBuilder`.

### ChangeTracker

- **Purpose**: Monitors changes in the code to determine what parts of the documentation need to be updated. This helps in optimizing the documentation generation process by focusing on modified sections.
- **Key Methods**:
  - Would include functionality for comparing current code state with previous states, identifying changes, and possibly versioning documentation.
- **Relationships**: Works closely with `CodeAnalyzer` and `DocumentationBuilder` to ensure documentation is up-to-date.

### DocumentationBuilder

- **Purpose**: Responsible for compiling the analyzed data into structured documentation. This could involve formatting the documentation into various output formats such as Markdown, HTML, or PDF.
- **Key Methods**:
  - Includes methods for organizing documentation structure, applying templates, and generating the final documentation files.
- **Relationships**: Utilizes information from `CodeAnalyzer` and `ChangeTracker` to build the final documentation.

## Key Dependencies and Imports

The package imports six internal modules, each representing a core component of the documentation generation process:

- `config`: Manages configuration settings.
- `doc_generator`: Orchestrates the documentation generation process.
- `file_scanner`: Scans for files to document.
- `code_analyzer`: Analyzes Python code for documentation.
- `change_tracker`: Tracks changes in code for documentation updates.
- `doc_builder`: Builds the final documentation files.

## Usage Examples

Usage examples are not provided in the code snippet. However, a typical usage scenario might involve initializing a `DocumentationGenerator` instance with appropriate configuration settings and then calling a method to start the documentation generation process.

```python
from ai_doc_generator import Config, DocumentationGenerator

# Initialize configuration
config = Config(...)
# Create a DocumentationGenerator instance
doc_gen = DocumentationGenerator(config)
# Generate documentation
doc_gen.generate()
```

## Important Notes

- The actual implementation details of the classes and their methods are not provided in the code snippet. Therefore, the descriptions above are based on the typical responsibilities associated with the class names and the general purpose of the package.
- The package version is specified as "1.0.0", indicating the initial release. This should be updated with each significant change to the package.
- The `__all__` variable explicitly declares the exported symbols from the module, making it clear which components are intended for external use.

This documentation provides a high-level overview and assumes further details are available in the implementation of each component.

#### Code Analysis

**Module Docstring:**
> Documentation generator for Python projects using OpenAI.

- **Lines of Code:** 20
- **Classes:** 0
- **Functions:** 0
- **Complexity Score:** 0

---

### __main__.py

# Documentation for `__main__.py` in ai_doc_generator

## Overview

The `__main__.py` file in the `ai_doc_generator` package allows the package to be executed as a module directly from the command line. This is particularly useful for creating command-line interfaces (CLI) or scripts that can be run without explicitly calling the Python interpreter with a script path. By including this file with the appropriate code, users can run the package using the command `python -m ai_doc_generator`, making it more accessible and user-friendly.

## Key Dependencies and Imports

### Imports

- `from .cli import main`: This line imports the `main` function from the `cli` module located within the same package. The `main` function is expected to contain the entry point logic for the command-line interface, handling any arguments passed by the user and initiating the appropriate actions.

## Functions

This file does not define any functions within its scope. However, it makes use of the `main` function imported from the `.cli` module.

### `main` Function (Imported)

#### Purpose

The `main` function serves as the entry point for the command-line interface of the `ai_doc_generator` package. It is responsible for parsing command-line arguments, executing the required actions based on those arguments, and providing feedback to the user.

#### Parameters

Since the `main` function is defined in another module (`cli`), its parameters are not explicitly listed in this file. Typically, a `main` function for a CLI does not take parameters directly but instead processes arguments passed to the script from the command line.

#### Return Values

The return value of the `main` function is not explicitly handled in this file. Conventionally, a `main` function may return an exit status code to the operating system, where `0` often indicates success, and any non-zero value indicates an error.

#### Exceptions

Any exceptions raised by the `main` function would depend on its internal implementation and are not documented in this file.

## Usage Example

To run the `ai_doc_generator` package as a module from the command line, navigate to the parent directory of the package and execute:

```bash
python -m ai_doc_generator
```

This command invokes the `main` function defined in the `cli` module, which then processes any command-line arguments and proceeds with the package's intended functionality.

## Important Notes or Considerations

- The `__main__.py` file is a convention used in Python to indicate that a package can be run as a script. It is crucial for packages intended to provide command-line utilities.
- The actual functionality and command-line options available through the `ai_doc_generator` package are defined in the `cli` module and the `main` function. To understand the capabilities and options of the CLI, refer to the documentation or source code of the `cli` module.
- Error handling and logging are not explicitly demonstrated in this file but are critical aspects of developing a robust CLI. These should be implemented within the `main` function or other parts of the package to ensure a smooth user experience.

This documentation provides a high-level overview of the `__main__.py` file's purpose within the `ai_doc_generator` package, focusing on its role in enabling command-line execution. For detailed information about the CLI's capabilities and options, refer to the documentation or source code of the `cli` module.

#### Code Analysis

**Module Docstring:**
> Allow package to be run as a module: python -m ai_doc_generator

- **Lines of Code:** 8
- **Classes:** 0
- **Functions:** 0
- **Complexity Score:** 0

---

### change_tracker.py

# Change Tracker Documentation

## Overview

The `change_tracker.py` module is designed to track changes in files between documentation runs for a Python project. It identifies new, modified, or deleted files since the last documentation run, leveraging both file system information and git history. This functionality is crucial for optimizing documentation processes, ensuring that only changed files are re-documented, thereby saving time and resources.

## Key Dependencies and Imports

- `json`: For loading and saving state information in JSON format.
- `subprocess`: For executing git commands and checking for changes in git-tracked files.
- `pathlib.Path`: For file and directory path manipulations.
- `datetime`: For handling dates and times, specifically for tracking when the last documentation run occurred.
- `typing`: Provides type hints for better code clarity and type checking.
- `logging`: For logging information, warnings, and errors.
- `hashlib`: For generating SHA256 hashes of file contents to detect changes.
- `config.Config`: A configuration class from a local module, used for accessing project configuration settings.
- `file_scanner.FileScanner`: A class from a local module for scanning the project's files.

## Class: ChangeTracker

### Purpose

The `ChangeTracker` class is responsible for tracking changes to files in a project between documentation runs. It identifies files that have been added, deleted, or modified since the last run, using both filesystem attributes and git history.

### Key Methods

#### `__init__(self, config: Config)`

Initializes a new instance of the `ChangeTracker` class.

- **Parameters**:
  - `config`: An instance of the `Config` class containing project configuration settings.
- **Returns**: None.

#### `has_previous_run(self) -> bool`

Checks if there has been a previous documentation run by looking for the existence of a state file and entries within it.

- **Returns**: `True` if a previous run is detected, `False` otherwise.

#### `get_changed_files(self) -> List[Path]`

Identifies and returns a list of files that have changed since the last documentation run.

- **Returns**: A sorted list of `Path` objects representing files that have changed.

#### `update_state(self, documented_files: List[Path]) -> None`

Updates the state with information about newly documented files, including their modification time, size, content hash, and the time they were documented.

- **Parameters**:
  - `documented_files`: A list of `Path` objects representing files that have been documented.
- **Returns**: None.

#### `clear_state(self) -> None`

Clears the current state, effectively forcing a full regeneration of documentation on the next run.

- **Returns**: None.

#### `get_documentation_stats(self) -> Dict`

Provides statistics about the documentation state, including the total number of files, the timestamp of the last run, and the dates of the oldest and newest documentation.

- **Returns**: A dictionary containing documentation statistics.

### Relationships

- Utilizes the `Config` class for configuration settings.
- Uses the `FileScanner` class to scan the project's files.

### Important Notes

- The class relies on a JSON file (`state_file`) to persist state information between runs.
- Git commands are used to detect changes for files tracked in a git repository. This requires the project to be a git repository and git to be available in the environment.
- File changes are detected using modification time, size, and a SHA256 hash of the file's content.

## Usage Example

```python
from config import Config
from change_tracker import ChangeTracker

# Assuming 'config' is an instance of Config with appropriate settings
change_tracker = ChangeTracker(config)

if change_tracker.has_previous_run():
    changed_files = change_tracker.get_changed_files()
    print(f"Changed files: {changed_files}")
else:
    print("No previous documentation run detected.")

# After documentation process
change_tracker.update_state(documented_files=changed_files)
```

This example demonstrates how to instantiate the `ChangeTracker`, check for a previous run, get a list of changed files, and then update the state after documenting those files. It assumes that a `Config` instance with appropriate settings is already available.

#### Code Analysis

**Module Docstring:**
> Change tracker for identifying modified files since last documentation run.

- **Lines of Code:** 230
- **Classes:** 1
- **Functions:** 0
- **Complexity Score:** 16

---

### cli.py

# AI Documentation Generator CLI Documentation

## Overview

This Python file serves as the command-line interface (CLI) for the AI Documentation Generator, a tool designed to automatically generate documentation for Python projects using AI models. It allows users to configure the documentation generation process through various command-line arguments, such as specifying the project path, output directory, and whether to include test files or not. The CLI also supports dry runs, verbose logging, and custom configurations through JSON files.

## Key Dependencies and Imports

- `sys`: Used for exiting the script with a status code.
- `argparse`: Facilitates the parsing of command-line arguments.
- `logging`: Provides logging functionalities.
- `pathlib.Path`: Used for handling file paths.
- `typing.Optional`: Annotation for optional typing.
- `config.Config`: Custom class for handling configuration settings.
- `doc_generator.DocumentationGenerator`: Core class responsible for generating the documentation.

## Functions

### `setup_logging(verbose: bool = False) -> None`

Configures the logging level and format based on the verbosity.

**Parameters:**

- `verbose` (`bool`): If `True`, sets the logging level to `DEBUG`. Otherwise, sets it to `INFO`. Defaults to `False`.

**Return Value:** None.

### `main() -> None`

Serves as the main entry point for the CLI. It parses command-line arguments, sets up logging, loads configurations, and initiates the documentation generation process.

**Parameters:** None.

**Return Value:** None.

**Exceptions:**

- `KeyboardInterrupt`: Catches and handles user interruption.
- `Exception`: Catches and logs any unexpected errors during execution.

## Usage Examples

### Generating Documentation for the Current Directory

```bash
ai-doc-gen
```

### Generating Documentation with a Custom Configuration File

```bash
ai-doc-gen --config my-config.json
```

### Forcing Full Documentation Regeneration

```bash
ai-doc-gen --full
```

### Specifying an Output Directory

```bash
ai-doc-gen --output docs/api
```

### Using a Specific OpenAI Model

```bash
ai-doc-gen --model gpt-4o-mini
```

## Important Notes and Considerations

- The CLI uses the `argparse` library to parse command-line arguments, providing a flexible interface for users to customize the documentation generation process.
- Logging configuration is adjustable via the `--verbose` flag, allowing for more detailed output when needed.
- Configuration settings can be loaded from a JSON file or specified directly through command-line arguments. Command-line arguments override settings in the configuration file.
- The CLI supports a dry-run mode (`--dry-run`), which outputs the files that would be documented without actually generating any documentation. This is useful for testing configuration settings.
- The tool is designed to be extensible, with the possibility to specify different OpenAI models for the documentation generation process.
- Error handling is implemented to ensure a graceful shutdown in case of user interruption or unexpected errors during execution.
- The `--exclude` option allows users to specify directories to be excluded from the documentation process, adding flexibility to the scope of documentation generation.

This documentation provides a comprehensive guide to using the AI Documentation Generator CLI, detailing its functionalities, usage, and configuration options.

#### Code Analysis

**Module Docstring:**
> Command-line interface for AI Documentation Generator.

- **Lines of Code:** 197
- **Classes:** 0
- **Functions:** 2
- **Complexity Score:** 4

---

### code_analyzer.py

# Code Analyzer Documentation

This document provides comprehensive details on the `code_analyzer.py` module, designed for extracting structural information from Python files. The module leverages the Abstract Syntax Tree (AST) to parse Python code, enabling the analysis of its structure, including modules, classes, functions, and more.

## Overview

The `code_analyzer.py` file is a Python module that analyzes Python code to extract structural information such as documentation strings, imports, classes, functions, constants, and more. It is primarily intended for static analysis of Python code, providing insights into code complexity, dependencies, and the use of decorators among other aspects.

## Dependencies and Imports

The module relies on the following key imports:

- `ast`: For parsing Python code into its Abstract Syntax Tree.
- `pathlib.Path`: For handling file paths.
- `typing`: For type annotations.
- `logging`: For logging warnings and errors encountered during analysis.

## Classes

### `CodeAnalyzer`

#### Purpose

Analyzes Python code files to extract structural information, including documentation, imports, classes, functions, constants, and more.

#### Key Methods

- `analyze_file(file_path: Path, content: str) -> Dict[str, Any]`: Analyzes the content of a Python file, returning a dictionary with the analysis results.

- `_calculate_complexity(analyzer: 'ASTAnalyzer') -> int`: Calculates a simple complexity score for the analyzed file based on the number of classes, functions, and decorators used.

#### Relationships

- Utilizes the `ASTAnalyzer` class for traversing the AST of the Python code.
- Logs warnings and errors using the `logging` module.

### `ASTAnalyzer`

#### Purpose

Serves as an AST visitor for extracting detailed information from Python code, including module docstrings, imports, classes, and functions.

#### Key Methods

- `visit_Module(node: ast.Module)`: Extracts the module docstring.
- `visit_Import(node: ast.Import)`, `visit_ImportFrom(node: ast.ImportFrom)`: Extracts import statements.
- `visit_ClassDef(node: ast.ClassDef)`: Extracts class definitions, including base classes, methods, and decorators.
- `visit_FunctionDef(node: ast.FunctionDef)`, `visit_AsyncFunctionDef(node: ast.AsyncFunctionDef)`: Extracts function and async function definitions.
- `visit_If(node: ast.If)`: Checks for a main guard pattern to determine if the script is executable as a script.
- `visit_AnnAssign(node: ast.AnnAssign)`, `visit_Assign(node: ast.Assign)`: Extracts annotated assignments and constants.

#### Relationships

- Inherits from `ast.NodeVisitor`, enabling it to traverse the AST.
- Used by the `CodeAnalyzer` class to perform the detailed analysis of the AST.

## Usage Examples

To use the `CodeAnalyzer`, you first need to read the content of a Python file and then pass it to the `analyze_file` method along with the file path.

```python
from pathlib import Path
from ai_doc_generator.code_analyzer import CodeAnalyzer

file_path = Path("/path/to/your/python_file.py")
with file_path.open("r") as file:
    content = file.read()

analyzer = CodeAnalyzer()
analysis_results = analyzer.analyze_file(file_path, content)
print(analysis_results)
```

This will output a dictionary containing the structural analysis of the Python file, including its complexity, imports, classes, functions, and more.

## Important Notes

- The complexity calculation provided by `_calculate_complexity` is simplistic and intended as a basic measure. For more detailed complexity metrics, consider integrating with tools like Radon.
- The module does not execute the Python code but analyzes its structure statically. Therefore, dynamic behaviors and runtime state changes are not captured.
- Syntax errors or other parsing issues in the analyzed file will be logged but may result in incomplete analysis.

## Limitations

- The analysis is limited to the structural aspects that can be extracted from the static AST. Runtime behaviors, such as dynamic imports or metaclass effects, are not analyzed.
- The module assumes standard Python coding practices and may not accurately analyze code that heavily utilizes metaprogramming or dynamically modifies its structure at runtime.

#### Code Analysis

**Module Docstring:**
> Code analyzer for extracting structural information from Python files.

- **Lines of Code:** 415
- **Classes:** 2
- **Functions:** 0
- **Complexity Score:** 34

---

### config.py

# Documentation for `config.py`

## Overview

The `config.py` file is responsible for managing the configuration settings for a documentation generator. This generator appears to be designed to work with Python projects, leveraging OpenAI's GPT models (specifically mentioned as "gpt-4-turbo-preview") to generate documentation. The configuration settings include OpenAI API credentials, project directories, file patterns for inclusion or exclusion, documentation preferences, and settings for the language model prompts.

## Key Dependencies and Imports

- `os`: Used for fetching environment variables.
- `json`: Utilized for loading and saving configuration settings from/to a JSON file.
- `pathlib.Path`: Handles file paths in a platform-independent manner.
- `typing.List, Optional`: For type annotations, enhancing code readability and maintainability.
- `dataclasses.dataclass, field, asdict`: Simplifies the creation of data classes and conversion to dictionaries.

## Classes

### `Config`

#### Purpose

The `Config` class encapsulates all the configuration settings required by the documentation generator. It includes settings for interacting with the OpenAI API, defining the scope of the project files to be documented, and customizing the documentation output.

#### Key Methods

- `__init__`: Automatically generated by the `@dataclass` decorator, initializes the configuration with default values or environment variables.
- `from_file(config_path: str) -> "Config"`: Class method to load configuration settings from a specified JSON file.
  - **Parameters**:
    - `config_path`: A string specifying the path to the configuration JSON file.
  - **Return Value**: An instance of `Config` populated with the settings from the file.
- `to_file(config_path: str) -> None`: Saves the current configuration settings to a JSON file, excluding sensitive information like the OpenAI API key.
  - **Parameters**:
    - `config_path`: A string specifying the path where the configuration should be saved.
- `validate() -> List[str]`: Validates the current configuration settings and returns a list of error messages, if any.
  - **Return Value**: A list of strings, each representing an error message related to the configuration validation.

#### Relationships

The `Config` class is a standalone entity in this file, designed to be instantiated and used by other parts of the documentation generator, particularly for loading, saving, and validating configuration settings.

## Functions

There are no standalone functions defined outside of the `Config` class in this file.

## Usage Examples

### Loading Configuration from a File

```python
config_path = "/path/to/config.json"
config = Config.from_file(config_path)
```

This example demonstrates how to load configuration settings from a JSON file into a `Config` object.

### Saving Configuration to a File

```python
config_path = "/path/to/save/config.json"
config.to_file(config_path)
```

This code snippet shows how to save the current configuration settings to a JSON file, excluding the OpenAI API key for security.

### Validating Configuration

```python
errors = config.validate()
if errors:
    for error in errors:
        print(error)
else:
    print("Configuration is valid.")
```

Here, the `validate` method is used to check the configuration for any issues, printing out any errors found.

## Important Notes and Considerations

- The OpenAI API key is required for the documentation generator to function. It is fetched from the environment variables for security reasons and is not stored in the configuration file.
- Paths (`project_root`, `output_dir`, `state_file`) are automatically converted to `Path` objects when loaded from a file, ensuring compatibility across different operating systems.
- The configuration intentionally excludes certain directories and files from documentation generation, such as Python caches, virtual environments, and setup files, which are typically not relevant for API documentation.
- The `max_file_size` setting is used to limit the size of files processed, which can help in avoiding excessive processing times or memory usage for very large files.
- The inclusion of tests and examples in the documentation can be toggled via the `include_tests` and `include_examples` settings, allowing for customizable documentation outputs based on the user's preferences.

#### Code Analysis

**Module Docstring:**
> Configuration management for the documentation generator.

- **Lines of Code:** 93
- **Classes:** 1
- **Functions:** 0
- **Complexity Score:** 10

---

### doc_builder.py

# Documentation for `doc_builder.py`

## Overview

The `doc_builder.py` script is designed to automate the process of building and organizing the final documentation for a Python project. It takes structured data about the codebase, such as documentation and analysis of each file, and compiles it into a comprehensive set of Markdown files. These files include a main README, module-specific documentation, an API reference, and a project overview, providing a detailed and navigable documentation structure for the project.

## Key Dependencies and Imports

- `json`: Used for loading and saving documentation in JSON format.
- `pathlib.Path`: For handling file and directory paths.
- `datetime.datetime`: To timestamp the generated documentation.
- `logging`: For logging information and errors during the documentation process.
- `typing.Dict, List, Any`: For type annotations, improving code readability and correctness.
- `.config.Config`: A custom configuration class (presumably from a local module `config.py`) that holds configuration details for the documentation process.

## Classes

### DocumentationBuilder

#### Purpose

The `DocumentationBuilder` class is responsible for building the entire documentation structure for a Python project. It organizes documentation into a coherent structure, saves it in various formats (JSON, Markdown), and generates several key documentation files, including a README, module documentation, an API reference, and a project overview.

#### Key Methods

- `__init__(self, config: Config)`: Initializes a new instance of the documentation builder with a given configuration.
- `load_existing_documentation(self) -> None`: Loads existing documentation from a JSON file for incremental updates.
- `add_file_documentation(self, file_path: Path, doc_content: Dict) -> None`: Adds documentation for a single file.
- `build_documentation(self) -> None`: Orchestrates the entire process of building the documentation, including saving raw data, generating Markdown files, and organizing the project structure.
- `_save_documentation_json(self) -> None`: Saves the raw documentation data as a JSON file.
- `_build_project_structure(self) -> None`: Creates a hierarchical structure of the project based on the documented files.
- `_generate_readme(self) -> None`: Generates the main README.md file for the project documentation.
- `_generate_module_docs(self) -> None`: Generates documentation for each module in the project.
- `_generate_api_reference(self) -> None`: Creates a comprehensive API reference document.
- `_generate_project_overview(self) -> None`: Produces a project overview document.

#### Relationships

- Uses the `Config` class for configuration settings, such as output directories and project root.
- Interacts with the filesystem to read from and write to files, utilizing `pathlib.Path`.

## Functions

This script does not define standalone functions outside of the `DocumentationBuilder` class.

## Usage Examples

To use the `DocumentationBuilder`, you must first instantiate it with a `Config` object that specifies the necessary configuration for your project. Below is a hypothetical example of how one might use this class:

```python
from config import Config
from doc_builder import DocumentationBuilder

# Assume Config is properly defined elsewhere to specify project settings
config = Config(project_root="/path/to/project", output_dir="/path/to/output/documentation")

doc_builder = DocumentationBuilder(config)

# Load existing documentation, if any
doc_builder.load_existing_documentation()

# Example: Add documentation for a specific file
doc_content = {
    "summary": "This file contains utility functions.",
    "functions": [
        {"name": "add", "description": "Adds two numbers."}
    ]
}
file_path = Path("/path/to/project/utils.py")
doc_builder.add_file_documentation(file_path, doc_content)

# Build the entire documentation
doc_builder.build_documentation()
```

## Important Notes and Considerations

- The script assumes a structured format for documentation content, relying on JSON for raw data storage and Markdown for human-readable output.
- Error handling is primarily done through logging, with exceptions caught and logged rather than raised. This design choice may affect debugging and should be considered when integrating or extending this script.
- The documentation structure is heavily dependent on the project's file and directory layout, as it generates a tree view and organizes documentation accordingly.
- Incremental updates are supported by loading existing documentation before adding new or updated files. This feature requires consistent JSON formatting and may be impacted by manual edits to the generated JSON file.
- The script's functionality is tightly coupled with the `Config` class, which must be defined to match the script's expectations for project root and output directory settings.

#### Code Analysis

**Module Docstring:**
> Documentation builder for organizing and formatting the final documentation.

- **Lines of Code:** 516
- **Classes:** 1
- **Functions:** 0
- **Complexity Score:** 29

---

### doc_generator.py

# Documentation for `doc_generator.py`

## Overview

The `doc_generator.py` script is part of the RainMakerz Document Processing project and serves as the main entry point for generating comprehensive documentation for Python projects. It leverages OpenAI's API to analyze source code and produce detailed, Markdown-formatted documentation automatically. This script integrates various components such as file scanning, code analysis, documentation building, and change tracking to efficiently update or generate documentation based on the latest code changes.

## Classes

### DocumentationGenerator

#### Purpose

The `DocumentationGenerator` class is the core component responsible for orchestrating the documentation generation process. It utilizes several helper classes (`FileScanner`, `CodeAnalyzer`, `ChangeTracker`, `DocumentationBuilder`) to scan for files, analyze code, track changes, and build the final documentation, respectively.

#### Key Methods

- `__init__(self, config: Config)`: Initializes a new instance of the documentation generator with the given configuration.
  - **Parameters:**
    - `config`: An instance of `Config` containing configuration settings for the documentation generator.
- `generate_documentation(self, force_full: bool = False)`: Main method to start the documentation generation process.
  - **Parameters:**
    - `force_full`: A boolean flag indicating whether to regenerate all documentation regardless of changes. Defaults to `False`.
- `_document_file(self, file_path: Path) -> Optional[Dict]`: Generates documentation for a single file.
  - **Parameters:**
    - `file_path`: A `Path` object pointing to the file to document.
  - **Returns:** An optional dictionary containing the documentation content, or `None` if documentation could not be generated.
- `_create_documentation_prompt(self, file_path: Path, content: str, analysis: Dict) -> str`: Creates a prompt for the LLM based on the file's content and analysis.
  - **Parameters:**
    - `file_path`: A `Path` object pointing to the file.
    - `content`: The content of the file as a string.
    - `analysis`: A dictionary containing the analysis of the file.
  - **Returns:** A string containing the prompt for the LLM.

#### Relationships

- Utilizes `Config` for configuration settings.
- Aggregates `FileScanner`, `CodeAnalyzer`, `ChangeTracker`, and `DocumentationBuilder` to handle specific parts of the documentation generation process.

## Functions

### main()

#### Purpose

Serves as the entry point for the documentation generator script. It parses command-line arguments, loads configuration, and initiates the documentation generation process.

#### Parameters

- `--config`: Path to the configuration file.
- `--full`: Flag to force full documentation regeneration.
- `--api-key`: OpenAI API key (overrides the configuration file).
- `--output`: Output directory for the generated documentation.

#### Return Values

None.

#### Exceptions

Exits with an error message if the OpenAI API key is not provided.

## Key Dependencies and Imports

- `sys`: Used for exiting the script with an error code.
- `logging`: Used for logging messages.
- `pathlib.Path`: Used for file and directory path manipulations.
- `typing.Dict`, `typing.Optional`: Used for type hinting.
- `datetime.datetime`: Used for timestamping documentation.
- `openai.OpenAI`: Used to interact with OpenAI's API for generating documentation content.
- `tqdm.tqdm`: Used for displaying progress bars during documentation generation.
- Local imports (`FileScanner`, `CodeAnalyzer`, `ChangeTracker`, `DocumentationBuilder`, `Config`): Components used in the documentation generation process.

## Usage Examples

To generate or update documentation for a project:

```bash
python doc_generator.py --config path/to/config.json --full
```

To override the OpenAI API key and specify an output directory:

```bash
python doc_generator.py --api-key "your_openai_api_key" --output path/to/output_directory
```

## Important Notes or Considerations

- The script requires a valid OpenAI API key to function. This can be provided via a configuration file or directly as a command-line argument.
- The `--full` flag forces the regeneration of all documentation, which might be necessary after significant changes to the project structure or as a periodic update to ensure documentation accuracy.
- The script is designed to be extensible, allowing for future enhancements such as support for additional programming languages or integration with other documentation standards.
- Error handling is implemented to gracefully skip files that cannot be documented due to read errors or issues with the LLM response.

#### Code Analysis

**Module Docstring:**
> Main documentation generator for the RainMakerz Document Processing project.
Generates comprehensive documentation using OpenAI's API.

- **Lines of Code:** 216
- **Classes:** 1
- **Functions:** 1
- **Complexity Score:** 11

**Dependencies:**
- openai
- tqdm

---

### file_scanner.py

# Documentation for `file_scanner.py`

## Overview

The `file_scanner.py` module is designed to identify Python files within a project that are relevant for documentation purposes. It scans the project directory based on specified patterns, excluding certain directories and files as configured. The module supports scanning for files with complex patterns using glob and handling specific cases like excluding large files or test files unless specified otherwise.

## Key Dependencies and Imports

- `os`: Standard library used for interacting with the operating system.
- `fnmatch`: Module for matching Unix shell-style wildcards.
- `pathlib.Path`, `pathlib.PurePath`: For filesystem paths with semantics appropriate for different operating systems.
- `typing.List`, `typing.Dict`, `typing.Any`, `typing.cast`: For type hinting.
- `logging`: Standard logging module.
- `config.Config`: Custom configuration class from the project's `config` module, used for accessing project settings.

## Classes

### `FileScanner`

#### Purpose

Scans the project directory for Python files that match specified inclusion patterns while respecting exclusion patterns for both files and directories. It aims to identify all relevant files for documentation by filtering out undesired files (e.g., too large, test files, or files in excluded directories).

#### Key Methods

- `__init__(self, config: Config)`: Initializes the `FileScanner` with project configuration.
- `scan_all_files(self) -> List[Path]`: Scans the entire project directory for files matching the include patterns and returns a list of `Path` objects for the files to document.
- `_find_files(self, pattern: str) -> List[Path]`: Helper method to find files matching a specific pattern.
- `_should_exclude_dir(self, dir_path: Path) -> bool`: Determines if a directory should be excluded based on the configuration.
- `_should_include_file(self, file_path: Path) -> bool`: Checks if a file meets the criteria to be included in the documentation.
- `_is_test_directory(self, dir_path: Path) -> bool`: Checks if a directory is a test directory.
- `_is_test_file(self, file_path: Path) -> bool`: Determines if a file is a test file.
- `get_project_structure(self) -> Dict[str, Any]`: Returns the project structure as a nested dictionary.

#### Relationships

The `FileScanner` class interacts closely with the `Config` class to access the project's configuration settings, such as include and exclude patterns, maximum file size for inclusion, and the root directory of the project.

## Usage Examples

### Scanning Project Files

To use `FileScanner` for scanning files in a project, you need to have a `Config` object initialized with your project's configuration. Here's a basic example:

```python
from ai_doc_generator.config import Config
from ai_doc_generator.file_scanner import FileScanner

# Assuming config is already set up with include and exclude patterns
config = Config(project_root=Path("/path/to/your/project"))

file_scanner = FileScanner(config)
files_to_document = file_scanner.scan_all_files()

print(f"Files to document: {files_to_document}")
```

### Getting Project Structure

To get the project structure as a nested dictionary:

```python
project_structure = file_scanner.get_project_structure()
print(project_structure)
```

## Important Notes and Considerations

- The scanning process is heavily dependent on the configuration provided, especially the include and exclude patterns. Incorrect patterns can lead to missing files or including undesired files.
- The method `_find_files` uses different strategies for pattern matching based on the presence of `**` in the pattern. This allows for more flexible file matching but requires understanding of glob patterns.
- Special handling is implemented for `__init__.py` files to ensure they are included if they contain significant code beyond mere imports or docstrings, even if they match exclude patterns.
- The module is designed with the assumption that it's part of a larger project with a specific structure, particularly the use of a `Config` object for configuration settings. This may limit its direct applicability in other projects without adaptation.
- Logging is used to provide debug information, which can be helpful for troubleshooting issues with file scanning and inclusion/exclusion decisions.

#### Code Analysis

**Module Docstring:**
> File scanner for identifying Python files in the project.

- **Lines of Code:** 166
- **Classes:** 1
- **Functions:** 0
- **Complexity Score:** 13

**Dependencies:**
- fnmatch

---
