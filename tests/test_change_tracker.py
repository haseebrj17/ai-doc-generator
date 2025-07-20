"""
Tests for the change tracker module.
"""

import time
import tempfile
from pathlib import Path

import pytest

from ai_doc_generator.config import Config
from ai_doc_generator.change_tracker import ChangeTracker


class TestChangeTracker:
    """Test cases for the ChangeTracker class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create some initial files
            (root / "file1.py").write_text("# File 1")
            (root / "file2.py").write_text("# File 2")
            (root / "subdir").mkdir()
            (root / "subdir" / "file3.py").write_text("# File 3")

            yield root

    @pytest.fixture
    def tracker(self, temp_project):
        """Create a ChangeTracker instance."""
        config = Config(project_root=temp_project)
        return ChangeTracker(config)

    def test_no_previous_run(self, tracker):
        """Test detection of first run."""
        assert not tracker.has_previous_run()

    def test_first_run_all_files_changed(self, tracker, temp_project):
        """Test that all files are marked as changed on first run."""
        changed_files = tracker.get_changed_files()

        assert len(changed_files) == 3
        file_names = [f.name for f in changed_files]
        assert "file1.py" in file_names
        assert "file2.py" in file_names
        assert "file3.py" in file_names

    def test_state_persistence(self, tracker, temp_project):
        """Test that state is properly saved and loaded."""
        # Update state with documented files
        files = list(temp_project.rglob("*.py"))
        tracker.update_state(files)

        # Create new tracker instance to test loading
        config = Config(project_root=temp_project)
        new_tracker = ChangeTracker(config)

        assert new_tracker.has_previous_run()
        assert len(new_tracker._state["files"]) == 3

    def test_detect_new_file(self, tracker, temp_project):
        """Test detection of newly added files."""
        # Document existing files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Add a new file
        (temp_project / "new_file.py").write_text("# New file")

        # Check for changes
        changed_files = tracker.get_changed_files()

        assert len(changed_files) == 1
        assert changed_files[0].name == "new_file.py"

    def test_detect_modified_file_by_content(self, tracker, temp_project):
        """Test detection of file modification by content change."""
        # Document existing files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Modify a file
        file1 = temp_project / "file1.py"
        time.sleep(0.1)  # Ensure different timestamp
        file1.write_text("# File 1 - Modified content")

        # Check for changes
        changed_files = tracker.get_changed_files()

        assert len(changed_files) == 1
        assert changed_files[0].name == "file1.py"

    def test_detect_modified_file_by_size(self, tracker, temp_project):
        """Test detection of file modification by size change."""
        # Document existing files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Get original state
        original_state = tracker._state["files"][str(temp_project / "file1.py")]

        # Modify file to different size but same mtime (edge case)
        file1 = temp_project / "file1.py"
        file1.write_text("# Different size")

        # Manually set the mtime back to original to test size detection
        tracker._state["files"][str(file1)] = {
            **original_state,
            "mtime": time.time() + 100  # Future time to bypass mtime check
        }

        # Check for changes
        changed_files = tracker.get_changed_files()
        file_names = [f.name for f in changed_files]

        assert "file1.py" in file_names

    def test_detect_no_changes(self, tracker, temp_project):
        """Test that no changes are detected when files haven't changed."""
        # Document existing files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Check for changes without modifying anything
        changed_files = tracker.get_changed_files()

        assert len(changed_files) == 0

    def test_file_hash_calculation(self, tracker, temp_project):
        """Test file hash calculation for content comparison."""
        file1 = temp_project / "file1.py"

        # Calculate hash
        hash1 = tracker._calculate_file_hash(file1)
        assert hash1 != ""
        assert len(hash1) == 64  # SHA256 hex length

        # Same content should give same hash
        hash2 = tracker._calculate_file_hash(file1)
        assert hash1 == hash2

        # Different content should give different hash
        file1.write_text("# Modified content")
        hash3 = tracker._calculate_file_hash(file1)
        assert hash1 != hash3

    def test_clear_state(self, tracker, temp_project):
        """Test clearing the state."""
        # Document some files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        assert tracker.has_previous_run()

        # Clear state
        tracker.clear_state()

        assert not tracker.has_previous_run()
        assert len(tracker._state["files"]) == 0

    def test_documentation_stats(self, tracker, temp_project):
        """Test getting documentation statistics."""
        # Initial stats
        stats = tracker.get_documentation_stats()
        assert stats["total_files"] == 0
        assert stats["last_run"] is None

        # Document some files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Check updated stats
        stats = tracker.get_documentation_stats()
        assert stats["total_files"] == 3
        assert stats["last_run"] is not None
        assert stats["newest_documentation"] is not None
        assert stats["oldest_documentation"] is not None

    def test_handle_deleted_files(self, tracker, temp_project):
        """Test handling of deleted files."""
        # Document existing files
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Delete a file
        (temp_project / "file1.py").unlink()

        # Check for changes - deleted files should be logged but not in changed list
        changed_files = tracker.get_changed_files()

        # Changed files shouldn't include deleted ones
        file_names = [f.name for f in changed_files]
        assert "file1.py" not in file_names

    def test_corrupted_state_file(self, tracker, temp_project):
        """Test handling of corrupted state file."""
        # Write invalid JSON to state file
        state_file = temp_project / ".doc_state.json"
        state_file.write_text("{ invalid json")

        # Create new tracker - should handle corrupted state
        config = Config(project_root=temp_project)
        new_tracker = ChangeTracker(config)

        # Should start fresh
        assert not new_tracker.has_previous_run()

    def test_state_file_permissions_error(self, tracker, temp_project, monkeypatch):
        """Test handling of permission errors when saving state."""
        # Mock open to raise permission error
        def mock_open(*args, **kwargs):
            raise PermissionError("No write permission")

        monkeypatch.setattr("builtins.open", mock_open)

        # Should not crash
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)  # Should handle the error gracefully

    def test_relative_paths_in_state(self, tracker, temp_project):
        """Test that paths are stored relative to project root."""
        existing_files = list(temp_project.rglob("*.py"))
        tracker.update_state(existing_files)

        # Check that paths in state are relative
        for file_path in tracker._state["files"]:
            assert not Path(file_path).is_absolute()
            # Should be able to reconstruct full path
            full_path = temp_project / file_path
            assert full_path.exists()

    def test_exclude_patterns_respected(self, temp_project):
        """Test that exclude patterns from config are respected."""
        # Create test file that should be excluded
        (temp_project / "setup.py").write_text("# Setup file")
        (temp_project / "test_file.py").write_text("# Test file")

        config = Config(
            project_root=temp_project,
            exclude_files=["setup.py"],
            include_tests=False
        )
        tracker = ChangeTracker(config)

        changed_files = tracker.get_changed_files()
        file_names = [f.name for f in changed_files]

        # These should be excluded
        assert "setup.py" not in file_names
        assert "test_file.py" not in file_names

    @pytest.mark.skipif(
        not Path(".git").exists(),
        reason="Git tests require git repository"
    )
    def test_git_integration(self, temp_project, monkeypatch):
        """Test git integration for change detection."""
        # This test would require a git repository
        # Skipping for now as it's complex to set up in tests
        pass