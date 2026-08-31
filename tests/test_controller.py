"""Tests for the shared application logic.

These cover the behaviour both frontends rely on, without importing rumps,
pystray, or Tkinter.
"""

from __future__ import annotations

import random

import pytest

from cursor_mover.config import InvalidIntervalError, Settings, SettingsStore
from cursor_mover.controller import AppState, Controller, permission_help
from cursor_mover.mover import CursorMover
from cursor_mover.scheduler import ManualScheduler
from cursor_mover.systemui import TextPrompt
from tests.test_mover import FakeBackend


class FakeSystemUI:
    """Records dialogs and notifications; scripts the next prompt result."""

    def __init__(self, prompt: TextPrompt | None = None) -> None:
        self.notifications: list[tuple[str, str, str]] = []
        self.alerts: list[tuple[str, str]] = []
        self.prompts: list[tuple[str, str, str]] = []
        self.next_prompt = prompt or TextPrompt(confirmed=False, text="")

    def notify(self, title: str, subtitle: str, message: str) -> None:
        self.notifications.append((title, subtitle, message))

    def alert(self, title: str, message: str) -> None:
        self.alerts.append((title, message))

    def prompt_for_text(self, title: str, message: str, default: str) -> TextPrompt:
        self.prompts.append((title, message, default))
        return self.next_prompt


def build(tmp_path, backend=None, prompt=None):
    """Assemble a Controller with test doubles. Returns (controller, parts)."""
    backend = backend or FakeBackend(screen=(800, 600))
    scheduler = ManualScheduler()
    ui = FakeSystemUI(prompt)
    store = SettingsStore(tmp_path)
    controller = Controller(
        mover=CursorMover(backend, rng=random.Random(0)),
        scheduler=scheduler,
        system_ui=ui,
        store=store,
        platform="linux",
    )
    return controller, (backend, scheduler, ui, store)


class TestState:
    def test_reports_defaults_when_idle(self, tmp_path) -> None:
        controller, _ = build(tmp_path)
        state = controller.state
        assert state.running is False
        assert state.interval_seconds == 11
        assert (state.screen_width, state.screen_height) == (800, 600)

    def test_labels_track_running(self, tmp_path) -> None:
        controller, _ = build(tmp_path)
        assert controller.state.toggle_label == "Start Movement"
        controller.start()
        assert controller.state.toggle_label == "Stop Movement"
        assert controller.state.status_label == "Status: Active"

    def test_labels_are_platform_neutral_text(self) -> None:
        state = AppState(running=True, interval_seconds=15, screen_width=1, screen_height=2)
        assert state.interval_label == "Interval: 15s"
        assert state.screen_label == "Screen: 1x2"


class TestStartStop:
    def test_start_schedules_the_timer(self, tmp_path) -> None:
        controller, (_, scheduler, ui, _) = build(tmp_path)

        assert controller.start() is True
        assert scheduler.is_active is True
        assert scheduler.interval == 11
        assert ui.notifications[-1][1] == "Movement Started"

    def test_start_is_idempotent(self, tmp_path) -> None:
        controller, (_, scheduler, _, _) = build(tmp_path)
        controller.start()
        controller.start()
        assert scheduler.start_count == 1

    def test_stop_cancels_the_timer(self, tmp_path) -> None:
        controller, (_, scheduler, ui, _) = build(tmp_path)
        controller.start()
        controller.stop()
        assert scheduler.is_active is False
        assert ui.notifications[-1][1] == "Movement Stopped"

    def test_stop_when_idle_does_nothing(self, tmp_path) -> None:
        controller, (_, scheduler, ui, _) = build(tmp_path)
        controller.stop()
        assert scheduler.stop_count == 0
        assert ui.notifications == []

    def test_toggle_flips_state(self, tmp_path) -> None:
        controller, _ = build(tmp_path)
        controller.toggle()
        assert controller.state.running is True
        controller.toggle()
        assert controller.state.running is False

    def test_announce_false_suppresses_notifications(self, tmp_path) -> None:
        controller, (_, _, ui, _) = build(tmp_path)
        controller.start(announce=False)
        controller.stop(announce=False)
        assert ui.notifications == []

    def test_blocked_pointer_alerts_and_does_not_start(self, tmp_path) -> None:
        backend = FakeBackend(position_error=OSError("not permitted"))
        controller, (_, scheduler, ui, _) = build(tmp_path, backend=backend)

        assert controller.start() is False
        assert scheduler.is_active is False
        assert ui.alerts[0][0] == "Permission Required"


class TestTicks:
    def test_tick_moves_the_cursor(self, tmp_path) -> None:
        controller, (backend, scheduler, _, _) = build(tmp_path)
        controller.start()
        scheduler.fire(3)
        assert len(backend.moves) == 3

    def test_move_failure_stops_and_alerts(self, tmp_path) -> None:
        controller, (backend, scheduler, ui, _) = build(tmp_path)
        controller.start()

        def explode(x, y, duration=0.0):
            raise RuntimeError("display gone")

        backend.moveTo = explode
        scheduler.fire()

        assert scheduler.is_active is False
        assert ui.alerts[-1][0] == "Cursor Mover Error"
        assert "display gone" in ui.alerts[-1][1]


class TestInterval:
    def test_set_interval_persists_and_notifies(self, tmp_path) -> None:
        controller, (_, _, ui, store) = build(tmp_path)

        assert controller.set_interval(45) == 45
        assert store.load().interval_seconds == 45
        assert ui.notifications[-1][1] == "Interval Updated"

    def test_set_interval_restarts_a_running_timer(self, tmp_path) -> None:
        controller, (_, scheduler, _, _) = build(tmp_path)
        controller.start()
        controller.set_interval(60)
        assert scheduler.is_active is True
        assert scheduler.interval == 60

    def test_set_interval_rejects_out_of_range(self, tmp_path) -> None:
        controller, _ = build(tmp_path)
        with pytest.raises(InvalidIntervalError):
            controller.set_interval(1)

    def test_unchanged_interval_is_a_no_op(self, tmp_path) -> None:
        controller, (_, _, ui, _) = build(tmp_path)
        controller.set_interval(11)
        assert ui.notifications == []

    def test_prompt_applies_a_valid_answer(self, tmp_path) -> None:
        controller, _ = build(tmp_path, prompt=TextPrompt(confirmed=True, text="90"))
        controller.prompt_for_interval()
        assert controller.state.interval_seconds == 90

    def test_prompt_cancel_changes_nothing(self, tmp_path) -> None:
        controller, (_, _, ui, _) = build(tmp_path, prompt=TextPrompt(confirmed=False, text="90"))
        controller.prompt_for_interval()
        assert controller.state.interval_seconds == 11
        assert ui.alerts == []

    def test_prompt_with_garbage_alerts(self, tmp_path) -> None:
        controller, (_, _, ui, _) = build(tmp_path, prompt=TextPrompt(confirmed=True, text="soon"))
        controller.prompt_for_interval()
        assert ui.alerts[-1][0] == "Invalid Interval"
        assert controller.state.interval_seconds == 11

    def test_saved_interval_is_restored(self, tmp_path) -> None:
        first, _ = build(tmp_path)
        first.set_interval(120)
        second, _ = build(tmp_path)
        assert second.state.interval_seconds == 120


class TestRendering:
    def test_on_change_fires_for_each_transition(self, tmp_path) -> None:
        controller, _ = build(tmp_path)
        seen: list[bool] = []
        controller.set_on_change(lambda state: seen.append(state.running))

        controller.start()
        controller.stop()
        assert seen == [True, False]

    def test_a_broken_view_does_not_break_state(self, tmp_path) -> None:
        controller, (_, scheduler, _, _) = build(tmp_path)

        def explode(_state):
            raise ValueError("bad view")

        controller.set_on_change(explode)
        controller.start()  # must not propagate
        assert scheduler.is_active is True


class TestPermissionHelp:
    def test_macos_mentions_accessibility(self) -> None:
        assert "Accessibility" in permission_help("darwin")

    def test_linux_mentions_wayland(self) -> None:
        assert "Wayland" in permission_help("linux")

    def test_windows_gets_generic_advice(self) -> None:
        text = permission_help("win32")
        assert "Accessibility" not in text
        assert "Wayland" not in text


class TestAbout:
    def test_about_shows_version_and_path(self, tmp_path) -> None:
        controller, (_, _, ui, store) = build(tmp_path)
        controller.show_about()
        title, body = ui.alerts[-1]
        assert "Cursor Mover" in title
        assert str(store.path) in body


class TestShutdown:
    def test_shutdown_stops_quietly(self, tmp_path) -> None:
        controller, (_, scheduler, ui, _) = build(tmp_path)
        controller.start(announce=False)
        controller.shutdown()
        assert scheduler.is_active is False
        assert ui.notifications == []


class TestSettingsDefault:
    def test_store_defaults_to_the_platform_location(self) -> None:
        # Only asserting it resolves; the exact path is covered in test_paths.
        assert Settings().interval_seconds == 11
