"""
Documentation builder for organizing and formatting the final documentation.
"""

import json
from typing import Dict, List, Any

from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

from .config import Config

logger = logging.getLogger(__name__)


class DocumentationBuilder:
    """Builds and organizes the final documentation structure."""

    def __init__(self, config: Config):
        self.config = config
        self.documentation: Dict[str, Any] = {}
        self.project_structure: Dict[str, Any] = {}

    def load_existing_documentation(self) -> None:
        """Load existing documentation for incremental updates."""
        doc_file = self.config.output_dir / "documentation.json"
        if doc_file.exists():
            try:
                with open(doc_file, 'r') as f:
                    self.documentation = json.load(f)
                logger.info(f"Loaded existing documentation with {len(self.documentation)} files")
            except Exception as e:
                logger.error(f"Error loading existing documentation: {e}")
                self.documentation = {}

    def add_file_documentation(self, file_path: Path, doc_content: Dict) -> None:
        """Add documentation for a single file."""
        relative_path = file_path.relative_to(self.config.project_root)
        self.documentation[str(relative_path)] = doc_content

    def build_documentation(self) -> None:
        """Build the final documentation structure."""
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Save raw documentation data
        self._save_documentation_json()

        # Build project structure
        self._build_project_structure()

        # Generate markdown files
        self._generate_readme()
        self._generate_module_docs()
        self._generate_api_reference()
        self._generate_project_overview()

        logger.info(f"Documentation built in {self.config.output_dir}")

    def _save_documentation_json(self) -> None:
        """Save the raw documentation data as JSON."""
        doc_file = self.config.output_dir / "documentation.json"
        try:
            with open(doc_file, 'w') as f:
                json.dump(self.documentation, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving documentation JSON: {e}")

    def _build_project_structure(self) -> None:
        """Build a hierarchical project structure from documented files."""
        self.project_structure = {"name": "root", "children": {}, "type": "directory"}

        for file_path in self.documentation.keys():
            parts = Path(file_path).parts
            current = self.project_structure["children"]

            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {"name": part, "children": {}, "type": "directory"}
                current = current[part]["children"]

            # Add file
            file_name = parts[-1]
            current[file_name] = {
                "name": file_name,
                "type": "file",
                "path": file_path
            }

    def _generate_readme(self) -> None:
        """Generate the main README.md file."""
        readme_path = self.config.output_dir / "README.md"

        content = [
            "# Project Documentation",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Table of Contents",
            "",
            "1. [Project Overview](project-overview.md)",
            "2. [Module Documentation](modules/)",
            "3. [API Reference](api-reference.md)",
            "",
            "## Quick Navigation",
            "",
            self._generate_tree_view(self.project_structure["children"]),
            "",
            "## Documentation Statistics",
            "",
            f"- Total Files Documented: {len(self.documentation)}",
            f"- Total Modules: {self._count_modules()}",
            f"- Total Classes: {self._count_classes()}",
            f"- Total Functions: {self._count_functions()}",
            ""
        ]

        try:
            with open(readme_path, 'w') as f:
                f.write('\n'.join(content))
        except Exception as e:
            logger.error(f"Error writing README: {e}")

    def _generate_module_docs(self) -> None:
        """Generate documentation for each module."""
        modules_dir = self.config.output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)

        # Group files by module
        modules = self._group_files_by_module()

        for module_path, files in modules.items():
            self._generate_module_doc(module_path, files, modules_dir)

    def _generate_module_doc(self, module_path: str, files: List[str], output_dir: Path) -> None:
        """Generate documentation for a single module."""
        # Create module directory
        module_dir = output_dir / module_path.replace('/', '_')
        module_dir.mkdir(exist_ok=True)

        # Create module index
        index_path = module_dir / "index.md"

        content = [
            f"# Module: {module_path}",
            "",
            "## Overview",
            "",
            self._generate_module_overview(module_path, files),
            "",
            "## Files",
            ""
        ]

        # Add file documentation
        for file_path in sorted(files):
            doc = self.documentation[file_path]
            file_name = Path(file_path).name

            content.extend([
                f"### {file_name}",
                "",
                doc.get("documentation", "No documentation available."),
                "",
                "#### Code Analysis",
                "",
                self._format_analysis(doc.get("analysis", {})),
                "",
                "---",
                ""
            ])

        try:
            with open(index_path, 'w') as f:
                f.write('\n'.join(content))
        except Exception as e:
            logger.error(f"Error writing module documentation for {module_path}: {e}")

    def _generate_api_reference(self) -> None:
        """Generate comprehensive API reference."""
        api_path = self.config.output_dir / "api-reference.md"

        content = [
            "# API Reference",
            "",
            "Complete API documentation for all classes and functions.",
            "",
            "## Classes",
            ""
        ]

        # Collect all classes
        all_classes = []
        for file_path, doc in self.documentation.items():
            analysis = doc.get("analysis", {})
            for cls in analysis.get("classes", []):
                cls["file_path"] = file_path
                all_classes.append(cls)

        # Sort and document classes
        for cls in sorted(all_classes, key=lambda x: x["name"]):
            content.extend(self._format_class_reference(cls))

        content.extend(["", "## Functions", ""])

        # Collect all functions
        all_functions = []
        for file_path, doc in self.documentation.items():
            analysis = doc.get("analysis", {})
            for func in analysis.get("functions", []):
                func["file_path"] = file_path
                all_functions.append(func)

        # Sort and document functions
        for func in sorted(all_functions, key=lambda x: x["name"]):
            content.extend(self._format_function_reference(func))

        try:
            with open(api_path, 'w') as f:
                f.write('\n'.join(content))
        except Exception as e:
            logger.error(f"Error writing API reference: {e}")

    def _generate_project_overview(self) -> None:
        """Generate project overview documentation."""
        overview_path = self.config.output_dir / "project-overview.md"

        content = [
            "# Project Overview",
            "",
            "## Architecture",
            "",
            self._analyze_architecture(),
            "",
            "## Dependencies",
            "",
            self._analyze_dependencies(),
            "",
            "## Key Components",
            "",
            self._identify_key_components(),
            "",
            "## Design Patterns",
            "",
            self._identify_design_patterns(),
            ""
        ]

        try:
            with open(overview_path, 'w') as f:
                f.write('\n'.join(content))
        except Exception as e:
            logger.error(f"Error writing project overview: {e}")

    def _generate_tree_view(self, structure: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Generate a tree view of the project structure."""
        lines = []
        items = sorted(structure.items())

        for i, (name, info) in enumerate(items):
            is_last_item = i == len(items) - 1

            if info["type"] == "directory":
                lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}/")
                extension = "    " if is_last_item else "│   "
                lines.append(self._generate_tree_view(
                    info.get("children", {}),
                    prefix + extension,
                    is_last_item
                ))
            else:
                lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}")

        return '\n'.join(filter(None, lines))

    def _group_files_by_module(self) -> Dict[str, List[str]]:
        """Group files by their module (directory)."""
        modules: Dict[str, List[str]] = {}

        for file_path in self.documentation.keys():
            module = str(Path(file_path).parent)
            if module == ".":
                module = "root"

            if module not in modules:
                modules[module] = []
            modules[module].append(file_path)

        return modules

    def _generate_module_overview(self, module_path: str, files: List[str]) -> str:
        """Generate an overview for a module based on its files."""
        total_classes = 0
        total_functions = 0
        total_loc = 0

        for file_path in files:
            analysis = self.documentation[file_path].get("analysis", {})
            total_classes += len(analysis.get("classes", []))
            total_functions += len(analysis.get("functions", []))
            total_loc += analysis.get("loc", 0)

        return f"""This module contains {len(files)} files with a total of:
- {total_classes} classes
- {total_functions} functions
- {total_loc} lines of code"""

    def _format_analysis(self, analysis: Dict) -> str:
        """Format code analysis results."""
        lines = []

        if analysis.get("module_docstring"):
            lines.extend([
                "**Module Docstring:**",
                f"> {analysis['module_docstring'][:200]}{'...' if len(analysis['module_docstring']) > 200 else ''}",
                ""
            ])

        lines.extend([
            f"- **Lines of Code:** {analysis.get('loc', 0)}",
            f"- **Classes:** {len(analysis.get('classes', []))}",
            f"- **Functions:** {len(analysis.get('functions', []))}",
            f"- **Complexity Score:** {analysis.get('complexity', 0)}"
        ])

        if analysis.get("dependencies"):
            lines.extend([
                "",
                "**Dependencies:**",
                *[f"- {dep}" for dep in sorted(analysis["dependencies"])]
            ])

        return '\n'.join(lines)

    def _format_class_reference(self, cls: Dict) -> List[str]:
        """Format class information for API reference."""
        lines = [
            f"### class {cls['name']}",
            f"*File: {cls['file_path']}*",
            ""
        ]

        if cls.get("docstring"):
            lines.extend([cls["docstring"], ""])

        if cls.get("bases"):
            lines.extend([f"**Inherits from:** {', '.join(cls['bases'])}", ""])

        if cls.get("methods"):
            lines.extend(["**Methods:**", ""])
            for method in cls["methods"]:
                method_sig = f"- `{method['name']}("
                if method.get("args"):
                    args = [arg["name"] for arg in method["args"] if arg["name"] != "self"]
                    method_sig += ", ".join(args)
                method_sig += ")`"

                if method.get("docstring"):
                    first_line = method['docstring'].split('\n')[0]
                    method_sig += f" - {first_line}"

                lines.append(method_sig)

        lines.extend(["", "---", ""])
        return lines

    def _format_function_reference(self, func: Dict) -> List[str]:
        """Format function information for API reference."""
        lines = [
            f"### {func['name']}",
            f"*File: {func['file_path']}*",
            ""
        ]

        # Build function signature
        sig = f"`{func['name']}("
        if func.get("args"):
            args = []
            for arg in func["args"]:
                arg_str = arg["name"]
                if arg.get("annotation"):
                    arg_str += f": {arg['annotation']}"
                args.append(arg_str)
            sig += ", ".join(args)
        sig += ")"

        if func.get("returns"):
            sig += f" -> {func['returns']}"
        sig += "`"

        lines.append(sig)
        lines.append("")

        if func.get("docstring"):
            lines.extend([func["docstring"], ""])

        if func.get("decorators"):
            lines.extend([
                "**Decorators:** " + ", ".join(func["decorators"]),
                ""
            ])

        if func.get("raises"):
            lines.extend([
                "**Raises:** " + ", ".join(func["raises"]),
                ""
            ])

        lines.extend(["---", ""])
        return lines

    def _count_modules(self) -> int:
        """Count the number of modules in the project."""
        modules = set()
        for file_path in self.documentation.keys():
            module = str(Path(file_path).parent)
            modules.add(module)
        return len(modules)

    def _count_classes(self) -> int:
        """Count total number of classes."""
        total = 0
        for doc in self.documentation.values():
            analysis = doc.get("analysis", {})
            total += len(analysis.get("classes", []))
        return total

    def _count_functions(self) -> int:
        """Count total number of functions."""
        total = 0
        for doc in self.documentation.values():
            analysis = doc.get("analysis", {})
            total += len(analysis.get("functions", []))
        return total

    def _analyze_architecture(self) -> str:
        """Analyze and describe the project architecture."""
        # This is a simplified analysis - could be enhanced
        layers: Dict[str, List[str]] = {
            "api": [],
            "application": [],
            "domain": [],
            "infrastructure": [],
            "core": []
        }

        for file_path in self.documentation.keys():
            for layer in layers:
                if f"/{layer}/" in file_path or file_path.startswith(f"{layer}/"):
                    layers[layer].append(file_path)

        description = []
        for layer, files in layers.items():
            if files:
                description.append(f"- **{layer.title()} Layer:** {len(files)} files")

        return '\n'.join(description) if description else "Architecture analysis not available."

    def _analyze_dependencies(self) -> str:
        """Analyze project dependencies."""
        all_deps = set()

        for doc in self.documentation.values():
            analysis = doc.get("analysis", {})
            all_deps.update(analysis.get("dependencies", []))

        if all_deps:
            return '\n'.join([f"- {dep}" for dep in sorted(all_deps)])
        return "No external dependencies identified."

    def _identify_key_components(self) -> str:
        """Identify and describe key components."""
        # Look for key patterns in class/file names
        components = []

        # Services
        services = [doc for path, doc in self.documentation.items() if "service" in path.lower()]
        if services:
            components.append(f"- **Services:** {len(services)} service modules identified")

        # Controllers
        controllers = [doc for path, doc in self.documentation.items() if "controller" in path.lower()]
        if controllers:
            components.append(f"- **Controllers:** {len(controllers)} controller modules identified")

        # Models/Entities
        entities = [doc for path, doc in self.documentation.items() if "entity" in path.lower() or "model" in path.lower()]
        if entities:
            components.append(f"- **Domain Entities:** {len(entities)} entity modules identified")

        return '\n'.join(components) if components else "Component analysis in progress."

    def _identify_design_patterns(self) -> str:
        """Identify design patterns used in the codebase."""
        patterns = []

        # Look for common patterns
        for doc in self.documentation.values():
            analysis = doc.get("analysis", {})

            # Check for decorators (Decorator pattern)
            if analysis.get("decorators_used"):
                if "@property" in analysis["decorators_used"]:
                    patterns.append("Property decorators for encapsulation")
                if "@classmethod" in analysis["decorators_used"] or "@staticmethod" in analysis["decorators_used"]:
                    patterns.append("Class and static methods for alternative constructors")

            # Check for base classes (Template Method, Strategy patterns)
            for cls in analysis.get("classes", []):
                if cls.get("bases") and any("Abstract" in base or "Base" in base for base in cls["bases"]):
                    patterns.append("Abstract base classes for interface definition")
                    break

        return '\n'.join([f"- {pattern}" for pattern in set(patterns)]) if patterns else "Pattern analysis in progress."