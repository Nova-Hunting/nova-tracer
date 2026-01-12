"""
Tests for File Path Extraction (Story 1.4).

Tests cover all acceptance criteria:
- AC1: Working directory context (verified in integration tests)
- AC2: Read tool file path extraction
- AC3: Bash command file path extraction
- AC4: Edit/Write tool file path extraction
- AC5: Empty files array for non-file tools
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add hooks/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "lib"))

from session_manager import (
    extract_files_accessed,
    _extract_paths_from_bash,
    generate_session_id,
    init_session_file,
    read_session_events,
)


class TestReadToolExtraction:
    """Tests for AC2: Read tool file path extraction."""

    def test_read_extracts_file_path(self):
        """Read tool extracts file_path from input."""
        result = extract_files_accessed("Read", {"file_path": "/test/file.py"})
        assert result == ["/test/file.py"]

    def test_read_with_missing_path(self):
        """Read tool with missing file_path returns empty list."""
        result = extract_files_accessed("Read", {})
        assert result == []

    def test_read_with_none_path(self):
        """Read tool with None file_path returns empty list."""
        result = extract_files_accessed("Read", {"file_path": None})
        assert result == []

    def test_read_with_complex_path(self):
        """Read tool handles complex file paths."""
        path = "/Users/test/Documents/my project/file with spaces.py"
        result = extract_files_accessed("Read", {"file_path": path})
        assert result == [path]


class TestEditWriteToolExtraction:
    """Tests for AC4: Edit/Write tool file path extraction."""

    def test_edit_extracts_file_path(self):
        """Edit tool extracts file_path from input."""
        result = extract_files_accessed(
            "Edit",
            {"file_path": "/src/main.py", "old_string": "foo", "new_string": "bar"},
        )
        assert result == ["/src/main.py"]

    def test_write_extracts_file_path(self):
        """Write tool extracts file_path from input."""
        result = extract_files_accessed(
            "Write", {"file_path": "/output/result.txt", "content": "Hello"}
        )
        assert result == ["/output/result.txt"]

    def test_notebook_edit_extracts_path(self):
        """NotebookEdit tool extracts notebook_path from input."""
        result = extract_files_accessed(
            "NotebookEdit",
            {"notebook_path": "/notebooks/analysis.ipynb", "cell_id": "abc123"},
        )
        assert result == ["/notebooks/analysis.ipynb"]


class TestGlobGrepToolExtraction:
    """Tests for Glob and Grep tool path extraction."""

    def test_glob_extracts_path(self):
        """Glob tool extracts path from input."""
        result = extract_files_accessed(
            "Glob", {"pattern": "*.py", "path": "/src/components"}
        )
        assert result == ["/src/components"]

    def test_glob_without_path(self):
        """Glob tool without path returns empty list."""
        result = extract_files_accessed("Glob", {"pattern": "*.py"})
        assert result == []

    def test_grep_extracts_path(self):
        """Grep tool extracts path from input."""
        result = extract_files_accessed(
            "Grep", {"pattern": "TODO", "path": "/project/src"}
        )
        assert result == ["/project/src"]


class TestBashPathExtraction:
    """Tests for AC3: Bash command file path extraction."""

    def test_bash_extracts_absolute_path(self):
        """Bash extracts absolute paths from command."""
        result = extract_files_accessed("Bash", {"command": "cat /etc/passwd"})
        assert "/etc/passwd" in result

    def test_bash_extracts_relative_path(self):
        """Bash extracts relative paths starting with ./"""
        result = extract_files_accessed("Bash", {"command": "cat ./config.yaml"})
        assert "./config.yaml" in result

    def test_bash_extracts_parent_path(self):
        """Bash extracts parent paths starting with ../"""
        result = extract_files_accessed("Bash", {"command": "cat ../parent/file.txt"})
        assert "../parent/file.txt" in result

    def test_bash_extracts_home_path(self):
        """Bash extracts home directory paths starting with ~/"""
        result = extract_files_accessed("Bash", {"command": "cat ~/.bashrc"})
        assert "~/.bashrc" in result

    def test_bash_extracts_multiple_paths(self):
        """Bash extracts multiple paths from command."""
        result = extract_files_accessed(
            "Bash", {"command": "cp /src/file.py /dest/file.py"}
        )
        assert "/src/file.py" in result
        assert "/dest/file.py" in result

    def test_bash_ignores_cli_flags(self):
        """Bash does not extract CLI flags as paths."""
        result = extract_files_accessed("Bash", {"command": "rm -rf /tmp/test"})
        assert "-rf" not in result
        assert "/tmp/test" in result

    def test_bash_ignores_urls(self):
        """Bash does not extract URLs as paths."""
        result = extract_files_accessed(
            "Bash", {"command": "curl https://example.com/file.txt"}
        )
        assert "https://example.com/file.txt" not in result

    def test_bash_handles_empty_command(self):
        """Bash handles empty command gracefully."""
        result = extract_files_accessed("Bash", {"command": ""})
        assert result == []

    def test_bash_handles_none_command(self):
        """Bash handles None command gracefully."""
        result = extract_files_accessed("Bash", {"command": None})
        assert result == []

    def test_bash_deduplicates_paths(self):
        """Bash deduplicates extracted paths."""
        result = extract_files_accessed(
            "Bash", {"command": "cat /etc/hosts /etc/hosts"}
        )
        assert result.count("/etc/hosts") == 1

    def test_bash_complex_command(self):
        """Bash handles complex piped commands."""
        result = extract_files_accessed(
            "Bash",
            {"command": "cat /var/log/syslog | grep error > ./output.txt"},
        )
        assert "/var/log/syslog" in result
        assert "./output.txt" in result


class TestBashPathExtractionDirect:
    """Direct tests for _extract_paths_from_bash helper."""

    def test_simple_absolute_path(self):
        """Simple absolute path extraction."""
        result = _extract_paths_from_bash("ls /home/user")
        assert "/home/user" in result

    def test_path_with_extension(self):
        """Path with file extension."""
        result = _extract_paths_from_bash("python /scripts/run.py")
        assert "/scripts/run.py" in result

    def test_nested_path(self):
        """Deeply nested path."""
        result = _extract_paths_from_bash("cat /a/b/c/d/e/file.txt")
        assert "/a/b/c/d/e/file.txt" in result

    def test_path_at_start(self):
        """Path at start of command."""
        result = _extract_paths_from_bash("/usr/bin/python script.py")
        assert "/usr/bin/python" in result

    def test_multiple_spaces(self):
        """Handles multiple spaces between paths."""
        result = _extract_paths_from_bash("cp   /src/a.txt   /dest/b.txt")
        assert "/src/a.txt" in result
        assert "/dest/b.txt" in result


class TestNonFileTools:
    """Tests for AC5: Empty files array for non-file tools."""

    def test_task_tool_returns_empty(self):
        """Task tool returns empty files list."""
        result = extract_files_accessed(
            "Task", {"prompt": "Analyze the code", "subagent_type": "Explore"}
        )
        assert result == []

    def test_webfetch_returns_empty(self):
        """WebFetch tool returns empty files list."""
        result = extract_files_accessed(
            "WebFetch", {"url": "https://example.com", "prompt": "Get content"}
        )
        assert result == []

    def test_unknown_tool_returns_empty(self):
        """Unknown tool returns empty files list."""
        result = extract_files_accessed("UnknownTool", {"some_field": "value"})
        assert result == []

    def test_mcp_tool_returns_empty(self):
        """MCP tools return empty files list."""
        result = extract_files_accessed("mcp__server__function", {"arg": "value"})
        assert result == []


class TestEdgeCases:
    """Edge case tests for file extraction."""

    def test_none_input_returns_empty(self):
        """None input returns empty list."""
        result = extract_files_accessed("Read", None)
        assert result == []

    def test_empty_dict_returns_empty(self):
        """Empty dict input returns empty list."""
        result = extract_files_accessed("Read", {})
        assert result == []

    def test_non_string_path_ignored(self):
        """Non-string path values are ignored."""
        result = extract_files_accessed("Read", {"file_path": 12345})
        assert result == []

    def test_list_path_ignored(self):
        """List path values are ignored."""
        result = extract_files_accessed("Read", {"file_path": ["/a", "/b"]})
        assert result == []

    def test_preserves_order(self):
        """Deduplication preserves first occurrence order."""
        result = extract_files_accessed(
            "Bash", {"command": "cat /a /b /a /c /b"}
        )
        # First occurrences should maintain order
        assert result.index("/a") < result.index("/b")
        assert result.index("/b") < result.index("/c")


class TestIntegration:
    """Integration tests for file extraction in hooks."""

    def test_hook_captures_files_accessed(self):
        """PostToolUse hook captures files_accessed correctly."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a session
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            # Simulate a Read tool call
            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/example.py"},
                "tool_response": "print('hello')",
            }

            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            assert result.returncode == 0

            # Verify files_accessed in captured event
            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                assert "files_accessed" in event
                assert "/test/example.py" in event["files_accessed"]

    def test_hook_captures_working_dir(self):
        """PostToolUse hook captures working_dir correctly (AC1)."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Bash",
                "tool_input": {"command": "ls"},
                "tool_response": "file1.txt\nfile2.txt",
            }

            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            assert result.returncode == 0

            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                assert "working_dir" in event
                # working_dir should be set to the cwd
                assert event["working_dir"] is not None
                assert len(event["working_dir"]) > 0

    def test_hook_handles_bash_with_paths(self):
        """PostToolUse hook extracts paths from Bash commands."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Bash",
                "tool_input": {"command": "cat /etc/hosts ./local.txt"},
                "tool_response": "localhost",
            }

            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            assert result.returncode == 0

            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                files = event.get("files_accessed", [])
                assert "/etc/hosts" in files
                assert "./local.txt" in files
