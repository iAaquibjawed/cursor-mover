"""macOS menu bar frontend, built on ``rumps``.

Threading note: movement is driven by :class:`RunLoopScheduler`, which wraps
``rumps.Timer`` and therefore fires on the Cocoa main run loop. Every callback
in this module already runs on the main thread, which is what AppKit requires
for the menu updates below.
"""

from __future__ import annotations

import logging

import rumps

from cursor_mover import __version__
from cursor_mover.constants import APP_NAME, MENU_BAR_TITLE
from cursor_mover.controller import AppState, Controller

logger = logging.getLogger(__name__)


class MenuBarFrontend(rumps.App):
    """Renders the controller as a macOS menu bar item."""

    def __init__(self, controller: Controller) -> None:
        super().__init__(APP_NAME, title=MENU_BAR_TITLE, icon=None, quit_button=None)

        self._controller = controller

        self._status_item = rumps.MenuItem("Status: Inactive")
        self._interval_item = rumps.MenuItem("Interval: -")
        self._screen_item = rumps.MenuItem("Screen: -")
        self._toggle_item = rumps.MenuItem("Start Movement", callback=self._on_toggle, key="s")

        self.menu = [
            self._status_item,
            rumps.separator,
            self._interval_item,
            rumps.MenuItem("Change Interval...", callback=self._on_interval, key="i"),
            rumps.separator,
            self._toggle_item,
            rumps.separator,
            self._screen_item,
            rumps.MenuItem(f"About {APP_NAME} {__version__}", callback=self._on_about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self._on_quit, key="q"),
        ]

        controller.set_on_change(self.render)
        self.render(controller.state)

    # -- rendering -------------------------------------------------------

    def render(self, state: AppState) -> None:
        """Sync every menu label with ``state``."""
        # Status glyphs live in the view, not in AppState, so each platform can
        # use what its own UI conventions allow.
        self._status_item.title = "Status: 🟢 Active" if state.running else "Status: 🔴 Inactive"
        self._toggle_item.title = "⏸ Stop Movement" if state.running else "▶ Start Movement"
        self._interval_item.title = state.interval_label
        self._screen_item.title = state.screen_label
        self.title = MENU_BAR_TITLE

    # -- callbacks -------------------------------------------------------

    def _on_toggle(self, _sender: rumps.MenuItem) -> None:
        self._controller.toggle()

    def _on_interval(self, _sender: rumps.MenuItem) -> None:
        self._controller.prompt_for_interval()

    def _on_about(self, _sender: rumps.MenuItem) -> None:
        self._controller.show_about()

    def _on_quit(self, _sender: rumps.MenuItem) -> None:
        self._controller.shutdown()
        rumps.quit_application()
