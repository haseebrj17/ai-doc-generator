"""
File scanner for identifying Python files in the project.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Any
import logging

from .config import Config

logger = logging.getLogger(__name__)


class FileScanner:
    """Scans the project directory for files to document."""

    def __init__(self, config: Config):
        self.config = config

    def scan_all_files(self) -> List[Path]:
        """
        Scan the entire project for files matching the include patterns.

        Returns:
            List of Path objects for files to document
        """
        files = []

        for pattern in self.config.include_patterns:
            files.extend(self._find_files(pattern))

        # Remove duplicates and sort
        files = sorted(list(set(files)))

        logger.info(f"Found {len(files)} files matching patterns")
        return files

    def _find_files(self, pattern: str) -> List[Path]:
        """Find all files matching the given pattern."""
        matches = []

        for root, dirs, files in os.walk(self.config.project_root):
            # Convert to Path for easier handling
            root_path = Path(root)

            # Skip excluded directories
            dirs_filtered = [d for d in dirs if not self._should_exclude_dir(root_path / d)]
            dirs.clear()
            dirs.extend(dirs_filtered)

            # Skip if we're in a test directory and not including tests
            if not self.config.include_tests and self._is_test_directory(root_path):
                continue

            # Check files
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    file_path = root_path / filename

                    if self._should_include_file(file_path):
                        matches.append(file_path)

        return matches

    def _should_exclude_dir(self, dir_path: Path) -> bool:
        """Check if a directory should be excluded."""
        dir_name = dir_path.name

        # Check against exclude patterns
        for exclude_pattern in self.config.exclude_dirs:
            if fnmatch.fnmatch(dir_name, exclude_pattern):
                logger.debug(f"Excluding directory: {dir_path}")
                return True

        return False

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in documentation."""

        # Check file size
        try:
            if file_path.stat().st_size > self.config.max_file_size:
                logger.debug(f"Excluding large file: {file_path}")
                return False
        except OSError:
            return False

        # Check against exclude patterns
        filename = file_path.name
        for exclude_pattern in self.config.exclude_files:
            if fnmatch.fnmatch(filename, exclude_pattern):
                # Special handling for __init__.py - include if it has content
                if filename == "__init__.py":
                    try:
                        content = file_path.read_text().strip()
                        # Include if it has more than just imports or docstrings
                        if len(content) > 100 or "class" in content or "def " in content:
                            return True
                    except:
                        pass
                logger.debug(f"Excluding file: {file_path}")
                return False

        # Skip test files if not including tests
        if not self.config.include_tests and self._is_test_file(file_path):
            logger.debug(f"Excluding test file: {file_path}")
            return False

        return True

    def _is_test_directory(self, dir_path: Path) -> bool:
        """Check if a directory is a test directory."""
        dir_name = dir_path.name.lower()
        return dir_name in ['tests', 'test', 'testing'] or dir_name.startswith('test_')

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        filename = file_path.name.lower()
        return (filename.startswith('test_') or
                filename.endswith('_test.py') or
                filename in ['test.py', 'tests.py'])

    def get_project_structure(self) -> Dict[str, Any]:
        """
        Get the project structure as a nested dictionary.

        Returns:
            Dictionary representing the project structure
        """
        structure = {"name": self.config.project_root.name, "type": "directory", "children": {}}

        for file_path in self.scan_all_files():
            relative_path = file_path.relative_to(self.config.project_root)
            parts = relative_path.parts

            current = structure["children"]
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {"name": part, "type": "directory", "children": {}}
                current = current[part]["children"]

            # Add the file
            file_name = parts[-1]
            current[file_name] = {"name": file_name, "type": "file", "path": str(file_path)}

        return structure