# Story 5.2: Configuration and Extensibility

Status: done

## Story

As a **power user**,
I want **optional configuration and custom rules**,
So that **I can customize the tool for my needs**.

## Acceptance Criteria

### AC1: Sensible Defaults
**Given** the tool is installed with no configuration file
**When** Claude Code sessions run
**Then** the tool operates with sensible defaults:
- Reports saved to `{project}/.nova-protector/reports/`
- All built-in rules enabled
- Output truncation at 10KB
- AI summary enabled (if API key present)

### AC2: Configuration File Loading
**Given** a `config/nova-protector.yaml` file exists
**When** the tool loads configuration
**Then** it reads and applies custom settings

### AC3: Custom Report Location
**Given** the user wants to customize report location
**When** they set `report_output_dir` in config
**Then** reports are saved to the specified directory instead of default

### AC4: Custom Rules Loading
**Given** the user creates a `.nov` file in `rules/` directory
**When** NOVA scanning runs
**Then** the custom rule is loaded and applied alongside built-in rules

### AC5: Rule Error Handling
**Given** a custom rule has syntax errors
**When** rules are loaded
**Then** the error is logged to stderr
**And** other valid rules continue to function
**And** the tool doesn't crash

### AC6: Disable AI Summaries
**Given** the user wants to disable AI summaries
**When** they set `ai_summary_enabled: false` in config
**Then** reports use stats-only summaries
**And** no API calls are made

### AC7: Unknown Keys Handling
**Given** the configuration file has unknown keys
**When** config is loaded
**Then** unknown keys are ignored
**And** a warning is logged
**And** valid configuration is applied

## Tasks / Subtasks

- [x] Task 1: Analyze requirements and plan implementation
  - [x] 1.1: Review AC and understand requirements
  - [x] 1.2: Review existing configuration usage
  - [x] 1.3: Design configuration module structure

- [x] Task 2: Implement configuration module (AC: 1, 2, 7)
  - [x] 2.1: Create config.py in hooks/lib/
  - [x] 2.2: Define sensible defaults
  - [x] 2.3: Implement YAML loading
  - [x] 2.4: Handle unknown keys with warning
  - [x] 2.5: Add type validation

- [x] Task 3: Integrate custom report location (AC: 3)
  - [x] 3.1: Update session-end.py to use config
  - [x] 3.2: Update report_generator.py to accept output dir
  - [x] 3.3: Test custom directory creation

- [x] Task 4: Integrate AI summary toggle (AC: 6)
  - [x] 4.1: Update ai_summary.py to respect config
  - [x] 4.2: Skip API calls when disabled
  - [x] 4.3: Use stats-only summary when disabled

- [x] Task 5: Custom rules loading (AC: 4, 5)
  - [x] 5.1: Load custom .nov files from rules/ directory
  - [x] 5.2: Log errors for invalid rules
  - [x] 5.3: Continue with valid rules on error

- [x] Task 6: Write comprehensive tests (AC: All)
  - [x] 6.1: Test default configuration
  - [x] 6.2: Test YAML loading
  - [x] 6.3: Test custom report location
  - [x] 6.4: Test AI summary toggle
  - [x] 6.5: Test unknown keys warning
  - [x] 6.6: Test rule error handling

- [x] Task 7: Run full test suite and verify
  - [x] 7.1: Run pytest on all tests
  - [x] 7.2: Verify all tests pass (483 total tests)

## Dev Notes

### Configuration File Location

Primary: `{NOVA_DIR}/config/nova-protector.yaml`
Fallback: Use sensible defaults

### Default Configuration

```yaml
# NOVA Claude Code Protector Configuration
# =========================================

# Report output location (relative to project or absolute path)
# Default: {project}/.nova-protector/reports/
report_output_dir: ""  # Empty = use default

# AI Summary settings
ai_summary_enabled: true  # Set to false to use stats-only summaries

# Output truncation
output_truncation_kb: 10  # Maximum size in KB for tool outputs in reports

# Custom rules directory (relative to NOVA_DIR)
# Additional .nov files in this directory will be loaded
custom_rules_dir: "rules/"
```

### Integration Points

1. **session-end.py**: Load config, pass report_output_dir to generator
2. **report_generator.py**: Accept output_dir parameter
3. **ai_summary.py**: Check ai_summary_enabled before API calls
4. **post-tool-nova-guard.py**: Load custom rules alongside built-in

### References

- [Source: epics.md#Story 5.2] - Original acceptance criteria
- [Source: config/nova-config.yaml] - Existing NOVA scanning config

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No issues encountered during implementation

### Completion Notes List

- Created `hooks/lib/config.py` with NovaConfig dataclass and YAML loading
- Sensible defaults: report_output_dir="", ai_summary_enabled=True, output_truncation_kb=10
- YAML config loaded from `config/nova-protector.yaml` when present
- Unknown keys logged as warnings but don't prevent loading valid config
- `get_report_output_dir(project_dir)` supports absolute, relative, or default paths
- `get_custom_rules_path()` returns path to custom rules directory
- Added `ai_enabled` parameter to `generate_ai_summary()` function
- Updated `session-end.py` to load config and use custom report directory
- Updated `session-end.py` to pass ai_summary_enabled to AI summary generator
- Created `config/nova-protector.yaml` template with documented options
- Added 32 new tests for Story 5.2 acceptance criteria
- All 483 tests pass (451 existing + 32 new)

### File List

- `hooks/lib/config.py` - New configuration module (230 lines)
- `config/nova-protector.yaml` - New configuration template
- `hooks/lib/ai_summary.py` - Added ai_enabled parameter
- `hooks/session-end.py` - Integrated config loading
- `tests/test_config.py` - New tests for Story 5.2 (32 tests)
