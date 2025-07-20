"""
Change tracker for identifying modified files since last documentation run.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, cast
import logging
import hashlib

from .config import Config
from .file_scanner import FileScanner

logger = logging.getLogger(__name__)


class ChangeTracker:
    """Tracks changes to files between documentation runs."""

    def __init__(self, config: Config):
        self.config = config
        self.state_file = config.project_root / config.state_file
        self.file_scanner = FileScanner(config)
        self._state = self._load_state()

    def has_previous_run(self) -> bool:
        """Check if there's a previous documentation run."""
        return self.state_file.exists() and bool(self._state.get("files"))

    def get_changed_files(self) -> List[Path]:
        """
        Get list of files that have changed since last run.

        Returns:
            List of Path objects for changed files
        """
        changed_files = []

        # Get all current files
        current_files = self.file_scanner.scan_all_files()
        # Convert to relative paths for comparison
        current_file_set = set(str(f.relative_to(self.config.project_root)) for f in current_files)

        # Get previous file set
        previous_files = self._state.get("files", {})
        previous_file_set = set(previous_files.keys())

        # Find new files
        new_files = current_file_set - previous_file_set
        for file_path_str in new_files:
            changed_files.append(Path(file_path_str))
            logger.info(f"New file: {file_path_str}")

        # Find deleted files (we'll handle these in the doc builder)
        deleted_files = previous_file_set - current_file_set
        for file_path_str in deleted_files:
            logger.info(f"Deleted file: {file_path_str}")

        # Find modified files
        for file_path in current_files:
            relative_str = str(file_path.relative_to(self.config.project_root))
            if relative_str in previous_files:
                # Check multiple indicators of change
                if self._has_file_changed(file_path, previous_files[relative_str]):
                    changed_files.append(file_path)
                    logger.info(f"Modified file: {file_path}")

        # Also check for files affected by git changes
        git_changed = self._get_git_changed_files()
        for git_file in git_changed:
            if git_file.exists() and git_file not in changed_files:
                changed_files.append(git_file)

        return sorted(list(set(changed_files)))

    def _has_file_changed(self, file_path: Path, previous_info: Dict) -> bool:
        """Check if a file has changed since last run."""
        try:
            # Get current file stats
            stat = file_path.stat()
            current_mtime = stat.st_mtime
            current_size = stat.st_size

            # Check modification time
            if current_mtime > previous_info.get("mtime", 0):
                return True

            # Check file size
            if current_size != previous_info.get("size", -1):
                return True

            # Check content hash as final verification
            current_hash = self._calculate_file_hash(file_path)
            if current_hash != previous_info.get("hash"):
                return True

        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            return True

        return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _get_git_changed_files(self) -> List[Path]:
        """Get files changed according to git."""
        changed_files = []

        try:
            # Check if we're in a git repository
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.config.project_root,
                check=True,
                capture_output=True
            )

            # Get the last documentation timestamp
            last_run = self._state.get("last_run")

            if last_run:
                # Get files changed since last run
                since_date = datetime.fromisoformat(last_run).strftime("%Y-%m-%d %H:%M:%S")
                result = subprocess.run(
                    ["git", "log", f"--since='{since_date}'", "--name-only", "--format="],
                    cwd=self.config.project_root,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and line.endswith('.py'):
                            file_path = self.config.project_root / line
                            if file_path.exists():
                                changed_files.append(file_path)

            # Also check for uncommitted changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.config.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and line.endswith('.py'):
                        file_path = self.config.project_root / line
                        if file_path.exists():
                            changed_files.append(file_path)

        except subprocess.CalledProcessError:
            # Not a git repository or git not available
            logger.debug("Git not available or not a git repository")

        return changed_files

    def update_state(self, documented_files: List[Path]) -> None:
        """Update the state with newly documented files."""
        # Update file information
        for file_path in documented_files:
            try:
                stat = file_path.stat()
                relative_path = file_path.relative_to(self.config.project_root)
                self._state["files"][str(relative_path)] = {
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "hash": self._calculate_file_hash(file_path),
                    "last_documented": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error updating state for {file_path}: {e}")

        # Update last run timestamp
        self._state["last_run"] = datetime.now().isoformat()

        # Save state
        self._save_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return cast(Dict[str, Any], data)
            except Exception as e:
                logger.error(f"Error loading state: {e}")

        return {"files": {}, "last_run": None}

    def _save_state(self) -> None:
        """Save state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self._state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def clear_state(self) -> None:
        """Clear the state (useful for forcing full regeneration)."""
        self._state = {"files": {}, "last_run": None}
        self._save_state()

    def get_documentation_stats(self) -> Dict:
        """Get statistics about the documentation state."""
        stats = {
            "total_files": len(self._state.get("files", {})),
            "last_run": self._state.get("last_run"),
            "oldest_documentation": None,
            "newest_documentation": None
        }

        if self._state.get("files"):
            dates = [f["last_documented"] for f in self._state["files"].values()
                    if "last_documented" in f]
            if dates:
                stats["oldest_documentation"] = min(dates)
                stats["newest_documentation"] = max(dates)

        return stats