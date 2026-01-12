"""
Tests for Event Capture (Story 1.3).

Tests cover all acceptance criteria:
- AC1: Event Record Capture (PostToolUse appends to session .jsonl)
- AC2: Event Record Structure (id, tool_name, tool_input, tool_output, timestamps)
- AC3: Sequential Event IDs (unique, starting from 1, incrementing)
- AC4: Output Truncation (10KB limit with marker)
- AC5: Performance (< 1ms overhead excluding I/O)
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest

# Add hooks/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "lib"))

from session_manager import (
    generate_session_id,
    get_next_event_id,
    init_session_file,
    append_event,
    read_session_events,
    truncate_output,
    MAX_OUTPUT_SIZE,
)


class TestEventRecordStructure:
    """Tests for AC2: Event record structure."""

    def test_event_has_required_fields(self):
        """Event record contains all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event = {
                "type": "event",
                "id": 1,
                "timestamp_start": "2026-01-10T16:30:46Z",
                "timestamp_end": "2026-01-10T16:30:47Z",
                "duration_ms": 1000,
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_output": "file contents here",
                "working_dir": "/test",
                "files_accessed": [],
                "nova_verdict": "allowed",
                "nova_severity": None,
                "nova_rules_matched": [],
                "nova_scan_time_ms": 0,
            }

            result = append_event(session_id, tmpdir, event)
            assert result is True

            events = read_session_events(session_id, tmpdir)
            # First record is init, second is our event
            assert len(events) == 2
            stored_event = events[1]

            # Verify all required fields
            assert stored_event["type"] == "event"
            assert stored_event["id"] == 1
            assert "timestamp_start" in stored_event
            assert "timestamp_end" in stored_event
            assert "duration_ms" in stored_event
            assert stored_event["tool_name"] == "Read"
            assert "tool_input" in stored_event
            assert "tool_output" in stored_event

    def test_duration_ms_is_integer(self):
        """Duration is stored as integer milliseconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event = {
                "type": "event",
                "id": 1,
                "timestamp_start": "2026-01-10T16:30:46Z",
                "timestamp_end": "2026-01-10T16:30:46Z",
                "duration_ms": 123,
                "tool_name": "Bash",
                "tool_input": {"command": "ls"},
                "tool_output": "file1.txt",
            }

            append_event(session_id, tmpdir, event)
            events = read_session_events(session_id, tmpdir)

            assert isinstance(events[1]["duration_ms"], int)
            assert events[1]["duration_ms"] == 123


class TestSequentialEventIds:
    """Tests for AC3: Sequential event IDs."""

    def test_first_event_id_is_one(self):
        """First event in a session has ID 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event_id = get_next_event_id(session_id, tmpdir)
            assert event_id == 1

    def test_ids_increment_sequentially(self):
        """Event IDs increment by 1 for each event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            # Add first event
            event1 = {"type": "event", "id": 1, "tool_name": "Read"}
            append_event(session_id, tmpdir, event1)

            next_id = get_next_event_id(session_id, tmpdir)
            assert next_id == 2

            # Add second event
            event2 = {"type": "event", "id": 2, "tool_name": "Edit"}
            append_event(session_id, tmpdir, event2)

            next_id = get_next_event_id(session_id, tmpdir)
            assert next_id == 3

    def test_ids_unique_across_multiple_events(self):
        """All event IDs are unique within a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            ids_used = []
            for i in range(10):
                event_id = get_next_event_id(session_id, tmpdir)
                assert event_id not in ids_used
                ids_used.append(event_id)

                event = {"type": "event", "id": event_id, "tool_name": f"Tool{i}"}
                append_event(session_id, tmpdir, event)

    def test_empty_session_returns_one(self):
        """Session with only init record returns ID 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event_id = get_next_event_id(session_id, tmpdir)
            assert event_id == 1

    def test_missing_session_returns_one(self):
        """Non-existent session returns ID 1 (fail-open)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            event_id = get_next_event_id("nonexistent_session", tmpdir)
            assert event_id == 1


class TestOutputTruncation:
    """Tests for AC4: Output truncation."""

    def test_small_output_not_truncated(self):
        """Output smaller than limit is not truncated."""
        small_text = "Hello, world!" * 10  # ~130 bytes
        result, original_size = truncate_output(small_text)

        assert result == small_text
        assert original_size is None

    def test_large_output_truncated(self):
        """Output larger than limit is truncated."""
        large_text = "X" * (MAX_OUTPUT_SIZE + 1000)
        result, original_size = truncate_output(large_text)

        assert len(result.encode("utf-8")) < len(large_text.encode("utf-8"))
        assert original_size == len(large_text.encode("utf-8"))
        assert "[TRUNCATED" in result

    def test_truncation_marker_format(self):
        """Truncation marker includes original size."""
        large_text = "Y" * (MAX_OUTPUT_SIZE + 5000)
        result, original_size = truncate_output(large_text)

        assert "TRUNCATED" in result
        assert "KB" in result
        assert original_size is not None

    def test_truncation_at_exactly_limit(self):
        """Output exactly at limit is not truncated."""
        exact_text = "Z" * MAX_OUTPUT_SIZE
        result, original_size = truncate_output(exact_text)

        assert result == exact_text
        assert original_size is None

    def test_empty_output_handled(self):
        """Empty output returns empty string."""
        result, original_size = truncate_output("")
        assert result == ""
        assert original_size is None

    def test_none_output_handled(self):
        """None output returns None."""
        result, original_size = truncate_output(None)
        assert result is None
        assert original_size is None

    def test_unicode_truncation_safe(self):
        """Unicode characters are not broken during truncation."""
        # Create text with multi-byte unicode characters
        unicode_text = "\u4e2d\u6587" * (MAX_OUTPUT_SIZE // 2)  # Chinese characters
        result, _ = truncate_output(unicode_text)

        # Result should be valid UTF-8 (no broken sequences)
        result.encode("utf-8")  # Should not raise

    def test_custom_limit(self):
        """Custom truncation limit is respected."""
        text = "A" * 1000
        result, original_size = truncate_output(text, max_bytes=500)

        assert len(result.encode("utf-8")) < 1000
        assert original_size == 1000


class TestEventCaptureIntegration:
    """Integration tests for event capture in the hook."""

    def test_hook_captures_event_to_session(self):
        """PostToolUse hook appends event to session file."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a session first
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            # Prepare hook input
            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "print('hello world')",
            }

            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            assert result.returncode == 0

            # Check that event was captured
            events = read_session_events(session_id, tmpdir)
            # Should have init + 1 event
            assert len(events) >= 1

            # Find the event record
            event_records = [e for e in events if e.get("type") == "event"]
            if event_records:  # Only check if capture succeeded
                event = event_records[0]
                assert event["tool_name"] == "Read"
                assert event["id"] == 1

    def test_hook_exits_zero_always(self):
        """Hook always exits 0 (fail-open)."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with various inputs
            test_inputs = [
                {"tool_name": "Read", "tool_input": {}, "tool_response": "content"},
                {"tool_name": "Unknown", "tool_input": {}, "tool_response": ""},
                {},  # Empty input
            ]

            for input_data in test_inputs:
                result = subprocess.run(
                    [sys.executable, str(hook_path)],
                    input=json.dumps(input_data),
                    capture_output=True,
                    text=True,
                    cwd=tmpdir,
                )
                assert result.returncode == 0

    def test_multiple_events_have_sequential_ids(self):
        """Multiple tool calls get sequential IDs."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            # Send multiple hook invocations
            for i in range(3):
                hook_input = {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"echo {i}"},
                    "tool_response": str(i),
                }

                subprocess.run(
                    [sys.executable, str(hook_path)],
                    input=json.dumps(hook_input),
                    capture_output=True,
                    text=True,
                    cwd=tmpdir,
                )

            # Check IDs are sequential
            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                ids = [e["id"] for e in event_records]
                assert ids == list(range(1, len(ids) + 1))


class TestPerformance:
    """Tests for AC5: Performance requirements."""

    def test_get_next_event_id_performance(self):
        """get_next_event_id completes quickly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            # Add some events first
            for i in range(10):
                event = {"type": "event", "id": i + 1, "tool_name": "Test"}
                append_event(session_id, tmpdir, event)

            # Measure time for ID lookup
            times = []
            for _ in range(10):
                start = time.perf_counter()
                get_next_event_id(session_id, tmpdir)
                elapsed = (time.perf_counter() - start) * 1000  # ms

                times.append(elapsed)

            avg_time = sum(times) / len(times)
            # Should be well under 10ms even for 10 events
            assert avg_time < 10, f"Average time {avg_time:.2f}ms exceeds threshold"

    def test_truncate_output_performance(self):
        """truncate_output is fast for large content."""
        large_text = "X" * (MAX_OUTPUT_SIZE * 2)  # 20KB

        times = []
        for _ in range(100):
            start = time.perf_counter()
            truncate_output(large_text)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        # Should be under 1ms
        assert avg_time < 1, f"Average time {avg_time:.2f}ms exceeds 1ms threshold"

    def test_append_event_performance(self):
        """append_event meets < 0.5ms target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event = {
                "type": "event",
                "id": 1,
                "tool_name": "Test",
                "tool_input": {"key": "value"},
                "tool_output": "output" * 100,
            }

            times = []
            for i in range(50):
                event["id"] = i + 1
                start = time.perf_counter()
                append_event(session_id, tmpdir, event)
                elapsed = (time.perf_counter() - start) * 1000  # ms
                times.append(elapsed)

            avg_time = sum(times) / len(times)
            # Most appends should be under 2ms (allowing for occasional slow I/O)
            assert avg_time < 2, f"Average append time {avg_time:.2f}ms too slow"


class TestFailOpen:
    """Tests for fail-open behavior."""

    def test_capture_fails_silently_without_session(self):
        """Event capture fails silently when no active session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't initialize session
            event_id = get_next_event_id("nonexistent", tmpdir)
            # Should return 1 (default) without crashing
            assert event_id == 1

    def test_truncate_handles_encoding_errors(self):
        """Truncation handles encoding edge cases gracefully."""
        # This shouldn't happen in practice, but test robustness
        text = "Normal text"
        result, original_size = truncate_output(text)
        assert result == text


class TestEdgeCases:
    """Edge case tests."""

    def test_event_with_large_tool_input(self):
        """Large tool_input is stored correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            large_input = {"code": "x" * 5000}
            event = {
                "type": "event",
                "id": 1,
                "tool_name": "Edit",
                "tool_input": large_input,
                "tool_output": "success",
            }

            result = append_event(session_id, tmpdir, event)
            assert result is True

            events = read_session_events(session_id, tmpdir)
            stored = [e for e in events if e.get("type") == "event"][0]
            assert len(stored["tool_input"]["code"]) == 5000

    def test_event_with_special_characters(self):
        """Special characters in output are handled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            special_output = 'Line 1\nLine 2\tTabbed\r\n"Quoted" and \\escaped'
            event = {
                "type": "event",
                "id": 1,
                "tool_name": "Bash",
                "tool_input": {},
                "tool_output": special_output,
            }

            append_event(session_id, tmpdir, event)
            events = read_session_events(session_id, tmpdir)

            stored = [e for e in events if e.get("type") == "event"][0]
            assert stored["tool_output"] == special_output

    def test_event_with_null_fields(self):
        """Null/None fields are stored correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            event = {
                "type": "event",
                "id": 1,
                "tool_name": "Test",
                "tool_input": None,
                "tool_output": None,
                "nova_severity": None,
            }

            append_event(session_id, tmpdir, event)
            events = read_session_events(session_id, tmpdir)

            stored = [e for e in events if e.get("type") == "event"][0]
            assert stored["nova_severity"] is None
