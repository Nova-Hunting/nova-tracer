# Story 1.4: Context and File Path Extraction

Status: done

## Story

As a **security analyst reviewing sessions**,
I want **to see which files were accessed and the working directory**,
So that **I can understand the context of each action**.

## Acceptance Criteria

### AC1: Working Directory Context
**Given** a tool call is captured
**When** the event is processed
**Then** working_dir is populated with the current working directory

### AC2: Read Tool File Extraction
**Given** a Read tool call with file_path input
**When** the event is captured
**Then** files_accessed contains the file path from the input

### AC3: Bash Command File Extraction
**Given** a Bash tool call
**When** the event is captured
**Then** files_accessed extracts any file paths mentioned in the command

### AC4: Edit/Write Tool File Extraction
**Given** an Edit or Write tool call
**When** the event is captured
**Then** files_accessed contains the target file path

### AC5: Empty Files Array for Non-File Tools
**Given** a tool with no file-related inputs
**When** the event is captured
**Then** files_accessed is an empty array (not null)

## Tasks / Subtasks

- [x] Task 1: Implement file path extraction function (AC: 2, 3, 4, 5)
  - [x] 1.1: Create `extract_files_accessed(tool_name, tool_input)` in session_manager
  - [x] 1.2: Handle Read tool - extract file_path from input
  - [x] 1.3: Handle Edit/Write tools - extract file_path from input
  - [x] 1.4: Handle Glob tool - extract path from input
  - [x] 1.5: Handle Grep tool - extract path from input
  - [x] 1.6: Handle Bash tool - regex extract file paths from command
  - [x] 1.7: Return empty array for unhandled tools

- [x] Task 2: Implement Bash file path extraction (AC: 3)
  - [x] 2.1: Define regex patterns for common file path formats
  - [x] 2.2: Handle absolute paths (/path/to/file)
  - [x] 2.3: Handle relative paths (./file, ../file)
  - [x] 2.4: Handle home directory paths (~/file)
  - [x] 2.5: Filter out false positives (URLs, options like -rf)
  - [x] 2.6: Deduplicate extracted paths

- [x] Task 3: Update post-tool-nova-guard.py (AC: 1, 2, 3, 4, 5)
  - [x] 3.1: Import extract_files_accessed from session_manager
  - [x] 3.2: Call extraction function with tool_name and tool_input
  - [x] 3.3: Replace placeholder `files_accessed: []` with extracted paths
  - [x] 3.4: Verify working_dir is already populated correctly

- [x] Task 4: Write comprehensive tests (AC: 1, 2, 3, 4, 5)
  - [x] 4.1: Test Read tool file path extraction
  - [x] 4.2: Test Edit/Write tool file path extraction
  - [x] 4.3: Test Bash command file path extraction
  - [x] 4.4: Test Glob/Grep tool path extraction
  - [x] 4.5: Test empty array for non-file tools
  - [x] 4.6: Test edge cases (no command, empty input)
  - [x] 4.7: Integration test with full hook flow

## Dev Notes

### Architecture Requirements

**Function Location:** `hooks/lib/session_manager.py`

This story adds file extraction to complete Epic 1's session capture functionality.

### File Path Extraction Patterns

**Direct Input Tools:**
| Tool | Input Field | Example |
|------|-------------|---------|
| Read | `file_path` | `{"file_path": "/path/to/file.py"}` |
| Edit | `file_path` | `{"file_path": "/path/to/file.py", ...}` |
| Write | `file_path` | `{"file_path": "/path/to/file.py", ...}` |
| Glob | `path` | `{"pattern": "*.py", "path": "/src"}` |
| Grep | `path` | `{"pattern": "TODO", "path": "/project"}` |

**Bash Command Extraction:**

Regex patterns to extract file paths from commands:

```python
BASH_PATH_PATTERNS = [
    r'(?:^|\s)(/[^\s]+)',           # Absolute paths: /path/to/file
    r'(?:^|\s)(\.\.?/[^\s]+)',      # Relative paths: ./file or ../file
    r'(?:^|\s)(~/[^\s]+)',          # Home dir: ~/file
]

BASH_PATH_EXCLUDES = [
    r'^-',                           # CLI options like -rf
    r'^https?://',                   # URLs
    r'^[a-z]+://',                   # Other URLs (ftp://, etc.)
]
```

### Implementation Pattern

```python
def extract_files_accessed(tool_name: str, tool_input: Dict[str, Any]) -> List[str]:
    """
    Extract file paths accessed by a tool.

    Args:
        tool_name: Name of the tool (Read, Edit, Bash, etc.)
        tool_input: The tool's input parameters

    Returns:
        List of file paths, empty list if none
    """
    if not tool_input:
        return []

    paths = []

    # Direct path extraction for file-based tools
    if tool_name in ("Read", "Edit", "Write"):
        file_path = tool_input.get("file_path")
        if file_path:
            paths.append(file_path)

    elif tool_name in ("Glob", "Grep"):
        path = tool_input.get("path")
        if path:
            paths.append(path)

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        paths.extend(_extract_paths_from_bash(command))

    # Deduplicate while preserving order
    seen = set()
    unique_paths = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique_paths.append(p)

    return unique_paths
```

### Bash Path Extraction Function

```python
def _extract_paths_from_bash(command: str) -> List[str]:
    """Extract file paths from a bash command."""
    import re

    if not command:
        return []

    paths = []

    # Pattern to match file paths
    # Matches: /absolute/path, ./relative, ../parent, ~/home
    path_pattern = r'(?:^|\s)([~/.]?/?[a-zA-Z0-9_\-./]+(?:\.[a-zA-Z0-9]+)?)'

    for match in re.finditer(path_pattern, command):
        path = match.group(1).strip()

        # Skip if it looks like a CLI flag
        if path.startswith('-'):
            continue

        # Skip if it looks like a URL
        if '://' in path:
            continue

        # Must start with /, ./, ../, or ~/
        if path.startswith(('/','./','../', '~/')):
            paths.append(path)

    return paths
```

### Integration into Hook

Current placeholder in `capture_event()`:
```python
event_record = {
    ...
    "files_accessed": [],  # Placeholder - Story 1.4
    ...
}
```

Replace with:
```python
from session_manager import extract_files_accessed

event_record = {
    ...
    "files_accessed": extract_files_accessed(tool_name, tool_input),
    ...
}
```

### Test Cases

**Read Tool:**
```python
def test_read_tool_extracts_file_path():
    result = extract_files_accessed("Read", {"file_path": "/test/file.py"})
    assert result == ["/test/file.py"]
```

**Bash Command:**
```python
def test_bash_extracts_absolute_paths():
    result = extract_files_accessed("Bash", {"command": "cat /etc/passwd"})
    assert "/etc/passwd" in result

def test_bash_ignores_cli_flags():
    result = extract_files_accessed("Bash", {"command": "rm -rf /tmp/test"})
    assert "-rf" not in result
    assert "/tmp/test" in result
```

### Performance Requirements

| Operation | Target | Notes |
|-----------|--------|-------|
| `extract_files_accessed()` | < 0.5ms | Simple string operations |

### Previous Story Intelligence

**From Stories 1.1-1.3:**
- Python 3.9 compatibility: Use `List[str]` not `list[str]`
- Fail-open: Never raise exceptions
- working_dir already populated correctly (AC1 satisfied)

### References

- [Source: architecture.md#Session Data Architecture] - files_accessed field
- [Source: epics.md#Story 1.4] - Original acceptance criteria
- [Source: hooks/post-tool-nova-guard.py] - Current placeholder implementation

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 106 tests pass (38 new file extraction tests + 68 existing)
- Test run duration: 120.12s

### Completion Notes List

1. Implemented `_extract_paths_from_bash()` with regex pattern for absolute, relative, parent, and home directory paths
2. Implemented `extract_files_accessed()` supporting Read, Edit, Write, Bash, Glob, Grep, NotebookEdit tools
3. Updated `__init__.py` exports to include `extract_files_accessed`
4. Integrated extraction into `post-tool-nova-guard.py` replacing placeholder
5. Created comprehensive test suite with 38 tests covering all acceptance criteria
6. All edge cases handled: None input, empty dict, non-string paths, URL filtering, CLI flag filtering

### File List

**Modified:**
- `hooks/lib/session_manager.py` - Added `_extract_paths_from_bash()` and `extract_files_accessed()` functions
- `hooks/lib/__init__.py` - Added `extract_files_accessed` to exports
- `hooks/post-tool-nova-guard.py` - Integrated file extraction into event capture

**Created:**
- `tests/test_file_extraction.py` - 38 comprehensive tests for file path extraction
