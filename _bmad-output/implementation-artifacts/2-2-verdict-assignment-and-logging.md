# Story 2.2: Verdict Assignment and Logging

Status: done

## Story

As a **security analyst**,
I want **to see clear verdicts and matched rules for each event**,
So that **I can quickly identify and investigate threats**.

## Acceptance Criteria

### AC1: No Matches - Allowed Verdict
**Given** NOVA scans an event with no rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"allowed"`
**And** `nova_severity` is set to `null`
**And** `nova_rules_matched` is an empty array

### AC2: Warning-Level Match
**Given** NOVA scans an event and a warning-level rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"warned"`
**And** `nova_severity` is set to the matched rule's severity (e.g., "medium")
**And** `nova_rules_matched` contains the rule name(s)

### AC3: Critical-Level Match (High Severity)
**Given** NOVA scans an event and a high-severity rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"blocked"` (for reporting purposes)
**And** `nova_severity` is set to `"high"`
**And** `nova_rules_matched` contains the rule name(s)

### AC4: Multiple Rules Match
**Given** multiple rules match an event
**When** the verdict is assigned
**Then** the highest severity determines the verdict
**And** all matched rule names are included in `nova_rules_matched`

### AC5: Scan Time Recording
**Given** an event is scanned
**When** the scan completes
**Then** `nova_scan_time_ms` records the scan duration in milliseconds

## Tasks / Subtasks

- [x] Task 1: Review existing verdict implementation (AC: All)
  - [x] 1.1: Check verdict assignment logic in post-tool-nova-guard.py
  - [x] 1.2: Verify severity mapping (high/medium/low)
  - [x] 1.3: Verify scan time recording

- [x] Task 2: Write comprehensive tests for verdict assignment (AC: All)
  - [x] 2.1: Test no-match returns allowed verdict (AC1)
  - [x] 2.2: Test medium severity returns warned verdict (AC2)
  - [x] 2.3: Test high severity returns blocked verdict (AC3)
  - [x] 2.4: Test multiple rules - highest severity wins (AC4)
  - [x] 2.5: Test scan time is recorded (AC5)
  - [x] 2.6: Test all matched rules are captured

- [x] Task 3: Verify event capture includes all fields (AC: All)
  - [x] 3.1: Test captured events have nova_verdict field
  - [x] 3.2: Test captured events have nova_severity field
  - [x] 3.3: Test captured events have nova_rules_matched array
  - [x] 3.4: Test captured events have nova_scan_time_ms field

- [x] Task 4: Run full test suite and verify
  - [x] 4.1: Run pytest on all tests
  - [x] 4.2: Verify all 157 tests pass

## Dev Notes

### Current Implementation Status

**Already Implemented in post-tool-nova-guard.py:**
- ✅ AC1: No matches → `allowed`, `null`, `[]` (default values)
- ✅ AC2: Medium severity → `warned`, `"medium"`, `[rules]`
- ✅ AC3: High severity → `blocked`, `"high"`, `[rules]`
- ✅ AC4: Multiple rules → highest severity wins, all rules captured
- ✅ AC5: `nova_scan_time_ms` recorded in milliseconds

### Severity Mapping

| NOVA Rule Severity | nova_verdict | nova_severity |
|-------------------|--------------|---------------|
| (no match) | allowed | null |
| low | warned | low |
| medium | warned | medium |
| high | blocked | high |

**Note:** The PRD mentions "critical" but NOVA rules use "high" as the highest severity. We map "high" → "blocked" to match the intent.

### Event Record Fields

```python
event_record = {
    "nova_verdict": "allowed" | "warned" | "blocked" | "scan_failed",
    "nova_severity": None | "low" | "medium" | "high",
    "nova_rules_matched": [],  # List of rule names
    "nova_scan_time_ms": 0,    # Integer milliseconds
}
```

### Test Strategy

Story 2.2 is primarily about verification - the implementation exists. Tests will:
1. Verify verdict logic with mock detections
2. Verify event capture includes all NOVA fields
3. Verify multiple rule handling
4. Verify timing recording

### References

- [Source: architecture.md#Security Protection] - Verdict handling
- [Source: epics.md#Story 2.2] - Original acceptance criteria
- [Source: hooks/post-tool-nova-guard.py:556-570] - Verdict assignment logic

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 157 tests pass (22 new verdict assignment tests + 135 existing)
- Test run duration: 405.34s

### Completion Notes List

1. Reviewed existing verdict logic in post-tool-nova-guard.py - all ACs already implemented
2. Created comprehensive test suite with 22 tests covering all acceptance criteria:
   - AC1: No matches → allowed verdict with null severity (3 tests)
   - AC2: Warning-level matches → warned verdict (3 tests)
   - AC3: High severity → blocked verdict (2 tests)
   - AC4: Multiple rules → highest severity wins (4 tests)
   - AC5: Scan time recording (2 tests)
   - Event capture NOVA fields (4 tests)
   - Edge cases (4 tests)
3. Fixed test issue: NOVA library outputs debug messages to stdout, updated test to handle non-JSON output

### File List

**Created:**
- `tests/test_verdict_assignment.py` - 22 tests for verdict assignment and logging
