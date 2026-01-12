# Story 4.1: Base Template and Design System

Status: done

## Story

As a **developer building the report UI**,
I want **a consistent design system with colors and icons**,
So that **all components have a unified, professional appearance**.

## Acceptance Criteria

### AC1: CSS Variables for Verdict Colors
**Given** the HTML template is loaded
**When** CSS is parsed
**Then** CSS variables define the verdict color scheme:
- `--color-allowed: #22c55e` (green)
- `--color-warned: #f59e0b` (amber)
- `--color-blocked: #ef4444` (red)
- `--color-neutral: #6b7280` (gray)

### AC2: Color Coding Communicates Severity
**Given** a user views the report
**When** they see event verdicts
**Then** color coding instantly communicates severity:
- Green = allowed/safe
- Amber = warned/caution
- Red = blocked/danger

### AC3: Tool Icons for Each Tool Type
**Given** the report displays tool types
**When** tool icons are rendered
**Then** each tool type has a distinct icon:
- Read: file icon
- Edit/Write: pencil icon
- Bash: terminal icon
- Glob/Grep: search icon
- WebFetch: globe icon
- Task: agent icon
- Other: gear icon

### AC4: Cross-Browser Compatibility
**Given** the HTML template
**When** rendered in Chrome, Firefox, Safari, or Edge
**Then** the layout displays correctly in all modern browsers
**And** no external resources are required

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and design (AC: All)
  - [x] 1.1: Review AC and understand design requirements
  - [x] 1.2: Design CSS structure
  - [x] 1.3: Plan testing strategy

- [x] Task 2: Create HTML base template (AC: All)
  - [x] 2.1: Create templates/report.html with basic structure
  - [x] 2.2: Add CSS variables for color scheme
  - [x] 2.3: Add tool icon definitions (SVG inline)
  - [x] 2.4: Add base layout and typography styles

- [x] Task 3: Update report generator (AC: All)
  - [x] 3.1: Update generate_html_report() to use new template
  - [x] 3.2: Add helper functions for tool icons (get_tool_icon)
  - [x] 3.3: Add helper functions for verdict styling

- [x] Task 4: Write comprehensive tests (AC: All)
  - [x] 4.1: Test CSS variables are present in output
  - [x] 4.2: Test tool icons are rendered correctly
  - [x] 4.3: Test verdict colors are applied
  - [x] 4.4: Test HTML is valid and self-contained

- [x] Task 5: Run full test suite and verify
  - [x] 5.1: Run pytest on all tests
  - [x] 5.2: Verify all tests pass (318 passed)

## Dev Notes

### Color Scheme (Tailwind-inspired)

```css
:root {
  --color-allowed: #22c55e;  /* green-500 */
  --color-warned: #f59e0b;   /* amber-500 */
  --color-blocked: #ef4444;  /* red-500 */
  --color-neutral: #6b7280;  /* gray-500 */

  /* Background variants */
  --bg-allowed: #dcfce7;     /* green-100 */
  --bg-warned: #fef3c7;      /* amber-100 */
  --bg-blocked: #fee2e2;     /* red-100 */
  --bg-neutral: #f3f4f6;     /* gray-100 */
}
```

### Tool Icons (SVG)

Using simple, recognizable SVG icons that work at small sizes:
- Read: document/file icon
- Edit/Write: pencil icon
- Bash: terminal/command-line icon
- Glob/Grep: magnifying glass icon
- WebFetch: globe icon
- Task: robot/agent icon
- Other: gear/cog icon

### Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NOVA Session Report - {session_id}</title>
  <style>/* All CSS embedded here */</style>
</head>
<body>
  <header><!-- Health badge, summary, stats --></header>
  <nav><!-- Timeline --></nav>
  <main><!-- Event cards --></main>
  <script>const SESSION_DATA = {...};</script>
  <script>/* All JS embedded here */</script>
</body>
</html>
```

### References

- [Source: epics.md#Story 4.1] - Original acceptance criteria
- [Source: architecture.md] - Self-contained HTML requirement

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No issues encountered during implementation
- CSS variables already existed from Story 3.2, just verified correct values

### Completion Notes List

- Added TOOL_ICONS dictionary with SVG icons for 9 tool types + default
- Added get_tool_icon() helper function for retrieving icons
- Updated _generate_events_html() to include tool icons in event cards
- Updated tools section to include icons next to tool names
- Added .tool-icon and .tool-name CSS classes for proper icon styling
- 26 new tests added for Story 4.1 acceptance criteria
- All 318 tests pass (73 report generator tests, 26 new for Story 4.1)

### File List

- `hooks/lib/report_generator.py` - Updated with TOOL_ICONS and get_tool_icon()
- `tests/test_report_generator.py` - Added 26 tests for Story 4.1
