"""Application logic shared by every frontend.

The macOS menu bar and the Windows/Linux tray icon are only *views*: they render
:class:`AppState` and forward user intent to :class:`Controller`. All of the
behaviour — permission checks, timer management, interval validation,
persistence, notification copy — lives here, where it can be tested without a
GUI toolkit.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass

from cursor_mover import __version__
from cursor_mover.config import (
    InvalidIntervalError,
    Settings,
    SettingsStore,
    validate_interval,
)
from cursor_mover.constants import APP_NAME, MAX_INTERVAL_SECONDS, MIN_INTERVAL_SECONDS
from cursor_mover.mover import AccessibilityPermissionError, CursorMover
from cursor_mover.scheduler import Scheduler
from cursor_mover.systemui import SystemUI

logger = logging.getLogger(__name__)


def _run_now(work: Callable[[], None]) -> None:
    """Default dispatcher: run on the calling thread."""
    work()


_MACOS_PERMISSION_HELP = (
    f"{APP_NAME} needs Accessibility permission to move the cursor.\n\n"
    "Open System Settings → Privacy & Security → Accessibility, then enable "
    f"{APP_NAME} (or your terminal, if you are running from source).\n\n"
    "Restart the app after granting permission."
)

_LINUX_PERMISSION_HELP = (
    f"{APP_NAME} could not control the pointer.\n\n"
    "This usually means the session is running Wayland, which does not allow "
    "applications to move the pointer. Log in to an X11 / Xorg session instead.\n\n"
    "On X11, make sure the python3-tk and python3-xlib packages are installed."
)

_GENERIC_PERMISSION_HELP = (
    f"{APP_NAME} could not control the pointer.\n\n"
    "Another application may be blocking pointer control, or the display "
    "server is not accessible."
)


def permission_help(platform: str | None = None) -> str:
    """Return platform-appropriate guidance for a blocked pointer."""
    plat = platform if platform is not None else sys.platform
    if plat == "darwin":
        return _MACOS_PERMISSION_HELP
    if plat.startswith("linux"):
        return _LINUX_PERMISSION_HELP
    return _GENERIC_PERMISSION_HELP


@dataclass(frozen=True, slots=True)
class AppState:
    """Everything a frontend needs in order to render itself."""

    running: bool
    interval_seconds: int
    screen_width: int
    screen_height: int

    @property
    def status_label(self) -> str:
        return "Status: Active" if self.running else "Status: Inactive"

    @property
    def toggle_label(self) -> str:
        return "Stop Movement" if self.running else "Start Movement"

    @property
    def interval_label(self) -> str:
        return f"Interval: {self.interval_seconds}s"

    @property
    def screen_label(self) -> str:
        return f"Screen: {self.screen_width}x{self.screen_height}"


class Controller:
    """Owns application state and mediates between the frontend and the engine."""

    def __init__(
        self,
        mover: CursorMover,
        scheduler: Scheduler,
        system_ui: SystemUI,
        store: SettingsStore | None = None,
        platform: str | None = None,
        dispatch: Callable[[Callable[[], None]], None] | None = None,
    ) -> None:
        self._mover = mover
        self._scheduler = scheduler
        self._ui = system_ui
        self._store = store if store is not None else SettingsStore()
        self._platform = platform if platform is not None else sys.platform
        self._settings: Settings = self._store.load()
        self._on_change: Callable[[AppState], None] | None = None
        # Frontends with a long-lived, thread-affine toolkit object (Tkinter)
        # supply a dispatcher so work triggered from the timer thread lands on
        # the main thread instead. Others run it inline.
        self._dispatch = dispatch if dispatch is not None else _run_now

    # -- frontend wiring -------------------------------------------------

    def set_on_change(self, callback: Callable[[AppState], None] | None) -> None:
        """Register a callback invoked whenever :meth:`state` changes."""
        self._on_change = callback

    def set_dispatcher(self, dispatch: Callable[[Callable[[], None]], None] | None) -> None:
        """Route UI work through ``dispatch``, e.g. Tkinter's ``after``.

        Frontends that own a thread-affine toolkit object call this so work
        raised on the scheduler thread runs on their event loop instead.
        """
        self._dispatch = dispatch if dispatch is not None else _run_now

    @property
    def state(self) -> AppState:
        """A snapshot of the current state."""
        width, height = self._mover.screen_size
        return AppState(
            running=self._scheduler.is_active,
            interval_seconds=self._settings.interval_seconds,
            screen_width=width,
            screen_height=height,
        )

    @property
    def system_ui(self) -> SystemUI:
        """The platform dialog/notification implementation in use."""
        return self._ui

    @property
    def settings_path(self):
        """Where settings are persisted, for display in About."""
        return self._store.path

    def _notify_change(self) -> None:
        if self._on_change is None:
            return
        try:
            self._on_change(self.state)
        except Exception:
            logger.exception("Frontend failed to re-render")

    # -- commands --------------------------------------------------------

    def start(self, announce: bool = True) -> bool:
        """Start moving the cursor. Returns whether it is now running."""
        if self._scheduler.is_active:
            return True

        try:
            self._mover.ensure_permission()
        except AccessibilityPermissionError as exc:
            logger.warning("Pointer control unavailable: %s", exc)
            self._ui.alert("Permission Required", permission_help(self._platform))
            return False

        self._mover.refresh_screen_size()
        self._scheduler.start(self._settings.interval_seconds, self._on_tick)
        self._notify_change()

        if announce:
            self._ui.notify(
                APP_NAME,
                "Movement Started",
                f"Moving the cursor every {self._settings.interval_seconds} seconds.",
            )
        return True

    def stop(self, announce: bool = True) -> None:
        """Stop moving the cursor."""
        if not self._scheduler.is_active:
            return

        self._scheduler.stop()
        self._notify_change()

        if announce:
            self._ui.notify(APP_NAME, "Movement Stopped", "The cursor is no longer being moved.")

    def toggle(self) -> None:
        """Start if stopped, stop if running."""
        if self._scheduler.is_active:
            self.stop()
        else:
            self.start()

    def prompt_for_interval(self) -> None:
        """Ask the user for a new interval and apply it."""
        response = self._ui.prompt_for_text(
            "Set Interval",
            f"Move the cursor every N seconds ({MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS}):",
            str(self._settings.interval_seconds),
        )
        if not response.confirmed:
            return

        try:
            self.set_interval(response.text)
        except InvalidIntervalError as exc:
            self._ui.alert("Invalid Interval", str(exc))

    def set_interval(self, value: object, announce: bool = True) -> int:
        """Validate, persist, and apply a new interval. Returns the new value.

        Raises:
            InvalidIntervalError: if ``value`` is not a usable interval.
        """
        new_interval = validate_interval(value)
        previous = self._settings.interval_seconds
        if new_interval == previous:
            return previous

        self._settings.interval_seconds = new_interval
        self._store.save(self._settings)

        # Restart the timer so the change takes effect immediately rather than
        # after one more cycle at the old interval.
        if self._scheduler.is_active:
            self._scheduler.stop()
            self._scheduler.start(new_interval, self._on_tick)

        self._notify_change()

        if announce:
            self._ui.notify(
                APP_NAME,
                "Interval Updated",
                f"Changed from {previous}s to {new_interval}s.",
            )
        return new_interval

    def show_about(self) -> None:
        """Display version and settings location."""
        self._ui.alert(
            f"{APP_NAME} {__version__}",
            "Keeps your computer awake by nudging the cursor to a random "
            f"position.\n\nSettings: {self.settings_path}",
        )

    def shutdown(self) -> None:
        """Stop the timer in preparation for exit."""
        self.stop(announce=False)

    # -- timer callback --------------------------------------------------

    def _on_tick(self) -> None:
        try:
            self._mover.move_once()
        except Exception as exc:
            logger.exception("Cursor movement failed")
            self._scheduler.stop()
            self._notify_change()
            self._ui.alert("Cursor Mover Error", f"Failed to move the cursor:\n\n{exc}")
