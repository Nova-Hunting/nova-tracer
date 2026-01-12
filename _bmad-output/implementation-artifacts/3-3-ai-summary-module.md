# Story 3.3: AI Summary Module

Status: done

## Story

As a **Claude Code user**,
I want **an AI-generated summary of my session**,
So that **I can understand what happened in 10 seconds**.

## Acceptance Criteria

### AC1: Generate AI Summary via API
**Given** a session with events
**When** `generate_ai_summary(session_data)` is called
**Then** it calls the Claude Haiku API with a summary prompt
**And** returns a 2-3 sentence summary describing:
- What was accomplished
- Key actions taken
- Any security events (warnings/blocks)

### AC2: Use Claude Haiku Model
**Given** the `ANTHROPIC_API_KEY` environment variable is set
**When** AI summary is requested
**Then** the API call uses `claude-3-5-haiku-20241022` model
**And** the prompt includes a condensed view of session events

### AC3: Stats-Only Fallback (No API Key)
**Given** the `ANTHROPIC_API_KEY` is not set
**When** AI summary is requested
**Then** a stats-only fallback summary is generated:
- "Session completed {n} tool calls over {duration}. Modified {files} files. {warnings} warnings, {blocked} blocked."
**And** no API error is raised

### AC4: Stats-Only Fallback (API Failure)
**Given** the Claude API call fails (timeout, error, rate limit)
**When** the failure is handled
**Then** the stats-only fallback summary is used
**And** the failure is logged to stderr
**And** report generation continues

### AC5: Summary in Session Data
**Given** the AI summary is generated
**When** included in the report
**Then** it appears in the `summary.ai_summary` field of session data

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and design (AC: All)
  - [x] 1.1: Review AC and understand API requirements
  - [x] 1.2: Design module interface
  - [x] 1.3: Plan testing strategy

- [x] Task 2: Implement ai_summary.py module (AC: All)
  - [x] 2.1: Create module with generate_ai_summary() function
  - [x] 2.2: Implement stats-only fallback function
  - [x] 2.3: Implement Claude API call with error handling
  - [x] 2.4: Create prompt template for session summarization

- [x] Task 3: Integrate with session-end hook (AC: 5)
  - [x] 3.1: Call generate_ai_summary() in session-end.py
  - [x] 3.2: Store result in summary.ai_summary

- [x] Task 4: Write comprehensive tests (AC: All)
  - [x] 4.1: Test stats-only fallback generation
  - [x] 4.2: Test API call mocking for success case
  - [x] 4.3: Test API failure fallback
  - [x] 4.4: Test missing API key behavior
  - [x] 4.5: Test summary content quality

- [x] Task 5: Run full test suite and verify
  - [x] 5.1: Run pytest on all tests
  - [x] 5.2: Verify all tests pass (292 tests passed)

## Dev Notes

### Module Interface

```python
def generate_ai_summary(session_data: Dict[str, Any]) -> str:
    """
    Generate an AI summary of the session using Claude Haiku.
    Falls back to stats-only summary if API unavailable.

    Args:
        session_data: Complete session object with events and summary

    Returns:
        A 2-3 sentence summary string
    """
```

### Stats-Only Fallback Format

```
Session completed {n} tool calls over {duration}. Modified {files} files. {warnings} warnings, {blocked} blocked.
```

### Claude Haiku API Call

```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=256,
    messages=[{"role": "user", "content": prompt}]
)
```

### Prompt Template

The prompt should include:
- Session statistics (total events, duration, files modified)
- List of tools used with counts
- Security summary (warnings, blocks)
- Condensed event list (tool names + verdicts)

### Error Handling

All errors should fail-open:
- Missing API key → stats fallback
- Network error → stats fallback
- API error (rate limit, etc.) → stats fallback
- Invalid response → stats fallback

### References

- [Source: epics.md#Story 3.3] - Original acceptance criteria
- [Source: architecture.md#AI Summary] - AI summary architecture

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Fixed anthropic mocking: Changed from `patch("ai_summary.anthropic")` to `patch("anthropic.Anthropic")` because anthropic is imported inside the function
- Required importing real anthropic module to create proper exception instances

### Completion Notes List

- Implemented `generate_ai_summary()` with Claude Haiku API integration
- Stats-only fallback works for: missing API key, API errors, rate limits, empty responses
- Prompt includes project dir, duration, tools used, security events, and event timeline
- All error handling is fail-open (never blocks report generation)
- 31 new tests added covering all acceptance criteria
- All 292 tests pass (31 new + 261 existing)

### File List

- `hooks/lib/ai_summary.py` - Core AI Summary module (new)
- `hooks/session-end.py` - Updated to integrate AI summary
- `tests/test_ai_summary.py` - 31 comprehensive tests (new)
