# Story 4.3: Visual Timeline Component

Status: done

## Story

As a **security analyst**,
I want **a visual timeline of the session**,
So that **I can see the flow and spot anomalies quickly**.

## Acceptance Criteria

### AC1: Chronological Event Order
**Given** a session with events
**When** the timeline renders
**Then** events appear in chronological order (by timestamp_start)
**And** each event is represented as a node/marker

### AC2: Timeline Node Display
**Given** the timeline is displayed
**When** a user views it
**Then** each node shows:
- Tool icon (from design system)
- Color indicator (green/amber/red based on verdict)
- Timestamp (HH:MM:SS format)

### AC3: Warned Event Highlighting
**Given** an event with `nova_verdict: "warned"`
**When** rendered in the timeline
**Then** the node is highlighted in amber
**And** stands out visually from allowed events

### AC4: Blocked Event Highlighting
**Given** an event with `nova_verdict: "blocked"`
**When** rendered in the timeline
**Then** the node is highlighted in red
**And** is immediately visible to the user

### AC5: Click-to-Navigate
**Given** a timeline node
**When** the user clicks on it
**Then** the view scrolls to the corresponding event detail card
**And** the event card is highlighted or expanded

### AC6: Large Session Performance
**Given** a session with many events (50+)
**When** the timeline renders
**Then** it remains usable and scrollable
**And** performance is acceptable (no lag)

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and plan implementation
  - [x] 1.1: Review AC and understand requirements
  - [x] 1.2: Review current events section in report_generator.py
  - [x] 1.3: Design timeline component structure

- [x] Task 2: Implement timeline HTML structure (AC: 1, 2)
  - [x] 2.1: Add timeline container with horizontal/vertical layout
  - [x] 2.2: Generate timeline nodes for each event
  - [x] 2.3: Include tool icons in nodes
  - [x] 2.4: Add timestamps in HH:MM:SS format

- [x] Task 3: Implement verdict color coding (AC: 3, 4)
  - [x] 3.1: Apply CSS classes for verdict colors
  - [x] 3.2: Style warned events to stand out in amber
  - [x] 3.3: Style blocked events prominently in red

- [x] Task 4: Implement click navigation (AC: 5)
  - [x] 4.1: Add event IDs to event cards
  - [x] 4.2: Add click handlers to timeline nodes
  - [x] 4.3: Implement smooth scroll to event card
  - [x] 4.4: Add highlight effect on target card

- [x] Task 5: Optimize for performance (AC: 6)
  - [x] 5.1: Test with 50+ events
  - [x] 5.2: Ensure scrollable timeline
  - [x] 5.3: Optimize CSS for smooth rendering

- [x] Task 6: Write comprehensive tests (AC: All)
  - [x] 6.1: Test chronological ordering
  - [x] 6.2: Test node display elements
  - [x] 6.3: Test verdict color classes
  - [x] 6.4: Test click navigation elements
  - [x] 6.5: Test large session handling

- [x] Task 7: Run full test suite and verify
  - [x] 7.1: Run pytest on all tests
  - [x] 7.2: Verify all tests pass (183 core tests)

## Dev Notes

### Timeline Design Options

**Option A: Horizontal Timeline**
- Events flow left to right
- Scrollable horizontally for long sessions
- Good for seeing overall flow

**Option B: Vertical Timeline (Recommended)**
- Events flow top to bottom
- Natural reading order
- Better for detailed view
- Easier to implement with existing event cards

### Timeline Node Structure

```html
<div class="timeline">
    <div class="timeline-node allowed" data-event-id="0" onclick="scrollToEvent(0)">
        <span class="node-icon">{tool_icon}</span>
        <span class="node-time">14:30:45</span>
    </div>
    <div class="timeline-node warned" data-event-id="1" onclick="scrollToEvent(1)">
        <span class="node-icon">{tool_icon}</span>
        <span class="node-time">14:31:02</span>
    </div>
</div>
```

### CSS Design

```css
.timeline {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    position: sticky;
    top: 1rem;
}
.timeline-node {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 8px;
    cursor: pointer;
    background: var(--bg-secondary);
    border-left: 3px solid var(--color-allowed);
}
.timeline-node.warned { border-left-color: var(--color-warned); }
.timeline-node.blocked { border-left-color: var(--color-blocked); }
.timeline-node:hover { background: rgba(255,255,255,0.1); }
```

### JavaScript for Navigation

```javascript
function scrollToEvent(eventId) {
    const card = document.getElementById('event-' + eventId);
    if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.add('highlighted');
        setTimeout(() => card.classList.remove('highlighted'), 2000);
    }
}
```

### References

- [Source: epics.md#Story 4.3] - Original acceptance criteria
- [Source: hooks/lib/report_generator.py] - Current implementation
- [Source: Story 4.1] - Design system with tool icons

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No issues encountered during implementation

### Completion Notes List

- Added `_generate_timeline_html()` function for vertical timeline nodes
- Each node shows: tool icon, HH:MM:SS timestamp, verdict color class
- Vertical layout with sticky positioning for navigation
- Click handler `scrollToEvent(eventId)` scrolls to event card with smooth animation
- Event cards now have `id="event-{idx}"` for scroll targeting
- Added `.highlighted` class with pulse animation for clicked cards
- Timeline CSS: sticky position, max-height, overflow-y for large sessions
- Warned nodes: amber border, Blocked nodes: red border + tinted background
- Added 27 new tests for Story 4.3 acceptance criteria
- All 183 core tests pass (127 report generator tests)

### File List

- `hooks/lib/report_generator.py` - Added timeline generation, CSS, JavaScript
- `tests/test_report_generator.py` - Added 27 Story 4.3 tests
