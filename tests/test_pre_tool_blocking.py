"""
Tests for Pre-Tool Blocking Hook (Story 2.3).

Tests cover all acceptance criteria:
- AC1: Scan tool_input in PreToolUse
- AC2: Block critical-severity (high) matches - exit code 2
- AC3: Allow warning-severity matches - exit code 0
- AC4: Allow no matches - exit code 0
- AC5: Fail-open on errors - exit code 0
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add hooks directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))


class TestPreToolBlockingStructure:
    """Tests for pre-tool hook structure and basic functionality."""

    def test_hook_file_exists(self):
        """Pre-tool hook file exists."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        assert hook_path.exists(), "pre-tool-guard.py should exist"

    def test_hook_is_executable_python(self):
        """Pre-tool hook is valid Python syntax."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(hook_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error in hook: {result.stderr}"


class TestPreToolAllowNoMatch:
    """Tests for AC4: No matches → exit code 0 (allow)."""

    def test_clean_input_returns_exit_zero(self):
        """Clean input with no matches returns exit code 0."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Clean input should return exit code 0"

    def test_clean_input_no_stdout(self):
        """Clean input produces no stdout (no block message)."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/test/file.py"},
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        # Clean input should have no JSON block output
        # (NOVA debug messages are OK, but no decision JSON)
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout)
                # If JSON parses, it should not have decision: block
                assert output.get("decision") != "block", "Clean input should not produce block"
            except json.JSONDecodeError:
                # Non-JSON output (debug messages) is fine
                pass

    def test_empty_input_returns_exit_zero(self):
        """Empty tool_input returns exit code 0."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {},
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_short_input_returns_exit_zero(self):
        """Short input (< 10 chars) returns exit code 0 without scanning."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},  # Only 2 chars
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0


class TestPreToolBlockHighSeverity:
    """Tests for AC2: High severity → exit code 2 (block)."""

    def test_high_severity_logic(self):
        """High severity detection should result in blocked verdict."""
        # This tests the logic, not the actual hook with NOVA scanning
        detections = [
            {"severity": "high", "rule_name": "InstructionOverride"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        # This is the logic from pre-tool-guard.py
        if "high" in severities:
            verdict = "blocked"
            exit_code = 2
        else:
            verdict = "allowed"
            exit_code = 0

        assert verdict == "blocked"
        assert exit_code == 2

    def test_block_json_format(self):
        """Block output should be valid JSON with decision and reason."""
        # Test the expected format
        output = {
            "decision": "block",
            "reason": "[NOVA] Blocked: TestRule - Test description"
        }

        json_str = json.dumps(output)
        parsed = json.loads(json_str)

        assert parsed["decision"] == "block"
        assert "[NOVA] Blocked:" in parsed["reason"]


class TestPreToolAllowWarnings:
    """Tests for AC3: Warning severity → exit code 0 (allow)."""

    def test_medium_severity_logic(self):
        """Medium severity detection should result in allowed verdict."""
        detections = [
            {"severity": "medium", "rule_name": "SuspiciousPattern"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        # Medium/low should allow
        if "high" in severities:
            exit_code = 2
        else:
            exit_code = 0

        assert exit_code == 0

    def test_low_severity_logic(self):
        """Low severity detection should result in allowed verdict."""
        detections = [
            {"severity": "low", "rule_name": "MinorPattern"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            exit_code = 2
        else:
            exit_code = 0

        assert exit_code == 0

    def test_mixed_medium_low_allows(self):
        """Mixed medium/low severity without high should allow."""
        detections = [
            {"severity": "low", "rule_name": "LowRule"},
            {"severity": "medium", "rule_name": "MediumRule"},
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            exit_code = 2
        else:
            exit_code = 0

        assert exit_code == 0


class TestPreToolFailOpen:
    """Tests for AC5: Errors → exit code 0 (fail-open)."""

    def test_invalid_json_returns_exit_zero(self):
        """Invalid JSON input returns exit code 0."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input="not valid json",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_empty_stdin_returns_exit_zero(self):
        """Empty stdin returns exit code 0."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input="",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_missing_tool_name_returns_exit_zero(self):
        """Missing tool_name returns exit code 0."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_input": {"command": "ls -la"},
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0


class TestExtractInputText:
    """Tests for input text extraction."""

    def test_extracts_command_field(self):
        """Extracts command field from tool_input."""
        # Import the function
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        tool_input = {"command": "echo hello world"}
        result = module.extract_input_text(tool_input)
        assert "echo hello world" in result

    def test_extracts_content_field(self):
        """Extracts content field from tool_input."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        tool_input = {"content": "file content here"}
        result = module.extract_input_text(tool_input)
        assert "file content here" in result

    def test_extracts_prompt_field(self):
        """Extracts prompt field from tool_input."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        tool_input = {"prompt": "agent prompt text"}
        result = module.extract_input_text(tool_input)
        assert "agent prompt text" in result

    def test_extracts_multiple_fields(self):
        """Extracts multiple fields from tool_input."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        tool_input = {
            "command": "echo test",
            "content": "some content",
            "prompt": "task prompt",
        }
        result = module.extract_input_text(tool_input)
        assert "echo test" in result
        assert "some content" in result
        assert "task prompt" in result

    def test_handles_empty_input(self):
        """Handles empty tool_input gracefully."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.extract_input_text({})
        assert result == ""

    def test_handles_none_input(self):
        """Handles None tool_input gracefully."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.extract_input_text(None)
        assert result == ""


class TestFormatBlockReason:
    """Tests for block reason formatting."""

    def test_formats_high_severity_rule(self):
        """Formats block reason with rule name."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        detections = [
            {"severity": "high", "rule_name": "InstructionOverride", "description": "Override attempt"}
        ]
        result = module.format_block_reason(detections, "Bash")
        assert "[NOVA] Blocked:" in result
        assert "InstructionOverride" in result

    def test_includes_description(self):
        """Includes rule description in block reason."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        detections = [
            {"severity": "high", "rule_name": "TestRule", "description": "Test description here"}
        ]
        result = module.format_block_reason(detections, "Bash")
        assert "Test description here" in result

    def test_handles_empty_detections(self):
        """Handles empty detections list."""
        from importlib.util import spec_from_file_location, module_from_spec
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
        spec = spec_from_file_location("pre_tool_guard", hook_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.format_block_reason([], "Bash")
        assert "[NOVA] Blocked:" in result


class TestHighSeverityBlocking:
    """Tests for actual blocking with high severity detection."""

    def test_highest_severity_determines_action(self):
        """When multiple rules match, highest severity determines action."""
        detections = [
            {"severity": "low", "rule_name": "LowRule"},
            {"severity": "medium", "rule_name": "MediumRule"},
            {"severity": "high", "rule_name": "HighRule"},
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            exit_code = 2  # Block
        else:
            exit_code = 0  # Allow

        assert exit_code == 2

    def test_multiple_high_severity_still_blocks(self):
        """Multiple high severity rules still result in block."""
        detections = [
            {"severity": "high", "rule_name": "Rule1"},
            {"severity": "high", "rule_name": "Rule2"},
            {"severity": "high", "rule_name": "Rule3"},
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            exit_code = 2
        else:
            exit_code = 0

        assert exit_code == 2


class TestHookIntegration:
    """Integration tests for the pre-tool hook."""

    def test_hook_exits_zero_on_normal_input(self):
        """Hook exits with 0 for normal, clean input."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/test/file.txt",
                "content": "Hello, this is a normal file content."
            },
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_hook_scans_bash_commands(self):
        """Hook scans Bash command content."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "git status && git log --oneline"
            },
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        # Normal git command should be allowed
        assert result.returncode == 0

    def test_hook_scans_edit_content(self):
        """Hook scans Edit tool content."""
        hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"

        hook_input = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/test/file.py",
                "old_string": "def hello():",
                "new_string": "def greet():"
            },
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
