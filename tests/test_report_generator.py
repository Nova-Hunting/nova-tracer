"""
Tests for the Report Generator Module (Story 3.2, 4.1).

Tests cover:
Story 3.2:
- AC1: HTML generation from session data
- AC2: Self-contained HTML (embedded CSS, JS, SESSION_DATA)
- AC3: Aggregate statistics calculation
- AC4: Metadata inclusion
- AC5: Empty session handling

Story 4.1:
- AC1: CSS Variables for Verdict Colors
- AC2: Color Coding Communicates Severity
- AC3: Tool Icons for Each Tool Type
- AC4: Cross-Browser Compatibility (self-contained)
"""

import json
import re
import sys
from pathlib import Path

import pytest

# Add lib directory for imports
HOOKS_DIR = Path(__file__).parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR / "lib"))

from report_generator import (
    NOVA_VERSION,
    TOOL_ICONS,
    _format_content_for_display,
    _format_timestamp,
    _generate_events_html,
    _generate_timeline_html,
    generate_html_report,
    get_tool_icon,
    save_report,
)


class TestHTMLGeneration:
    """Tests for AC1: HTML generation from session data."""

    def test_generate_html_report_returns_string(self):
        """AC1: generate_html_report returns a string."""
        session_data = {
            "session_id": "test123",
            "events": [],
            "summary": {},
        }
        result = generate_html_report(session_data)
        assert isinstance(result, str)

    def test_generate_html_report_returns_valid_html(self):
        """AC1: Result is valid HTML with doctype."""
        session_data = {
            "session_id": "test123",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert html.startswith("<!DOCTYPE html>")
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_generate_html_report_contains_session_id(self):
        """AC1: Report contains the session ID."""
        session_data = {
            "session_id": "unique_test_session_xyz",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "unique_test_session_xyz" in html


class TestSelfContainedHTML:
    """Tests for AC2: Self-contained HTML."""

    def test_css_embedded_in_style_tag(self):
        """AC2: CSS is embedded in <style> tag."""
        session_data = {"session_id": "test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should have style tag with CSS
        assert "<style>" in html
        assert "</style>" in html

        # Should contain CSS variables
        assert "--color-allowed" in html
        assert "--color-warned" in html
        assert "--color-blocked" in html

    def test_no_external_css_links(self):
        """AC2: No external CSS files linked."""
        session_data = {"session_id": "test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should not have external stylesheet links
        assert 'rel="stylesheet"' not in html
        assert "<link" not in html.lower() or 'href="http' not in html

    def test_javascript_embedded_in_script_tag(self):
        """AC2: JavaScript is embedded in <script> tag."""
        session_data = {"session_id": "test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "<script>" in html
        assert "</script>" in html

    def test_no_external_javascript(self):
        """AC2: No external JavaScript files linked."""
        session_data = {"session_id": "test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should not have script src attributes
        assert 'src="http' not in html

    def test_session_data_embedded_as_const(self):
        """AC2: Session data embedded as const SESSION_DATA."""
        session_data = {
            "session_id": "embed_test",
            "events": [{"tool_name": "Read"}],
            "summary": {"total_events": 1},
        }
        html = generate_html_report(session_data)

        assert "const SESSION_DATA = " in html

        # Extract the JSON and verify it's valid
        match = re.search(r"const SESSION_DATA = ({.*?});", html, re.DOTALL)
        assert match is not None
        embedded_data = json.loads(match.group(1))
        assert embedded_data["session_id"] == "embed_test"


class TestAggregateStatistics:
    """Tests for AC3: Aggregate statistics calculation."""

    def test_total_events_displayed(self):
        """AC3: Total events count is displayed."""
        session_data = {
            "session_id": "stats_test",
            "events": [],
            "summary": {"total_events": 42},
        }
        html = generate_html_report(session_data)

        assert ">42<" in html  # Value in a tag
        assert "Total Events" in html

    def test_tools_used_displayed(self):
        """AC3: Tools used breakdown is displayed."""
        session_data = {
            "session_id": "tools_test",
            "events": [],
            "summary": {
                "tools_used": {"Read": 10, "Bash": 5, "Write": 3},
            },
        }
        html = generate_html_report(session_data)

        assert "Read" in html
        assert "Bash" in html
        assert "Write" in html
        assert "Tools Used" in html

    def test_files_touched_displayed(self):
        """AC3: Files touched count is displayed."""
        session_data = {
            "session_id": "files_test",
            "events": [],
            "summary": {"files_touched": 15},
        }
        html = generate_html_report(session_data)

        assert ">15<" in html
        assert "Files Touched" in html

    def test_warnings_count_displayed(self):
        """AC3: Warnings count is displayed."""
        session_data = {
            "session_id": "warnings_test",
            "events": [],
            "summary": {"warnings": 3},
        }
        html = generate_html_report(session_data)

        assert ">3<" in html
        assert "Warnings" in html

    def test_blocked_count_displayed(self):
        """AC3: Blocked count is displayed."""
        session_data = {
            "session_id": "blocked_test",
            "events": [],
            "summary": {"blocked": 2},
        }
        html = generate_html_report(session_data)

        assert ">2<" in html
        assert "Blocked" in html


class TestMetadataInclusion:
    """Tests for AC4: Metadata inclusion."""

    def test_session_id_in_metadata(self):
        """AC4: Session ID is included in metadata."""
        session_data = {
            "session_id": "meta_session_123",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "meta_session_123" in html

    def test_session_start_in_metadata(self):
        """AC4: Session start time is included."""
        session_data = {
            "session_id": "start_test",
            "session_start": "2024-01-01T12:00:00Z",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Session Start" in html
        assert "2024-01-01" in html

    def test_session_end_in_metadata(self):
        """AC4: Session end time is included."""
        session_data = {
            "session_id": "end_test",
            "session_end": "2024-01-01T14:30:00Z",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Session End" in html
        assert "2024-01-01" in html

    def test_platform_in_metadata(self):
        """AC4: Platform is included in metadata."""
        session_data = {
            "session_id": "platform_test",
            "platform": "darwin",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Platform" in html
        assert "darwin" in html

    def test_nova_version_in_metadata(self):
        """AC4: NOVA version is included in metadata."""
        session_data = {
            "session_id": "version_test",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "NOVA Version" in html
        assert NOVA_VERSION in html

    def test_project_dir_in_metadata(self):
        """AC4: Project directory is included in metadata."""
        session_data = {
            "session_id": "project_test",
            "project_dir": "/path/to/my/project",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Project Directory" in html
        assert "/path/to/my/project" in html

    def test_duration_seconds_calculated(self):
        """AC4: Duration is calculated and displayed."""
        session_data = {
            "session_id": "duration_test",
            "events": [],
            "summary": {"duration_seconds": 3661},  # 1h 1m 1s
        }
        html = generate_html_report(session_data)

        assert "Duration" in html
        assert "1h" in html


class TestEmptySessionHandling:
    """Tests for AC5: Empty session handling."""

    def test_empty_events_produces_valid_html(self):
        """AC5: Empty events list produces valid HTML."""
        session_data = {
            "session_id": "empty_test",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_empty_session_shows_zero_events(self):
        """AC5: Empty session shows 0 total events."""
        session_data = {
            "session_id": "zero_test",
            "events": [],
            "summary": {"total_events": 0},
        }
        html = generate_html_report(session_data)

        assert ">0<" in html

    def test_empty_session_shows_zero_warnings(self):
        """AC5: Empty session shows 0 warnings."""
        session_data = {
            "session_id": "zero_warn_test",
            "events": [],
            "summary": {"warnings": 0},
        }
        html = generate_html_report(session_data)

        # Should have warning stat showing 0
        assert "Warnings" in html

    def test_empty_session_shows_zero_blocked(self):
        """AC5: Empty session shows 0 blocked."""
        session_data = {
            "session_id": "zero_block_test",
            "events": [],
            "summary": {"blocked": 0},
        }
        html = generate_html_report(session_data)

        # Should have blocked stat showing 0
        assert "Blocked" in html

    def test_empty_session_has_no_event_cards(self):
        """AC5: Empty session has no event cards."""
        session_data = {
            "session_id": "no_events_test",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Should show "No events recorded" message
        assert "No events recorded" in html

    def test_missing_summary_handled(self):
        """AC5: Missing summary dict is handled gracefully."""
        session_data = {
            "session_id": "no_summary",
            "events": [],
        }
        html = generate_html_report(session_data)

        assert "<!DOCTYPE html>" in html

    def test_completely_empty_session_data(self):
        """AC5: Completely empty session data is handled."""
        session_data = {}
        html = generate_html_report(session_data)

        assert "<!DOCTYPE html>" in html
        assert "unknown" in html  # Default session_id


class TestHealthStatus:
    """Tests for health status badge display."""

    def test_clean_status_when_no_issues(self):
        """Health status is CLEAN when no warnings or blocks."""
        session_data = {
            "session_id": "clean",
            "events": [],
            "summary": {"warnings": 0, "blocked": 0},
        }
        html = generate_html_report(session_data)
        assert "CLEAN" in html

    def test_warnings_status_when_warnings_only(self):
        """Health status is WARNINGS when warnings exist."""
        session_data = {
            "session_id": "warned",
            "events": [],
            "summary": {"warnings": 2, "blocked": 0},
        }
        html = generate_html_report(session_data)
        assert "WARNINGS" in html

    def test_blocked_status_takes_precedence(self):
        """Health status is BLOCKED when any blocks exist."""
        session_data = {
            "session_id": "blocked",
            "events": [],
            "summary": {"warnings": 2, "blocked": 1},
        }
        html = generate_html_report(session_data)
        assert "BLOCKED" in html


class TestEventDisplay:
    """Tests for event timeline display."""

    def test_events_displayed_with_tool_name(self):
        """Events show tool name."""
        session_data = {
            "session_id": "events_display",
            "events": [
                {"tool_name": "Read", "nova_verdict": "allowed"},
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "Read" in html

    def test_events_displayed_with_verdict(self):
        """Events show verdict badge."""
        session_data = {
            "session_id": "verdict_display",
            "events": [
                {"tool_name": "Bash", "nova_verdict": "warned"},
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "WARNED" in html

    def test_events_displayed_with_timestamp(self):
        """Events show timestamp."""
        session_data = {
            "session_id": "time_display",
            "events": [
                {
                    "tool_name": "Read",
                    "nova_verdict": "allowed",
                    "timestamp_start": "2024-01-01T12:30:45Z",
                },
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "12:30:45" in html

    def test_events_displayed_with_files(self):
        """Events show files accessed."""
        session_data = {
            "session_id": "files_display",
            "events": [
                {
                    "tool_name": "Read",
                    "nova_verdict": "allowed",
                    "files_accessed": ["/path/to/file.py"],
                },
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)
        assert "/path/to/file.py" in html


class TestTimestampFormatting:
    """Tests for timestamp formatting helper."""

    def test_format_valid_timestamp(self):
        """Valid ISO timestamp is formatted correctly."""
        result = _format_timestamp("2024-01-15T14:30:00Z")
        assert "2024-01-15" in result
        assert "14:30:00" in result

    def test_format_empty_timestamp(self):
        """Empty timestamp returns N/A."""
        result = _format_timestamp("")
        assert result == "N/A"

    def test_format_none_timestamp(self):
        """None-ish timestamp returns N/A."""
        result = _format_timestamp(None)
        assert result == "N/A"

    def test_format_invalid_timestamp(self):
        """Invalid timestamp returns truncated string."""
        result = _format_timestamp("invalid-timestamp-format")
        assert "invalid-timestamp" in result


class TestSaveReport:
    """Tests for save_report function."""

    def test_save_creates_file(self, tmp_path):
        """save_report creates file at specified path."""
        report_path = tmp_path / "test_report.html"
        html_content = "<!DOCTYPE html><html></html>"

        result = save_report(html_content, report_path)

        assert result is True
        assert report_path.exists()
        assert report_path.read_text() == html_content

    def test_save_creates_parent_directories(self, tmp_path):
        """save_report creates parent directories."""
        report_path = tmp_path / "deep" / "nested" / "report.html"
        html_content = "<html></html>"

        result = save_report(html_content, report_path)

        assert result is True
        assert report_path.exists()

    def test_save_returns_false_on_error(self, tmp_path):
        """save_report returns False on write error."""
        # Try to write to an invalid path
        report_path = Path("/nonexistent/path/that/cannot/exist/report.html")
        html_content = "<html></html>"

        result = save_report(html_content, report_path)

        assert result is False


class TestDurationFormatting:
    """Tests for duration display formatting."""

    def test_duration_seconds_only(self):
        """Duration under a minute shows seconds."""
        session_data = {
            "session_id": "short",
            "events": [],
            "summary": {"duration_seconds": 45},
        }
        html = generate_html_report(session_data)
        assert "45s" in html

    def test_duration_minutes_and_seconds(self):
        """Duration shows minutes and seconds."""
        session_data = {
            "session_id": "medium",
            "events": [],
            "summary": {"duration_seconds": 125},  # 2m 5s
        }
        html = generate_html_report(session_data)
        assert "2m" in html

    def test_duration_hours_and_minutes(self):
        """Duration shows hours and minutes."""
        session_data = {
            "session_id": "long",
            "events": [],
            "summary": {"duration_seconds": 7380},  # 2h 3m
        }
        html = generate_html_report(session_data)
        assert "2h" in html
        assert "3m" in html


class TestXSSPrevention:
    """Tests for XSS prevention through HTML escaping."""

    def test_session_id_escaped(self):
        """Session ID with special chars is escaped."""
        session_data = {
            "session_id": "<script>alert('xss')</script>",
            "events": [],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Should be escaped
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html

    def test_tool_name_escaped(self):
        """Tool name with special chars is escaped."""
        session_data = {
            "session_id": "xss_test",
            "events": [{"tool_name": "<img src=x onerror=alert(1)>", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "<img src=x" not in html

    def test_file_path_escaped(self):
        """File path with special chars is escaped."""
        session_data = {
            "session_id": "xss_test",
            "events": [
                {
                    "tool_name": "Read",
                    "nova_verdict": "allowed",
                    "files_accessed": ["<script>bad</script>"],
                }
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "<script>bad" not in html


# ============================================================================
# Story 4.1: Base Template and Design System
# ============================================================================


class TestCSSVariables:
    """Tests for Story 4.1 AC1: CSS Variables for Verdict Colors."""

    def test_color_allowed_defined(self):
        """AC1: --color-allowed CSS variable is defined with correct value."""
        session_data = {"session_id": "css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "--color-allowed: #22c55e" in html

    def test_color_warned_defined(self):
        """AC1: --color-warned CSS variable is defined with correct value."""
        session_data = {"session_id": "css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "--color-warned: #f59e0b" in html

    def test_color_blocked_defined(self):
        """AC1: --color-blocked CSS variable is defined with correct value."""
        session_data = {"session_id": "css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "--color-blocked: #ef4444" in html

    def test_color_neutral_defined(self):
        """AC1: --color-neutral CSS variable is defined with correct value."""
        session_data = {"session_id": "css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "--color-neutral: #6b7280" in html

    def test_all_color_variables_in_root(self):
        """AC1: All color variables are defined in :root."""
        session_data = {"session_id": "root_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Find :root block
        assert ":root {" in html or ":root{" in html


class TestColorCoding:
    """Tests for Story 4.1 AC2: Color Coding Communicates Severity."""

    def test_allowed_event_uses_green_border(self):
        """AC2: Allowed events have green color coding."""
        session_data = {
            "session_id": "color_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Event card should have 'allowed' class
        assert 'class="event-card allowed"' in html

    def test_warned_event_uses_amber_border(self):
        """AC2: Warned events have amber color coding."""
        session_data = {
            "session_id": "color_test",
            "events": [{"tool_name": "Bash", "nova_verdict": "warned"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Event card should have 'warned' class
        assert 'class="event-card warned"' in html

    def test_blocked_event_uses_red_border(self):
        """AC2: Blocked events have red color coding."""
        session_data = {
            "session_id": "color_test",
            "events": [{"tool_name": "Bash", "nova_verdict": "blocked"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Event card should have 'blocked' class
        assert 'class="event-card blocked"' in html

    def test_verdict_badge_has_color_class(self):
        """AC2: Verdict badges have appropriate color classes."""
        session_data = {
            "session_id": "badge_test",
            "events": [{"tool_name": "Read", "nova_verdict": "warned"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="event-verdict warned"' in html


class TestToolIcons:
    """Tests for Story 4.1 AC3: Tool Icons for Each Tool Type."""

    def test_tool_icons_dict_has_required_tools(self):
        """AC3: TOOL_ICONS contains all required tool types."""
        required_tools = ["Read", "Edit", "Write", "Bash", "Glob", "Grep", "WebFetch", "Task"]
        for tool in required_tools:
            assert tool in TOOL_ICONS, f"Missing icon for {tool}"

    def test_tool_icons_has_default(self):
        """AC3: TOOL_ICONS has a default fallback icon."""
        assert "_default" in TOOL_ICONS

    def test_get_tool_icon_returns_known_icon(self):
        """AC3: get_tool_icon returns correct icon for known tools."""
        icon = get_tool_icon("Read")
        assert "<svg" in icon
        assert "tool-icon" in icon

    def test_get_tool_icon_returns_default_for_unknown(self):
        """AC3: get_tool_icon returns default for unknown tools."""
        icon = get_tool_icon("UnknownToolXYZ")
        assert "<svg" in icon
        assert icon == TOOL_ICONS["_default"]

    def test_read_icon_is_file_icon(self):
        """AC3: Read tool has a file/document icon."""
        icon = TOOL_ICONS["Read"]
        # File icon typically has path elements for document shape
        assert "<svg" in icon
        assert "viewBox" in icon

    def test_bash_icon_is_terminal_icon(self):
        """AC3: Bash tool has a terminal icon."""
        icon = TOOL_ICONS["Bash"]
        # Terminal icon has characteristic elements
        assert "<svg" in icon
        assert "polyline" in icon or "line" in icon

    def test_glob_icon_is_search_icon(self):
        """AC3: Glob tool has a search/magnifying glass icon."""
        icon = TOOL_ICONS["Glob"]
        # Search icon has circle element
        assert "<svg" in icon
        assert "circle" in icon

    def test_webfetch_icon_is_globe_icon(self):
        """AC3: WebFetch tool has a globe icon."""
        icon = TOOL_ICONS["WebFetch"]
        assert "<svg" in icon
        assert "circle" in icon

    def test_events_html_includes_tool_icons(self):
        """AC3: Generated events HTML includes tool icons."""
        session_data = {
            "session_id": "icon_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Should contain SVG icon in event
        assert '<svg class="tool-icon"' in html

    def test_tools_section_includes_icons(self):
        """AC3: Tools used section includes icons."""
        session_data = {
            "session_id": "tools_icon_test",
            "events": [],
            "summary": {"tools_used": {"Read": 5, "Bash": 3}},
        }
        html = generate_html_report(session_data)

        # Should have SVG icons in tools section
        svg_count = html.count('<svg class="tool-icon"')
        assert svg_count >= 2, f"Expected at least 2 tool icons, found {svg_count}"

    def test_all_tool_icons_are_valid_svg(self):
        """AC3: All tool icons are valid SVG elements."""
        for tool_name, icon in TOOL_ICONS.items():
            assert icon.strip().startswith("<svg"), f"{tool_name} icon doesn't start with <svg"
            assert "</svg>" in icon, f"{tool_name} icon missing closing </svg>"
            assert 'class="tool-icon"' in icon, f"{tool_name} icon missing tool-icon class"


class TestSelfContainedTemplate:
    """Tests for Story 4.1 AC4: Cross-Browser Compatibility (Self-Contained)."""

    def test_no_external_fonts(self):
        """AC4: No external font links."""
        session_data = {"session_id": "font_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should not link to Google Fonts or other external fonts
        assert "fonts.googleapis.com" not in html
        assert "fonts.gstatic.com" not in html

    def test_uses_system_fonts(self):
        """AC4: Uses system font stack for cross-browser compatibility."""
        session_data = {"session_id": "system_font_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should use system font stack
        assert "-apple-system" in html or "system-ui" in html or "BlinkMacSystemFont" in html

    def test_has_viewport_meta_tag(self):
        """AC4: Has viewport meta tag for responsive design."""
        session_data = {"session_id": "viewport_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert 'name="viewport"' in html
        assert "width=device-width" in html

    def test_has_charset_meta_tag(self):
        """AC4: Has charset meta tag."""
        session_data = {"session_id": "charset_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html

    def test_html_has_lang_attribute(self):
        """AC4: HTML tag has lang attribute."""
        session_data = {"session_id": "lang_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert '<html lang="en">' in html

    def test_tool_icon_css_defined(self):
        """AC4: CSS for tool icons is defined."""
        session_data = {"session_id": "icon_css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".tool-icon" in html
        assert "width:" in html or "width :" in html


# ============================================================================
# Story 4.2: Report Header Component
# ============================================================================


class TestHealthBadgeClean:
    """Tests for Story 4.2 AC1: Clean Health Badge."""

    def test_clean_badge_displays_clean_text(self):
        """AC1: Health badge displays 'CLEAN' when no issues."""
        session_data = {
            "session_id": "clean_test",
            "events": [],
            "summary": {"warnings": 0, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert ">CLEAN<" in html

    def test_clean_badge_has_green_color(self):
        """AC1: Clean badge uses green color (#22c55e)."""
        session_data = {
            "session_id": "clean_color",
            "events": [],
            "summary": {"warnings": 0, "blocked": 0},
        }
        html = generate_html_report(session_data)

        # Badge background should be green
        assert "background: #22c55e" in html

    def test_clean_badge_no_subtitle(self):
        """AC1: Clean badge has no subtitle (no counts to show)."""
        session_data = {
            "session_id": "clean_no_subtitle",
            "events": [],
            "summary": {"warnings": 0, "blocked": 0},
        }
        html = generate_html_report(session_data)

        # Should not have health-subtitle with content
        # The badge container should not have a subtitle div
        assert 'class="health-badge">CLEAN</div>' in html
        # Verify no "0 warnings" subtitle
        assert "0 warnings" not in html or "health-subtitle" not in html.split("CLEAN")[1].split("</div>")[0]

    def test_clean_badge_prominent_position(self):
        """AC1: Health badge is prominently visible at the top."""
        session_data = {
            "session_id": "clean_prominent",
            "events": [],
            "summary": {"warnings": 0, "blocked": 0},
        }
        html = generate_html_report(session_data)

        # Badge should be in header section
        header_section = html.split('<div class="header">')[1].split('</div>')[0:5]
        header_content = "</div>".join(header_section)
        assert "health-badge" in header_content


class TestHealthBadgeWarnings:
    """Tests for Story 4.2 AC2: Warnings Health Badge."""

    def test_warnings_badge_displays_warnings_text(self):
        """AC2: Health badge displays 'WARNINGS' when warnings exist."""
        session_data = {
            "session_id": "warn_test",
            "events": [],
            "summary": {"warnings": 3, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert ">WARNINGS<" in html

    def test_warnings_badge_has_amber_color(self):
        """AC2: Warnings badge uses amber color (#f59e0b)."""
        session_data = {
            "session_id": "warn_color",
            "events": [],
            "summary": {"warnings": 2, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert "background: #f59e0b" in html

    def test_warnings_badge_shows_count(self):
        """AC2: Warnings badge shows count: 'X warnings'."""
        session_data = {
            "session_id": "warn_count",
            "events": [],
            "summary": {"warnings": 5, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert "5 warnings" in html

    def test_warnings_badge_has_subtitle_class(self):
        """AC2: Warnings count uses health-subtitle class."""
        session_data = {
            "session_id": "warn_subtitle",
            "events": [],
            "summary": {"warnings": 2, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert 'class="health-subtitle"' in html
        assert "2 warnings" in html


class TestHealthBadgeBlocked:
    """Tests for Story 4.2 AC3: Blocked Health Badge."""

    def test_blocked_badge_displays_blocked_text(self):
        """AC3: Health badge displays 'BLOCKED' when blocked events exist."""
        session_data = {
            "session_id": "block_test",
            "events": [],
            "summary": {"warnings": 1, "blocked": 2},
        }
        html = generate_html_report(session_data)

        assert ">BLOCKED<" in html

    def test_blocked_badge_has_red_color(self):
        """AC3: Blocked badge uses red color (#ef4444)."""
        session_data = {
            "session_id": "block_color",
            "events": [],
            "summary": {"warnings": 0, "blocked": 1},
        }
        html = generate_html_report(session_data)

        assert "background: #ef4444" in html

    def test_blocked_badge_shows_both_counts(self):
        """AC3: Blocked badge shows counts: 'X blocked, Y warnings'."""
        session_data = {
            "session_id": "block_count",
            "events": [],
            "summary": {"warnings": 3, "blocked": 2},
        }
        html = generate_html_report(session_data)

        assert "2 blocked, 3 warnings" in html

    def test_blocked_takes_precedence_over_warnings(self):
        """AC3: BLOCKED status takes precedence when both blocked and warnings exist."""
        session_data = {
            "session_id": "block_precedence",
            "events": [],
            "summary": {"warnings": 5, "blocked": 1},
        }
        html = generate_html_report(session_data)

        assert ">BLOCKED<" in html
        assert ">WARNINGS<" not in html

    def test_blocked_only_no_warnings(self):
        """AC3: Blocked badge works with zero warnings."""
        session_data = {
            "session_id": "block_only",
            "events": [],
            "summary": {"warnings": 0, "blocked": 3},
        }
        html = generate_html_report(session_data)

        assert ">BLOCKED<" in html
        assert "3 blocked, 0 warnings" in html


class TestAISummaryDisplay:
    """Tests for Story 4.2 AC4: AI Summary Display."""

    def test_ai_summary_displayed(self):
        """AC4: AI summary text is displayed when present."""
        session_data = {
            "session_id": "summary_test",
            "events": [],
            "summary": {
                "ai_summary": "This session performed file operations and security scans."
            },
        }
        html = generate_html_report(session_data)

        assert "This session performed file operations and security scans." in html

    def test_ai_summary_in_summary_section(self):
        """AC4: AI summary is in a dedicated summary section."""
        session_data = {
            "session_id": "summary_section",
            "events": [],
            "summary": {"ai_summary": "Custom AI summary text here."},
        }
        html = generate_html_report(session_data)

        # Summary should be in summary section
        assert 'class="summary"' in html
        assert "Session Summary" in html

    def test_ai_summary_fallback_when_missing(self):
        """AC4: Fallback summary is generated when AI summary is missing."""
        session_data = {
            "session_id": "fallback_test",
            "events": [],
            "summary": {
                "total_events": 10,
                "files_touched": 5,
                "warnings": 1,
                "blocked": 0,
                "duration_seconds": 120,
            },
        }
        html = generate_html_report(session_data)

        # Should have a fallback summary
        assert "Session completed" in html
        assert "10 tool calls" in html

    def test_ai_summary_below_header(self):
        """AC4: AI summary is below the health badge."""
        session_data = {
            "session_id": "summary_position",
            "events": [],
            "summary": {"ai_summary": "Position test summary."},
        }
        html = generate_html_report(session_data)

        # Find positions
        badge_pos = html.find("health-badge")
        summary_pos = html.find("Position test summary")

        assert summary_pos > badge_pos, "Summary should be after health badge"


class TestSessionStatistics:
    """Tests for Story 4.2 AC5: Session Statistics."""

    def test_total_events_in_stats(self):
        """AC5: Total event count is displayed."""
        session_data = {
            "session_id": "stats_events",
            "events": [],
            "summary": {"total_events": 42},
        }
        html = generate_html_report(session_data)

        assert ">42<" in html
        assert "Total Events" in html

    def test_duration_formatted_seconds(self):
        """AC5: Session duration is formatted (seconds)."""
        session_data = {
            "session_id": "stats_duration",
            "events": [],
            "summary": {"duration_seconds": 45},
        }
        html = generate_html_report(session_data)

        assert "45s" in html
        assert "Duration" in html

    def test_duration_formatted_minutes(self):
        """AC5: Session duration is formatted (minutes and seconds)."""
        session_data = {
            "session_id": "stats_minutes",
            "events": [],
            "summary": {"duration_seconds": 754},  # 12m 34s
        }
        html = generate_html_report(session_data)

        assert "12m" in html

    def test_blocked_count_in_stats(self):
        """AC5: Blocked count is displayed in statistics."""
        session_data = {
            "session_id": "stats_blocked",
            "events": [],
            "summary": {"blocked": 5},
        }
        html = generate_html_report(session_data)

        assert ">5<" in html
        assert "Blocked" in html

    def test_warning_count_in_stats(self):
        """AC5: Warning count is displayed in statistics."""
        session_data = {
            "session_id": "stats_warnings",
            "events": [],
            "summary": {"warnings": 3},
        }
        html = generate_html_report(session_data)

        assert ">3<" in html
        assert "Warnings" in html

    def test_stats_section_has_grid_layout(self):
        """AC5: Statistics are in a grid layout for visual clarity."""
        session_data = {
            "session_id": "stats_grid",
            "events": [],
            "summary": {"total_events": 10, "warnings": 1, "blocked": 0},
        }
        html = generate_html_report(session_data)

        assert 'class="stats"' in html
        assert "stat-card" in html

    def test_files_touched_in_stats(self):
        """AC5: Files touched count is displayed."""
        session_data = {
            "session_id": "stats_files",
            "events": [],
            "summary": {"files_touched": 15},
        }
        html = generate_html_report(session_data)

        assert ">15<" in html
        assert "Files Touched" in html


class TestHealthBadgeContainer:
    """Tests for badge container styling."""

    def test_health_badge_container_css(self):
        """Badge container CSS is defined."""
        session_data = {"session_id": "container_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".health-badge-container" in html

    def test_health_subtitle_css(self):
        """Health subtitle CSS is defined."""
        session_data = {"session_id": "subtitle_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".health-subtitle" in html

    def test_badge_container_in_header(self):
        """Badge container is present in header HTML."""
        session_data = {"session_id": "container_html", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert 'class="health-badge-container"' in html


# ============================================================================
# Story 4.3: Visual Timeline Component
# ============================================================================


class TestTimelineChronologicalOrder:
    """Tests for Story 4.3 AC1: Chronological Event Order."""

    def test_timeline_container_present(self):
        """AC1: Timeline container is present when events exist."""
        session_data = {
            "session_id": "timeline_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="timeline-container"' in html

    def test_timeline_div_present(self):
        """AC1: Timeline div is present."""
        session_data = {
            "session_id": "timeline_div",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="timeline">' in html

    def test_timeline_nodes_for_each_event(self):
        """AC1: Each event has a timeline node."""
        session_data = {
            "session_id": "nodes_test",
            "events": [
                {"tool_name": "Read", "nova_verdict": "allowed"},
                {"tool_name": "Bash", "nova_verdict": "warned"},
                {"tool_name": "Write", "nova_verdict": "allowed"},
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Count timeline nodes
        node_count = html.count('class="timeline-node')
        assert node_count == 3

    def test_events_in_order(self):
        """AC1: Events appear in order by index."""
        session_data = {
            "session_id": "order_test",
            "events": [
                {"tool_name": "Read", "nova_verdict": "allowed", "timestamp_start": "2024-01-01T10:00:00Z"},
                {"tool_name": "Bash", "nova_verdict": "allowed", "timestamp_start": "2024-01-01T10:01:00Z"},
            ],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # First event (id=0) should appear before second (id=1)
        pos_0 = html.find('data-event-id="0"')
        pos_1 = html.find('data-event-id="1"')
        assert pos_0 < pos_1


class TestTimelineNodeDisplay:
    """Tests for Story 4.3 AC2: Timeline Node Display."""

    def test_node_has_tool_icon(self):
        """AC2: Each node shows tool icon."""
        session_data = {
            "session_id": "icon_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Find the timeline section and check for icon
        timeline_section = html.split('class="timeline">')[1].split('</div>')[0:5]
        timeline_content = "</div>".join(timeline_section)
        assert '<svg class="tool-icon"' in timeline_content or "node-icon" in timeline_content

    def test_node_has_timestamp(self):
        """AC2: Each node shows timestamp in HH:MM:SS format."""
        session_data = {
            "session_id": "time_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "timestamp_start": "2024-01-01T14:30:45Z"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "14:30:45" in html
        assert 'class="node-time"' in html

    def test_node_has_color_class(self):
        """AC2: Each node has color indicator class."""
        session_data = {
            "session_id": "color_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="timeline-node allowed"' in html


class TestTimelineWarnedHighlighting:
    """Tests for Story 4.3 AC3: Warned Event Highlighting."""

    def test_warned_node_has_warned_class(self):
        """AC3: Warned events have warned class."""
        session_data = {
            "session_id": "warned_test",
            "events": [{"tool_name": "Bash", "nova_verdict": "warned"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="timeline-node warned"' in html

    def test_warned_css_uses_amber(self):
        """AC3: Warned nodes use amber color."""
        session_data = {"session_id": "amber_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".timeline-node.warned" in html
        assert "--color-warned" in html


class TestTimelineBlockedHighlighting:
    """Tests for Story 4.3 AC4: Blocked Event Highlighting."""

    def test_blocked_node_has_blocked_class(self):
        """AC4: Blocked events have blocked class."""
        session_data = {
            "session_id": "blocked_test",
            "events": [{"tool_name": "Bash", "nova_verdict": "blocked"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="timeline-node blocked"' in html

    def test_blocked_css_uses_red(self):
        """AC4: Blocked nodes use red color."""
        session_data = {"session_id": "red_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".timeline-node.blocked" in html
        assert "--color-blocked" in html

    def test_blocked_node_has_background(self):
        """AC4: Blocked nodes have distinct background for visibility."""
        session_data = {"session_id": "bg_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Blocked nodes should have a red-tinted background
        assert "rgba(239, 68, 68" in html


class TestTimelineClickNavigation:
    """Tests for Story 4.3 AC5: Click-to-Navigate."""

    def test_node_has_onclick(self):
        """AC5: Timeline nodes have onclick handler."""
        session_data = {
            "session_id": "onclick_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "onclick=\"scrollToEvent(0)\"" in html

    def test_node_has_data_event_id(self):
        """AC5: Timeline nodes have data-event-id attribute."""
        session_data = {
            "session_id": "data_id_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'data-event-id="0"' in html

    def test_event_card_has_id(self):
        """AC5: Event cards have id for scroll target."""
        session_data = {
            "session_id": "card_id_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'id="event-0"' in html

    def test_scroll_function_defined(self):
        """AC5: scrollToEvent function is defined."""
        session_data = {"session_id": "scroll_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "function scrollToEvent(eventId)" in html

    def test_highlight_class_defined(self):
        """AC5: Highlighted card CSS is defined."""
        session_data = {"session_id": "highlight_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".event-card.highlighted" in html

    def test_scroll_uses_smooth_behavior(self):
        """AC5: Scroll uses smooth behavior."""
        session_data = {"session_id": "smooth_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "behavior: 'smooth'" in html


class TestTimelineLargeSessionPerformance:
    """Tests for Story 4.3 AC6: Large Session Performance."""

    def test_timeline_with_50_events(self):
        """AC6: Timeline renders with 50+ events."""
        events = [
            {"tool_name": f"Tool{i}", "nova_verdict": "allowed", "timestamp_start": f"2024-01-01T10:{i:02d}:00Z"}
            for i in range(55)
        ]
        session_data = {
            "session_id": "large_test",
            "events": events,
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Should have 55 timeline nodes
        node_count = html.count('class="timeline-node')
        assert node_count == 55

    def test_timeline_scrollable_css(self):
        """AC6: Timeline has overflow-y for scrolling."""
        session_data = {"session_id": "scroll_css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "overflow-y: auto" in html

    def test_timeline_max_height(self):
        """AC6: Timeline has max-height for constrained viewport."""
        session_data = {"session_id": "max_height_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "max-height:" in html

    def test_timeline_sticky_position(self):
        """AC6: Timeline is sticky for easy navigation."""
        session_data = {"session_id": "sticky_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "position: sticky" in html


class TestTimelineEmptySession:
    """Tests for timeline with empty session."""

    def test_no_timeline_when_no_events(self):
        """Timeline container not shown when no events."""
        session_data = {"session_id": "empty_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        # Should show "No events recorded" instead of timeline
        assert "No events recorded" in html

    def test_timeline_function_returns_empty_for_no_events(self):
        """_generate_timeline_html returns empty for no events."""
        from report_generator import _generate_timeline_html

        result = _generate_timeline_html([])
        assert result == ""


class TestTimelineCSS:
    """Tests for timeline CSS styling."""

    def test_timeline_css_defined(self):
        """Timeline CSS classes are defined."""
        session_data = {"session_id": "css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".timeline {" in html or ".timeline{" in html

    def test_timeline_node_css_defined(self):
        """Timeline node CSS is defined."""
        session_data = {"session_id": "node_css_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".timeline-node {" in html or ".timeline-node{" in html

    def test_timeline_hover_effect(self):
        """Timeline nodes have hover effect."""
        session_data = {"session_id": "hover_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".timeline-node:hover" in html


# ============================================================================
# Story 4.4: Event Detail Cards
# ============================================================================


class TestCollapsedViewDefault:
    """Tests for Story 4.4 AC1: Collapsed View Default."""

    def test_event_id_visible_in_collapsed(self):
        """AC1: Event ID is visible in collapsed view."""
        session_data = {
            "session_id": "collapsed_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="event-id"' in html
        assert "#0" in html

    def test_tool_name_in_header(self):
        """AC1: Tool name is visible in collapsed view header."""
        session_data = {
            "session_id": "tool_header",
            "events": [{"tool_name": "Bash", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Bash" in html

    def test_tool_icon_in_header(self):
        """AC1: Tool icon is visible in collapsed view header."""
        session_data = {
            "session_id": "icon_header",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # Should have tool icon (SVG) in event header
        assert '<svg class="tool-icon"' in html

    def test_timestamp_in_header(self):
        """AC1: Timestamp is visible in collapsed view header."""
        session_data = {
            "session_id": "time_header",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "timestamp_start": "2024-01-01T15:45:30Z"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "15:45:30" in html

    def test_verdict_badge_in_header(self):
        """AC1: Verdict badge is visible in collapsed view header."""
        session_data = {
            "session_id": "verdict_header",
            "events": [{"tool_name": "Read", "nova_verdict": "warned"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="event-verdict warned"' in html
        assert "WARNED" in html

    def test_expand_icon_present(self):
        """AC1: Expand indicator icon is present."""
        session_data = {
            "session_id": "expand_icon",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'class="expand-icon"' in html
        assert "▼" in html

    def test_details_hidden_by_default(self):
        """AC1: Details section is hidden by default."""
        session_data = {
            "session_id": "hidden_details",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'style="display: none;"' in html


class TestExpandToFullDetails:
    """Tests for Story 4.4 AC2: Expand to Full Details."""

    def test_details_section_exists(self):
        """AC2: Event details section exists."""
        session_data = {
            "session_id": "details_exist",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'id="details-0"' in html
        assert 'class="event-details"' in html

    def test_tool_input_displayed(self):
        """AC2: Tool input is displayed in expanded view."""
        session_data = {
            "session_id": "input_display",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "tool_input": {"file_path": "/test/file.py"}}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Tool Input" in html
        assert "/test/file.py" in html

    def test_tool_output_displayed(self):
        """AC2: Tool output is displayed in expanded view."""
        session_data = {
            "session_id": "output_display",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "tool_output": "File contents here"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Tool Output" in html
        assert "File contents here" in html

    def test_duration_ms_displayed(self):
        """AC2: Duration in ms is displayed in expanded view."""
        session_data = {
            "session_id": "duration_display",
            "events": [{"tool_name": "Bash", "nova_verdict": "allowed", "duration_ms": 1234}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Duration:" in html
        assert "1234ms" in html

    def test_working_dir_displayed(self):
        """AC2: Working directory is displayed in expanded view."""
        session_data = {
            "session_id": "workdir_display",
            "events": [{"tool_name": "Bash", "nova_verdict": "allowed", "working_dir": "/home/user/project"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Working Dir:" in html
        assert "/home/user/project" in html

    def test_files_accessed_displayed(self):
        """AC2: Files accessed list is displayed in expanded view."""
        session_data = {
            "session_id": "files_display",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "files_accessed": ["/path/file1.py", "/path/file2.py"]}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Files Accessed" in html
        assert "/path/file1.py" in html
        assert "/path/file2.py" in html

    def test_files_count_shown(self):
        """AC2: Files accessed count is shown."""
        session_data = {
            "session_id": "files_count",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "files_accessed": ["/f1", "/f2", "/f3"]}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Files Accessed (3)" in html


class TestCollapseToggle:
    """Tests for Story 4.4 AC3: Collapse Back."""

    def test_header_has_onclick(self):
        """AC3: Header has onclick handler for toggle."""
        session_data = {
            "session_id": "toggle_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert 'onclick="toggleEvent(0)"' in html

    def test_toggle_function_defined(self):
        """AC3: toggleEvent function is defined."""
        session_data = {"session_id": "toggle_fn", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "function toggleEvent(eventId)" in html

    def test_toggle_adds_expanded_class(self):
        """AC3: Toggle function adds expanded class."""
        session_data = {"session_id": "expanded_class", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "classList.add('expanded')" in html

    def test_toggle_removes_expanded_class(self):
        """AC3: Toggle function removes expanded class."""
        session_data = {"session_id": "remove_class", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "classList.remove('expanded')" in html

    def test_expand_icon_rotation_css(self):
        """AC3: Expand icon rotates when expanded."""
        session_data = {"session_id": "rotation_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".event-card.expanded .expand-icon" in html
        assert "rotate(180deg)" in html

    def test_header_cursor_pointer(self):
        """AC3: Header has cursor pointer for clickability."""
        session_data = {"session_id": "cursor_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "cursor: pointer" in html


class TestNOVAVerdictDetails:
    """Tests for Story 4.4 AC4: NOVA Verdict Details."""

    def test_nova_severity_displayed(self):
        """AC4: nova_severity is displayed for warned events."""
        session_data = {
            "session_id": "severity_test",
            "events": [{
                "tool_name": "Bash",
                "nova_verdict": "warned",
                "nova_severity": "high",
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Severity: high" in html

    def test_nova_rules_matched_displayed(self):
        """AC4: nova_rules_matched is displayed."""
        session_data = {
            "session_id": "rules_test",
            "events": [{
                "tool_name": "Bash",
                "nova_verdict": "blocked",
                "nova_rules_matched": ["dangerous_command", "network_access"],
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Rules matched:" in html
        assert "dangerous_command" in html
        assert "network_access" in html

    def test_nova_scan_time_displayed(self):
        """AC4: nova_scan_time_ms is displayed."""
        session_data = {
            "session_id": "scan_time_test",
            "events": [{
                "tool_name": "Bash",
                "nova_verdict": "warned",
                "nova_scan_time_ms": 42,
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "Scan time: 42ms" in html

    def test_nova_section_only_for_warned_blocked(self):
        """AC4: NOVA section only appears for warned/blocked events."""
        session_data = {
            "session_id": "allowed_no_nova",
            "events": [{
                "tool_name": "Read",
                "nova_verdict": "allowed",
                "nova_severity": "low",  # Should not appear
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "NOVA Analysis" not in html

    def test_nova_section_present_for_warned(self):
        """AC4: NOVA section appears for warned events."""
        session_data = {
            "session_id": "warned_nova",
            "events": [{
                "tool_name": "Bash",
                "nova_verdict": "warned",
                "nova_severity": "medium",
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "NOVA Analysis" in html
        assert 'class="nova-verdict-section"' in html

    def test_nova_section_present_for_blocked(self):
        """AC4: NOVA section appears for blocked events."""
        session_data = {
            "session_id": "blocked_nova",
            "events": [{
                "tool_name": "Bash",
                "nova_verdict": "blocked",
                "nova_severity": "critical",
            }],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "NOVA Analysis" in html

    def test_severity_classes_for_levels(self):
        """AC4: Severity has appropriate CSS classes."""
        session_data = {"session_id": "severity_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".nova-severity.low" in html
        assert ".nova-severity.medium" in html
        assert ".nova-severity.high" in html
        assert ".nova-severity.critical" in html


class TestCodeFormatting:
    """Tests for Story 4.4 AC5: Code Formatting."""

    def test_detail_value_uses_pre(self):
        """AC5: Tool input/output use pre tags."""
        session_data = {
            "session_id": "pre_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "tool_output": "code content"}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert '<pre>' in html

    def test_monospace_font_defined(self):
        """AC5: Monospace font is used for code content."""
        session_data = {"session_id": "mono_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "font-family:" in html
        assert "monospace" in html

    def test_whitespace_preserved(self):
        """AC5: Whitespace is preserved in pre elements."""
        session_data = {"session_id": "whitespace_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert "white-space: pre-wrap" in html

    def test_json_formatted_display(self):
        """AC5: JSON content is formatted for display."""
        session_data = {
            "session_id": "json_format",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "tool_input": {"key": "value", "nested": {"a": 1}}}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        # JSON should be formatted with indentation
        assert '"key":' in html or '"key": ' in html

    def test_detail_value_background(self):
        """AC5: Code content has background for visibility."""
        session_data = {"session_id": "bg_test", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".detail-value" in html
        assert "background:" in html


class TestTruncationIndicator:
    """Tests for Story 4.4 AC6: Truncation Indicator."""

    def test_format_content_truncates_large(self):
        """AC6: Large content is truncated."""
        large_content = "x" * 15000
        result, truncated = _format_content_for_display(large_content, max_size=10000)

        assert truncated is True
        assert len(result) == 10000

    def test_format_content_small_not_truncated(self):
        """AC6: Small content is not truncated."""
        small_content = "small content"
        result, truncated = _format_content_for_display(small_content)

        assert truncated is False
        assert result == small_content

    def test_truncation_indicator_displayed(self):
        """AC6: Truncation indicator shows size info."""
        large_content = "x" * 15000
        session_data = {
            "session_id": "truncation_test",
            "events": [{"tool_name": "Read", "nova_verdict": "allowed", "tool_output": large_content}],
            "summary": {},
        }
        html = generate_html_report(session_data)

        assert "truncated" in html
        assert "original size:" in html
        assert "KB" in html

    def test_truncation_indicator_css(self):
        """AC6: Truncation indicator has styling."""
        session_data = {"session_id": "trunc_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".truncation-indicator" in html

    def test_format_none_returns_empty(self):
        """AC6: None content returns empty string."""
        result, truncated = _format_content_for_display(None)

        assert result == ""
        assert truncated is False

    def test_format_dict_to_json(self):
        """AC6: Dict content is formatted as JSON."""
        content = {"key": "value", "num": 42}
        result, truncated = _format_content_for_display(content)

        assert "key" in result
        assert "value" in result
        assert truncated is False

    def test_format_list_to_json(self):
        """AC6: List content is formatted as JSON."""
        content = [1, 2, 3, "test"]
        result, truncated = _format_content_for_display(content)

        assert "1" in result
        assert "test" in result


class TestExpandedDetailsCSS:
    """Tests for Story 4.4 expanded details styling."""

    def test_event_details_css(self):
        """Event details CSS is defined."""
        session_data = {"session_id": "details_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".event-details" in html

    def test_detail_section_css(self):
        """Detail section CSS is defined."""
        session_data = {"session_id": "section_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".detail-section" in html

    def test_detail_label_css(self):
        """Detail label CSS is defined."""
        session_data = {"session_id": "label_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".detail-label" in html

    def test_files_list_css(self):
        """Files list CSS is defined."""
        session_data = {"session_id": "files_css", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".files-list" in html

    def test_header_hover_effect(self):
        """Event header has hover effect."""
        session_data = {"session_id": "header_hover", "events": [], "summary": {}}
        html = generate_html_report(session_data)

        assert ".event-header:hover" in html
