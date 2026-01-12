# Story 3.2: Report Generator Module

Status: done

## Story

As a **developer building report generation**,
I want **a report generator module that converts session JSON to HTML**,
So that **reports are consistent, self-contained, and portable**.

## Acceptance Criteria

### AC1: Generate HTML from Session Data
**Given** a complete session JSON object
**When** `generate_html_report(session_data)` is called
**Then** it returns a complete HTML string

### AC2: Self-Contained HTML
**Given** the generated HTML
**When** rendered in a browser
**Then** CSS styles are embedded in a `<style>` tag (no external files)
**And** JavaScript is embedded in `<script>` tags (no external files)
**And** session data is embedded as `const SESSION_DATA = {...}`

### AC3: Aggregate Statistics
**Given** session data with events
**When** the report is generated
**Then** aggregate statistics are calculated:
- `total_events`: count of all events
- `tools_used`: object mapping tool names to counts
- `files_touched`: count of unique files in files_accessed
- `warnings`: count of events with `nova_verdict: "warned"`
- `blocked`: count of events with `nova_verdict: "blocked"`

### AC4: Metadata Included
**Given** session data
**When** the report is generated
**Then** metadata is included:
- `session_id`, `session_start`, `session_end`
- `platform`, `nova_version`, `project_dir`
- `duration_seconds`: calculated from start/end

### AC5: Empty Session Handling
**Given** an empty session (no events)
**When** the report is generated
**Then** a valid HTML report is created with zero events displayed
**And** statistics show all counts as 0

## Tasks / Subtasks

- [x] Task 1: Analyze existing implementation (AC: All)
  - [x] 1.1: Review existing report_generator.py from Story 3.1
  - [x] 1.2: Identify gaps vs Story 3.2 requirements
  - [x] 1.3: Plan enhancements needed

- [x] Task 2: Enhance report generator (AC: 2, 4)
  - [x] 2.1: Add nova_version to metadata display
  - [x] 2.2: Add metadata section showing platform, project_dir, timestamps
  - [x] 2.3: Update docstrings and comments
  - [x] 2.4: Add XSS prevention for embedded JSON

- [x] Task 3: Write comprehensive tests (AC: All)
  - [x] 3.1: Test HTML structure (AC1, AC2)
  - [x] 3.2: Test statistics calculation (AC3)
  - [x] 3.3: Test metadata inclusion (AC4)
  - [x] 3.4: Test empty session handling (AC5)
  - [x] 3.5: Test XSS prevention

- [x] Task 4: Run full test suite and verify
  - [x] 4.1: Run pytest on all tests
  - [x] 4.2: Verify all 261 tests pass

## Dev Notes

### Current Implementation Status

The `report_generator.py` module was created in Story 3.1 with most Story 3.2 features:

**Already Implemented:**
- `generate_html_report(session_data)` returns complete HTML
- CSS embedded in `<style>` tag
- JavaScript with `const SESSION_DATA = {...}`
- Statistics: total_events, tools_used, files_touched, warnings, blocked
- duration_seconds calculation and display
- Empty session handling

**Needs Enhancement:**
- Add `nova_version` to displayed metadata
- Show platform and project_dir in report
- Display session_start and session_end timestamps
- Comprehensive tests for all criteria

### NOVA Version

The NOVA version should come from the nova-framework package or be stored in a constant.

### References

- [Source: epics.md#Story 3.2] - Original acceptance criteria
- [Source: hooks/lib/report_generator.py] - Existing implementation

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 261 tests pass (47 new report generator tests + 214 existing)
- Test run duration: ~15 minutes

### Completion Notes List

1. Enhanced `hooks/lib/report_generator.py` with:
   - `NOVA_VERSION = "0.1.0"` constant for version tracking
   - `_format_timestamp()` helper for ISO timestamp display
   - `_json_for_html()` helper for XSS-safe JSON embedding
   - Metadata section showing platform, project_dir, session_start, session_end, NOVA Version
   - Updated footer with version information
2. Added XSS prevention by escaping `<`, `>`, `&` in embedded SESSION_DATA JSON
3. Created comprehensive test suite `tests/test_report_generator.py` with 47 tests covering:
   - AC1: HTML generation (3 tests)
   - AC2: Self-contained HTML (5 tests)
   - AC3: Aggregate statistics (5 tests)
   - AC4: Metadata inclusion (7 tests)
   - AC5: Empty session handling (7 tests)
   - Health status display (3 tests)
   - Event display (4 tests)
   - Timestamp formatting (4 tests)
   - Save report functionality (3 tests)
   - Duration formatting (3 tests)
   - XSS prevention (3 tests)

### File List

**Modified:**
- `hooks/lib/report_generator.py` - Enhanced with metadata section and XSS prevention

**Created:**
- `tests/test_report_generator.py` - 47 comprehensive tests for Story 3.2
