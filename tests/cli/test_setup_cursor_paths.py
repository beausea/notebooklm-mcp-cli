"""Tests for Cursor MCP config path resolution."""

import json
from pathlib import Path

import pytest

from notebooklm_tools.cli.commands.setup import (
    _cursor_canonical_config_path,
    _cursor_config_candidates,
    _cursor_config_path,
    _find_cursor_configured_path,
)


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


def test_canonical_path_is_home_dot_cursor(fake_home):
    assert _cursor_canonical_config_path() == fake_home / ".cursor" / "mcp.json"


def test_defaults_to_canonical_when_no_files_exist(fake_home, monkeypatch):
    monkeypatch.setenv("APPDATA", str(fake_home / "AppData" / "Roaming"))
    monkeypatch.setattr("notebooklm_tools.cli.commands.setup.platform.system", lambda: "Windows")

    assert _cursor_config_path() == fake_home / ".cursor" / "mcp.json"


def test_prefers_existing_canonical_over_legacy(fake_home, monkeypatch):
    monkeypatch.setenv("APPDATA", str(fake_home / "AppData" / "Roaming"))
    monkeypatch.setattr("notebooklm_tools.cli.commands.setup.platform.system", lambda: "Windows")

    canonical = fake_home / ".cursor" / "mcp.json"
    legacy = fake_home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp.json"
    canonical.parent.mkdir(parents=True)
    legacy.parent.mkdir(parents=True)
    canonical.write_text("{}")
    legacy.write_text('{"mcpServers": {}}')

    assert _cursor_config_path() == canonical


def test_uses_legacy_when_only_legacy_exists(fake_home, monkeypatch):
    monkeypatch.setenv("APPDATA", str(fake_home / "AppData" / "Roaming"))
    monkeypatch.setattr("notebooklm_tools.cli.commands.setup.platform.system", lambda: "Windows")

    legacy = fake_home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text('{"mcpServers": {}}')

    assert _cursor_config_path() == legacy


def test_find_configured_path_checks_all_candidates(fake_home, monkeypatch):
    monkeypatch.setenv("APPDATA", str(fake_home / "AppData" / "Roaming"))
    monkeypatch.setattr("notebooklm_tools.cli.commands.setup.platform.system", lambda: "Windows")

    canonical = fake_home / ".cursor" / "mcp.json"
    legacy = fake_home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp.json"
    canonical.parent.mkdir(parents=True)
    legacy.parent.mkdir(parents=True)
    canonical.write_text(json.dumps({"mcpServers": {}}))
    legacy.write_text(json.dumps({"mcpServers": {"notebooklm-mcp": {"command": "notebooklm-mcp"}}}))

    assert _find_cursor_configured_path() == legacy


def test_windows_candidates_include_legacy_path(fake_home, monkeypatch):
    appdata = fake_home / "AppData" / "Roaming"
    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.setattr("notebooklm_tools.cli.commands.setup.platform.system", lambda: "Windows")

    candidates = _cursor_config_candidates()
    assert candidates[0] == fake_home / ".cursor" / "mcp.json"
    assert candidates[1] == appdata / "Cursor" / "User" / "mcp.json"
