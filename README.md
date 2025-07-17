# AI Documentation Generator 🤖📚

[![PyPI version](https://badge.fury.io/py/ai-doc-generator.svg)](https://badge.fury.io/py/ai-doc-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/ai-doc-generator.svg)](https://pypi.org/project/ai-doc-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/haseebrj17/ai-doc-generator/workflows/tests/badge.svg)](https://github.com/haseebrj17/ai-doc-generator/actions)
[![codecov](https://codecov.io/gh/haseebrj17/ai-doc-generator/branch/main/graph/badge.svg)](https://codecov.io/gh/haseebrj17/ai-doc-generator)

Automatically generate comprehensive documentation for your Python projects using OpenAI's GPT models. This tool analyzes your codebase and creates detailed, well-structured documentation that helps developers understand and use your code effectively.

## ✨ Features

- 🔍 **Intelligent Code Analysis**: Uses AST parsing to understand your code structure
- 📝 **Comprehensive Documentation**: Generates detailed docs for modules, classes, functions, and more
- 🚀 **Incremental Updates**: Only regenerates docs for files that have changed
- 🔧 **Git Integration**: Tracks changes through git history
- 💰 **Cost-Effective**: Minimal API usage through smart caching and incremental updates
- 🎨 **Beautiful Output**: Generates well-structured Markdown documentation
- ⚙️ **Highly Configurable**: Customize what gets documented and how
- 🖥️ **CLI & API**: Use as a command-line tool or integrate into your Python projects

## 📦 Installation

```bash
pip install ai-doc-generator
```

Or install from source:

```bash
git clone https://github.com/haseebrj17/ai-doc-generator.git
cd ai-doc-generator
pip install -e .
```

## 🚀 Quick Start

1. **Set your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. **Generate documentation for your project:**
```bash
ai-doc-gen /path/to/your/project
```

That's it! Your documentation will be generated in `docs/generated/`.

## 📖 Usage

### Command Line Interface

```bash
# Generate docs for current directory
ai-doc-gen

# Generate docs for specific path
ai-doc-gen /path/to/project

# Force full regeneration (ignore cache)
ai-doc-gen --full

# Use a specific model
ai-doc-gen --model gpt-4o-mini

# Custom output directory
ai-doc-gen --output docs/api

# Include test files
ai-doc-gen --include-tests

# Dry run to see what would be documented
ai-doc-gen --dry-run
```

### Python API

```python
from ai_doc_generator import Config, DocumentationGenerator

# Create configuration
config = Config(
    project_root="./my_project",
    output_dir="./docs",
    include_tests=False,
    model="gpt-4o"
)

# Generate documentation
generator = DocumentationGenerator(config)
generator.generate_documentation()
```

## ⚙️ Configuration

Create a `ai-doc-config.json` file in your project root:

```json
{
  "model": "gpt-4o",
  "output_dir": "docs/generated",
  "include_patterns": ["*.py"],
  "exclude_dirs": ["tests", "__pycache__", ".venv"],
  "exclude_files": ["setup.py"],
  "max_file_size": 100000,
  "include_tests": false
}
```

## 💸 Cost Estimation

For a typical Python project:
- **Small project** (10k lines): ~$2-3
- **Medium project** (50k lines): ~$8-12  
- **Large project** (100k lines): ~$15-25

After initial generation, incremental updates cost 90% less!

## 📁 Output Structure

```
docs/generated/
├── README.md                 # Main documentation index
├── project-overview.md       # High-level project analysis
├── api-reference.md         # Complete API reference
├── modules/                 # Module-specific documentation
│   ├── core/
│   ├── utils/
│   └── ...
└── documentation.json       # Raw documentation data
```

## 🛠️ Advanced Features

### Incremental Documentation
Only regenerate documentation for files that have changed:
```bash
# First run - documents everything
ai-doc-gen

# Subsequent runs - only changed files
ai-doc-gen
```

### Custom Prompts
Customize the documentation style:
```python
config = Config(
    system_prompt="Generate concise API documentation focusing on usage examples..."
)
```

### Multiple Models
Use different models for different purposes:
- `gpt-4o`: Best quality, detailed documentation
- `gpt-4o-mini`: Faster and cheaper, good for most projects
- `gpt-4-turbo-preview`: Balance of quality and cost

## 🧪 Development

```bash
# Clone the repository
git clone https://github.com/haseebrj17/ai-doc-generator.git
cd ai-doc-generator

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .

# Run tests with coverage
pytest --cov=ai_doc_generator
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The Python AST module for code analysis
- All contributors and users of this project

## 📞 Support

- 📧 Email: muhamadhaseeb2001@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/haseebrj17/ai-doc-generator/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/haseebrj17/ai-doc-generator/discussions)

---

**Made with ❤️ by [Muhammad Haseeb](https://github.com/haseebrj17)**