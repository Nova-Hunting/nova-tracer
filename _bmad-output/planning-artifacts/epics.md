---
stepsCompleted: [1, 2, 3, 4]
status: complete
inputDocuments:
  - path: '_bmad-output/planning-artifacts/prd.md'
    type: 'prd'
  - path: '_bmad-output/planning-artifacts/architecture.md'
    type: 'architecture'
---

# nova_claude_code_protector - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for nova_claude_code_protector, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Session Tracing (FR1-FR9):**
- FR1: System can capture every Claude Code tool call during a session
- FR2: System can record timestamp (start, end, duration) for each tool call
- FR3: System can capture complete tool input for each tool call
- FR4: System can capture complete tool output for each tool call
- FR5: System can assign sequential identifiers to maintain event order
- FR6: System can record the tool name for each captured event
- FR7: System can capture working directory context for relevant operations
- FR8: System can identify file paths accessed or modified during tool calls
- FR9: System can store captured events in append-only JSON during session

**Security Protection (FR10-FR16):**
- FR10: System can scan tool inputs against NOVA security rules
- FR11: System can scan tool outputs against NOVA security rules
- FR12: System can assign a verdict (allowed/warned/blocked) to each scanned event
- FR13: System can assign severity level to flagged events
- FR14: System can record which NOVA rules matched for each flagged event
- FR15: System can record scan timing for performance monitoring
- FR16: System can block tool execution when NOVA rules detect critical threats (PreToolUse hook)

**Report Generation (FR17-FR22):**
- FR17: System can automatically generate HTML report when Claude Code session exits
- FR18: System can convert session JSON to human-readable HTML format
- FR19: System can generate AI summary describing session purpose and key actions
- FR20: System can calculate aggregate statistics (total events, tools used, files touched)
- FR21: System can save reports to predictable location for easy retrieval
- FR22: System can include session metadata (platform, NOVA version, timestamps) in report

**Report Viewing - Overview (FR23-FR26):**
- FR23: User can view health badge showing session security status at a glance
- FR24: User can read AI summary to understand session in 10 seconds
- FR25: User can see count of warnings and blocked events immediately
- FR26: User can identify session duration and event count from report header

**Report Viewing - Timeline & Navigation (FR27-FR30):**
- FR27: User can view visual timeline showing session flow chronologically
- FR28: User can click timeline nodes to navigate to specific events
- FR29: User can scan timeline to identify flagged events visually (color coding)
- FR30: User can see tool icons indicating event types in timeline

**Report Viewing - Event Details (FR31-FR34):**
- FR31: User can expand events to reveal full details (input, output, NOVA verdict)
- FR32: User can collapse events to maintain clean overview
- FR33: User can view NOVA verdict details for flagged events (rules matched, severity)
- FR34: User can view complete tool input/output for investigation

**Report Viewing - Visual Design (FR35-FR37):**
- FR35: User can distinguish event severity via color coding (green/amber/red)
- FR36: User can identify tool types via icons (Read, Edit, Bash, etc.)
- FR37: User can view timestamps for each event in the timeline

**Installation & Configuration (FR38-FR42):**
- FR38: User can install system via single install script
- FR39: System can automatically register hooks with Claude Code settings
- FR40: System can operate with zero configuration for default use case
- FR41: User can customize report output location via configuration file (optional)
- FR42: User can add custom NOVA rules to extend security coverage

### NonFunctional Requirements

**Performance:**
- NFR1: Event capture overhead < 1ms per tool call
- NFR2: NOVA scan time < 5ms per event
- NFR3: JSON append operation < 0.5ms per write
- NFR4: HTML report generation < 3 seconds for 500 events
- NFR5: Memory footprint < 50MB during session

**Security:**
- NFR6: Reports treated as sensitive artifacts (contain full session data)
- NFR7: Reports stored in user-controlled directory with standard file permissions
- NFR8: All processing is local; no data leaves the user's machine
- NFR9: Tool does not store or manage credentials; uses existing NOVA installation
- NFR10: Users responsible for securing/deleting reports containing sensitive data

**Reliability:**
- NFR11: Event capture rate 100% - zero gaps in session recording
- NFR12: Report generation success 100% - must never fail on session exit
- NFR13: Graceful degradation - if NOVA scan fails, event logged with "scan_failed" status
- NFR14: Hook registration must survive Claude Code updates when possible
- NFR15: Corrupted session JSON should not prevent partial report generation

**Integration:**
- NFR16: Compatible with official hooks API (SessionStart, PreToolUse, PostToolUse, SessionEnd)
- NFR17: Uses NOVA Python package for pattern matching
- NFR18: Single script modifies ~/.claude/settings.json to register hooks
- NFR19: Clean removal script restores original Claude Code settings
- NFR20: Hook scripts can be updated independently of Claude Code

**Compatibility:**
- NFR21: Operating systems: macOS (primary), Linux (supported), Windows (best effort)
- NFR22: Python version: Python 3.9+ (3.10+ preferred for PEP 723)
- NFR23: Compatible with current stable Claude Code release
- NFR24: HTML reports viewable in any modern browser

### Additional Requirements

**From Architecture - Technical Constraints:**
- AR1: Extend existing codebase structure (no external starter template)
- AR2: Hook events: SessionStart, PreToolUse, PostToolUse, SubagentStop, SessionEnd
- AR3: Storage location: `{project}/.nova-protector/sessions/` and `{project}/.nova-protector/reports/`
- AR4: Session capture format: JSON Lines (.jsonl) during session, converted to .json at end
- AR5: HTML reports must be self-contained (CSS + JS + data embedded)
- AR6: AI Summary via Claude Haiku API with stats-only fallback
- AR7: Python 3.10+ with PEP 723 inline metadata (no setup.py/pyproject.toml required)
- AR8: Fail-open error handling pattern (exit 0 on errors, never block user)
- AR9: Session ID format: `YYYY-MM-DD_HH-MM-SS_abc123` (timestamp + hash)
- AR10: Output truncation: 10KB default limit per tool output

**From Architecture - Module Structure:**
- AR11: New hooks: `session-start.py`, `pre-tool-guard.py`, `session-end.py`
- AR12: Extend existing: `post-tool-nova-guard.py`
- AR13: New lib modules: `session_manager.py`, `report_generator.py`, `ai_summary.py`
- AR14: New directory: `hooks/lib/` for shared modules
- AR15: New directory: `templates/` for HTML report template

**From Architecture - Implementation Priority:**
- Phase 1 (Foundation): session_manager.py, session-start.py, post-tool extension
- Phase 2 (Security): pre-tool-guard.py
- Phase 3 (Reporting): report_generator.py, templates/report.html, session-end.py
- Phase 4 (Enhancement): ai_summary.py, install.sh updates

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | Capture every Claude Code tool call |
| FR2 | Epic 1 | Record timestamps (start, end, duration) |
| FR3 | Epic 1 | Capture complete tool input |
| FR4 | Epic 1 | Capture complete tool output |
| FR5 | Epic 1 | Assign sequential identifiers |
| FR6 | Epic 1 | Record tool name |
| FR7 | Epic 1 | Capture working directory context |
| FR8 | Epic 1 | Identify file paths accessed/modified |
| FR9 | Epic 1 | Store events in append-only JSON |
| FR10 | Epic 2 | Scan tool inputs against NOVA rules |
| FR11 | Epic 2 | Scan tool outputs against NOVA rules |
| FR12 | Epic 2 | Assign verdict (allowed/warned/blocked) |
| FR13 | Epic 2 | Assign severity level to flagged events |
| FR14 | Epic 2 | Record which NOVA rules matched |
| FR15 | Epic 2 | Record scan timing for performance |
| FR16 | Epic 2 | Block tool execution on critical threats |
| FR17 | Epic 3 | Auto-generate HTML report on session exit |
| FR18 | Epic 3 | Convert session JSON to HTML format |
| FR19 | Epic 3 | Generate AI summary of session |
| FR20 | Epic 3 | Calculate aggregate statistics |
| FR21 | Epic 3 | Save reports to predictable location |
| FR22 | Epic 3 | Include session metadata in report |
| FR23 | Epic 4 | View health badge for security status |
| FR24 | Epic 4 | Read AI summary (10-second understanding) |
| FR25 | Epic 4 | See warning/blocked counts immediately |
| FR26 | Epic 4 | Identify session duration and event count |
| FR27 | Epic 4 | View visual timeline chronologically |
| FR28 | Epic 4 | Click timeline nodes to navigate |
| FR29 | Epic 4 | Scan timeline for flagged events (colors) |
| FR30 | Epic 4 | See tool icons in timeline |
| FR31 | Epic 4 | Expand events for full details |
| FR32 | Epic 4 | Collapse events for clean overview |
| FR33 | Epic 4 | View NOVA verdict details for flagged events |
| FR34 | Epic 4 | View complete tool input/output |
| FR35 | Epic 4 | Distinguish severity via color coding |
| FR36 | Epic 4 | Identify tool types via icons |
| FR37 | Epic 4 | View timestamps for each event |
| FR38 | Epic 5 | Install via single install script |
| FR39 | Epic 5 | Auto-register hooks with Claude Code |
| FR40 | Epic 5 | Zero-config default operation |
| FR41 | Epic 5 | Customize report output location |
| FR42 | Epic 5 | Add custom NOVA rules |

## Epic List

### Epic 1: Session Capture Foundation
Users can have their Claude Code sessions automatically recorded with complete event details.

**User Outcome:** Every tool call Claude makes is captured - timestamps, inputs, outputs, file paths - stored reliably as the session runs.

**FRs Covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9 (9 FRs)

**Deliverables:**
- `hooks/session-start.py` - SessionStart hook
- `hooks/lib/session_manager.py` - Session lifecycle management
- Extended `hooks/post-tool-nova-guard.py` - Event capture
- JSON Lines storage in `{project}/.nova-protector/sessions/`

---

### Epic 2: Security Protection
Users are protected from prompt injection and malicious content with real-time NOVA scanning.

**User Outcome:** Every event gets scanned. Threats are detected, flagged, or blocked. Users see verdicts (allowed/warned/blocked) for each action.

**FRs Covered:** FR10, FR11, FR12, FR13, FR14, FR15, FR16 (7 FRs)

**Deliverables:**
- `hooks/pre-tool-guard.py` - PreToolUse blocking hook
- NOVA integration for input/output scanning
- Verdict attachment to captured events
- Rule matching and severity logging

---

### Epic 3: Report Generation
Users get comprehensive, shareable HTML reports automatically when sessions end.

**User Outcome:** Session exits → HTML report appears. Contains AI summary, statistics, metadata. Zero friction.

**FRs Covered:** FR17, FR18, FR19, FR20, FR21, FR22 (6 FRs)

**Deliverables:**
- `hooks/session-end.py` - SessionEnd hook
- `hooks/lib/report_generator.py` - JSON → HTML conversion
- `hooks/lib/ai_summary.py` - LLM summary with fallback
- `templates/report.html` - Base report template

---

### Epic 4: Interactive Report Experience
Users can navigate, explore, and investigate sessions with an interactive timeline and progressive disclosure.

**User Outcome:** Open report → see health badge + AI summary (10-second understanding) → click timeline → drill into any event → see full details. Visual color-coding makes flagged events jump out.

**FRs Covered:** FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR37 (15 FRs)

**Deliverables:**
- Health badge component (CLEAN/WARNINGS/BLOCKED)
- Visual timeline with click navigation
- Expandable/collapsible event cards
- Color coding system (green/amber/red)
- Tool icons (Read, Edit, Bash, etc.)
- Complete CSS + JS embedded in self-contained HTML

---

### Epic 5: Installation & Distribution
Users can install with a single command and extend with custom rules.

**User Outcome:** Run `./install.sh` → done. Zero configuration needed. Advanced users can add custom NOVA rules.

**FRs Covered:** FR38, FR39, FR40, FR41, FR42 (5 FRs)

**Deliverables:**
- Updated `install.sh` (registers all hooks)
- Zero-config defaults
- Optional `config/nova-protector.yaml` for customization
- Custom rules directory support
- Updated README with documentation

---

## Epic Summary

| Epic | Title | FRs | Status |
|------|-------|-----|--------|
| 1 | Session Capture Foundation | 9 | Pending |
| 2 | Security Protection | 7 | Pending |
| 3 | Report Generation | 6 | Pending |
| 4 | Interactive Report Experience | 15 | Pending |
| 5 | Installation & Distribution | 5 | Pending |
| **Total** | | **42** | |

---

## Epic 1: Session Capture Foundation

Users can have their Claude Code sessions automatically recorded with complete event details.

**FRs Covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9

### Story 1.1: Session Manager Module

**As a** developer implementing session capture,
**I want** a shared session manager module,
**So that** all hooks can consistently manage session state, IDs, and storage.

**Acceptance Criteria:**

**Given** the session manager module is imported
**When** `generate_session_id()` is called
**Then** it returns a string in format `YYYY-MM-DD_HH-MM-SS_abc123`
**And** the timestamp portion reflects the current time
**And** the hash portion is unique per call

**Given** a project directory path
**When** `get_session_paths(project_dir)` is called
**Then** it returns paths for `.nova-protector/sessions/` and `.nova-protector/reports/`
**And** directories are created if they don't exist

**Given** a session ID and project directory
**When** `init_session_file(session_id, project_dir)` is called
**Then** a new `.jsonl` file is created at the correct path
**And** an init record is written with session_id, timestamp, platform, project_dir

**Given** an active session file
**When** `append_event(session_id, event_data)` is called
**Then** the event is appended as a single JSON line
**And** file I/O completes in < 0.5ms
**And** errors do not raise exceptions (fail-open)

---

### Story 1.2: Session Initialization Hook

**As a** Claude Code user,
**I want** sessions to automatically start recording when I begin working,
**So that** no tool calls are missed from the start.

**Acceptance Criteria:**

**Given** Claude Code starts a new session
**When** the SessionStart hook fires
**Then** a new session ID is generated
**And** a session `.jsonl` file is created in `.nova-protector/sessions/`
**And** the init record contains: session_id, session_start timestamp, platform, project_dir

**Given** Claude Code resumes an existing session
**When** the SessionStart hook fires
**Then** the hook detects the existing active session
**And** continues appending to the existing `.jsonl` file

**Given** any error occurs during initialization
**When** the hook processes the error
**Then** it logs to stderr and exits 0 (fail-open)
**And** Claude Code operation is not blocked

---

### Story 1.3: Basic Event Capture

**As a** Claude Code user,
**I want** every tool call to be captured with full details,
**So that** I have complete visibility into what Claude did.

**Acceptance Criteria:**

**Given** Claude executes a tool (Read, Edit, Bash, etc.)
**When** the PostToolUse hook fires
**Then** an event record is appended to the session `.jsonl`

**Given** an event is captured
**When** the record is written
**Then** it includes: id (sequential integer), tool_name, tool_input, tool_output
**And** it includes: timestamp_start, timestamp_end, duration_ms

**Given** multiple tool calls in a session
**When** events are captured
**Then** each event has a unique sequential id starting from 1
**And** ids increment correctly even across hook invocations

**Given** tool_output exceeds 10KB
**When** the event is captured
**Then** the output is truncated to 10KB with a truncation marker
**And** the full output size is noted in the record

**Given** the capture overhead is measured
**When** an event is processed
**Then** the total hook execution time is < 1ms (excluding I/O)

---

### Story 1.4: Context and File Path Extraction

**As a** security analyst reviewing sessions,
**I want** to see which files were accessed and the working directory,
**So that** I can understand the context of each action.

**Acceptance Criteria:**

**Given** a tool call is captured
**When** the event is processed
**Then** working_dir is populated with the current working directory

**Given** a Read tool call with file_path input
**When** the event is captured
**Then** files_accessed contains the file path from the input

**Given** a Bash tool call
**When** the event is captured
**Then** files_accessed extracts any file paths mentioned in the command

**Given** an Edit or Write tool call
**When** the event is captured
**Then** files_accessed contains the target file path

**Given** a tool with no file-related inputs
**When** the event is captured
**Then** files_accessed is an empty array (not null)

---

## Epic 2: Security Protection

Users are protected from prompt injection and malicious content with real-time NOVA scanning.

**FRs Covered:** FR10, FR11, FR12, FR13, FR14, FR15, FR16

### Story 2.1: NOVA Scanner Integration

**As a** Claude Code user,
**I want** every tool input and output scanned by NOVA,
**So that** malicious content is detected in real-time.

**Acceptance Criteria:**

**Given** a tool call is captured in PostToolUse
**When** the event is processed
**Then** the tool_input is scanned against all NOVA rules in `rules/`

**Given** a tool call is captured in PostToolUse
**When** the event is processed
**Then** the tool_output is scanned against all NOVA rules in `rules/`

**Given** NOVA rules are loaded
**When** scanning is performed
**Then** all `.nov` files in the rules directory are applied

**Given** the NOVA scanner encounters an error
**When** the scan fails
**Then** the event is logged with `nova_verdict: "scan_failed"`
**And** the hook exits 0 (fail-open)
**And** Claude Code operation continues unblocked

**Given** scan performance is measured
**When** a scan completes
**Then** total scan time is < 5ms per event

---

### Story 2.2: Verdict Assignment and Logging

**As a** security analyst,
**I want** to see clear verdicts and matched rules for each event,
**So that** I can quickly identify and investigate threats.

**Acceptance Criteria:**

**Given** NOVA scans an event with no rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"allowed"`
**And** `nova_severity` is set to `null`
**And** `nova_rules_matched` is an empty array

**Given** NOVA scans an event and a warning-level rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"warned"`
**And** `nova_severity` is set to the matched rule's severity (e.g., "medium")
**And** `nova_rules_matched` contains the rule name(s)

**Given** NOVA scans an event and a critical-level rule matches
**When** the verdict is assigned
**Then** `nova_verdict` is set to `"blocked"` (for reporting purposes)
**And** `nova_severity` is set to `"critical"`
**And** `nova_rules_matched` contains the rule name(s)

**Given** multiple rules match an event
**When** the verdict is assigned
**Then** the highest severity determines the verdict
**And** all matched rule names are included in `nova_rules_matched`

**Given** an event is scanned
**When** the scan completes
**Then** `nova_scan_time_ms` records the scan duration in milliseconds

---

### Story 2.3: Pre-Tool Blocking Hook

**As a** Claude Code user,
**I want** critical threats blocked before execution,
**So that** dangerous actions are prevented, not just logged.

**Acceptance Criteria:**

**Given** Claude is about to execute a tool
**When** the PreToolUse hook fires
**Then** the tool_input is scanned against NOVA rules

**Given** NOVA detects a critical-severity match in PreToolUse
**When** the scan result is evaluated
**Then** the hook exits with code 2 (block)
**And** outputs JSON: `{"decision": "block", "reason": "[NOVA] Blocked: {rule_name}"}`
**And** Claude receives the block message

**Given** NOVA detects a warning-severity match in PreToolUse
**When** the scan result is evaluated
**Then** the hook exits with code 0 (allow)
**And** the warning is logged for PostToolUse capture

**Given** NOVA scan finds no matches in PreToolUse
**When** the scan completes
**Then** the hook exits with code 0 (allow)
**And** no output is sent to stdout

**Given** the PreToolUse hook encounters any error
**When** the error is handled
**Then** it logs to stderr and exits 0 (fail-open)
**And** the tool execution proceeds

---

## Epic 3: Report Generation

Users get comprehensive, shareable HTML reports automatically when sessions end.

**FRs Covered:** FR17, FR18, FR19, FR20, FR21, FR22

### Story 3.1: Session End Hook

**As a** Claude Code user,
**I want** an HTML report generated automatically when my session ends,
**So that** I always have a complete audit trail without manual action.

**Acceptance Criteria:**

**Given** a Claude Code session ends normally
**When** the SessionEnd hook fires
**Then** the session `.jsonl` file is finalized
**And** events are converted to a complete session `.json` file
**And** an HTML report is generated at `.nova-protector/reports/{session_id}.html`

**Given** a session with captured events
**When** the report is generated
**Then** the report path is predictable: `{project}/.nova-protector/reports/{session_id}.html`
**And** the report filename matches the session ID

**Given** the session JSON is partially corrupted
**When** the SessionEnd hook runs
**Then** it generates a partial report with available events
**And** logs the corruption warning to stderr
**And** never fails completely (100% generation success)

**Given** report generation is measured
**When** a session with 500 events completes
**Then** the total generation time is < 3 seconds

**Given** any error occurs during report generation
**When** the error is handled
**Then** it logs to stderr and exits 0 (fail-open)
**And** a partial or error report is created if possible

---

### Story 3.2: Report Generator Module

**As a** developer building report generation,
**I want** a report generator module that converts session JSON to HTML,
**So that** reports are consistent, self-contained, and portable.

**Acceptance Criteria:**

**Given** a complete session JSON object
**When** `generate_html_report(session_data)` is called
**Then** it returns a complete HTML string

**Given** the generated HTML
**When** rendered in a browser
**Then** CSS styles are embedded in a `<style>` tag (no external files)
**And** JavaScript is embedded in `<script>` tags (no external files)
**And** session data is embedded as `const SESSION_DATA = {...}`

**Given** session data with events
**When** the report is generated
**Then** aggregate statistics are calculated:
- `total_events`: count of all events
- `tools_used`: object mapping tool names to counts
- `files_touched`: count of unique files in files_accessed
- `warnings`: count of events with `nova_verdict: "warned"`
- `blocked`: count of events with `nova_verdict: "blocked"`

**Given** session data
**When** the report is generated
**Then** metadata is included:
- `session_id`, `session_start`, `session_end`
- `platform`, `nova_version`, `project_dir`
- `duration_seconds`: calculated from start/end

**Given** an empty session (no events)
**When** the report is generated
**Then** a valid HTML report is created with zero events displayed
**And** statistics show all counts as 0

---

### Story 3.3: AI Summary Module

**As a** Claude Code user,
**I want** an AI-generated summary of my session,
**So that** I can understand what happened in 10 seconds.

**Acceptance Criteria:**

**Given** a session with events
**When** `generate_ai_summary(session_data)` is called
**Then** it calls the Claude Haiku API with a summary prompt
**And** returns a 2-3 sentence summary describing:
- What was accomplished
- Key actions taken
- Any security events (warnings/blocks)

**Given** the `ANTHROPIC_API_KEY` environment variable is set
**When** AI summary is requested
**Then** the API call uses `claude-3-5-haiku-20241022` model
**And** the prompt includes a condensed view of session events

**Given** the `ANTHROPIC_API_KEY` is not set
**When** AI summary is requested
**Then** a stats-only fallback summary is generated:
- "Session completed {n} tool calls over {duration}. Modified {files} files. {warnings} warnings, {blocked} blocked."
**And** no API error is raised

**Given** the Claude API call fails (timeout, error, rate limit)
**When** the failure is handled
**Then** the stats-only fallback summary is used
**And** the failure is logged to stderr
**And** report generation continues

**Given** the AI summary is generated
**When** included in the report
**Then** it appears in the `summary.ai_summary` field of session data

---

## Epic 4: Interactive Report Experience

Users can navigate, explore, and investigate sessions with an interactive timeline and progressive disclosure.

**FRs Covered:** FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36, FR37

### Story 4.1: Base Template and Design System

**As a** developer building the report UI,
**I want** a consistent design system with colors and icons,
**So that** all components have a unified, professional appearance.

**Acceptance Criteria:**

**Given** the HTML template is loaded
**When** CSS is parsed
**Then** CSS variables define the verdict color scheme:
- `--color-allowed: #22c55e` (green)
- `--color-warned: #f59e0b` (amber)
- `--color-blocked: #ef4444` (red)
- `--color-neutral: #6b7280` (gray)

**Given** a user views the report
**When** they see event verdicts
**Then** color coding instantly communicates severity:
- Green = allowed/safe
- Amber = warned/caution
- Red = blocked/danger

**Given** the report displays tool types
**When** tool icons are rendered
**Then** each tool type has a distinct icon:
- Read: 📖 or file icon
- Edit/Write: ✏️ or pencil icon
- Bash: 💻 or terminal icon
- Glob/Grep: 🔍 or search icon
- WebFetch: 🌐 or globe icon
- Task: 🤖 or agent icon
- Other: ⚙️ or gear icon

**Given** the HTML template
**When** rendered in Chrome, Firefox, Safari, or Edge
**Then** the layout displays correctly in all modern browsers
**And** no external resources are required

---

### Story 4.2: Report Header Component

**As a** Claude Code user,
**I want** to see session status at a glance,
**So that** I understand the session in 10 seconds.

**Acceptance Criteria:**

**Given** a session with all events `nova_verdict: "allowed"`
**When** the report header renders
**Then** the health badge displays "CLEAN" in green
**And** the badge is prominently visible at the top

**Given** a session with some `nova_verdict: "warned"` events
**When** the report header renders
**Then** the health badge displays "WARNINGS" in amber
**And** shows count: "X warnings"

**Given** a session with any `nova_verdict: "blocked"` events
**When** the report header renders
**Then** the health badge displays "BLOCKED" in red
**And** shows counts: "X blocked, Y warnings"

**Given** the session has an AI summary
**When** the header renders
**Then** the AI summary text is displayed prominently below the badge
**And** the user can read it within 5 seconds

**Given** session statistics
**When** the header renders
**Then** it displays:
- Total event count
- Session duration (formatted: "12m 34s")
- Blocked count (if any)
- Warning count (if any)

---

### Story 4.3: Visual Timeline Component

**As a** security analyst,
**I want** a visual timeline of the session,
**So that** I can see the flow and spot anomalies quickly.

**Acceptance Criteria:**

**Given** a session with events
**When** the timeline renders
**Then** events appear in chronological order (by timestamp_start)
**And** each event is represented as a node/marker

**Given** the timeline is displayed
**When** a user views it
**Then** each node shows:
- Tool icon (from design system)
- Color indicator (green/amber/red based on verdict)
- Timestamp (HH:MM:SS format)

**Given** an event with `nova_verdict: "warned"`
**When** rendered in the timeline
**Then** the node is highlighted in amber
**And** stands out visually from allowed events

**Given** an event with `nova_verdict: "blocked"`
**When** rendered in the timeline
**Then** the node is highlighted in red
**And** is immediately visible to the user

**Given** a timeline node
**When** the user clicks on it
**Then** the view scrolls to the corresponding event detail card
**And** the event card is highlighted or expanded

**Given** a session with many events (50+)
**When** the timeline renders
**Then** it remains usable and scrollable
**And** performance is acceptable (no lag)

---

### Story 4.4: Event Detail Cards

**As a** user investigating a session,
**I want** to expand events to see full details,
**So that** I can investigate suspicious activity.

**Acceptance Criteria:**

**Given** the event list is displayed
**When** initially rendered
**Then** events show collapsed view:
- Event ID, tool name, tool icon
- Timestamp
- Verdict badge (color-coded)

**Given** a collapsed event card
**When** the user clicks to expand
**Then** the card reveals full details:
- Complete tool_input (formatted JSON or text)
- Complete tool_output (formatted, with syntax highlighting if applicable)
- duration_ms
- working_dir
- files_accessed list

**Given** an expanded event card
**When** the user clicks to collapse
**Then** the card returns to collapsed view
**And** maintains scroll position

**Given** an event with `nova_verdict: "warned"` or `"blocked"`
**When** expanded
**Then** it shows NOVA verdict details:
- `nova_severity` level
- `nova_rules_matched` list with rule names
- `nova_scan_time_ms`

**Given** tool_output with code content
**When** displayed in expanded view
**Then** it uses monospace font
**And** preserves formatting/indentation

**Given** very large tool_input or tool_output (truncated)
**When** displayed
**Then** truncation is indicated: "[truncated - original size: X KB]"

---

## Epic 5: Installation & Distribution

Users can install with a single command and extend with custom rules.

**FRs Covered:** FR38, FR39, FR40, FR41, FR42

### Story 5.1: Installation Script

**As a** Claude Code user,
**I want** to install NOVA Claude Code Protector with a single command,
**So that** I can start protecting my sessions immediately.

**Acceptance Criteria:**

**Given** the user has cloned the repository
**When** they run `./install.sh`
**Then** the script completes without errors
**And** provides clear progress output

**Given** the install script runs
**When** it registers hooks
**Then** it modifies `~/.claude/settings.json` to add:
- SessionStart hook → `session-start.py`
- PreToolUse hook → `pre-tool-guard.py`
- PostToolUse hook → `post-tool-nova-guard.py`
- SessionEnd hook → `session-end.py`

**Given** `~/.claude/settings.json` already exists with other hooks
**When** install runs
**Then** existing hooks are preserved
**And** NOVA hooks are added/merged correctly

**Given** `~/.claude/settings.json` doesn't exist
**When** install runs
**Then** the file is created with proper structure
**And** NOVA hooks are registered

**Given** the install completes
**When** the user starts a Claude Code session
**Then** all NOVA hooks activate automatically

**Given** the user wants to uninstall
**When** they run `./uninstall.sh`
**Then** NOVA hooks are removed from settings.json
**And** other hooks remain intact
**And** `.nova-protector/` directories are optionally preserved (user prompted)

---

### Story 5.2: Configuration and Extensibility

**As a** power user,
**I want** optional configuration and custom rules,
**So that** I can customize the tool for my needs.

**Acceptance Criteria:**

**Given** the tool is installed with no configuration file
**When** Claude Code sessions run
**Then** the tool operates with sensible defaults:
- Reports saved to `{project}/.nova-protector/reports/`
- All built-in rules enabled
- Output truncation at 10KB
- AI summary enabled (if API key present)

**Given** a `config/nova-protector.yaml` file exists
**When** the tool loads configuration
**Then** it reads and applies custom settings

**Given** the user wants to customize report location
**When** they set `report_output_dir` in config
**Then** reports are saved to the specified directory instead of default

**Given** the user creates a `.nov` file in `rules/` directory
**When** NOVA scanning runs
**Then** the custom rule is loaded and applied alongside built-in rules

**Given** a custom rule has syntax errors
**When** rules are loaded
**Then** the error is logged to stderr
**And** other valid rules continue to function
**And** the tool doesn't crash

**Given** the user wants to disable AI summaries
**When** they set `ai_summary_enabled: false` in config
**Then** reports use stats-only summaries
**And** no API calls are made

**Given** the configuration file has unknown keys
**When** config is loaded
**Then** unknown keys are ignored
**And** a warning is logged
**And** valid configuration is applied
