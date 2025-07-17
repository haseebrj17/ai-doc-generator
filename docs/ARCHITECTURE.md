# Documentation Generator Architecture

## System Overview

The documentation generator is a modular Python system that uses OpenAI's GPT models to automatically generate comprehensive documentation for Python projects. It's designed with incremental updates in mind to minimize API usage and costs.

## Core Components

### 1. Configuration Module (`config.py`)
- **Purpose**: Centralized configuration management
- **Key Features**:
  - Environment variable support for API keys
  - JSON-based configuration files
  - Sensible defaults for Python projects
  - Validation of configuration values

### 2. Documentation Generator (`doc_generator.py`)
- **Purpose**: Main orchestration and coordination
- **Responsibilities**:
  - Coordinate between all modules
  - Manage the documentation generation workflow
  - Handle OpenAI API interactions
  - Create prompts for the LLM
  - Command-line interface

### 3. File Scanner (`file_scanner.py`)
- **Purpose**: Identify files to document
- **Features**:
  - Pattern-based file inclusion/exclusion
  - Directory traversal with filtering
  - Project structure analysis
  - Test file detection

### 4. Code Analyzer (`code_analyzer.py`)
- **Purpose**: Extract structural information from Python code
- **Uses**: Python's Abstract Syntax Tree (AST)
- **Extracts**:
  - Classes, methods, and attributes
  - Functions and their signatures
  - Imports and dependencies
  - Decorators and patterns
  - Docstrings and type annotations

### 5. Change Tracker (`change_tracker.py`)
- **Purpose**: Identify modified files for incremental updates
- **Methods**:
  - Git integration for version history
  - File modification timestamps
  - Content hashing (SHA256)
  - State persistence between runs

### 6. Documentation Builder (`doc_builder.py`)
- **Purpose**: Organize and format the final documentation
- **Outputs**:
  - Hierarchical module documentation
  - Comprehensive API reference
  - Project overview and analysis
  - Navigation and indices

## Data Flow

```
1. Configuration Loading
   └─> Config validation and setup

2. File Discovery
   ├─> FileScanner identifies Python files
   └─> ChangeTracker determines what needs updating

3. Code Analysis
   ├─> CodeAnalyzer extracts AST information
   └─> Structural data prepared for LLM

4. Documentation Generation
   ├─> LLM prompts created with code + analysis
   ├─> OpenAI API generates documentation
   └─> Responses parsed and stored

5. Documentation Building
   ├─> Existing docs loaded (if incremental)
   ├─> New/updated docs integrated
   ├─> Markdown files generated
   └─> Navigation structure created

6. State Update
   └─> ChangeTracker saves current state
```

## Key Design Decisions

### 1. Incremental Updates
- **Rationale**: Minimize API costs and processing time
- **Implementation**: Multi-layered change detection
- **Benefits**: Efficient for large projects

### 2. AST-Based Analysis
- **Rationale**: Accurate code structure extraction
- **Benefits**: No regex parsing, handles edge cases
- **Trade-off**: Only works with syntactically valid Python

### 3. Modular Architecture
- **Rationale**: Maintainability and extensibility
- **Benefits**: Easy to test, modify, or extend individual components
- **Example**: Could easily add support for other languages

### 4. JSON State Persistence
- **Rationale**: Simple, human-readable state tracking
- **Benefits**: Easy debugging, no database required
- **Location**: `.doc_state.json` in project root

### 5. Hierarchical Documentation Structure
- **Rationale**: Mirrors project structure for intuitive navigation
- **Benefits**: Scalable for large projects
- **Output**: Multiple interlinked Markdown files

## Extension Points

### Adding New Languages
1. Create a new analyzer (e.g., `js_analyzer.py`)
2. Implement language-specific AST parsing
3. Update `FileScanner` patterns
4. Adjust prompts in `DocumentationGenerator`

### Custom Documentation Formats
1. Extend `DocumentationBuilder`
2. Add new output methods (e.g., `_generate_sphinx_docs()`)
3. Configure output format in config

### Alternative LLM Providers
1. Create adapter interface in `doc_generator.py`
2. Implement provider-specific adapters
3. Configure provider in settings

## Performance Considerations

### API Rate Limiting
- Currently relies on OpenAI's built-in rate limiting
- Could add custom rate limiting with `time.sleep()`
- Consider batching for very large projects

### Memory Usage
- Files processed one at a time
- Large files truncated in prompts (configurable)
- State stored incrementally

### Scalability
- Tested on projects with 1000+ files
- Incremental mode essential for large codebases
- Consider parallel processing for independent modules

## Security Considerations

1. **API Key Management**: Never stored in config files
2. **File Access**: Respects OS permissions
3. **Code Execution**: Only static analysis, no code execution
4. **Output Sanitization**: LLM output used directly (trust OpenAI)

## Future Enhancements

1. **Parallel Processing**: Process multiple files concurrently
2. **Caching**: Cache LLM responses for unchanged files
3. **Diff-Based Updates**: Only send changed parts to LLM
4. **Multi-Language Support**: Extend beyond Python
5. **IDE Integration**: VSCode/PyCharm extensions
6. **CI/CD Integration**: GitHub Actions, GitLab CI
7. **Documentation Quality Metrics**: Analyze completeness
8. **Custom Prompt Templates**: User-defined documentation styles