"""Tests for frontend selection.

The frontends themselves need a GUI session, but the *choice* between them is
pure logic and is where a user-visible mistake would hide: picking a tray on a
desktop that has none leaves the app running with no way to control it.
"""

from __future__ import annotations

import pytest

from cursor_mover.frontend import create_frontend, tray_is_available


class RecordingFactory:
    """Stands in for a frontend class, recording that it was chosen."""

    def __init__(self, controller) -> None:
        self.controller = controller

    def run(self) -> None:  # pragma: no cover - never called in tests
        raise AssertionError("run() should not be invoked by these tests")


@pytest.fixture
def stub_frontends(monkeypatch):
    """Replace every real frontend with a recording stub."""
    import cursor_mover.frontend.tray as tray_mod
    import cursor_mover.frontend.window as window_mod

    class Tray(RecordingFactory):
        pass

    class Window(RecordingFactory):
        pass

    monkeypatch.setattr(tray_mod, "TrayFrontend", Tray, raising=False)
    monkeypatch.setattr(window_mod, "WindowFrontend", Window, raising=False)
    return Tray, Window


class TestTrayAvailability:
    def test_missing_pystray_means_no_tray(self, monkeypatch) -> None:
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pystray":
                raise ImportError("no pystray")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        assert tray_is_available() is False

    def test_dummy_backend_means_no_tray(self, monkeypatch) -> None:
        import pystray

        class DummyIcon:
            __module__ = "pystray._dummy"

        monkeypatch.setattr(pystray, "Icon", DummyIcon)
        assert tray_is_available() is False

    def test_real_backend_with_a_menu_means_tray(self, monkeypatch) -> None:
        import pystray

        class RealIcon:
            __module__ = "pystray._win32"
            HAS_MENU = True

        monkeypatch.setattr(pystray, "Icon", RealIcon)
        assert tray_is_available() is True


class TestCreateFrontend:
    def test_unknown_platform_raises(self) -> None:
        with pytest.raises(RuntimeError, match="No Cursor Mover frontend"):
            create_frontend(controller=None, platform="emscripten")

    def test_linux_falls_back_to_window_without_a_tray(self, monkeypatch, stub_frontends) -> None:
        _tray, window = stub_frontends
        monkeypatch.setattr("cursor_mover.frontend.tray_is_available", lambda: False)

        result = create_frontend(controller=None, platform="linux")
        assert isinstance(result, window)

    def test_linux_uses_the_tray_when_available(self, monkeypatch, stub_frontends) -> None:
        tray, _window = stub_frontends
        monkeypatch.setattr("cursor_mover.frontend.tray_is_available", lambda: True)

        result = create_frontend(controller=None, platform="linux")
        assert isinstance(result, tray)

    def test_window_can_be_forced(self, monkeypatch, stub_frontends) -> None:
        _tray, window = stub_frontends
        monkeypatch.setattr("cursor_mover.frontend.tray_is_available", lambda: True)

        result = create_frontend(controller=None, platform="linux", choice="window")
        assert isinstance(result, window)

    def test_tray_can_be_forced_without_availability_check(
        self, monkeypatch, stub_frontends
    ) -> None:
        tray, _window = stub_frontends

        def explode() -> bool:
            raise AssertionError("availability must not be consulted when forced")

        monkeypatch.setattr("cursor_mover.frontend.tray_is_available", explode)
        result = create_frontend(controller=None, platform="win32", choice="tray")
        assert isinstance(result, tray)

    def test_macos_window_override_is_honoured(self, monkeypatch, stub_frontends) -> None:
        _tray, window = stub_frontends
        result = create_frontend(controller=None, platform="darwin", choice="window")
        assert isinstance(result, window)


class TestBackendsWithoutMenus:
    """A tray icon with no menu is unusable: the menu is the whole interface."""

    def test_menuless_backend_is_rejected(self, monkeypatch) -> None:
        import pystray

        from cursor_mover.frontend import tray_is_available

        class XorgIcon:
            __module__ = "pystray._xorg"
            HAS_MENU = False

        monkeypatch.setattr(pystray, "Icon", XorgIcon)
        assert tray_is_available() is False

    def test_backend_with_a_menu_is_accepted(self, monkeypatch) -> None:
        import pystray

        from cursor_mover.frontend import tray_is_available

        class AppIndicatorIcon:
            __module__ = "pystray._appindicator"
            HAS_MENU = True

        monkeypatch.setattr(pystray, "Icon", AppIndicatorIcon)
        assert tray_is_available() is True

    def test_menuless_backend_falls_back_to_a_window(self, monkeypatch, stub_frontends) -> None:
        import pystray

        from cursor_mover.frontend import create_frontend

        _tray, window = stub_frontends

        class XorgIcon:
            __module__ = "pystray._xorg"
            HAS_MENU = False

        monkeypatch.setattr(pystray, "Icon", XorgIcon)
        assert isinstance(create_frontend(controller=None, platform="linux"), window)
