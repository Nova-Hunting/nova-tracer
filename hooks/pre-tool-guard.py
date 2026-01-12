# /// script
# requires-python = ">=3.9"
# dependencies = ["nova-hunting", "pyyaml"]
# ///
"""
Claude Code NOVA Prompt Injection Guard - PreToolUse Hook
==============================================================

Scans tool inputs BEFORE execution using NOVA Framework detection.
Blocks critical-severity threats to prevent dangerous actions.

This hook runs BEFORE tool execution and can BLOCK dangerous tool calls.

Exit codes:
  0 = Allow tool execution (no threats, warnings only, or errors)
  2 = Block tool execution (high-severity threat detected)

JSON output for blocks:
  {"decision": "block", "reason": "[NOVA] Blocked: {rule_name}"}

For warnings (medium/low severity), the hook allows execution (exit 0)
and lets PostToolUse capture the warning details.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

# NOVA Framework imports
try:
    from nova.core.scanner import NovaScanner
    from nova.core.parser import NovaRuleFileParser
    NOVA_AVAILABLE = True
except ImportError:
    NOVA_AVAILABLE = False


def load_config() -> Dict[str, Any]:
    """Load NOVA configuration from config file.

    Checks multiple locations in order:
    1. Script's own directory (installed location)
    2. Parent config directory (development location)
    3. Project hooks directory (custom installation)
    """
    script_dir = Path(__file__).parent

    config_paths = [
        script_dir / "config" / "nova-config.yaml",
        script_dir.parent / "config" / "nova-config.yaml",
    ]

    # Check project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        config_paths.append(
            Path(project_dir) / ".claude" / "hooks" / "nova-guard" / "config" / "nova-config.yaml"
        )

    for path in config_paths:
        if path.exists():
            return _load_yaml(path)

    # Default configuration
    return {
        "llm_provider": "anthropic",
        "model": "claude-3-5-haiku-20241022",
        "enable_keywords": True,
        "enable_semantics": True,
        "enable_llm": True,
        "semantic_threshold": 0.7,
        "llm_threshold": 0.7,
        "min_severity": "low",
        "debug": False,
    }


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file safely."""
    if yaml is None:
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_rules_directory() -> Optional[Path]:
    """Find the rules directory.

    Checks multiple locations in order:
    1. Script's sibling rules directory (installed location)
    2. Parent rules directory (development location)
    3. Project hooks directory
    """
    script_dir = Path(__file__).parent

    rules_paths = [
        script_dir / "rules",
        script_dir.parent / "rules",
    ]

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        rules_paths.append(
            Path(project_dir) / ".claude" / "hooks" / "nova-guard" / "rules"
        )

    for path in rules_paths:
        if path.exists() and path.is_dir():
            return path

    return None


def extract_input_text(tool_input: Dict[str, Any]) -> str:
    """Extract scannable text from tool input.

    Focuses on fields that could contain prompt injection payloads:
    - command: Bash commands that might echo malicious content
    - content: Write tool content
    - prompt: Task/agent prompts
    - query: Search queries
    - new_string: Edit tool replacement text
    - old_string: Edit tool search text (less likely, but check)
    - pattern: Grep/Glob patterns
    """
    if not tool_input:
        return ""

    text_parts = []

    # Fields that could contain injection attempts
    scannable_fields = [
        "command",      # Bash commands
        "content",      # Write tool content
        "prompt",       # Task/agent prompts
        "query",        # Search queries
        "new_string",   # Edit tool replacement text
        "old_string",   # Edit tool search text
        "pattern",      # Grep/Glob patterns
    ]

    for field in scannable_fields:
        if field in tool_input:
            value = tool_input[field]
            if isinstance(value, str) and value:
                text_parts.append(value)

    return "\n".join(text_parts)


def scan_with_nova(text: str, config: Dict[str, Any], rules_dir: Path) -> List[Dict]:
    """Scan text using NOVA Framework rules.

    Args:
        text: The text content to scan
        config: Configuration dict with NOVA settings
        rules_dir: Path to directory containing .nov rule files

    Returns:
        List of detection dicts with rule_name, severity, description, etc.
    """
    if not NOVA_AVAILABLE:
        return []

    detections = []

    try:
        # Initialize NOVA scanner and parser
        scanner = NovaScanner()
        parser = NovaRuleFileParser()

        # Load rules from all .nov files
        rule_files = list(rules_dir.glob("*.nov"))

        for rule_file in rule_files:
            try:
                rules = parser.parse_file(str(rule_file))
                scanner.add_rules(rules)
            except Exception as e:
                if config.get("debug", False):
                    print(f"Warning: Failed to load {rule_file}: {e}", file=sys.stderr)

        # Run the scan
        results = scanner.scan(text)

        # Process results
        for match in results:
            if match.get("matched", False):
                meta = match.get("meta", {})
                detection = {
                    "rule_name": match.get("rule_name", "unknown"),
                    "severity": meta.get("severity", "medium"),
                    "description": meta.get("description", ""),
                    "category": meta.get("category", "unknown"),
                    "matched_keywords": list(match.get("matching_keywords", {}).keys()),
                    "matched_semantics": list(match.get("matching_semantics", {}).keys()),
                    "llm_match": bool(match.get("matching_llm", {})),
                }
                detections.append(detection)

    except Exception as e:
        if config.get("debug", False):
            print(f"NOVA scan error: {e}", file=sys.stderr)

    return detections


def filter_by_severity(detections: List[Dict], min_severity: str) -> List[Dict]:
    """Filter detections by minimum severity level."""
    severity_order = {"low": 0, "medium": 1, "high": 2}
    min_level = severity_order.get(min_severity.lower(), 0)

    return [
        d for d in detections
        if severity_order.get(d.get("severity", "medium").lower(), 1) >= min_level
    ]


def format_block_reason(detections: List[Dict], tool_name: str) -> str:
    """Format a block reason message for Claude."""
    high_severity = [d for d in detections if d.get("severity") == "high"]

    if not high_severity:
        return "[NOVA] Blocked: High-severity threat detected"

    # Get the first high-severity rule name
    first_rule = high_severity[0]
    rule_name = first_rule.get("rule_name", "unknown")
    description = first_rule.get("description", "")

    if description:
        return f"[NOVA] Blocked: {rule_name} - {description}"
    else:
        return f"[NOVA] Blocked: {rule_name}"


def main() -> None:
    """Main entry point for the PreToolUse hook."""
    # Load configuration
    config = load_config()

    # Find rules directory
    rules_dir = get_rules_directory()

    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Invalid JSON input, fail open (allow)
        sys.exit(0)
    except Exception:
        # Any other error, fail open
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Extract text content from tool input (AC1)
    input_text = extract_input_text(tool_input)

    # If no scannable content or NOVA not available, allow
    if not input_text or len(input_text) < 10:
        sys.exit(0)

    if not NOVA_AVAILABLE or not rules_dir:
        sys.exit(0)

    # Scan tool_input against NOVA rules
    try:
        max_length = config.get("max_content_length", 50000)
        min_severity = config.get("min_severity", "low")

        scan_input = input_text[:max_length] if len(input_text) > max_length else input_text
        detections = scan_with_nova(scan_input, config, rules_dir)

        # Filter by minimum severity
        detections = filter_by_severity(detections, min_severity)

        # Deduplicate by rule_name
        seen_rules = set()
        unique_detections = []
        for d in detections:
            rule_name = d.get("rule_name", "unknown")
            if rule_name not in seen_rules:
                seen_rules.add(rule_name)
                unique_detections.append(d)
        detections = unique_detections

        if detections:
            # Check for high severity (AC2 - Block)
            severities = [d.get("severity", "medium") for d in detections]
            if "high" in severities:
                # Block: Exit code 2 with JSON output
                reason = format_block_reason(detections, tool_name)
                output = {"decision": "block", "reason": reason}
                print(json.dumps(output))
                sys.exit(2)
            else:
                # Medium/Low severity: Allow (AC3)
                # Warning will be captured by PostToolUse
                sys.exit(0)
        else:
            # No matches: Allow (AC4)
            sys.exit(0)

    except Exception as e:
        # AC5: Fail-open on any error
        if config.get("debug", False):
            print(f"Pre-tool scan failed: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
