# Story 3.1: Session End Hook

Status: done

## Story

As a **Claude Code user**,
I want **an HTML report generated automatically when my session ends**,
So that **I always have a complete audit trail without manual action**.

## Acceptance Criteria

### AC1: Generate HTML Report on Session End
**Given** a Claude Code session ends normally
**When** the SessionEnd hook fires
**Then** the session `.jsonl` file is finalized
**And** events are converted to a complete session `.json` file
**And** an HTML report is generated at `.nova-protector/reports/{session_id}.html`

### AC2: Predictable Report Path
**Given** a session with captured events
**When** the report is generated
**Then** the report path is predictable: `{project}/.nova-protector/reports/{session_id}.html`
**And** the report filename matches the session ID

### AC3: Graceful Handling of Corrupted Data
**Given** the session JSON is partially corrupted
**When** the SessionEnd hook runs
**Then** it generates a partial report with available events
**And** logs the corruption warning to stderr
**And** never fails completely (100% generation success)

### AC4: Performance Target
**Given** report generation is measured
**When** a session with 500 events completes
**Then** the total generation time is < 3 seconds

### AC5: Fail-Open Error Handling
**Given** any error occurs during report generation
**When** the error is handled
**Then** it logs to stderr and exits 0 (fail-open)
**And** a partial or error report is created if possible

## Tasks / Subtasks

- [x] Task 1: Analyze session-end requirements (AC: All)
  - [x] 1.1: Review session_manager.py for finalization functions
  - [x] 1.2: Review Claude Code hooks API for SessionEnd
  - [x] 1.3: Design report generation flow

- [x] Task 2: Implement session-end.py hook (AC: All)
  - [x] 2.1: Create basic hook structure with stdin parsing
  - [x] 2.2: Implement JSONL to JSON conversion
  - [x] 2.3: Call report generator (placeholder for Story 3.2)
  - [x] 2.4: Implement fail-open error handling
  - [x] 2.5: Mark session as finalized

- [x] Task 3: Extend session_manager.py (AC: 1, 3)
  - [x] 3.1: Add read_session_events() function
  - [x] 3.2: Add finalize_session() to convert JSONL → JSON
  - [x] 3.3: Handle corrupted line parsing gracefully

- [x] Task 4: Write tests for session-end hook (AC: All)
  - [x] 4.1: Test hook creates report file (AC1)
  - [x] 4.2: Test report path matches session ID (AC2)
  - [x] 4.3: Test partial report on corrupted data (AC3)
  - [x] 4.4: Test fail-open on errors (AC5)

- [x] Task 5: Run full test suite and verify
  - [x] 5.1: Run pytest on all tests
  - [x] 5.2: Verify all 214 tests pass

## Dev Notes

### SessionEnd Hook Input Format

The SessionEnd hook receives:
```json
{
  "session_id": "abc123",
  "session_start_time": "2024-01-01T00:00:00Z",
  "session_end_time": "2024-01-01T01:00:00Z"
}
```

### Report Generation Flow

```
SessionEnd hook fires
    ↓
Read active session from marker
    ↓
Read all events from .jsonl file
    ↓
Construct complete session object
    ↓
Generate AI summary (Story 3.3)
    ↓
Generate HTML report (Story 3.2)
    ↓
Save to .nova-protector/reports/{session_id}.html
    ↓
Remove active session marker
    ↓
Exit 0
```

### Session Object Structure

```python
session = {
    "session_id": "2024-01-01_12-00-00_abc123",
    "session_start": "2024-01-01T12:00:00Z",
    "session_end": "2024-01-01T13:00:00Z",
    "platform": "darwin",
    "project_dir": "/path/to/project",
    "events": [...],  # List of event records
    "summary": {
        "ai_summary": "...",  # From Story 3.3
        "total_events": 42,
        "tools_used": {"Read": 10, "Bash": 5, ...},
        "files_touched": 15,
        "warnings": 2,
        "blocked": 0,
        "duration_seconds": 3600
    }
}
```

### Dependencies

- Story 3.2: Report Generator Module (can use placeholder initially)
- Story 3.3: AI Summary Module (can use placeholder initially)

For this story, we can create placeholder functions that return minimal HTML
and stats-only summaries, then implement the full versions in Stories 3.2/3.3.

### Existing Functions in session_manager.py

Already implemented:
- `generate_session_id()` - Creates session IDs
- `get_session_paths()` - Gets session/report directories
- `init_session_file()` - Creates new session JSONL
- `append_event()` - Appends events to JSONL
- `get_active_session()` - Gets current active session
- `finalize_session()` - Removes active marker
- `read_session_events()` - Reads events from JSONL

May need to add/extend:
- `convert_jsonl_to_json()` - Convert JSONL to complete JSON
- `get_session_statistics()` - Calculate aggregate stats

### References

- [Source: architecture.md#Report Generation] - Report generation flow
- [Source: epics.md#Story 3.1] - Original acceptance criteria
- [Source: hooks/lib/session_manager.py] - Session management functions

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 214 tests pass (29 new session end tests + 185 existing)
- Test run duration: ~8.5 minutes

### Completion Notes List

1. Created `hooks/session-end.py` implementing SessionEnd hook
2. Extended `hooks/lib/session_manager.py` with:
   - `calculate_session_statistics()` - Aggregate stats from events
   - `build_session_object()` - Complete session object for report generation
3. Created `hooks/lib/report_generator.py` with:
   - `generate_html_report()` - Self-contained HTML with embedded CSS
   - `save_report()` - File writing with parent directory creation
4. Implemented fail-open error handling (exit 0 on any exception)
5. Created comprehensive test suite with 29 tests covering all acceptance criteria
6. Report includes health status (CLEAN/WARNINGS/BLOCKED), stats, tools breakdown, event timeline

### File List

**Created:**
- `hooks/session-end.py` - SessionEnd hook
- `hooks/lib/report_generator.py` - HTML report generator
- `tests/test_session_end_hook.py` - 29 tests for session end functionality

**Modified:**
- `hooks/lib/session_manager.py` - Added statistics and session building functions
