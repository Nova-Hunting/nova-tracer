# Story 2.3: Pre-Tool Blocking Hook

Status: done

## Story

As a **Claude Code user**,
I want **critical threats blocked before execution**,
So that **dangerous actions are prevented, not just logged**.

## Acceptance Criteria

### AC1: Scan Tool Inputs in PreToolUse
**Given** Claude is about to execute a tool
**When** the PreToolUse hook fires
**Then** the tool_input is scanned against NOVA rules

### AC2: Block Critical-Severity Matches
**Given** NOVA detects a critical-severity (high) match in PreToolUse
**When** the scan result is evaluated
**Then** the hook exits with code 2 (block)
**And** outputs JSON: `{"decision": "block", "reason": "[NOVA] Blocked: {rule_name}"}`
**And** Claude receives the block message

### AC3: Allow Warning-Severity Matches
**Given** NOVA detects a warning-severity match in PreToolUse
**When** the scan result is evaluated
**Then** the hook exits with code 0 (allow)
**And** the warning is logged for PostToolUse capture

### AC4: Allow No Matches
**Given** NOVA scan finds no matches in PreToolUse
**When** the scan completes
**Then** the hook exits with code 0 (allow)
**And** no output is sent to stdout

### AC5: Fail-Open on Error
**Given** the PreToolUse hook encounters any error
**When** the error is handled
**Then** it logs to stderr and exits 0 (fail-open)
**And** the tool execution proceeds

## Tasks / Subtasks

- [x] Task 1: Analyze existing post-tool hook structure (AC: All)
  - [x] 1.1: Review post-tool-nova-guard.py for reusable patterns
  - [x] 1.2: Identify shared functions (load_config, get_rules_directory, scan_with_nova)
  - [x] 1.3: Document exit code requirements (2=block, 0=allow)

- [x] Task 2: Implement PreToolUse hook (AC: All)
  - [x] 2.1: Create pre-tool-guard.py with input scanning
  - [x] 2.2: Implement exit code 2 for high severity (block)
  - [x] 2.3: Implement exit code 0 for medium/low severity (allow)
  - [x] 2.4: Implement fail-open error handling

- [x] Task 3: Write tests for PreToolUse blocking (AC: All)
  - [x] 3.1: Test high severity returns exit code 2 (AC2)
  - [x] 3.2: Test medium severity returns exit code 0 (AC3)
  - [x] 3.3: Test no matches returns exit code 0 (AC4)
  - [x] 3.4: Test errors return exit code 0 (AC5)
  - [x] 3.5: Test JSON output format for blocks

- [x] Task 4: Run full test suite and verify
  - [x] 4.1: Run pytest on all tests
  - [x] 4.2: Verify all 185 tests pass

## Dev Notes

### PreToolUse vs PostToolUse

| Aspect | PreToolUse | PostToolUse |
|--------|------------|-------------|
| Timing | BEFORE execution | AFTER execution |
| Exit 0 | Allow tool | Allow with optional warning |
| Exit 2 | Block tool | N/A (tool already ran) |
| Input | tool_name, tool_input | tool_name, tool_input, tool_response |
| Scans | tool_input only | tool_input + tool_output |
| Purpose | Prevent dangerous actions | Warn about suspicious content |

### Exit Code Semantics

| Exit Code | Meaning | When to Use |
|-----------|---------|-------------|
| 0 | Allow | No threats, warnings only, or errors |
| 2 | Block | High-severity detection |

### Block JSON Output Format

```json
{
  "decision": "block",
  "reason": "[NOVA] Blocked: {rule_name} - {description}"
}
```

### Shared Code Strategy

The pre-tool hook will reuse functions from post-tool-nova-guard.py:
- `load_config()` - Load NOVA configuration
- `get_rules_directory()` - Find rules directory
- `scan_with_nova()` - Perform NOVA scan
- `extract_input_text()` - Extract scannable text from tool_input
- `filter_by_severity()` - Filter detections

These functions can be imported by adding the hooks directory to sys.path.

### Tools to Scan in PreToolUse

Focus on tools that could execute dangerous actions:
- `Bash` - Shell commands
- `Write` - File writes
- `Edit` - File modifications
- `Task` - Agent prompts (could contain injection)

Read-only tools (Read, Grep, Glob, WebFetch) are lower priority since they
don't modify state, but we scan them anyway for consistency.

### References

- [Source: architecture.md#Security Protection] - PreToolUse blocking hook
- [Source: epics.md#Story 2.3] - Original acceptance criteria
- [Source: hooks/post-tool-nova-guard.py] - Existing patterns to reuse

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 185 tests pass (28 new pre-tool blocking tests + 157 existing)
- Test run duration: 558.87s

### Completion Notes List

1. Created `hooks/pre-tool-guard.py` implementing PreToolUse hook
2. Reused patterns from post-tool-nova-guard.py (load_config, get_rules_directory, scan_with_nova, extract_input_text, filter_by_severity)
3. Implemented exit code 2 for high-severity blocks with JSON output format
4. Implemented exit code 0 for medium/low severity (allow - warnings captured by PostToolUse)
5. Implemented fail-open error handling (exit 0 on any exception)
6. Created comprehensive test suite with 28 tests covering all acceptance criteria

### File List

**Created:**
- `hooks/pre-tool-guard.py` - PreToolUse blocking hook
- `tests/test_pre_tool_blocking.py` - 28 tests for pre-tool blocking
