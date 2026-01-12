# Story 1.2: Session Initialization Hook

Status: done

## Story

As a **Claude Code user**,
I want **sessions to automatically start recording when I begin working**,
So that **no tool calls are missed from the start**.

## Acceptance Criteria

### AC1: New Session Initialization
**Given** Claude Code starts a new session
**When** the SessionStart hook fires
**Then** a new session ID is generated
**And** a session `.jsonl` file is created in `.nova-protector/sessions/`
**And** the init record contains: session_id, session_start timestamp, platform, project_dir

### AC2: Session Resume Detection
**Given** Claude Code resumes an existing session
**When** the SessionStart hook fires
**Then** the hook detects the existing active session
**And** continues appending to the existing `.jsonl` file

### AC3: Fail-Open Error Handling
**Given** any error occurs during initialization
**When** the hook processes the error
**Then** it logs to stderr and exits 0 (fail-open)
**And** Claude Code operation is not blocked

## Tasks / Subtasks

- [x] Task 1: Create session-start.py hook skeleton (AC: 1, 2, 3)
  - [x] 1.1: Create `hooks/session-start.py` with PEP 723 inline metadata
  - [x] 1.2: Add shebang, docstring, and hook metadata block
  - [x] 1.3: Import session_manager module using established path pattern
  - [x] 1.4: Implement main() function with basic structure

- [x] Task 2: Implement new session initialization (AC: 1)
  - [x] 2.1: Read hook input from stdin (JSON format)
  - [x] 2.2: Extract project_dir from hook context (cwd or session_id parsing)
  - [x] 2.3: Call `generate_session_id()` from session_manager
  - [x] 2.4: Call `init_session_file()` to create `.jsonl` with init record
  - [x] 2.5: Write unit tests for new session initialization flow

- [x] Task 3: Implement session resume detection (AC: 2)
  - [x] 3.1: Call `get_active_session()` to check for existing session
  - [x] 3.2: If active session exists, skip initialization
  - [x] 3.3: Log resume action to stderr for debugging
  - [x] 3.4: Write unit tests for session resume detection

- [x] Task 4: Implement fail-open error handling (AC: 3)
  - [x] 4.1: Wrap all logic in try/except with proper error handling
  - [x] 4.2: Log errors to stderr (never stdout - reserved for Claude feedback)
  - [x] 4.3: Always exit 0 regardless of errors
  - [x] 4.4: Write unit tests verifying fail-open behavior

- [x] Task 5: Integration testing (AC: 1, 2, 3)
  - [x] 5.1: Create test for full hook execution with stdin input
  - [x] 5.2: Verify .jsonl file creation with correct init record
  - [x] 5.3: Verify session resume skips new file creation
  - [x] 5.4: Run manual integration test with Claude Code (optional)

## Dev Notes

### Architecture Requirements

**Hook Location:** `hooks/session-start.py`

**Hook Event:** `SessionStart` - Fires when Claude Code session starts or resumes

**This hook uses the session_manager module** created in Story 1.1:
- `generate_session_id()` - Creates unique session ID
- `init_session_file()` - Creates `.jsonl` with init record
- `get_active_session()` - Detects existing active session
- `get_session_paths()` - Gets storage directory paths

### Claude Code Hooks API Reference

**SessionStart Hook Input (stdin JSON):**
```json
{
  "session_id": "abc123",
  "event": "session_start"
}
```

**Hook Output:**
- stdout: Optional JSON feedback for Claude (usually empty for SessionStart)
- stderr: Logging/debug output
- Exit code: 0 = success, 2 = block (not applicable for SessionStart)

**Exit Code Rules:**
- Always exit 0 for SessionStart (cannot block session start)
- Fail-open: even on errors, exit 0

### Import Pattern (MUST use exactly as Story 1.1)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session_manager import (
    generate_session_id,
    get_session_paths,
    init_session_file,
    get_active_session,
)
```

### PEP 723 Inline Metadata Template

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
NOVA Claude Code Protector - Session Start Hook

Initializes session capture when Claude Code session starts.
Creates .jsonl file for event logging.
"""
```

### JSON Schema Reference (from Story 1.1)

**Init Record Schema:**
```json
{"type": "init", "session_id": "2026-01-10_16-30-45_a1b2c3", "timestamp": "2026-01-10T16:30:45Z", "platform": "darwin", "project_dir": "/path/to/project"}
```

### Error Handling Pattern (CRITICAL)

**Fail-open philosophy:** This hook must NEVER crash or block Claude Code.

```python
def main():
    try:
        # Parse stdin
        hook_input = json.load(sys.stdin)

        # Get project directory (cwd is the project)
        project_dir = os.getcwd()

        # Check for existing active session
        active_session = get_active_session(project_dir)
        if active_session:
            logger.debug(f"Resuming existing session: {active_session}")
            sys.exit(0)

        # Create new session
        session_id = generate_session_id()
        result = init_session_file(session_id, project_dir)

        if result:
            logger.debug(f"Session initialized: {session_id}")
        else:
            logger.warning("Failed to initialize session file")

    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON input: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    # Always exit 0 - never block Claude Code
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Logging Pattern (MUST follow)

```python
import logging
logging.basicConfig(
    level=logging.WARNING,
    format="[NOVA %(levelname)s] %(message)s",
    stream=sys.stderr  # CRITICAL: Never use stdout
)
logger = logging.getLogger("nova-protector.session-start")
```

### Storage Paths (from session_manager)

```
{project}/.nova-protector/
├── sessions/
│   ├── {session_id}.jsonl    # Created by this hook
│   └── .active               # Marker file with current session ID
└── reports/
    └── {session_id}.html     # Created by session-end hook (later)
```

### Performance Requirements

| Operation | Target | Notes |
|-----------|--------|-------|
| Hook execution | < 50ms | Including stdin parsing and file I/O |
| Session file creation | < 10ms | Uses session_manager functions |

### Previous Story Intelligence (Story 1.1)

**Learnings from Story 1.1:**
- Python 3.9 compatibility: Use `Union[str, Path]` not `str | Path`
- Timing edge cases: Allow tolerance for timestamp comparisons
- Fail-open: All functions return bool or None, never raise
- Active session tracking: Uses `.active` marker file pattern

**Functions available from session_manager.py:**
- `generate_session_id() -> str` - Returns `YYYY-MM-DD_HH-MM-SS_abc123`
- `get_session_paths(project_dir) -> Dict[str, Path]` - Returns {"sessions": Path, "reports": Path}
- `init_session_file(session_id, project_dir) -> Optional[Path]` - Creates .jsonl, returns path
- `get_active_session(project_dir) -> Optional[str]` - Returns session_id if active
- `finalize_session(session_id, project_dir) -> Optional[Path]` - Removes active marker
- `append_event(session_id, project_dir, event_data) -> bool` - Appends event line
- `read_session_events(session_id, project_dir) -> List[Dict]` - Reads all events

### Testing Framework

Use `pytest` for all tests. Test file: `tests/test_session_start.py`

**Test Categories:**
1. New session initialization (stdin parsing, file creation)
2. Session resume detection (active session handling)
3. Fail-open behavior (error scenarios)
4. Integration with session_manager module

### Project Structure Notes

- Hook goes in `hooks/` directory alongside existing `post-tool-nova-guard.py`
- Uses `hooks/lib/session_manager.py` from Story 1.1
- No new directories needed
- Will be registered in `~/.claude/settings.json` by install.sh (Epic 5)

### References

- [Source: architecture.md#Claude Code Hooks API] - Hook input/output format
- [Source: architecture.md#Hook Architecture] - SessionStart hook specification
- [Source: architecture.md#Implementation Patterns] - Error handling, logging
- [Source: epics.md#Story 1.2] - Original acceptance criteria
- [Source: Story 1.1 Dev Agent Record] - Previous learnings and patterns

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Fixed macOS path symlink issue: `/var/folders/...` resolves to `/private/var/folders/...` on macOS, causing path comparison failures in tests. Fixed by using `Path().resolve()` for consistent path comparisons.

### Completion Notes List

- All 17 tests passing (0.28s execution time)
- Full regression: 42 tests passing (25 session_manager + 17 session_start)
- Fail-open philosophy implemented: hook always exits 0
- Session resume detection via `.active` marker file
- stdin parsing handles: valid JSON, empty input, invalid JSON
- Logging to stderr only (stdout reserved for Claude feedback)
- PEP 723 inline metadata for dependency management
- Python 3.9+ compatible (uses `Union` from typing, not `|` syntax)

### File List

- `hooks/session-start.py` - SessionStart hook implementation (159 lines)
- `tests/test_session_start.py` - Comprehensive test suite with 17 tests (358 lines)

