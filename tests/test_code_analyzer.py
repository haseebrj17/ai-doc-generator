"""
Tests for the code analyzer module.
"""

from pathlib import Path
from scripts.documentation import conftest

from scripts.documentation.code_analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Test cases for the CodeAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a CodeAnalyzer instance."""
        return CodeAnalyzer()

    def test_analyze_simple_module(self, analyzer):
        """Test analyzing a simple module."""
        code = '''"""Module docstring."""

import os
import sys

CONSTANT_VALUE = 42

def simple_function(arg1, arg2):
    """Function docstring."""
    return arg1 + arg2
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        assert result["module_docstring"] == "Module docstring."
        assert result["loc"] == 10
        assert len(result["imports"]) == 2
        assert len(result["functions"]) == 1
        assert len(result["constants"]) == 1
        assert result["constants"][0]["name"] == "CONSTANT_VALUE"

    def test_analyze_class_definition(self, analyzer):
        """Test analyzing a class with methods."""
        code = '''
class MyClass:
    """Class docstring."""

    def __init__(self, value):
        """Initialize."""
        self.value = value

    def method(self):
        """Instance method."""
        return self.value

    @classmethod
    def class_method(cls):
        """Class method."""
        return cls

    @staticmethod
    def static_method():
        """Static method."""
        return 42

    @property
    def prop(self):
        """Property."""
        return self.value
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        assert len(result["classes"]) == 1
        cls = result["classes"][0]
        assert cls["name"] == "MyClass"
        assert cls["docstring"] == "Class docstring."
        assert len(cls["methods"]) == 5

        # Check method types
        methods = {m["name"]: m for m in cls["methods"]}
        assert methods["class_method"]["is_classmethod"]
        assert methods["static_method"]["is_staticmethod"]
        assert methods["prop"]["is_property"]

    def test_analyze_decorators(self, analyzer):
        """Test decorator detection."""
        code = '''
from functools import wraps
from dataclasses import dataclass

@dataclass
class Data:
    value: int

@wraps(print)
def wrapped_function():
    pass

@custom_decorator
@another.decorator()
def multi_decorated():
    pass
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        assert "@dataclass" in result["decorators_used"]
        assert "@wraps" in result["decorators_used"]
        assert "@custom_decorator" in result["decorators_used"]
        assert "@another.decorator" in result["decorators_used"]

    def test_analyze_imports(self, analyzer):
        """Test import analysis."""
        code = '''
import os
import sys as system
from pathlib import Path
from typing import List, Dict as DictType
from ..utils import helper
import external_package
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        imports = result["imports"]
        assert len(imports) == 6

        # Check import types
        import_map = {imp["module"]: imp for imp in imports if imp["type"] == "import"}
        assert import_map["os"]["alias"] is None
        assert import_map["sys"]["alias"] == "system"

        # Check from imports
        from_imports = [imp for imp in imports if imp["type"] == "from"]
        assert any(imp["module"] == "pathlib" and imp["name"] == "Path" for imp in from_imports)
        assert any(imp["module"] == "typing" and imp["name"] == "Dict" and imp["alias"] == "DictType" for imp in from_imports)

        # Check dependencies
        assert "external_package" in result["dependencies"]
        assert "os" not in result["dependencies"]  # stdlib

    def test_analyze_type_annotations(self, analyzer):
        """Test type annotation extraction."""
        code = '''
from typing import List, Optional

class TypedClass:
    name: str
    age: int
    items: List[str] = []

def typed_function(
    arg1: str,
    arg2: int = 0,
    *args: str,
    **kwargs: dict
) -> Optional[str]:
    """Typed function."""
    return arg1 if arg2 > 0 else None
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        # Check class attributes
        cls = result["classes"][0]
        attrs = {attr["name"]: attr for attr in cls["attributes"]}
        assert attrs["name"]["type"] == "str"
        assert attrs["age"]["type"] == "int"
        assert attrs["items"]["type"] == "List[str]"
        assert attrs["items"]["has_default"]

        # Check function annotations
        func = result["functions"][0]
        args = {arg["name"]: arg for arg in func["args"]}
        assert args["arg1"]["annotation"] == "str"
        assert args["arg2"]["annotation"] == "int"
        assert args["arg2"]["has_default"]
        assert args["args"]["type"] == "vararg"
        assert args["kwargs"]["type"] == "kwarg"
        assert func["returns"] == "Optional[str]"

    def test_analyze_exceptions(self, analyzer):
        """Test exception detection."""
        code = '''
class CustomError(Exception):
    pass

def risky_function():
    """Function that raises exceptions."""
    if True:
        raise ValueError("Invalid value")
    elif False:
        raise CustomError()
    else:
        raise Exception
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        # Check exception class detection
        cls = result["classes"][0]
        assert cls["is_exception"]

        # Check raised exceptions
        func = result["functions"][0]
        assert "ValueError" in func["raises"]
        assert "CustomError" in func["raises"]

    def test_analyze_generators(self, analyzer):
        """Test generator detection."""
        code = '''
def regular_function():
    return [1, 2, 3]

def generator_function():
    yield 1
    yield 2
    yield 3

def generator_with_yield_from():
    yield from range(3)

async def async_generator():
    for i in range(3):
        yield i
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        funcs = {f["name"]: f for f in result["functions"]}
        assert not funcs["regular_function"]["is_generator"]
        assert funcs["generator_function"]["is_generator"]
        assert funcs["generator_with_yield_from"]["is_generator"]
        assert funcs["async_generator"]["is_async"]
        assert funcs["async_generator"]["is_generator"]

    def test_analyze_main_guard(self, analyzer):
        """Test detection of if __name__ == "__main__": guard."""
        code_with_main = '''
def main():
    print("Hello")

if __name__ == "__main__":
    main()
'''

        code_without_main = '''
def main():
    print("Hello")

if __name__ == "test":
    main()
'''

        result_with = analyzer.analyze_file(Path("test.py"), code_with_main)
        result_without = analyzer.analyze_file(Path("test.py"), code_without_main)

        assert result_with["has_main"]
        assert not result_without["has_main"]

    def test_analyze_complexity(self, analyzer):
        """Test complexity calculation."""
        code = '''
@decorator1
@decorator2
class ComplexClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass

@decorator3
def function1(): pass

def function2(): pass
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        # Complexity = 5 (class) + 3 (methods) + 2*2 (functions) + 3 (decorators) = 15
        assert result["complexity"] == 15

    def test_analyze_metaclass(self, analyzer):
        """Test metaclass detection."""
        code = '''
class Meta(type):
    pass

class MyClass(metaclass=Meta):
    pass

class Regular:
    pass
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        classes = {cls["name"]: cls for cls in result["classes"]}
        assert classes["MyClass"]["metaclass"] == "Meta"
        assert classes["Regular"]["metaclass"] is None

    def test_analyze_syntax_error(self, analyzer):
        """Test handling of syntax errors."""
        code = '''
def broken_function(
    print("This is invalid syntax")
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        assert "parse_error" in result
        assert result["loc"] == 3  # Still counts lines

    def test_analyze_empty_file(self, analyzer):
        """Test analyzing an empty file."""
        result = analyzer.analyze_file(Path("empty.py"), "")

        assert result["module_docstring"] is None
        assert result["loc"] == 0
        assert len(result["imports"]) == 0
        assert len(result["classes"]) == 0
        assert len(result["functions"]) == 0

    def test_analyze_complex_inheritance(self, analyzer):
        """Test analyzing complex class inheritance."""
        code = '''
from abc import ABC, abstractmethod

class BaseClass(ABC):
    pass

class Mixin:
    pass

class DerivedClass(BaseClass, Mixin):
    pass

class MultipleInheritance(DerivedClass, dict):
    pass
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        classes = {cls["name"]: cls for cls in result["classes"]}
        assert classes["BaseClass"]["bases"] == ["ABC"]
        assert classes["DerivedClass"]["bases"] == ["BaseClass", "Mixin"]
        assert classes["MultipleInheritance"]["bases"] == ["DerivedClass", "dict"]

    def test_analyze_relative_imports(self, analyzer):
        """Test relative import handling."""
        code = '''
from . import sibling
from .. import parent
from ...package import module
from .submodule import function
'''

        result = analyzer.analyze_file(Path("test.py"), code)

        imports = result["imports"]
        relative_imports = [imp for imp in imports if imp.get("level", 0) > 0]

        assert len(relative_imports) == 4
        levels = [imp["level"] for imp in relative_imports]
        assert 1 in levels
        assert 2 in levels
        assert 3 in levels