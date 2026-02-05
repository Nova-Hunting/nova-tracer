# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Nova-tracer - PreToolUse Hook (Fast Blocking)
Agent Monitoring and Visibility
=============================================================

Fast pre-execution check that blocks dangerous commands BEFORE execution.
Uses simple pattern matching for speed - full NOVA scanning happens in PostToolUse.

Supports configurable compliance rules via JSON config files.
Config search order:
  1. $CLAUDE_PROJECT_DIR/.nova-tracer/pre-tool-rules.json (project override)
  2. {nova_dir}/config/pre-tool-rules.json (installation config)
  3. Default hardcoded patterns (always available)

Exit codes:
  0 = Allow tool execution
  2 = Block tool execution (dangerous command detected)

JSON output for blocks:
  {"decision": "block", "reason": "[Nova-tracer] Blocked: {reason}"}
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Protected file paths - these should not be modified by the agent
PROTECTED_FILES: List[Tuple[str, str]] = [
    (r'(^|/)\.claude/settings\.json$', "Claude settings file"),
]

# Default dangerous command patterns to block (security baseline)
DEFAULT_BASH_PATTERNS: List[Tuple[str, str]] = [
    # Destructive file operations
    (r'\brm\s+(-[rf]+\s+)*(/|~|\$HOME|\$PAI_DIR|/\*)', "Destructive rm command"),
    (r'\brm\s+-rf\s+/', "rm -rf on root"),
    (r'\bsudo\s+rm\s+-rf', "sudo rm -rf"),

    # Disk operations
    (r'\bmkfs\b', "Filesystem format command"),
    (r'\bdd\s+if=.+of=/dev/', "Direct disk write"),
    (r'\bdiskutil\s+(erase|partition|zero)', "Disk utility erase"),

    # Fork bombs and system abuse
    (r':\(\)\s*\{\s*:\|:\s*&\s*\}', "Fork bomb"),
    (r'\bfork\s*bomb', "Fork bomb reference"),

    # Credential/key exfiltration
    (r'curl.+\|\s*sh', "Pipe curl to shell"),
    (r'wget.+\|\s*sh', "Pipe wget to shell"),
    (r'cat\s+.*(id_rsa|\.pem|\.key|password|credentials)', "Reading sensitive files"),

    # Dangerous redirects
    (r'>\s*/dev/sd[a-z]', "Redirect to disk device"),
    (r'>\s*/dev/null\s*2>&1\s*&', "Background with hidden output"),

    # Block skills management commands
    (r'\bnpx\s+skills\s+add', "Skills add command blocked"),
    (r'\bnpx\s+skills\s+find', "Skills find command blocked"),
]

# Default write content patterns to block (security baseline)
# Note: These patterns target actual malicious payloads, not legitimate code.
# innerHTML, document.write are valid JS APIs - we only block suspicious combinations.
DEFAULT_CONTENT_PATTERNS: List[Tuple[str, str]] = [
    # XSS: Block eval with user-controlled input patterns
    (r'eval\s*\(\s*(location|document\.URL|document\.cookie|window\.name)', "XSS eval injection"),
    # XSS: Block document.write with script injection
    (r'document\.write\s*\([^)]*<script', "XSS document.write injection"),
    # SQL injection patterns
    (r";\s*DROP\s+TABLE", "SQL injection attempt"),
    (r"UNION\s+SELECT.*FROM", "SQL injection attempt"),
    (r"'\s*OR\s+'1'\s*=\s*'1", "SQL injection attempt"),
]


def _find_config_file() -> Optional[Path]:
    """Find config file with priority: project > installation.

    Returns the first existing config file path, or None if not found.
    """
    # 1. Project-level override
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        project_config = Path(project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        if project_config.exists():
            return project_config

    # 2. Installation-level config
    script_dir = Path(__file__).parent
    install_config = script_dir.parent / "config" / "pre-tool-rules.json"
    if install_config.exists():
        return install_config

    return None


def _load_config() -> Dict[str, Any]:
    """Load config from file, return empty dict on error (fail-open)."""
    config_path = _find_config_file()
    if not config_path:
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fail-open: if config is invalid, use defaults only
        return {}


def _get_patterns() -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Return merged patterns (default + compliance rules).

    Returns:
        Tuple of (bash_patterns, content_patterns)
    """
    bash_patterns = list(DEFAULT_BASH_PATTERNS)
    content_patterns = list(DEFAULT_CONTENT_PATTERNS)

    config = _load_config()

    # Check if any default rules should be disabled (for testing)
    disabled_defaults = set(config.get("disable_default_rules", []))
    if disabled_defaults:
        # Filter out disabled default rules by their reason
        bash_patterns = [(p, r) for p, r in bash_patterns if r not in disabled_defaults]
        content_patterns = [(p, r) for p, r in content_patterns if r not in disabled_defaults]

    # Add compliance rules
    compliance = config.get("compliance_rules", {})

    for rule in compliance.get("bash", []):
        if rule.get("enabled", True):
            pattern = rule.get("pattern")
            reason = rule.get("reason", "Blocked by compliance policy")
            if pattern:
                bash_patterns.append((pattern, reason))

    for rule in compliance.get("write", []):
        if rule.get("enabled", True):
            pattern = rule.get("pattern")
            reason = rule.get("reason", "Blocked by compliance policy")
            if pattern:
                content_patterns.append((pattern, reason))

    return bash_patterns, content_patterns


def check_protected_file(file_path: str) -> Optional[str]:
    """Check if a file path is protected from modification.

    Returns the reason if protected, None if allowed.
    """
    if not file_path:
        return None

    for pattern, reason in PROTECTED_FILES:
        if re.search(pattern, file_path):
            return reason

    return None


def check_dangerous_command(command: str, patterns: Optional[List[Tuple[str, str]]] = None) -> Optional[str]:
    """Check if a bash command is dangerous.

    Args:
        command: The bash command to check
        patterns: List of (pattern, reason) tuples. If None, uses DEFAULT_BASH_PATTERNS.

    Returns the reason if dangerous, None if safe.
    """
    if not command:
        return None

    if patterns is None:
        patterns = DEFAULT_BASH_PATTERNS

    for pattern, reason in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return reason

    return None


def check_dangerous_content(content: str, patterns: Optional[List[Tuple[str, str]]] = None) -> Optional[str]:
    """Check if write content contains dangerous patterns.

    Args:
        content: The content to check
        patterns: List of (pattern, reason) tuples. If None, uses DEFAULT_CONTENT_PATTERNS.

    Returns the reason if dangerous, None if safe.
    """
    if not content:
        return None

    if patterns is None:
        patterns = DEFAULT_CONTENT_PATTERNS

    for pattern, reason in patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            return reason

    return None


def main() -> None:
    """Main entry point for the PreToolUse hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        # Invalid input, fail open (allow)
        sys.exit(0)

    # Load patterns (default + compliance rules)
    bash_patterns, content_patterns = _get_patterns()

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    block_reason = None

    # Check Bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        block_reason = check_dangerous_command(command, bash_patterns)

    # Check Write content and protected files
    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        block_reason = check_protected_file(file_path)
        if not block_reason:
            content = tool_input.get("content", "")
            block_reason = check_dangerous_content(content, content_patterns)

    # Check Edit content and protected files
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        block_reason = check_protected_file(file_path)
        if not block_reason:
            new_string = tool_input.get("new_string", "")
            block_reason = check_dangerous_content(new_string, content_patterns)

    if block_reason:
        # Block the operation
        output = {
            "decision": "block",
            "reason": f"[Nova-tracer] Blocked: {block_reason}"
        }
        print(json.dumps(output))
        # Note: Telemetry logging disabled for performance - each hook is a new process
        # and log_event() re-parses config + discovers plugins on every call
        sys.exit(2)

    # Allow the operation
    sys.exit(0)

if __name__ == "__main__":
    main()
