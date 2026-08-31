"""The rumps menu bar application.

All UI state lives here; the actual pointer work is delegated to
:class:`cursor_mover.mover.CursorMover`.

Threading note: movement is driven by a ``rumps.Timer``, which fires on the
main run loop. That means every menu update in this module already runs on the
main thread, and no locking is required.
"""

from __future__ import annotations

import logging

import rumps

from cursor_mover import __version__
from cursor_mover.config import InvalidIntervalError, Settings, SettingsStore, validate_interval
from cursor_mover.constants import (
    APP_NAME,
    MAX_INTERVAL_SECONDS,
    MENU_BAR_TITLE,
    MIN_INTERVAL_SECONDS,
)
from cursor_mover.macos import alert, notify, prompt_for_text
from cursor_mover.mover import AccessibilityPermissionError, CursorMover

logger = logging.getLogger(__name__)

PERMISSION_HELP = (
    f"{APP_NAME} needs Accessibility permission to move the cursor.\n\n"
    "Open System Settings → Privacy & Security → Accessibility, then enable "
    f"{APP_NAME} (or your terminal, if you are running from source).\n\n"
    "Restart the app after granting permission."
)


class CursorMoverApp(rumps.App):
    """Menu bar front end for Cursor Mover."""

    def __init__(
        self,
        mover: CursorMover,
        store: SettingsStore | None = None,
    ) -> None:
        super().__init__(APP_NAME, title=MENU_BAR_TITLE, icon=None, quit_button=None)

        self._mover = mover
        self._store = store or SettingsStore()
        self._settings: Settings = self._store.load()

        self._status_item = rumps.MenuItem("Status: 🔴 Inactive")
        self._interval_item = rumps.MenuItem("Interval: —")
        self._screen_item = rumps.MenuItem("Screen: —")
        self._toggle_item = rumps.MenuItem("▶ Start Movement", callback=self.on_toggle, key="s")

        self.menu = [
            self._status_item,
            rumps.separator,
            self._interval_item,
            rumps.MenuItem("⚙️ Change Interval…", callback=self.on_change_interval, key="i"),
            rumps.separator,
            self._toggle_item,
            rumps.separator,
            self._screen_item,
            rumps.MenuItem(f"About {APP_NAME} {__version__}", callback=self.on_about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.on_quit, key="q"),
        ]

        self._timer = rumps.Timer(self._on_tick, self._settings.interval_seconds)
        self._render()

        if self._settings.start_on_launch:
            self.start_movement(announce=False)

    # -- state -----------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """Whether cursor movement is currently active."""
        return self._timer.is_alive()

    def start_movement(self, announce: bool = True) -> None:
        """Begin moving the cursor, after confirming Accessibility access."""
        if self.is_running:
            return

        try:
            self._mover.ensure_permission()
        except AccessibilityPermissionError as exc:
            logger.warning("Accessibility check failed: %s", exc)
            alert("Permission Required", PERMISSION_HELP)
            return

        self._mover.refresh_screen_size()
        self._timer.interval = self._settings.interval_seconds
        self._timer.start()
        self._render()

        if announce:
            notify(
                APP_NAME,
                "Movement Started",
                f"Moving the cursor every {self._settings.interval_seconds} seconds.",
            )

    def stop_movement(self, announce: bool = True) -> None:
        """Stop moving the cursor."""
        if not self.is_running:
            return

        self._timer.stop()
        self._render()

        if announce:
            notify(APP_NAME, "Movement Stopped", "The cursor is no longer being moved.")

    # -- callbacks -------------------------------------------------------

    def _on_tick(self, _timer: rumps.Timer) -> None:
        try:
            self._mover.move_once()
        except Exception as exc:
            logger.exception("Cursor movement failed")
            self.stop_movement(announce=False)
            alert("Cursor Mover Error", f"Failed to move the cursor:\n\n{exc}")

    def on_toggle(self, _sender: rumps.MenuItem) -> None:
        """Menu handler: start or stop movement."""
        if self.is_running:
            self.stop_movement()
        else:
            self.start_movement()

    def on_change_interval(self, _sender: rumps.MenuItem) -> None:
        """Menu handler: prompt for a new interval and apply it."""
        response = prompt_for_text(
            title="Set Interval",
            message=(
                f"Move the cursor every N seconds ({MIN_INTERVAL_SECONDS}–{MAX_INTERVAL_SECONDS}):"
            ),
            default=str(self._settings.interval_seconds),
        )
        if not response.confirmed:
            return

        try:
            new_interval = validate_interval(response.text)
        except InvalidIntervalError as exc:
            alert("Invalid Interval", str(exc))
            return

        if new_interval == self._settings.interval_seconds:
            return

        previous = self._settings.interval_seconds
        self._settings.interval_seconds = new_interval
        self._store.save(self._settings)

        # rumps.Timer only picks up a new interval on the next start.
        if self.is_running:
            self._timer.stop()
            self._timer.interval = new_interval
            self._timer.start()
        else:
            self._timer.interval = new_interval

        self._render()
        notify(APP_NAME, "Interval Updated", f"Changed from {previous}s to {new_interval}s.")

    def on_about(self, _sender: rumps.MenuItem) -> None:
        """Menu handler: show version and settings location."""
        alert(
            f"{APP_NAME} {__version__}",
            "Keeps your Mac awake by nudging the cursor to a random position.\n\n"
            f"Settings: {self._store.path}",
        )

    def on_quit(self, _sender: rumps.MenuItem) -> None:
        """Menu handler: stop movement and exit cleanly."""
        self.stop_movement(announce=False)
        rumps.quit_application()

    # -- rendering -------------------------------------------------------

    def _render(self) -> None:
        """Sync every menu label with the current state."""
        running = self.is_running
        width, height = self._mover.screen_size

        self._status_item.title = "Status: 🟢 Active" if running else "Status: 🔴 Inactive"
        self._toggle_item.title = "⏸ Stop Movement" if running else "▶ Start Movement"
        self._interval_item.title = f"Interval: {self._settings.interval_seconds}s"
        self._screen_item.title = f"Screen: {width}×{height}"
        self.title = MENU_BAR_TITLE
