# Story 1.3: Basic Event Capture

Status: done

## Story

As a **Claude Code user**,
I want **every tool call to be captured with full details**,
So that **I have complete visibility into what Claude did**.

## Acceptance Criteria

### AC1: Event Record Capture
**Given** Claude executes a tool (Read, Edit, Bash, etc.)
**When** the PostToolUse hook fires
**Then** an event record is appended to the session `.jsonl`

### AC2: Event Record Structure
**Given** an event is captured
**When** the record is written
**Then** it includes: id (sequential integer), tool_name, tool_input, tool_output
**And** it includes: timestamp_start, timestamp_end, duration_ms

### AC3: Sequential Event IDs
**Given** multiple tool calls in a session
**When** events are captured
**Then** each event has a unique sequential id starting from 1
**And** ids increment correctly even across hook invocations

### AC4: Output Truncation
**Given** tool_output exceeds 10KB
**When** the event is captured
**Then** the output is truncated to 10KB with a truncation marker
**And** the full output size is noted in the record

### AC5: Performance
**Given** the capture overhead is measured
**When** an event is processed
**Then** the total hook execution time is < 1ms (excluding I/O)

## Tasks / Subtasks

- [x] Task 1: Extend post-tool-nova-guard.py to capture events (AC: 1, 2)
  - [x] 1.1: Add imports for session_manager module (same pattern as session-start.py)
  - [x] 1.2: Capture timestamp_start at hook entry
  - [x] 1.3: Capture timestamp_end after processing completes
  - [x] 1.4: Calculate duration_ms from timestamps
  - [x] 1.5: Build event record dict with all required fields

- [x] Task 2: Implement sequential event ID tracking (AC: 3)
  - [x] 2.1: Add `get_next_event_id(session_id, project_dir)` to session_manager
  - [x] 2.2: Read last event ID from session file
  - [x] 2.3: Return incremented ID (starting from 1 if no events)
  - [x] 2.4: Handle concurrent access gracefully (file-based locking or atomic)
  - [x] 2.5: Write unit tests for event ID tracking

- [x] Task 3: Implement output truncation (AC: 4)
  - [x] 3.1: Add `truncate_output(text, max_bytes)` helper function
  - [x] 3.2: If output > 10KB, truncate to 10KB with marker `[TRUNCATED - original size: X KB]`
  - [x] 3.3: Add `original_output_size` field to event record when truncated
  - [x] 3.4: Make truncation limit configurable (default 10KB = 10240 bytes)
  - [x] 3.5: Write unit tests for output truncation

- [x] Task 4: Integrate event capture into hook flow (AC: 1, 2)
  - [x] 4.1: Get active session ID using `get_active_session(project_dir)`
  - [x] 4.2: If no active session, skip capture (log warning, fail-open)
  - [x] 4.3: Call `append_event()` after NOVA scan completes
  - [x] 4.4: Include NOVA verdict fields in event record (placeholder until Story 2.x)
  - [x] 4.5: Ensure fail-open: event capture errors never block hook

- [x] Task 5: Performance optimization and testing (AC: 5)
  - [x] 5.1: Measure baseline hook execution time
  - [x] 5.2: Optimize hot path (minimize allocations, avoid redundant parsing)
  - [x] 5.3: Write performance test verifying < 1ms overhead (excluding I/O)
  - [x] 5.4: Write integration tests for full capture flow

## Dev Notes

### Architecture Requirements

**Hook to Extend:** `hooks/post-tool-nova-guard.py`

This story EXTENDS the existing hook (437 lines) - do NOT rewrite from scratch.

**Integration Points:**
- Import session_manager module at top
- Capture timestamps at entry/exit
- Build event record after NOVA scan
- Call `append_event()` before exit

### Import Pattern (MUST match Story 1.1 and 1.2)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session_manager import (
    get_active_session,
    append_event,
    get_next_event_id,  # New function to add
)
```

### Event Record Schema (from architecture.md)

```json
{
  "type": "event",
  "id": 1,
  "timestamp_start": "2026-01-10T16:30:46Z",
  "timestamp_end": "2026-01-10T16:30:46Z",
  "duration_ms": 123,
  "tool_name": "Read",
  "tool_input": {},
  "tool_output": "...",
  "working_dir": "/path",
  "files_accessed": [],
  "nova_verdict": "allowed",
  "nova_severity": null,
  "nova_rules_matched": [],
  "nova_scan_time_ms": 5
}
```

**Note:** `files_accessed` and NOVA fields are implemented in Story 1.4 and Epic 2. For now:
- `files_accessed`: `[]` (empty array - placeholder)
- `nova_verdict`: `"allowed"` (placeholder)
- `nova_severity`: `null` (placeholder)
- `nova_rules_matched`: `[]` (placeholder)
- `nova_scan_time_ms`: `0` (placeholder)

### Output Truncation Pattern

```python
MAX_OUTPUT_SIZE = 10 * 1024  # 10KB default

def truncate_output(text: str, max_bytes: int = MAX_OUTPUT_SIZE) -> tuple[str, Optional[int]]:
    """Truncate output if exceeds max_bytes.

    Returns:
        tuple of (truncated_text, original_size_or_None)
    """
    encoded = text.encode('utf-8')
    if len(encoded) <= max_bytes:
        return text, None

    # Truncate at byte boundary, decode safely
    truncated = encoded[:max_bytes].decode('utf-8', errors='ignore')
    original_size = len(encoded)
    marker = f"\n[TRUNCATED - original size: {original_size / 1024:.1f} KB]"

    return truncated + marker, original_size
```

### Sequential ID Implementation

Option A: Read last ID from file (simple but slower):
```python
def get_next_event_id(session_id: str, project_dir: str) -> int:
    """Get next sequential event ID for session."""
    events = read_session_events(session_id, project_dir)
    if not events:
        return 1
    # Find max ID among events (not init record)
    event_ids = [e.get("id", 0) for e in events if e.get("type") == "event"]
    return max(event_ids, default=0) + 1
```

Option B: Track in separate counter file (faster but more complex):
```python
def get_next_event_id(session_id: str, project_dir: str) -> int:
    """Get next event ID using atomic counter file."""
    counter_file = Path(project_dir) / ".nova-protector" / "sessions" / f".{session_id}.counter"
    # Read, increment, write atomically
    ...
```

**Recommendation:** Start with Option A for simplicity. If performance tests fail, refactor to Option B.

### Integration into main() Flow

```python
def main() -> None:
    """Main entry point for the PostToolUse hook."""
    # Capture start timestamp FIRST
    timestamp_start = datetime.now(timezone.utc)

    # ... existing config and rules loading ...

    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # ... existing tool processing and NOVA scan ...

    # Capture end timestamp
    timestamp_end = datetime.now(timezone.utc)
    duration_ms = int((timestamp_end - timestamp_start).total_seconds() * 1000)

    # Build event record
    project_dir = os.getcwd()
    active_session = get_active_session(project_dir)

    if active_session:
        event_id = get_next_event_id(active_session, project_dir)

        # Truncate output if needed
        tool_output_str = extract_text_content(tool_name, tool_result)
        truncated_output, original_size = truncate_output(tool_output_str)

        event_record = {
            "type": "event",
            "id": event_id,
            "timestamp_start": timestamp_start.isoformat(),
            "timestamp_end": timestamp_end.isoformat(),
            "duration_ms": duration_ms,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": truncated_output,
            "original_output_size": original_size,  # None if not truncated
            "working_dir": project_dir,
            "files_accessed": [],  # Placeholder - Story 1.4
            "nova_verdict": "allowed",  # Placeholder - Epic 2
            "nova_severity": None,
            "nova_rules_matched": [],
            "nova_scan_time_ms": 0,
        }

        append_event(active_session, project_dir, event_record)

    # ... existing warning output logic ...

    sys.exit(0)
```

### Performance Requirements

| Operation | Target | Notes |
|-----------|--------|-------|
| Hook execution overhead | < 1ms | Excluding I/O (file reads/writes) |
| Event append | < 0.5ms | Already verified in Story 1.1 |
| ID lookup | < 0.5ms | May need optimization |

### Testing Strategy

**Unit Tests (test_event_capture.py):**
1. Event record structure validation
2. Sequential ID generation
3. Output truncation (various sizes)
4. Fail-open behavior on errors

**Integration Tests:**
1. Full hook execution with event capture
2. Multiple events in single session
3. Session resume with continued IDs
4. Large output truncation

### Previous Story Intelligence (Stories 1.1, 1.2)

**From Story 1.1:**
- Python 3.9 compatibility: Use `Union[X, Y]` not `X | Y`
- Fail-open pattern: Return bool/None, never raise
- Performance: append_event < 0.5ms verified

**From Story 1.2:**
- macOS path symlink: Use `Path().resolve()` for comparisons
- stdin parsing: Handle empty, invalid JSON gracefully
- Logging: stderr only, never stdout

### Existing Code to Preserve

The existing `post-tool-nova-guard.py` has:
- NOVA scanning logic (lines 189-244) - KEEP
- Tool monitoring logic (lines 374-388) - KEEP
- Warning formatting (lines 247-306) - KEEP
- Config loading (lines 47-97) - KEEP

Only ADD event capture logic, don't remove existing functionality.

### References

- [Source: architecture.md#Session Data Architecture] - Event record schema
- [Source: architecture.md#Performance Architecture] - < 1ms requirement
- [Source: epics.md#Story 1.3] - Original acceptance criteria
- [Source: hooks/post-tool-nova-guard.py] - Existing code to extend
- [Source: Story 1.1 Dev Agent Record] - session_manager patterns
- [Source: Story 1.2 Dev Agent Record] - Hook implementation patterns

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No significant debug issues encountered
- All acceptance criteria verified through 26 new tests

### Completion Notes List

- All 26 new tests passing (test_event_capture.py)
- Full regression: 68 tests passing (25 session_manager + 17 session_start + 26 event_capture)
- Added `get_next_event_id()` and `truncate_output()` to session_manager.py
- Extended post-tool-nova-guard.py to capture ALL tool calls (not just monitored)
- Event capture is fail-open: errors never block the hook
- Output truncation at 10KB with marker including original size
- Sequential IDs verified through integration tests
- Performance verified: truncate_output < 1ms, append_event < 2ms average
- NOVA verdict fields integrated (placeholder values until Epic 2)

### File List

- `hooks/lib/session_manager.py` - Extended with get_next_event_id, truncate_output (now 340 lines)
- `hooks/lib/__init__.py` - Updated exports
- `hooks/post-tool-nova-guard.py` - Extended with event capture (now 543 lines)
- `tests/test_event_capture.py` - Comprehensive test suite with 26 tests

