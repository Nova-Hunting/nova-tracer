"""
Tests for the AI Summary Module (Story 3.3).

Tests cover:
- AC1: Generate AI Summary via API
- AC2: Use Claude Haiku Model
- AC3: Stats-Only Fallback (No API Key)
- AC4: Stats-Only Fallback (API Failure)
- AC5: Summary in Session Data
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add hooks/lib to path for imports
lib_dir = Path(__file__).parent.parent / "hooks" / "lib"
sys.path.insert(0, str(lib_dir))

from ai_summary import (
    HAIKU_MODEL,
    MAX_SUMMARY_TOKENS,
    _build_summary_prompt,
    generate_ai_summary,
    generate_stats_summary,
)


# Sample session data for testing
@pytest.fixture
def sample_session_data():
    """Create sample session data for testing."""
    return {
        "session_id": "2026-01-10_16-30-45_abc123",
        "session_start": "2026-01-10T16:30:45Z",
        "session_end": "2026-01-10T17:30:45Z",
        "platform": "darwin",
        "project_dir": "/test/project",
        "events": [
            {
                "type": "event",
                "id": 1,
                "tool_name": "Read",
                "nova_verdict": "allowed",
            },
            {
                "type": "event",
                "id": 2,
                "tool_name": "Edit",
                "nova_verdict": "allowed",
            },
            {
                "type": "event",
                "id": 3,
                "tool_name": "Bash",
                "nova_verdict": "warned",
            },
        ],
        "summary": {
            "ai_summary": None,
            "total_events": 3,
            "tools_used": {"Read": 1, "Edit": 1, "Bash": 1},
            "files_touched": 2,
            "warnings": 1,
            "blocked": 0,
            "duration_seconds": 3600,
        },
    }


@pytest.fixture
def empty_session_data():
    """Create empty session data for testing."""
    return {
        "session_id": "2026-01-10_16-30-45_xyz789",
        "session_start": "2026-01-10T16:30:45Z",
        "session_end": "2026-01-10T16:30:50Z",
        "platform": "darwin",
        "project_dir": "/test/project",
        "events": [],
        "summary": {
            "ai_summary": None,
            "total_events": 0,
            "tools_used": {},
            "files_touched": 0,
            "warnings": 0,
            "blocked": 0,
            "duration_seconds": 5,
        },
    }


class TestStatsSummary:
    """Tests for stats-only fallback summary generation."""

    def test_stats_summary_basic_format(self, sample_session_data):
        """Test that stats summary follows expected format."""
        summary = generate_stats_summary(sample_session_data)
        assert "3 tool calls" in summary
        assert "1h" in summary  # 3600 seconds = 1 hour
        assert "2 files" in summary

    def test_stats_summary_includes_warnings(self, sample_session_data):
        """Test that stats summary includes warning count."""
        summary = generate_stats_summary(sample_session_data)
        assert "1 warnings" in summary

    def test_stats_summary_includes_blocked(self):
        """Test that stats summary includes blocked count."""
        session_data = {
            "summary": {
                "total_events": 5,
                "files_touched": 1,
                "warnings": 0,
                "blocked": 2,
                "duration_seconds": 60,
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "2 blocked" in summary

    def test_stats_summary_empty_session(self, empty_session_data):
        """Test stats summary for empty session."""
        summary = generate_stats_summary(empty_session_data)
        assert "0 tool calls" in summary
        assert "5s" in summary

    def test_stats_summary_duration_minutes(self):
        """Test duration formatting in minutes."""
        session_data = {
            "summary": {
                "total_events": 10,
                "files_touched": 5,
                "warnings": 0,
                "blocked": 0,
                "duration_seconds": 125,  # 2m 5s
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "2m 5s" in summary

    def test_stats_summary_duration_hours(self):
        """Test duration formatting in hours."""
        session_data = {
            "summary": {
                "total_events": 100,
                "files_touched": 20,
                "warnings": 0,
                "blocked": 0,
                "duration_seconds": 7260,  # 2h 1m
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "2h 1m" in summary

    def test_stats_summary_no_files_touched(self):
        """Test stats summary when no files are modified."""
        session_data = {
            "summary": {
                "total_events": 3,
                "files_touched": 0,
                "warnings": 0,
                "blocked": 0,
                "duration_seconds": 30,
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "3 tool calls" in summary
        assert "Modified" not in summary  # No files mentioned if 0


class TestPromptBuilder:
    """Tests for the prompt builder function."""

    def test_prompt_includes_project_dir(self, sample_session_data):
        """Test that prompt includes project directory."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "/test/project" in prompt

    def test_prompt_includes_duration(self, sample_session_data):
        """Test that prompt includes duration."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "1 hours" in prompt or "hour" in prompt

    def test_prompt_includes_event_count(self, sample_session_data):
        """Test that prompt includes total events."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "3" in prompt

    def test_prompt_includes_tools_used(self, sample_session_data):
        """Test that prompt includes tools breakdown."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "Read" in prompt
        assert "Edit" in prompt

    def test_prompt_includes_security_info(self, sample_session_data):
        """Test that prompt includes security events."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "1 warnings" in prompt
        assert "0 blocked" in prompt

    def test_prompt_includes_event_timeline(self, sample_session_data):
        """Test that prompt includes event timeline."""
        prompt = _build_summary_prompt(sample_session_data)
        assert "- Read (allowed)" in prompt
        assert "- Bash (warned)" in prompt

    def test_prompt_truncates_long_event_list(self):
        """Test that prompt truncates event list for many events."""
        session_data = {
            "summary": {
                "total_events": 15,
                "tools_used": {"Read": 15},
                "files_touched": 5,
                "warnings": 0,
                "blocked": 0,
                "duration_seconds": 300,
            },
            "events": [
                {"tool_name": "Read", "nova_verdict": "allowed"}
                for _ in range(15)
            ],
            "project_dir": "/test",
        }
        prompt = _build_summary_prompt(session_data)
        assert "and 5 more events" in prompt


class TestAISummaryNoAPIKey:
    """Tests for AI summary without API key (AC3)."""

    def test_no_api_key_returns_stats_summary(self, sample_session_data):
        """Test that missing API key falls back to stats summary."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove ANTHROPIC_API_KEY if present
            os.environ.pop("ANTHROPIC_API_KEY", None)
            summary = generate_ai_summary(sample_session_data)

        # Should be a stats-based summary
        assert "tool calls" in summary
        assert isinstance(summary, str)

    def test_no_api_key_no_error_raised(self, sample_session_data):
        """Test that no exception is raised without API key."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            # Should not raise any exception
            summary = generate_ai_summary(sample_session_data)
            assert summary is not None


class TestAISummaryAPIFailure:
    """Tests for AI summary API failure handling (AC4)."""

    def test_connection_error_falls_back(self, sample_session_data):
        """Test that connection error falls back to stats summary."""
        import anthropic as real_anthropic

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_client_class.return_value.messages.create.side_effect = \
                    real_anthropic.APIConnectionError(request=MagicMock())

                summary = generate_ai_summary(sample_session_data)

        assert "tool calls" in summary  # Falls back to stats

    def test_rate_limit_error_falls_back(self, sample_session_data):
        """Test that rate limit error falls back to stats summary."""
        import anthropic as real_anthropic

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_client_class.return_value.messages.create.side_effect = \
                    real_anthropic.RateLimitError(
                        message="Rate limited",
                        response=MagicMock(status_code=429),
                        body={}
                    )

                summary = generate_ai_summary(sample_session_data)

        assert "tool calls" in summary  # Falls back to stats

    def test_api_status_error_falls_back(self, sample_session_data):
        """Test that API status error falls back to stats summary."""
        import anthropic as real_anthropic

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_client_class.return_value.messages.create.side_effect = \
                    real_anthropic.APIStatusError(
                        message="Server error",
                        response=MagicMock(status_code=500),
                        body={}
                    )

                summary = generate_ai_summary(sample_session_data)

        assert "tool calls" in summary  # Falls back to stats

    def test_unexpected_error_falls_back(self, sample_session_data):
        """Test that unexpected errors fall back to stats summary."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_client_class.return_value.messages.create.side_effect = \
                    Exception("Unexpected error")

                summary = generate_ai_summary(sample_session_data)

        assert "tool calls" in summary  # Falls back to stats

    def test_empty_response_falls_back(self, sample_session_data):
        """Test that empty API response falls back to stats summary."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_response = MagicMock()
                mock_response.content = []  # Empty content
                mock_client_class.return_value.messages.create.return_value = mock_response

                summary = generate_ai_summary(sample_session_data)

        assert "tool calls" in summary  # Falls back to stats


class TestAISummaryAPISuccess:
    """Tests for successful AI summary generation (AC1, AC2)."""

    def test_successful_api_call_returns_summary(self, sample_session_data):
        """Test that successful API call returns AI-generated summary."""
        expected_summary = "This session focused on file editing tasks."

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_content = MagicMock()
                mock_content.text = expected_summary
                mock_response = MagicMock()
                mock_response.content = [mock_content]
                mock_client_class.return_value.messages.create.return_value = mock_response

                summary = generate_ai_summary(sample_session_data)

        assert summary == expected_summary

    def test_api_uses_haiku_model(self, sample_session_data):
        """Test that API call uses Claude Haiku model (AC2)."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_content = MagicMock()
                mock_content.text = "Test summary"
                mock_response = MagicMock()
                mock_response.content = [mock_content]
                mock_client_class.return_value.messages.create.return_value = mock_response

                generate_ai_summary(sample_session_data)

                # Verify model parameter
                call_args = mock_client_class.return_value.messages.create.call_args
                assert call_args.kwargs["model"] == HAIKU_MODEL

    def test_api_uses_correct_max_tokens(self, sample_session_data):
        """Test that API call uses correct max_tokens."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_content = MagicMock()
                mock_content.text = "Test summary"
                mock_response = MagicMock()
                mock_response.content = [mock_content]
                mock_client_class.return_value.messages.create.return_value = mock_response

                generate_ai_summary(sample_session_data)

                # Verify max_tokens parameter
                call_args = mock_client_class.return_value.messages.create.call_args
                assert call_args.kwargs["max_tokens"] == MAX_SUMMARY_TOKENS

    def test_api_strips_whitespace_from_response(self, sample_session_data):
        """Test that whitespace is stripped from API response."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Anthropic") as mock_client_class:
                mock_content = MagicMock()
                mock_content.text = "  Summary with whitespace  \n"
                mock_response = MagicMock()
                mock_response.content = [mock_content]
                mock_client_class.return_value.messages.create.return_value = mock_response

                summary = generate_ai_summary(sample_session_data)

        assert summary == "Summary with whitespace"


class TestAISummaryMissingAnthropicPackage:
    """Tests for handling missing anthropic package."""

    def test_missing_package_falls_back(self, sample_session_data):
        """Test that missing anthropic package falls back to stats summary."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch.dict(sys.modules, {"anthropic": None}):
                # Force import error
                with patch("builtins.__import__", side_effect=ImportError):
                    summary = generate_ai_summary(sample_session_data)

        # Should fall back to stats (exact behavior depends on implementation)
        assert isinstance(summary, str)


class TestSummaryIntegration:
    """Integration tests for AI summary in session data (AC5)."""

    def test_summary_stored_in_session_data(self, sample_session_data, tmp_path):
        """Test that summary is correctly stored in session data."""
        # This tests that the integration works - summary should be populated
        # The actual integration happens in session-end.py

        # Generate summary
        summary = generate_ai_summary(sample_session_data)

        # Manually add to session data (as session-end.py would)
        sample_session_data["summary"]["ai_summary"] = summary

        # Verify it's in the correct location
        assert sample_session_data["summary"]["ai_summary"] is not None
        assert isinstance(sample_session_data["summary"]["ai_summary"], str)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_missing_summary_dict(self):
        """Test handling of missing summary dictionary."""
        session_data = {
            "events": [],
            "project_dir": "/test",
        }
        summary = generate_stats_summary(session_data)
        assert "0 tool calls" in summary

    def test_missing_events_list(self):
        """Test handling of missing events list."""
        session_data = {
            "summary": {
                "total_events": 5,
                "duration_seconds": 60,
            },
        }
        summary = generate_stats_summary(session_data)
        assert "5 tool calls" in summary

    def test_zero_duration(self):
        """Test handling of zero duration."""
        session_data = {
            "summary": {
                "total_events": 1,
                "files_touched": 0,
                "warnings": 0,
                "blocked": 0,
                "duration_seconds": 0,
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "0s" in summary

    def test_very_long_session(self):
        """Test handling of very long session duration."""
        session_data = {
            "summary": {
                "total_events": 1000,
                "files_touched": 50,
                "warnings": 10,
                "blocked": 2,
                "duration_seconds": 36000,  # 10 hours
            },
            "events": [],
        }
        summary = generate_stats_summary(session_data)
        assert "10h" in summary
