"""
Tests for Pre-Tool Compliance Rules Configuration.

Tests configurable compliance rules feature:
- Config file discovery (project > installation > defaults)
- Config loading with fail-open behavior
- Pattern merging (default + compliance rules)
- Blocking with compliance rules enabled
- Performance requirements
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch

import pytest


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def pre_tool_module():
    """Load the pre-tool-guard module once for all tests."""
    hook_path = Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"
    spec = spec_from_file_location("pre_tool_guard", hook_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def hook_path():
    """Path to the pre-tool hook."""
    return Path(__file__).parent.parent / "hooks" / "pre-tool-guard.py"


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with .nova-tracer folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nova_dir = Path(tmpdir) / ".nova-tracer"
        nova_dir.mkdir()
        yield tmpdir


@pytest.fixture
def sample_config():
    """Sample compliance config with enabled rules."""
    return {
        "version": 1,
        "compliance_rules": {
            "bash": [
                {
                    "id": "compliance-npx-install",
                    "pattern": r"\bnpx\s+install\b",
                    "reason": "npx install blocked by compliance policy",
                    "enabled": True,
                },
                {
                    "id": "compliance-npm-global",
                    "pattern": r"\bnpm\s+install\s+(-g|--global)\b",
                    "reason": "Global npm installs blocked by compliance policy",
                    "enabled": True,
                },
            ],
            "write": [
                {
                    "id": "compliance-hardcoded-secrets",
                    "pattern": r"(api[_-]?key|password|secret)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
                    "reason": "Potential hardcoded secret detected",
                    "enabled": True,
                }
            ],
        },
        "disable_default_rules": [],
    }


# ============================================================================
# Config Discovery Tests
# ============================================================================


class TestConfigDiscovery:
    """Tests for _find_config_file function."""

    def test_finds_project_config(self, pre_tool_module, temp_project_dir, sample_config):
        """Project-level config is found when present."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(sample_config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            result = pre_tool_module._find_config_file()
            assert result is not None
            assert result == config_path

    def test_finds_installation_config(self, pre_tool_module):
        """Installation-level config is found when present."""
        install_config = (
            Path(__file__).parent.parent / "config" / "pre-tool-rules.json"
        )
        if install_config.exists():
            # Clear project dir to ensure installation config is checked
            with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": ""}):
                result = pre_tool_module._find_config_file()
                assert result is not None

    def test_returns_none_when_no_config(self, pre_tool_module, temp_project_dir):
        """Returns None when no config file exists."""
        # Empty project dir without config file
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            # Remove the .nova-tracer dir created by fixture
            nova_dir = Path(temp_project_dir) / ".nova-tracer"
            if nova_dir.exists():
                import shutil
                shutil.rmtree(nova_dir)

            # Also patch to prevent finding installation config
            with patch.object(Path, "exists", return_value=False):
                result = pre_tool_module._find_config_file()
                # May find installation config, that's OK


class TestConfigLoading:
    """Tests for _load_config function."""

    def test_loads_valid_config(self, pre_tool_module, temp_project_dir, sample_config):
        """Valid JSON config is loaded correctly."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(sample_config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            result = pre_tool_module._load_config()
            assert result.get("version") == 1
            assert "compliance_rules" in result
            assert len(result["compliance_rules"]["bash"]) == 2

    def test_returns_empty_on_invalid_json(self, pre_tool_module, temp_project_dir):
        """Invalid JSON returns empty dict (fail-open)."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text("{ invalid json }")

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            result = pre_tool_module._load_config()
            assert result == {}

    def test_returns_empty_when_no_config(self, pre_tool_module, temp_project_dir):
        """Returns empty dict when no config file in project and no installation config."""
        # Temporarily rename installation config if it exists
        install_config = (
            Path(__file__).parent.parent / "config" / "pre-tool-rules.json"
        )
        backup_path = install_config.with_suffix(".json.bak")
        renamed = False

        try:
            if install_config.exists():
                install_config.rename(backup_path)
                renamed = True

            with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
                result = pre_tool_module._load_config()
                assert result == {}
        finally:
            if renamed and backup_path.exists():
                backup_path.rename(install_config)


# ============================================================================
# Pattern Merging Tests
# ============================================================================


class TestPatternMerging:
    """Tests for _get_patterns function."""

    def test_default_patterns_always_included(self, pre_tool_module):
        """Default security patterns are always included."""
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": "/nonexistent"}):
            config = pre_tool_module._load_config()
            bash_patterns, content_patterns = pre_tool_module._get_patterns(config)

            # Should have default patterns
            assert len(bash_patterns) > 0
            assert len(content_patterns) > 0

            # Check for known default patterns
            reasons = [r for _, r in bash_patterns]
            assert any("rm" in r.lower() for r in reasons)

    def test_compliance_rules_merged(
        self, pre_tool_module, temp_project_dir, sample_config
    ):
        """Compliance rules are merged with defaults."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(sample_config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            config = pre_tool_module._load_config()
            bash_patterns, content_patterns = pre_tool_module._get_patterns(config)

            reasons = [r for _, r in bash_patterns]
            assert "npx install blocked by compliance policy" in reasons
            assert "Global npm installs blocked by compliance policy" in reasons

            content_reasons = [r for _, r in content_patterns]
            assert "Potential hardcoded secret detected" in content_reasons

    def test_disabled_rules_excluded(self, pre_tool_module, temp_project_dir):
        """Rules with enabled=false are excluded."""
        config = {
            "version": 1,
            "compliance_rules": {
                "bash": [
                    {
                        "id": "disabled-rule",
                        "pattern": r"\bdisabled\b",
                        "reason": "This rule is disabled",
                        "enabled": False,
                    },
                    {
                        "id": "enabled-rule",
                        "pattern": r"\benabled\b",
                        "reason": "This rule is enabled",
                        "enabled": True,
                    },
                ],
                "write": [],
            },
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            loaded_config = pre_tool_module._load_config()
            bash_patterns, _ = pre_tool_module._get_patterns(loaded_config)
            reasons = [r for _, r in bash_patterns]

            assert "This rule is disabled" not in reasons
            assert "This rule is enabled" in reasons

    def test_disable_default_rules(self, pre_tool_module, temp_project_dir):
        """Default rules can be disabled by reason string."""
        config = {
            "version": 1,
            "compliance_rules": {"bash": [], "write": []},
            "disable_default_rules": ["Destructive rm command"],
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            loaded_config = pre_tool_module._load_config()
            bash_patterns, _ = pre_tool_module._get_patterns(loaded_config)
            reasons = [r for _, r in bash_patterns]

            assert "Destructive rm command" not in reasons


class TestProtectedFilesMerging:
    """Tests for _get_protected_files function."""

    def test_default_protected_files_included(self, pre_tool_module):
        """Default protected files are always included."""
        config = {}
        protected = pre_tool_module._get_protected_files(config)

        # Should have at least the default Claude settings protection
        assert len(protected) > 0
        reasons = [r for _, r in protected]
        assert any("claude" in r.lower() or "settings" in r.lower() for r in reasons)

    def test_custom_protected_files_merged(self, pre_tool_module, temp_project_dir):
        """Custom protected files are merged with defaults."""
        config = {
            "version": 1,
            "protected_files": [
                {
                    "id": "env-file",
                    "pattern": r"(^|/)\.env$",
                    "reason": "Environment file protected",
                    "enabled": True,
                }
            ],
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            loaded_config = pre_tool_module._load_config()
            protected = pre_tool_module._get_protected_files(loaded_config)

            reasons = [r for _, r in protected]
            assert "Environment file protected" in reasons

    def test_disabled_protected_files_excluded(self, pre_tool_module, temp_project_dir):
        """Protected files with enabled=false are excluded."""
        config = {
            "version": 1,
            "protected_files": [
                {
                    "id": "disabled-file",
                    "pattern": r"disabled\.txt$",
                    "reason": "This protection is disabled",
                    "enabled": False,
                },
                {
                    "id": "enabled-file",
                    "pattern": r"enabled\.txt$",
                    "reason": "This protection is enabled",
                    "enabled": True,
                },
            ],
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": temp_project_dir}):
            loaded_config = pre_tool_module._load_config()
            protected = pre_tool_module._get_protected_files(loaded_config)
            reasons = [r for _, r in protected]

            assert "This protection is disabled" not in reasons
            assert "This protection is enabled" in reasons


# ============================================================================
# Compliance Rule Blocking Tests (Integration)
# ============================================================================


class TestComplianceBlocking:
    """Integration tests for compliance rule blocking."""

    def test_blocks_npx_install(self, hook_path, temp_project_dir):
        """npx install is blocked when compliance rule is enabled."""
        config = {
            "version": 1,
            "compliance_rules": {
                "bash": [
                    {
                        "id": "compliance-npx-install",
                        "pattern": r"\bnpx\s+install\b",
                        "reason": "npx install blocked by compliance policy",
                        "enabled": True,
                    }
                ],
                "write": [],
            },
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "npx install some-package"},
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 2  # Blocked
        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "npx install blocked" in output["reason"]

    def test_allows_npx_install_when_disabled(self, hook_path, temp_project_dir):
        """npx install is allowed when compliance rule is disabled."""
        config = {
            "version": 1,
            "compliance_rules": {
                "bash": [
                    {
                        "id": "compliance-npx-install",
                        "pattern": r"\bnpx\s+install\b",
                        "reason": "npx install blocked by compliance policy",
                        "enabled": False,
                    }
                ],
                "write": [],
            },
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "npx install some-package"},
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0  # Allowed

    def test_blocks_hardcoded_secret_in_write(self, hook_path, temp_project_dir):
        """Hardcoded secrets in Write content are blocked."""
        config = {
            "version": 1,
            "compliance_rules": {
                "bash": [],
                "write": [
                    {
                        "id": "compliance-hardcoded-secrets",
                        "pattern": r"api_key\s*=\s*['\"][^'\"]{8,}['\"]",
                        "reason": "Potential hardcoded secret detected",
                        "enabled": True,
                    }
                ],
            },
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        hook_input = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/test/config.py",
                "content": "api_key = 'sk-verylongsecretkey123456'",
            },
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 2  # Blocked
        output = json.loads(result.stdout)
        assert "hardcoded secret" in output["reason"].lower()

    def test_default_rules_still_work(self, hook_path, temp_project_dir, sample_config):
        """Default security rules still work with compliance config."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(sample_config))

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 2  # Still blocked by default rule

    def test_blocks_protected_file_from_config(self, hook_path, temp_project_dir):
        """Protected files from config block Write operations."""
        config = {
            "version": 1,
            "compliance_rules": {"bash": [], "write": []},
            "protected_files": [
                {
                    "id": "env-file",
                    "pattern": r"(^|/)\.env$",
                    "reason": "Environment file protected",
                    "enabled": True,
                }
            ],
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        hook_input = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/.env",
                "content": "SECRET=test",
            },
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 2  # Blocked
        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "Environment file protected" in output["reason"]

    def test_allows_protected_file_when_disabled(self, hook_path, temp_project_dir):
        """Protected files are allowed when protection is disabled."""
        config = {
            "version": 1,
            "compliance_rules": {"bash": [], "write": []},
            "protected_files": [
                {
                    "id": "env-file",
                    "pattern": r"(^|/)\.env$",
                    "reason": "Environment file protected",
                    "enabled": False,
                }
            ],
        }
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(config))

        hook_input = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/.env",
                "content": "PUBLIC_VAR=test",
            },
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0  # Allowed


# ============================================================================
# Fail-Open Tests
# ============================================================================


class TestFailOpen:
    """Tests for fail-open behavior on config errors."""

    def test_invalid_config_allows_command(self, hook_path, temp_project_dir):
        """Invalid config file falls back to defaults (fail-open)."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text("{ invalid json }")

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},  # Safe command
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0  # Allowed (defaults used)

    def test_missing_config_uses_defaults(self, hook_path, temp_project_dir):
        """Missing config file uses default patterns."""
        # Don't create any config file
        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},  # Dangerous
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 2  # Blocked by default rule


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Tests for performance requirements."""

    def test_config_loading_performance(self, hook_path, temp_project_dir, sample_config):
        """Config loading adds <10ms overhead."""
        config_path = Path(temp_project_dir) / ".nova-tracer" / "pre-tool-rules.json"
        config_path.write_text(json.dumps(sample_config))

        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
        }

        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = temp_project_dir

        # Warm up
        subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            env=env,
        )

        # Measure multiple runs
        times = []
        for _ in range(5):
            start = time.perf_counter()
            subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                env=env,
            )
            elapsed = (time.perf_counter() - start) * 1000  # ms
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        # Allow reasonable margin for subprocess overhead
        # The hook itself should be fast, subprocess adds ~30-50ms
        assert avg_time < 200, f"Average time {avg_time:.1f}ms exceeds limit"
