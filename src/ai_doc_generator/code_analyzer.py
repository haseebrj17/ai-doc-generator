"""
Code analyzer for extracting structural information from Python files.
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes Python code to extract structural information."""

    def analyze_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Analyze a Python file and extract its structure.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Dictionary containing analysis results
        """
        analysis: Dict[str, Any] = {
            "file_path": str(file_path),
            "module_docstring": None,
            "imports": [],
            "classes": [],
            "functions": [],
            "constants": [],
            "loc": len(content.splitlines()),
            "complexity": 0,
            "has_main": False,
            "decorators_used": set(),
            "dependencies": set()
        }

        try:
            tree = ast.parse(content)
            analyzer = ASTAnalyzer()
            analyzer.visit(tree)

            analysis.update({
                "module_docstring": analyzer.module_docstring,
                "imports": analyzer.imports,
                "classes": analyzer.classes,
                "functions": analyzer.functions,
                "constants": analyzer.constants,
                "has_main": analyzer.has_main,
                "decorators_used": list(analyzer.decorators_used),
                "dependencies": list(analyzer.dependencies)
            })

            # Calculate complexity
            analysis["complexity"] = self._calculate_complexity(analyzer)

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            analysis["parse_error"] = str(e)
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            analysis["error"] = str(e)

        return analysis

    def _calculate_complexity(self, analyzer: 'ASTAnalyzer') -> int:
        """Calculate a simple complexity score for the file."""
        complexity = 0

        # Add complexity for classes
        for cls in analyzer.classes:
            complexity += 5
            complexity += len(cls.get("methods", []))

        # Add complexity for functions
        complexity += len(analyzer.functions) * 2

        # Add complexity for decorators
        complexity += len(analyzer.decorators_used)

        return complexity


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for extracting information from Python code."""

    def __init__(self) -> None:
        self.module_docstring: Optional[str] = None
        self.imports: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.constants: List[Dict[str, Any]] = []
        self.has_main = False
        self.decorators_used: set[str] = set()
        self.dependencies: set[str] = set()
        self._current_class: Optional[Dict[str, Any]] = None

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module node to extract module docstring."""
        docstring = ast.get_docstring(node)
        if docstring:
            self.module_docstring = docstring
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            import_info = {
                "type": "import",
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            }
            self.imports.append(import_info)

            # Track external dependencies
            base_module = alias.name.split('.')[0]
            if not self._is_stdlib_module(base_module):
                self.dependencies.add(base_module)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements."""
        module = node.module or ""
        for alias in node.names:
            import_info = {
                "type": "from",
                "module": module,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "level": node.level  # Relative import level
            }
            self.imports.append(import_info)

        # Track external dependencies
        if module and node.level == 0:  # Absolute import
            base_module = module.split('.')[0]
            if not self._is_stdlib_module(base_module):
                self.dependencies.add(base_module)

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "docstring": ast.get_docstring(node),
            "bases": [self._get_name(base) for base in node.bases],
            "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list],
            "methods": [],
            "attributes": [],
            "is_exception": self._is_exception_class(node),
            "metaclass": self._get_metaclass(node)
        }

        # Track decorators
        for dec in node.decorator_list:
            self.decorators_used.add(self._get_decorator_name(dec))

        # Temporarily store current class
        old_class = self._current_class
        self._current_class = class_info

        # Visit children
        self.generic_visit(node)

        # Restore previous class context
        self._current_class = old_class

        self.classes.append(class_info)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self._process_function(node, is_async=True)

    def _process_function(self, node: Any, is_async: bool = False) -> None:
        """Process function or async function definition."""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "docstring": ast.get_docstring(node),
            "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list],
            "args": self._extract_arguments(node.args),
            "returns": self._get_return_annotation(node),
            "is_async": is_async,
            "is_generator": self._is_generator(node),
            "raises": self._extract_exceptions(node)
        }

        # Track decorators
        for dec in node.decorator_list:
            self.decorators_used.add(self._get_decorator_name(dec))

        # Add to appropriate list
        if self._current_class:
            # It's a method
            func_info["is_method"] = True
            func_info["is_classmethod"] = "@classmethod" in func_info["decorators"]
            func_info["is_staticmethod"] = "@staticmethod" in func_info["decorators"]
            func_info["is_property"] = "@property" in func_info["decorators"]
            self._current_class["methods"].append(func_info)
        else:
            # It's a function
            func_info["is_method"] = False
            self.functions.append(func_info)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statements to check for main guard."""
        # Check for if __name__ == "__main__":
        if self._is_main_guard(node):
            self.has_main = True

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignments (type hints)."""
        if isinstance(node.target, ast.Name) and self._current_class:
            attr_info = {
                "name": node.target.id,
                "type": self._get_annotation(node.annotation),
                "line": node.lineno,
                "has_default": node.value is not None
            }
            self._current_class["attributes"].append(attr_info)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignments to find constants."""
        # Look for module-level constants (UPPER_CASE names)
        if not self._current_class and node.targets:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if name.isupper() and '_' in name:
                        const_info = {
                            "name": name,
                            "line": node.lineno,
                            "value_type": type(node.value).__name__
                        }
                        self.constants.append(const_info)
        self.generic_visit(node)

    def _is_main_guard(self, node: ast.If) -> bool:
        """Check if an if statement is a main guard."""
        if not isinstance(node.test, ast.Compare):
            return False

        if len(node.test.ops) != 1 or not isinstance(node.test.ops[0], ast.Eq):
            return False

        if not isinstance(node.test.left, ast.Name) or node.test.left.id != "__name__":
            return False

        if len(node.test.comparators) != 1:
            return False

        comparator = node.test.comparators[0]
        if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
            return True
        # Backward compatibility for older Python versions
        elif hasattr(ast, 'Str') and isinstance(comparator, ast.Str) and comparator.s == "__main__":
            return True

        return False

    def _get_name(self, node: ast.AST) -> str:
        """Get the name from various node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        elif isinstance(node, ast.Constant):
            # For string constants in annotations
            if isinstance(node.value, str):
                return node.value
            return str(node.value)
        # Backward compatibility
        elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return node.s
        elif hasattr(ast, 'NameConstant') and isinstance(node, ast.NameConstant):
            return str(node.value)
        else:
            # For complex expressions, return a simplified representation
            return f"<{type(node).__name__}>"

    def _get_decorator_name(self, node: ast.AST) -> str:
        """Get decorator name as a string."""
        if isinstance(node, ast.Name):
            return f"@{node.id}"
        elif isinstance(node, ast.Attribute):
            base = self._get_name(node.value)
            return f"@{base}.{node.attr}" if base else f"@{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        else:
            return f"@<{type(node).__name__}>"

    def _extract_arguments(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Extract function arguments."""
        arg_info = []

        # Regular arguments
        for i, arg in enumerate(args.args):
            info: Dict[str, Any] = {"name": arg.arg, "type": "positional"}
            if arg.annotation:
                info["annotation"] = self._get_annotation(arg.annotation)

            # Check for defaults
            default_offset = len(args.args) - len(args.defaults)
            if i >= default_offset:
                info["has_default"] = True

            arg_info.append(info)

        # *args
        if args.vararg:
            vararg_info: Dict[str, Any] = {"name": args.vararg.arg, "type": "vararg"}
            if args.vararg.annotation:
                vararg_info["annotation"] = self._get_annotation(args.vararg.annotation)
            arg_info.append(vararg_info)

        # **kwargs
        if args.kwarg:
            kwarg_info: Dict[str, Any] = {"name": args.kwarg.arg, "type": "kwarg"}
            if args.kwarg.annotation:
                kwarg_info["annotation"] = self._get_annotation(args.kwarg.annotation)
            arg_info.append(kwarg_info)

        return arg_info

    def _get_annotation(self, node: ast.AST) -> str:
        """Get type annotation as a string."""
        if isinstance(node, ast.Subscript):
            # Handle generic types like List[str], Dict[str, int]
            value = self._get_name(node.value)
            # Handle both Python < 3.9 and >= 3.9
            if hasattr(ast, 'Index') and isinstance(node.slice, ast.Index):
                # Python < 3.9 - ast.Index wraps the actual value
                slice_node = node.slice.value  # type: ignore
            else:
                # Python >= 3.9 - slice is the expression directly
                slice_node = node.slice
            slice_value = self._get_annotation(slice_node)
            return f"{value}[{slice_value}]"
        elif isinstance(node, ast.Tuple):
            # Handle tuple in generics like Dict[str, int]
            elements = [self._get_annotation(el) for el in node.elts]
            return ", ".join(elements)
        else:
            return self._get_name(node)

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation."""
        if node.returns:
            return self._get_annotation(node.returns)
        return None

    def _is_generator(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a generator."""
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False

    def _extract_exceptions(self, node: ast.FunctionDef) -> list:
        """Extract exceptions that might be raised."""
        exceptions = []
        for child in ast.walk(node):
            if isinstance(child, ast.Raise) and child.exc:
                if isinstance(child.exc, ast.Call) and hasattr(child.exc, 'func'):
                    exc_name = self._get_name(child.exc.func)
                    if exc_name and exc_name != f"<{type(child.exc.func).__name__}>":
                        exceptions.append(exc_name)
                elif isinstance(child.exc, ast.Name):
                    exceptions.append(child.exc.id)
        return list(set(exceptions))

    def _is_exception_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is an exception class."""
        for base in node.bases:
            base_name = self._get_name(base)
            if 'Exception' in base_name or 'Error' in base_name:
                return True
        return False

    def _get_metaclass(self, node: ast.ClassDef) -> Optional[str]:
        """Extract metaclass if specified."""
        for keyword in node.keywords:
            if keyword.arg == 'metaclass':
                return self._get_name(keyword.value)
        return None

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if a module is part of the standard library."""
        stdlib_modules = {
            'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
            'concurrent', 'contextlib', 'copy', 'dataclasses', 'datetime',
            'decimal', 'enum', 'functools', 'hashlib', 'http', 'importlib',
            'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'os',
            'pathlib', 'pickle', 're', 'shutil', 'socket', 'sqlite3',
            'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback',
            'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref'
        }
        return module_name in stdlib_modules