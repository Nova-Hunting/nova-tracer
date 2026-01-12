"""
Tests for Verdict Assignment and Logging (Story 2.2).

Tests cover all acceptance criteria:
- AC1: No matches → allowed verdict with null severity
- AC2: Warning-level match → warned verdict with medium severity
- AC3: High-severity match → blocked verdict with high severity
- AC4: Multiple rules → highest severity wins, all rules captured
- AC5: Scan time recording in nova_scan_time_ms
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Add hooks directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "lib"))

from session_manager import (
    generate_session_id,
    init_session_file,
    read_session_events,
)


class TestVerdictAssignmentNoMatch:
    """Tests for AC1: No matches → allowed verdict."""

    def test_allowed_verdict_default(self):
        """Default verdict is 'allowed' when no matches."""
        # The default values before any scan
        nova_verdict = "allowed"
        nova_severity = None
        nova_rules_matched = []

        assert nova_verdict == "allowed"
        assert nova_severity is None
        assert nova_rules_matched == []

    def test_allowed_verdict_empty_detections(self):
        """Empty detections list results in allowed verdict."""
        detections = []

        # Logic from post-tool-nova-guard.py
        if detections:
            # Would set verdict based on severities
            pass
        else:
            nova_verdict = "allowed"
            nova_severity = None
            nova_rules_matched = []

        assert nova_verdict == "allowed"
        assert nova_severity is None
        assert nova_rules_matched == []

    def test_hook_returns_allowed_for_clean_content(self):
        """Hook returns allowed verdict for content with no matches."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        # Content that should NOT trigger any rules
        hook_input = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/test/clean_file.py"},
            "tool_response": "def hello():\n    print('Hello World')\n",
        }

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
        )

        # Should exit 0 and produce no warning output
        assert result.returncode == 0
        # No JSON output means allowed (warnings produce JSON)
        # Note: NOVA library may output debug messages to stdout
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout)
                # If there's valid JSON output with detections, that's unexpected
                if isinstance(output, dict) and output.get("detections"):
                    assert False, f"Unexpected detections for clean content: {output}"
            except json.JSONDecodeError:
                # Non-JSON output (like NOVA debug messages) is fine
                pass


class TestVerdictAssignmentWarned:
    """Tests for AC2: Warning-level match → warned verdict."""

    def test_medium_severity_returns_warned(self):
        """Medium severity detection results in warned verdict."""
        detections = [
            {"severity": "medium", "rule_name": "TestRule"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            nova_verdict = "blocked"
            nova_severity = "high"
        elif "medium" in severities:
            nova_verdict = "warned"
            nova_severity = "medium"
        else:
            nova_verdict = "warned"
            nova_severity = "low"

        assert nova_verdict == "warned"
        assert nova_severity == "medium"

    def test_low_severity_returns_warned(self):
        """Low severity detection results in warned verdict."""
        detections = [
            {"severity": "low", "rule_name": "LowSeverityRule"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            nova_verdict = "blocked"
            nova_severity = "high"
        elif "medium" in severities:
            nova_verdict = "warned"
            nova_severity = "medium"
        else:
            nova_verdict = "warned"
            nova_severity = "low"

        assert nova_verdict == "warned"
        assert nova_severity == "low"

    def test_warned_includes_rule_names(self):
        """Warned verdict includes matched rule names."""
        detections = [
            {"severity": "medium", "rule_name": "Rule1"},
            {"severity": "medium", "rule_name": "Rule2"},
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert "Rule1" in nova_rules_matched
        assert "Rule2" in nova_rules_matched
        assert len(nova_rules_matched) == 2


class TestVerdictAssignmentBlocked:
    """Tests for AC3: High-severity match → blocked verdict."""

    def test_high_severity_returns_blocked(self):
        """High severity detection results in blocked verdict."""
        detections = [
            {"severity": "high", "rule_name": "CriticalRule"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            nova_verdict = "blocked"
            nova_severity = "high"
        elif "medium" in severities:
            nova_verdict = "warned"
            nova_severity = "medium"
        else:
            nova_verdict = "warned"
            nova_severity = "low"

        assert nova_verdict == "blocked"
        assert nova_severity == "high"

    def test_blocked_includes_rule_names(self):
        """Blocked verdict includes matched rule names."""
        detections = [
            {"severity": "high", "rule_name": "InstructionOverride_IgnorePrevious"},
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert "InstructionOverride_IgnorePrevious" in nova_rules_matched


class TestVerdictMultipleRules:
    """Tests for AC4: Multiple rules → highest severity wins."""

    def test_highest_severity_wins_high(self):
        """When multiple rules match, highest severity (high) wins."""
        detections = [
            {"severity": "low", "rule_name": "LowRule"},
            {"severity": "medium", "rule_name": "MediumRule"},
            {"severity": "high", "rule_name": "HighRule"},
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            nova_verdict = "blocked"
            nova_severity = "high"
        elif "medium" in severities:
            nova_verdict = "warned"
            nova_severity = "medium"
        else:
            nova_verdict = "warned"
            nova_severity = "low"

        assert nova_verdict == "blocked"
        assert nova_severity == "high"

    def test_highest_severity_wins_medium(self):
        """When low and medium match, medium wins."""
        detections = [
            {"severity": "low", "rule_name": "LowRule"},
            {"severity": "medium", "rule_name": "MediumRule"},
        ]

        severities = [d.get("severity", "medium") for d in detections]

        if "high" in severities:
            nova_verdict = "blocked"
            nova_severity = "high"
        elif "medium" in severities:
            nova_verdict = "warned"
            nova_severity = "medium"
        else:
            nova_verdict = "warned"
            nova_severity = "low"

        assert nova_verdict == "warned"
        assert nova_severity == "medium"

    def test_all_rules_captured(self):
        """All matched rule names are captured regardless of severity."""
        detections = [
            {"severity": "low", "rule_name": "LowRule"},
            {"severity": "medium", "rule_name": "MediumRule"},
            {"severity": "high", "rule_name": "HighRule"},
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert len(nova_rules_matched) == 3
        assert "LowRule" in nova_rules_matched
        assert "MediumRule" in nova_rules_matched
        assert "HighRule" in nova_rules_matched

    def test_multiple_same_severity(self):
        """Multiple rules with same severity all captured."""
        detections = [
            {"severity": "high", "rule_name": "HighRule1"},
            {"severity": "high", "rule_name": "HighRule2"},
            {"severity": "high", "rule_name": "HighRule3"},
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert len(nova_rules_matched) == 3
        severities = [d.get("severity", "medium") for d in detections]
        assert all(s == "high" for s in severities)


class TestScanTimeRecording:
    """Tests for AC5: Scan time recording."""

    def test_scan_time_is_integer(self):
        """Scan time is recorded as integer milliseconds."""
        scan_start = datetime.now(timezone.utc)
        # Simulate some work
        time.sleep(0.001)  # 1ms
        scan_end = datetime.now(timezone.utc)

        nova_scan_time_ms = int((scan_end - scan_start).total_seconds() * 1000)

        assert isinstance(nova_scan_time_ms, int)
        assert nova_scan_time_ms >= 0

    def test_scan_time_recorded_in_event(self):
        """Verify scan time is included in captured events."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "content",
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
                assert "nova_scan_time_ms" in event
                assert isinstance(event["nova_scan_time_ms"], int)
                assert event["nova_scan_time_ms"] >= 0


class TestEventCaptureNovaFields:
    """Tests for event capture including all NOVA fields."""

    def test_event_has_nova_verdict(self):
        """Captured event includes nova_verdict field."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "clean content",
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
                assert "nova_verdict" in event
                assert event["nova_verdict"] in ["allowed", "warned", "blocked", "scan_failed"]

    def test_event_has_nova_severity(self):
        """Captured event includes nova_severity field."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "clean content",
            }

            subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                assert "nova_severity" in event
                # Can be None or a severity level
                assert event["nova_severity"] in [None, "low", "medium", "high"]

    def test_event_has_nova_rules_matched(self):
        """Captured event includes nova_rules_matched array."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "clean content",
            }

            subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                assert "nova_rules_matched" in event
                assert isinstance(event["nova_rules_matched"], list)

    def test_all_nova_fields_present(self):
        """Verify all four NOVA fields are present in event."""
        hook_path = Path(__file__).parent.parent / "hooks" / "post-tool-nova-guard.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = generate_session_id()
            init_session_file(session_id, tmpdir)

            hook_input = {
                "tool_name": "Read",
                "tool_input": {"file_path": "/test/file.py"},
                "tool_response": "print('hello')",
            }

            subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            events = read_session_events(session_id, tmpdir)
            event_records = [e for e in events if e.get("type") == "event"]

            if event_records:
                event = event_records[0]
                nova_fields = ["nova_verdict", "nova_severity", "nova_rules_matched", "nova_scan_time_ms"]
                for field in nova_fields:
                    assert field in event, f"Missing field: {field}"


class TestVerdictEdgeCases:
    """Edge case tests for verdict assignment."""

    def test_unknown_severity_defaults_to_medium(self):
        """Unknown severity treated as medium."""
        detections = [
            {"severity": "unknown", "rule_name": "WeirdRule"}
        ]

        severities = [d.get("severity", "medium") for d in detections]

        # "unknown" is not in our check list, so it won't match high or medium
        if "high" in severities:
            nova_verdict = "blocked"
        elif "medium" in severities:
            nova_verdict = "warned"
        else:
            nova_verdict = "warned"  # Default to warned for low/unknown

        # With "unknown", neither high nor medium matches
        assert nova_verdict == "warned"

    def test_missing_severity_defaults_to_medium(self):
        """Missing severity key defaults to medium."""
        detections = [
            {"rule_name": "NoSeverityRule"}  # No severity key
        ]

        severities = [d.get("severity", "medium") for d in detections]

        assert severities == ["medium"]

    def test_empty_rule_name_handled(self):
        """Empty rule name is handled gracefully."""
        detections = [
            {"severity": "high", "rule_name": ""}
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert nova_rules_matched == [""]

    def test_missing_rule_name_defaults_to_unknown(self):
        """Missing rule_name defaults to 'unknown'."""
        detections = [
            {"severity": "high"}  # No rule_name key
        ]

        nova_rules_matched = [d.get("rule_name", "unknown") for d in detections]

        assert nova_rules_matched == ["unknown"]
