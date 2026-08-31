"""Tests for platform-specific data locations."""

from __future__ import annotations

from pathlib import Path

from cursor_mover.paths import config_dir


class TestConfigDir:
    def test_macos_uses_application_support(self) -> None:
        result = config_dir(platform="darwin", env={})
        assert result == Path.home() / "Library" / "Application Support" / "CursorMover"

    def test_windows_uses_appdata(self) -> None:
        result = config_dir(platform="win32", env={"APPDATA": r"C:\Users\a\AppData\Roaming"})
        assert result == Path(r"C:\Users\a\AppData\Roaming") / "CursorMover"

    def test_windows_falls_back_without_appdata(self) -> None:
        result = config_dir(platform="win32", env={})
        assert result == Path.home() / "AppData" / "Roaming" / "CursorMover"

    def test_linux_respects_xdg_config_home(self) -> None:
        result = config_dir(platform="linux", env={"XDG_CONFIG_HOME": "/custom/cfg"})
        assert result == Path("/custom/cfg/cursor-mover")

    def test_linux_defaults_to_dot_config(self) -> None:
        result = config_dir(platform="linux", env={})
        assert result == Path.home() / ".config" / "cursor-mover"

    def test_bsd_is_treated_as_xdg(self) -> None:
        result = config_dir(platform="freebsd14", env={})
        assert result == Path.home() / ".config" / "cursor-mover"

    def test_each_platform_differs(self) -> None:
        seen = {
            str(config_dir(platform=p, env={"APPDATA": "/appdata"}))
            for p in ("darwin", "win32", "linux")
        }
        assert len(seen) == 3
