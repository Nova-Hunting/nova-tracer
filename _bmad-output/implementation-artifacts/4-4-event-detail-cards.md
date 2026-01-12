# Story 4.4: Event Detail Cards

Status: done

## Story

As a **user investigating a session**,
I want **to expand events to see full details**,
So that **I can investigate suspicious activity**.

## Acceptance Criteria

### AC1: Collapsed View Default
**Given** the event list is displayed
**When** initially rendered
**Then** events show collapsed view:
- Event ID, tool name, tool icon
- Timestamp
- Verdict badge (color-coded)

### AC2: Expand to Full Details
**Given** a collapsed event card
**When** the user clicks to expand
**Then** the card reveals full details:
- Complete tool_input (formatted JSON or text)
- Complete tool_output (formatted, with syntax highlighting if applicable)
- duration_ms
- working_dir
- files_accessed list

### AC3: Collapse Back
**Given** an expanded event card
**When** the user clicks to collapse
**Then** the card returns to collapsed view
**And** maintains scroll position

### AC4: NOVA Verdict Details
**Given** an event with `nova_verdict: "warned"` or `"blocked"`
**When** expanded
**Then** it shows NOVA verdict details:
- `nova_severity` level
- `nova_rules_matched` list with rule names
- `nova_scan_time_ms`

### AC5: Code Formatting
**Given** tool_output with code content
**When** displayed in expanded view
**Then** it uses monospace font
**And** preserves formatting/indentation

### AC6: Truncation Indicator
**Given** very large tool_input or tool_output (truncated)
**When** displayed
**Then** truncation is indicated: "[truncated - original size: X KB]"

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and plan implementation
  - [x] 1.1: Review AC and understand requirements
  - [x] 1.2: Review current event card implementation
  - [x] 1.3: Design expandable card structure

- [x] Task 2: Implement collapsed view enhancements (AC: 1)
  - [x] 2.1: Ensure event ID is visible
  - [x] 2.2: Add click-to-expand indicator/button

- [x] Task 3: Implement expanded view (AC: 2)
  - [x] 3.1: Add expanded details section
  - [x] 3.2: Display tool_input formatted
  - [x] 3.3: Display tool_output formatted
  - [x] 3.4: Show duration_ms, working_dir, files_accessed

- [x] Task 4: Implement expand/collapse toggle (AC: 3)
  - [x] 4.1: Add JavaScript toggle function
  - [x] 4.2: Add CSS for expanded state
  - [x] 4.3: Ensure scroll position maintained

- [x] Task 5: Implement NOVA verdict details (AC: 4)
  - [x] 5.1: Display nova_severity
  - [x] 5.2: Display nova_rules_matched
  - [x] 5.3: Display nova_scan_time_ms

- [x] Task 6: Implement code formatting (AC: 5)
  - [x] 6.1: Add monospace styling for code content
  - [x] 6.2: Preserve whitespace and indentation

- [x] Task 7: Implement truncation indicator (AC: 6)
  - [x] 7.1: Detect truncated content
  - [x] 7.2: Display truncation message with size

- [x] Task 8: Write comprehensive tests (AC: All)
  - [x] 8.1: Test collapsed view elements
  - [x] 8.2: Test expanded view elements
  - [x] 8.3: Test toggle functionality
  - [x] 8.4: Test NOVA verdict display
  - [x] 8.5: Test code formatting
  - [x] 8.6: Test truncation indicator

- [x] Task 9: Run full test suite and verify
  - [x] 9.1: Run pytest on all tests
  - [x] 9.2: Verify all tests pass (171 report generator tests)

## Dev Notes

### Card Structure

```html
<div class="event-card {verdict}" id="event-{idx}">
    <div class="event-header" onclick="toggleEvent({idx})">
        <span class="event-id">#{idx}</span>
        <span class="event-tool">{icon}{tool_name}</span>
        <span class="event-verdict">{verdict}</span>
        <span class="event-time">{timestamp}</span>
        <span class="expand-icon">▼</span>
    </div>
    <div class="event-details" id="details-{idx}" style="display: none;">
        <!-- Full details here -->
    </div>
</div>
```

### CSS for Expandable Cards

```css
.event-header {
    cursor: pointer;
}
.event-header:hover {
    background: rgba(255,255,255,0.05);
}
.expand-icon {
    transition: transform 0.2s;
}
.event-card.expanded .expand-icon {
    transform: rotate(180deg);
}
.event-details {
    padding: 1rem;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.detail-section {
    margin-bottom: 1rem;
}
.detail-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
}
.detail-value {
    font-family: monospace;
    white-space: pre-wrap;
    background: rgba(0,0,0,0.2);
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
}
```

### JavaScript Toggle

```javascript
function toggleEvent(eventId) {
    const card = document.getElementById('event-' + eventId);
    const details = document.getElementById('details-' + eventId);
    if (card.classList.contains('expanded')) {
        card.classList.remove('expanded');
        details.style.display = 'none';
    } else {
        card.classList.add('expanded');
        details.style.display = 'block';
    }
}
```

### NOVA Verdict Section

```html
<div class="nova-verdict-section">
    <div class="detail-label">NOVA Analysis</div>
    <div class="nova-details">
        <span class="nova-severity {severity}">Severity: {nova_severity}</span>
        <span class="nova-scan-time">Scan time: {nova_scan_time_ms}ms</span>
        <div class="nova-rules">
            Rules matched: {nova_rules_matched}
        </div>
    </div>
</div>
```

### References

- [Source: epics.md#Story 4.4] - Original acceptance criteria
- [Source: hooks/lib/report_generator.py] - Current implementation
- [Source: Story 4.3] - Timeline with event IDs

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No issues encountered during implementation

### Completion Notes List

- Added `_format_content_for_display()` helper function for truncation
- Updated `_generate_events_html()` for expandable card structure
- Collapsed view shows: event ID (#idx), tool icon, tool name, verdict badge, timestamp, expand icon
- Expanded view shows: tool_input, tool_output, duration_ms, working_dir, files_accessed list
- NOVA verdict section appears only for warned/blocked events with severity, rules_matched, scan_time_ms
- Added `toggleEvent(eventId)` JavaScript function for expand/collapse
- Added CSS for `.event-details`, `.detail-section`, `.detail-label`, `.detail-value`
- Added CSS for `.nova-verdict-section` with severity color classes (low, medium, high, critical)
- Monospace font with `pre` tags for tool input/output
- Truncation indicator shows "[truncated - original size: X KB]" for content > 10KB
- Added 49 new tests for Story 4.4 acceptance criteria
- All 171 report generator tests pass

### File List

- `hooks/lib/report_generator.py` - Added expandable cards, NOVA details, truncation
- `tests/test_report_generator.py` - Added 49 Story 4.4 tests
