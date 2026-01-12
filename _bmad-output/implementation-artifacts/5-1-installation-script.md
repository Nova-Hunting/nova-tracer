# Story 5.1: Installation Script

Status: done

## Story

As a **Claude Code user**,
I want **to install NOVA Claude Code Protector with a single command**,
So that **I can start protecting my sessions immediately**.

## Acceptance Criteria

### AC1: Script Completes Without Errors
**Given** the user has cloned the repository
**When** they run `./install.sh`
**Then** the script completes without errors
**And** provides clear progress output

### AC2: Hook Registration
**Given** the install script runs
**When** it registers hooks
**Then** it modifies `~/.claude/settings.json` to add:
- SessionStart hook -> `session-start.py`
- PreToolUse hook -> `pre-tool-guard.py`
- PostToolUse hook -> `post-tool-nova-guard.py`
- SessionEnd hook -> `session-end.py`

### AC3: Preserve Existing Hooks
**Given** `~/.claude/settings.json` already exists with other hooks
**When** install runs
**Then** existing hooks are preserved
**And** NOVA hooks are added/merged correctly

### AC4: Create Settings If Missing
**Given** `~/.claude/settings.json` doesn't exist
**When** install runs
**Then** the file is created with proper structure
**And** NOVA hooks are registered

### AC5: Hooks Activate Automatically
**Given** the install completes
**When** the user starts a Claude Code session
**Then** all NOVA hooks activate automatically

### AC6: Uninstall Script
**Given** the user wants to uninstall
**When** they run `./uninstall.sh`
**Then** NOVA hooks are removed from settings.json
**And** other hooks remain intact
**And** `.nova-protector/` directories are optionally preserved (user prompted)

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and plan implementation
  - [x] 1.1: Review AC and understand requirements
  - [x] 1.2: Review Claude Code hook registration format
  - [x] 1.3: Design install/uninstall script structure

- [x] Task 2: Implement install.sh (AC: 1, 2, 3, 4)
  - [x] 2.1: Create bash script with error handling
  - [x] 2.2: Detect and create ~/.claude directory if needed
  - [x] 2.3: Handle settings.json creation/modification
  - [x] 2.4: Register all four NOVA hooks
  - [x] 2.5: Preserve existing hooks when merging
  - [x] 2.6: Provide clear progress output

- [x] Task 3: Implement uninstall.sh (AC: 6)
  - [x] 3.1: Create uninstall bash script
  - [x] 3.2: Remove NOVA hooks from settings.json
  - [x] 3.3: Preserve other hooks
  - [x] 3.4: Prompt for .nova-protector directory cleanup

- [x] Task 4: Test installation flow (AC: 5)
  - [x] 4.1: Test fresh install
  - [x] 4.2: Test install with existing settings
  - [x] 4.3: Test uninstall

- [x] Task 5: Write comprehensive tests (AC: All)
  - [x] 5.1: Test install script execution
  - [x] 5.2: Test hook registration
  - [x] 5.3: Test existing hooks preservation
  - [x] 5.4: Test uninstall script

- [x] Task 6: Run full test suite and verify
  - [x] 6.1: Run pytest on all tests
  - [x] 6.2: Verify all tests pass (451 total tests)

## Dev Notes

### Claude Code Hook Registration Format

Based on the Claude Code hooks system, `~/.claude/settings.json` has this structure:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "/path/to/script.py"
      }
    ],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "SessionEnd": [...]
  }
}
```

### NOVA Hooks to Register

1. **SessionStart**: `hooks/session-start.py` - Initialize session
2. **PreToolUse**: `hooks/pre-tool-guard.py` - Block dangerous commands
3. **PostToolUse**: `hooks/post-tool-nova-guard.py` - Log and scan
4. **SessionEnd**: `hooks/session-end.py` - Generate report

### Install Script Flow

```bash
#!/bin/bash
# 1. Detect NOVA_DIR (script location)
# 2. Check for ~/.claude directory
# 3. Read or create settings.json
# 4. Merge NOVA hooks with existing hooks
# 5. Write updated settings.json
# 6. Verify installation
```

### Uninstall Script Flow

```bash
#!/bin/bash
# 1. Read settings.json
# 2. Remove NOVA hooks (by matching command paths)
# 3. Write updated settings.json
# 4. Prompt for .nova-protector cleanup
```

### References

- [Source: epics.md#Story 5.1] - Original acceptance criteria
- [Source: Claude Code docs] - Hook registration format

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No issues encountered during implementation

### Completion Notes List

- Rewrote install.sh to register hooks globally in ~/.claude/settings.json
- Uses jq for JSON manipulation (added as prerequisite check)
- Registers all 4 NOVA hooks: SessionStart, PreToolUse, PostToolUse, SessionEnd
- SessionStart: hooks/session-start.py for session tracking
- PreToolUse: hooks/pre-tool-guard.py for Bash, Write, Edit tools
- PostToolUse: hooks/post-tool-nova-guard.py for Read, WebFetch, Bash, Grep, Glob, Task, mcp__*, mcp_*
- SessionEnd: hooks/session-end.py for report generation
- Preserves existing hooks when merging using jq deep merge
- Creates backup of settings.json before modification
- Created uninstall.sh to remove NOVA hooks while preserving others
- Uninstall prompts for optional .nova-protector directory cleanup
- Added 35 new tests for Story 5.1 acceptance criteria
- All 451 tests pass (416 existing + 35 new)

### File List

- `install.sh` - Updated global installation script (402 lines)
- `uninstall.sh` - New uninstall script (149 lines)
- `tests/test_installation.py` - New tests for Story 5.1 (35 tests)
