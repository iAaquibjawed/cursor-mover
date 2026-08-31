"""Tests for the system UI factory and the Tkinter implementation.

The Tkinter paths are exercised without a display by driving the fallbacks.
"""

from __future__ import annotations

import contextlib
import logging

from cursor_mover.systemui import TextPrompt, create_system_ui
from cursor_mover.systemui.tk import TkUI


class TestFactory:
    def test_darwin_gets_applescript(self) -> None:
        from cursor_mover.systemui.applescript import AppleScriptUI

        assert isinstance(create_system_ui("darwin"), AppleScriptUI)

    def test_other_platforms_get_tk(self) -> None:
        assert isinstance(create_system_ui("win32"), TkUI)
        assert isinstance(create_system_ui("linux"), TkUI)

    def test_notifier_is_passed_through(self) -> None:
        seen: list[tuple[str, str]] = []
        ui = create_system_ui("win32", notifier=lambda body, title: seen.append((title, body)))
        ui.notify("Cursor Mover", "Started", "Every 11 seconds.")
        assert seen == [("Cursor Mover", "Started\nEvery 11 seconds.")]


class TestTkNotify:
    def test_prefers_the_notifier(self) -> None:
        seen: list[tuple[str, str]] = []
        ui = TkUI(notifier=lambda body, title: seen.append((title, body)))
        ui.notify("T", "Sub", "Body")
        assert seen == [("T", "Sub\nBody")]

    def test_omits_an_empty_subtitle(self) -> None:
        seen: list[str] = []
        ui = TkUI(notifier=lambda body, title: seen.append(body))
        ui.notify("T", "", "Body")
        assert seen == ["Body"]

    def test_falls_through_when_the_notifier_raises(self, caplog, monkeypatch) -> None:
        monkeypatch.setattr("cursor_mover.systemui.tk.shutil.which", lambda name: None)
        caplog.set_level(logging.DEBUG, logger="cursor_mover.systemui.tk")

        def broken(body: str, title: str) -> None:
            raise RuntimeError("no tray")

        TkUI(notifier=broken).notify("T", "Sub", "Body")  # must not raise

        messages = [r.getMessage() for r in caplog.records]
        assert any("Tray notification failed" in m for m in messages)
        # And it still reached the final log-only channel.
        assert any("[notification]" in m for m in messages)

    def test_set_notifier_rebinds(self) -> None:
        seen: list[str] = []
        ui = TkUI()
        ui.set_notifier(lambda body, title: seen.append(body))
        ui.notify("T", "", "Body")
        assert seen == ["Body"]

    def test_notify_without_any_channel_only_logs(self, caplog, monkeypatch) -> None:
        monkeypatch.setattr("cursor_mover.systemui.tk.shutil.which", lambda name: None)
        TkUI().notify("T", "Sub", "Body")  # must not raise


class TestTkDialogsDegrade:
    """With no usable Tk root, dialogs must degrade rather than crash."""

    def test_alert_without_tk_logs(self, monkeypatch, caplog) -> None:
        monkeypatch.setattr("cursor_mover.systemui.tk._hidden_root", _no_root, raising=True)
        TkUI().alert("Title", "Message")  # must not raise

    def test_prompt_without_tk_is_not_confirmed(self, monkeypatch) -> None:
        monkeypatch.setattr("cursor_mover.systemui.tk._hidden_root", _no_root, raising=True)
        assert TkUI().prompt_for_text("T", "M", "11") == TextPrompt(False, "")


@contextlib.contextmanager
def _no_root():
    """Stand in for _hidden_root when Tkinter is unavailable."""
    yield None
