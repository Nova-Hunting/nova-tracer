---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
status: complete
inputDocuments:
  - path: '_bmad-output/planning-artifacts/prd.md'
    type: 'prd'
workflowType: 'architecture'
project_name: 'nova_claude_code_protector'
user_name: 'Fr0gger'
date: '2026-01-10'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

42 functional requirements across 8 categories:

| Category | FRs | Architectural Implication |
|----------|-----|---------------------------|
| Session Tracing | FR1-FR9 | Event capture pipeline, JSON schema design |
| Security Protection | FR10-FR16 | NOVA integration layer, verdict handling |
| Report Generation | FR17-FR22 | Batch processing, template engine |
| Report Viewing - Overview | FR23-FR26 | HTML header component, health badge logic |
| Report Viewing - Timeline | FR27-FR30 | Interactive timeline component, navigation |
| Report Viewing - Event Details | FR31-FR34 | Expandable card components, detail rendering |
| Report Viewing - Visual Design | FR35-FR37 | Design system (colors, icons, typography) |
| Installation & Configuration | FR38-FR42 | Install script, config file handling |

**Non-Functional Requirements:**

| Category | Key Constraints |
|----------|-----------------|
| Performance | <1ms capture, <5ms scan, <3s report gen, <50MB memory |
| Security | Local-only, no external transmission, sensitive report data |
| Reliability | 100% event capture, 100% report generation, graceful degradation |
| Integration | Claude Code hooks API (SessionStart, PreToolUse, PostToolUse, SessionEnd) |
| Compatibility | macOS/Linux/Windows, Python 3.9+, modern browsers |

**Scale & Complexity:**

- Primary domain: CLI Tool with Hooks Integration
- Complexity level: Medium
- Estimated architectural components: 5-7 major modules

### Technical Constraints & Dependencies

| Constraint | Source | Impact |
|------------|--------|--------|
| Claude Code hooks API | External dependency | Architecture must use SessionStart, PreToolUse, PostToolUse, SessionEnd hooks |
| NOVA Python package | Existing library | Security scanning delegated to NOVA, not reimplemented |
| Python 3.10+ | Existing codebase | Language choice locked (PEP 723 inline metadata) |
| JSON append-only | Performance requirement | Cannot restructure JSON during session |
| HTML single-file | Portability requirement | Report must be self-contained |

### Cross-Cutting Concerns Identified

| Concern | Components Affected | Architectural Strategy |
|---------|---------------------|------------------------|
| Performance (<1ms) | Event capture, JSON append | Async/non-blocking patterns, minimal hot path |
| Reliability (100%) | All capture code | Never throw, always log, graceful degradation |
| Error Handling | NOVA integration, file I/O | Fallback states, partial report generation |
| Data Sensitivity | Report storage, JSON files | Document user responsibility, predictable paths |

## Starter Template Evaluation

### Primary Technology Domain

**Python Hooks Integration** - No CLI, no framework. Pure Python scripts executed by Claude Code hooks system.

### Existing Architecture (Preserve)

The project already has an established structure that we will extend, not replace:

```
nova_claude_code_protector/
├── hooks/           # Hook scripts (extend with new hooks)
│   ├── post-tool-nova-guard.py   # Existing: PostToolUse NOVA scanning
│   └── test-nova-guard.py        # Existing: Test script
├── config/          # Configuration (extend with new settings)
│   ├── nova-config.yaml          # Existing: NOVA scanner config
│   └── settings-template.json    # Existing: Claude Code settings
├── rules/           # NOVA rules (existing, complete for MVP)
│   ├── context_manipulation.nov
│   ├── encoding_obfuscation.nov
│   ├── instruction_override.nov
│   └── roleplay_jailbreak.nov
├── cookbook/        # Documentation (extend)
├── test-files/      # Test data (extend)
├── install.sh       # Installation (update for new hooks)
├── README.md
└── SKILL.md
```

### Technical Decisions (Locked by Existing Code)

| Decision | Value | Source |
|----------|-------|--------|
| Language | Python 3.10+ | PEP 723 in existing hooks |
| Dependencies | `nova-hunting`, `pyyaml` | Existing inline metadata |
| Hook I/O | JSON stdin/stdout | Claude Code hooks spec |
| Configuration | YAML with multi-path discovery | Existing pattern |
| Error Handling | Fail-open (exit 0) | Existing pattern |
| Rules Format | `.nov` files in `rules/` | Existing pattern |

### Claude Code Hooks API (Corrected from Documentation)

**Available Hook Events:**

| Hook Event | When It Fires | Our Use |
|------------|---------------|---------|
| `SessionStart` | Session starts or resumes | Initialize session JSON |
| `PreToolUse` | Before tool calls (can block) | Block critical threats |
| `PostToolUse` | After tool calls complete | Capture event + NOVA scan |
| `SubagentStop` | Subagent tasks complete | Capture subagent events |
| `SessionEnd` | Session ends | Generate HTML report |

**Important Clarification:** PRD referenced `Stop` hook, but documentation shows:
- `Stop` = fires when Claude finishes responding (per-turn)
- `SessionEnd` = fires when session ends (correct for report generation)

**Exit Codes:**
- `0` = Allow (with optional JSON feedback)
- `2` = Block (PreToolUse only)

**JSON Output Format:**
```json
{"decision": "block", "reason": "Warning message for Claude"}
```

### Hook Architecture (Final)

| Hook | Matcher | Script | Purpose |
|------|---------|--------|---------|
| `SessionStart` | `*` | `session-start.py` | Initialize session JSON at `{project}/.nova-protector/sessions/` |
| `PreToolUse` | `*` | `pre-tool-guard.py` | Scan inputs, block critical threats (exit 2) |
| `PostToolUse` | `Read\|WebFetch\|Bash\|Grep\|Task\|mcp__*` | `post-tool-nova-guard.py` | Capture event + NOVA scan (extend existing) |
| `SubagentStop` | `*` | `post-tool-nova-guard.py` | Capture subagent completion |
| `SessionEnd` | `*` | `session-end.py` | Generate HTML report from session JSON |

### Extensions Required

**New Hook Scripts:**

| Script | Hook Event | Purpose |
|--------|------------|---------|
| `session-start.py` | SessionStart | Initialize session, create JSON file |
| `pre-tool-guard.py` | PreToolUse | Pre-execution threat blocking |
| `session-end.py` | SessionEnd | Report generation orchestration |

**New Modules:**

| Module | Purpose | Location |
|--------|---------|----------|
| `report_generator.py` | JSON → HTML conversion | `hooks/lib/` |
| `ai_summary.py` | Generate session summary via LLM | `hooks/lib/` |
| `session_manager.py` | Session JSON read/write utilities | `hooks/lib/` |

**New Directories:**

| Directory | Purpose |
|-----------|---------|
| `hooks/lib/` | Shared Python modules between hooks |
| `templates/` | HTML report template(s) |

### Starter Selection

**Decision: No external starter template needed.**

Rationale:
1. Existing codebase provides the foundation
2. PEP 723 inline metadata eliminates packaging complexity
3. Structure is simple and purpose-built for hooks
4. Adding complexity would violate "boring technology" principle

**Initialization Command:** N/A - extend existing codebase

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Session JSON schema (defines all data structures)
- Storage location strategy (affects install script)
- HTML generation approach (defines report pipeline)

**Important Decisions (Shape Architecture):**
- AI summary integration (affects dependencies)
- Performance strategy (affects reliability)

**Deferred Decisions (Post-MVP):**
- Custom rule authoring UI
- Session comparison/diff features
- Checksum integrity verification

### Session Data Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **JSON Schema** | 10 event fields + 7 NOVA fields + summary | Matches PRD FR1-FR16 requirements |
| **Storage Location** | `{project}/.nova-protector/sessions/` | Project-specific, easy to gitignore |
| **Report Location** | `{project}/.nova-protector/reports/` | Alongside sessions |
| **Session ID Format** | `YYYY-MM-DD_HH-MM-SS_abc123` | Sortable timestamp + uniqueness hash |
| **Session File Format** | JSON Lines (`.jsonl`) during capture | Fast append, converted at session end |

**Session JSON Schema:**

```json
{
  "session_id": "2026-01-10_16-30-45_a1b2c3",
  "session_start": "2026-01-10T16:30:45Z",
  "session_end": "2026-01-10T16:45:30Z",
  "platform": "darwin",
  "nova_version": "1.0.0",
  "project_dir": "/path/to/project",
  "events": [
    {
      "id": 1,
      "timestamp_start": "2026-01-10T16:30:46Z",
      "timestamp_end": "2026-01-10T16:30:46Z",
      "duration_ms": 123,
      "tool_name": "Read",
      "tool_input": {},
      "tool_output": "...",
      "working_dir": "/path",
      "files_accessed": ["/path/to/file"],
      "nova_verdict": "allowed",
      "nova_severity": null,
      "nova_rules_matched": [],
      "nova_scan_time_ms": 5
    }
  ],
  "summary": {
    "total_events": 47,
    "tools_used": {"Read": 10, "Bash": 5},
    "files_touched": 8,
    "warnings": 2,
    "blocked": 0,
    "ai_summary": "Session refactored authentication module..."
  }
}
```

### HTML Report Generation

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Templating** | Python f-strings | Zero dependencies, structure is fixed |
| **Single-File** | CSS + JS + data embedded | Portable, shareable |
| **Data Injection** | JSON in `<script>` tag | Clean separation, JS renders UI |

**Report Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <style>/* Embedded CSS */</style>
</head>
<body>
  <script>const SESSION_DATA = {...};</script>
  <script>/* Embedded JS - renders timeline, events */</script>
</body>
</html>
```

### AI Summary Integration

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **LLM Provider** | Anthropic Claude API | Consistent with Claude Code ecosystem |
| **Model** | `claude-3-5-haiku-20241022` | Fast, cost-effective for summaries |
| **API Key** | `ANTHROPIC_API_KEY` env var | Standard, secure |
| **Fallback** | Stats-only summary | Report useful even without LLM |

**Summary Prompt Template:**
```
Summarize this Claude Code session in 2-3 sentences:
- What was accomplished
- Key actions taken
- Any security events (warnings/blocks)

Session data: {events_summary}
```

### Performance Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Event Capture** | JSON Lines append | <1ms per write, no reparse |
| **File Locking** | None | Hooks execute sequentially |
| **Output Truncation** | 10KB default (configurable) | Prevent storage runaway |
| **Report Generation** | Synchronous at SessionEnd | Acceptable <3s for 500 events |

**Data Flow:**
```
SessionStart → init .jsonl file
     ↓
PostToolUse → append line to .jsonl (repeat per tool)
     ↓
SessionEnd → parse .jsonl → generate summary → write .json → generate .html
```

### Decision Impact Analysis

**Implementation Sequence:**
1. Session manager (JSON schema, storage paths)
2. SessionStart hook (initialize session)
3. PostToolUse hook extension (event capture + NOVA scan)
4. PreToolUse hook (threat blocking)
5. SessionEnd hook (report generation)
6. HTML template and renderer
7. AI summary integration
8. Install script updates

**Cross-Component Dependencies:**
- Session manager is foundation for all hooks
- HTML generator depends on finalized JSON schema
- AI summary depends on session JSON being complete
- Install script depends on all hooks being ready

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Addressed:** 6 areas standardized to ensure consistent implementation across all hooks and modules.

### Naming Patterns

**Python Code (PEP 8):**

| Element | Convention | Example |
|---------|------------|---------|
| Modules | `snake_case` | `session_manager.py`, `report_generator.py` |
| Functions | `snake_case` | `load_config()`, `scan_with_nova()` |
| Variables | `snake_case` | `tool_name`, `session_id` |
| Constants | `UPPER_SNAKE` | `MAX_OUTPUT_SIZE`, `DEFAULT_TIMEOUT` |
| Classes | `PascalCase` | `NovaScanner`, `SessionManager` |

**JSON Fields:**

| Convention | Example |
|------------|---------|
| `snake_case` | `tool_name`, `timestamp_start`, `nova_verdict` |
| Explicit nulls | `"nova_severity": null` (not omitted) |

**File Naming:**

| Type | Convention | Example |
|------|------------|---------|
| Hook scripts | `{hook-type}-{purpose}.py` | `session-start.py`, `pre-tool-guard.py` |
| Lib modules | `{purpose}_manager.py` | `session_manager.py`, `report_generator.py` |
| Config files | `{purpose}-config.yaml` | `nova-config.yaml` |
| Session files | `{timestamp}_{hash}.jsonl` | `2026-01-10_16-30-45_a1b2c3.jsonl` |
| Report files | `{timestamp}_{hash}.html` | `2026-01-10_16-30-45_a1b2c3.html` |

### Structure Patterns

**Project Organization:**

```
hooks/
├── session-start.py      # SessionStart hook
├── pre-tool-guard.py     # PreToolUse hook
├── post-tool-nova-guard.py  # PostToolUse hook (existing, extend)
├── session-end.py        # SessionEnd hook
├── test-nova-guard.py    # Test script (existing)
└── lib/                  # Shared modules
    ├── __init__.py
    ├── session_manager.py
    ├── report_generator.py
    └── ai_summary.py
```

**Import Pattern:**

All hooks use relative path manipulation for lib imports:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session_manager import SessionManager
```

### Format Patterns

**JSON Schema Consistency:**

- All timestamps: ISO 8601 format (`2026-01-10T16:30:45Z`)
- All durations: Milliseconds as integer (`duration_ms: 123`)
- All paths: Absolute paths as strings
- All arrays: Empty array `[]` not null when no items
- All objects: Include all fields, use `null` for missing values

**Session JSON Lines Format (.jsonl):**

Each line is a complete JSON object:

```json
{"type": "init", "session_id": "...", "timestamp": "..."}
{"type": "event", "id": 1, "tool_name": "Read", ...}
{"type": "event", "id": 2, "tool_name": "Bash", ...}
```

### Communication Patterns

**Hook I/O Standard:**

| Direction | Format | Destination |
|-----------|--------|-------------|
| Input | JSON from stdin | Parsed with `json.load(sys.stdin)` |
| Output | JSON to stdout | Only for Claude feedback |
| Logs | Text to stderr | Debug/error information |
| Exit | Code 0 or 2 | 0=allow, 2=block (PreToolUse only) |

**Logging Pattern:**

```python
import logging
logging.basicConfig(
    level=logging.DEBUG if config.get("debug") else logging.WARNING,
    format="[NOVA %(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("nova-protector")
```

### Process Patterns

**Error Handling (Fail-Open):**

```python
def main():
    try:
        # Hook logic here
        pass
    except json.JSONDecodeError:
        logger.warning("Invalid JSON input, allowing")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}, allowing")
        sys.exit(0)

    # Success path
    sys.exit(0)
```

**Configuration Loading:**

```python
def load_config() -> dict:
    """Load config with multi-path discovery."""
    paths = [
        Path(__file__).parent / "config" / "nova-config.yaml",
        Path(__file__).parent.parent / "config" / "nova-config.yaml",
    ]
    for path in paths:
        if path.exists():
            return yaml.safe_load(path.read_text())
    return DEFAULT_CONFIG
```

### Visual Design Patterns

**CSS Variables:**

```css
:root {
  /* Verdict colors */
  --color-allowed: #22c55e;
  --color-warned: #f59e0b;
  --color-blocked: #ef4444;
  --color-neutral: #6b7280;

  /* UI colors */
  --color-bg: #ffffff;
  --color-text: #1f2937;
  --color-border: #e5e7eb;
}
```

**Health Badge Logic:**

| Condition | Badge | Color |
|-----------|-------|-------|
| Any blocked | "BLOCKED" | Red |
| Any warned, no blocked | "WARNINGS" | Amber |
| All allowed | "CLEAN" | Green |

### Enforcement Guidelines

**All AI Agents MUST:**

1. Use `snake_case` for all Python code and JSON fields
2. Include explicit `null` values (never omit fields)
3. Use `logging` module, never `print()` for debug output
4. Always exit 0 except PreToolUse blocking (exit 2)
5. Use relative path manipulation for lib imports
6. Follow ISO 8601 for all timestamps

**Pattern Verification:**

- Code review checks naming conventions
- JSON schema validation in tests
- Linting with `ruff` for Python style

### Pattern Examples

**Good Example - Event Capture:**

```python
event = {
    "id": self.event_counter,
    "timestamp_start": start_time.isoformat() + "Z",
    "timestamp_end": end_time.isoformat() + "Z",
    "duration_ms": int((end_time - start_time).total_seconds() * 1000),
    "tool_name": tool_name,
    "tool_input": tool_input,
    "tool_output": truncate_output(tool_output, MAX_OUTPUT_SIZE),
    "nova_verdict": verdict,
    "nova_severity": severity,  # null if allowed
    "nova_rules_matched": matched_rules,  # [] if none
}
```

**Anti-Pattern - Avoid:**

```python
# BAD: camelCase
event = {"toolName": "Read", "timestampStart": "..."}

# BAD: omitting null fields
event = {"tool_name": "Read"}  # missing nova_severity

# BAD: print for logging
print(f"Debug: {event}")  # Use logger.debug()
```

## Project Structure & Boundaries

### Complete Directory Tree

```
nova_claude_code_protector/
├── hooks/                            # All hook scripts
│   ├── session-start.py              # NEW: SessionStart hook
│   ├── pre-tool-guard.py             # NEW: PreToolUse hook (threat blocking)
│   ├── post-tool-nova-guard.py       # EXTEND: PostToolUse hook (event capture + NOVA scan)
│   ├── session-end.py                # NEW: SessionEnd hook (report generation)
│   ├── test-nova-guard.py            # EXISTING: Test script
│   └── lib/                          # NEW: Shared modules
│       ├── __init__.py
│       ├── session_manager.py        # Session JSON read/write utilities
│       ├── report_generator.py       # JSON → HTML conversion
│       └── ai_summary.py             # LLM-powered session summaries
│
├── config/                           # Configuration files
│   ├── nova-config.yaml              # EXISTING: NOVA scanner config
│   └── settings-template.json        # EXISTING: Claude Code settings template
│
├── templates/                        # NEW: HTML templates
│   └── report.html                   # Report template (CSS + JS + placeholders)
│
├── rules/                            # EXISTING: NOVA detection rules
│   ├── context_manipulation.nov
│   ├── encoding_obfuscation.nov
│   ├── instruction_override.nov
│   └── roleplay_jailbreak.nov
│
├── cookbook/                         # EXISTING: Documentation
├── test-files/                       # EXISTING: Test data
│
├── install.sh                        # UPDATE: Add new hooks registration
├── README.md                         # UPDATE: Add session tracing docs
├── SKILL.md                          # EXISTING: PAI skill definition
└── pyproject.toml                    # OPTIONAL: For development tooling
```

### Runtime Storage (Per-Project)

Created automatically by hooks in each Claude Code project:

```
{user-project}/
└── .nova-protector/                  # Gitignored by default
    ├── sessions/                     # Raw session data
    │   ├── {session_id}.jsonl        # Active session (JSON Lines)
    │   └── {session_id}.json         # Completed session
    └── reports/                      # Generated HTML reports
        └── {session_id}.html
```

### Requirements-to-Structure Mapping

| Requirement Group | Files Responsible |
|-------------------|-------------------|
| **FR1-FR9** Session Tracing | `session-start.py`, `post-tool-nova-guard.py`, `lib/session_manager.py` |
| **FR10-FR16** Security Protection | `pre-tool-guard.py`, `post-tool-nova-guard.py`, `rules/*.nov` |
| **FR17-FR22** Report Generation | `session-end.py`, `lib/report_generator.py`, `lib/ai_summary.py` |
| **FR23-FR37** Report Viewing | `templates/report.html` (embedded CSS/JS) |
| **FR38-FR42** Installation | `install.sh`, `config/settings-template.json` |

### Architectural Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code                               │
│                    (Triggers hook events)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  session-start  │  │   pre-tool      │  │   post-tool     │
│     .py         │  │   guard.py      │  │  nova-guard.py  │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │    hooks/lib/     │
                    │ (shared modules)  │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   .jsonl/.json  │  │  NOVA Scanner   │  │  Claude API     │
│   (storage)     │  │  (nova-hunting) │  │  (AI summary)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   session-end.py    │
                    │ (report generation) │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   .html report      │
                    │ (self-contained)    │
                    └─────────────────────┘
```

### Module Responsibilities

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `session_manager.py` | Session lifecycle, JSON read/write, path resolution | `pyyaml` |
| `report_generator.py` | HTML generation, template rendering | None (f-strings) |
| `ai_summary.py` | LLM API calls, prompt construction, fallback handling | `anthropic` SDK |

## Architecture Validation

### Validation Checklist

| Check | Status | Notes |
|-------|--------|-------|
| **All 42 FRs have assigned files** | ✅ PASS | FR1-FR42 mapped in Requirements-to-Structure table |
| **All NFRs have architectural support** | ✅ PASS | Performance (<1ms), Security, Reliability addressed |
| **No orphan components** | ✅ PASS | Every module has clear responsibility and consumer |
| **Dependencies are minimal** | ✅ PASS | Only `nova-hunting`, `pyyaml`, `anthropic` (optional) |
| **Existing patterns preserved** | ✅ PASS | PEP 723, fail-open, multi-path config maintained |
| **Hook events correctly mapped** | ✅ PASS | SessionStart, PreToolUse, PostToolUse, SessionEnd |

### Coherence Verification

**Data Flow Traceability:**

```
SessionStart hook
    └── Creates: {session_id}.jsonl (init record)
         │
PostToolUse hook (per tool call)
    └── Appends: event record to .jsonl
    └── Uses: NOVA scanner for threat detection
         │
SessionEnd hook
    └── Reads: .jsonl file
    └── Generates: .json (complete session)
    └── Generates: .html (interactive report)
    └── Uses: Claude API for AI summary (optional)
```

### Gap Analysis

| Potential Gap | Resolution |
|---------------|------------|
| Session resume handling | SessionStart detects existing .jsonl, continues appending |
| Concurrent sessions | Session ID includes timestamp+hash, unique per session |
| Large output truncation | Configurable 10KB limit in config |
| Missing ANTHROPIC_API_KEY | Falls back to stats-only summary |
| Disk full scenarios | Fail-open, log error, session continues |

### Implementation Priority

**Phase 1 - Foundation (Must Have):**
1. `hooks/lib/session_manager.py` - Core session handling
2. `hooks/session-start.py` - Initialize session
3. `hooks/post-tool-nova-guard.py` - Extend for event capture

**Phase 2 - Security (Must Have):**
4. `hooks/pre-tool-guard.py` - Pre-execution blocking

**Phase 3 - Reporting (Must Have):**
5. `hooks/lib/report_generator.py` - HTML generation
6. `templates/report.html` - Report template
7. `hooks/session-end.py` - Report orchestration

**Phase 4 - Enhancement (Should Have):**
8. `hooks/lib/ai_summary.py` - AI-powered summaries
9. `install.sh` updates - One-command installation

### Final Architecture Summary

| Metric | Value |
|--------|-------|
| **New Hook Scripts** | 3 (`session-start.py`, `pre-tool-guard.py`, `session-end.py`) |
| **Extended Scripts** | 1 (`post-tool-nova-guard.py`) |
| **New Modules** | 3 (`session_manager.py`, `report_generator.py`, `ai_summary.py`) |
| **New Directories** | 2 (`hooks/lib/`, `templates/`) |
| **External Dependencies** | 3 (`nova-hunting`, `pyyaml`, `anthropic`) |
| **Total FRs Covered** | 42/42 |

---

_Architecture document completed on 2026-01-11. Ready for implementation._

