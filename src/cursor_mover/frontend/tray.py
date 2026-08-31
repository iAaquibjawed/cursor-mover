"""Windows and Linux system tray frontend, built on ``pystray``.

``pystray`` menus are immutable: labels are supplied as callables that it
re-evaluates each time the menu is opened, and :meth:`pystray.Icon.update_menu`
refreshes any always-visible state. That is why this module hands pystray
lambdas rather than pre-rendered strings.

Threading note: ``Icon.run()`` is called on the main thread and menu callbacks
are dispatched from that same thread, which is what makes the Tkinter dialogs in
:mod:`cursor_mover.systemui.tk` safe. Movement runs on a
:class:`~cursor_mover.scheduler.ThreadScheduler` because the tray backends do
not expose a reusable timer.
"""

from __future__ import annotations

import logging

import pystray

from cursor_mover import __version__
from cursor_mover.constants import APP_NAME, BUNDLE_NAME, TRAY_TOOLTIP
from cursor_mover.controller import AppState, Controller
from cursor_mover.icon import load_tray_image

logger = logging.getLogger(__name__)


class TrayFrontend:
    """Renders the controller as a system tray icon."""

    def __init__(self, controller: Controller) -> None:
        self._controller = controller
        self._icon = pystray.Icon(
            name=BUNDLE_NAME,
            title=self._tooltip(controller.state),
            icon=load_tray_image(),
            menu=self._build_menu(),
        )

        # Route notifications through the tray icon when it supports them.
        set_notifier = getattr(controller.system_ui, "set_notifier", None)
        if set_notifier is not None and self._icon.HAS_NOTIFICATION:
            set_notifier(self._icon.notify)

        controller.set_on_change(self.render)

    # -- menu ------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        """Build the menu once; labels are callables so they stay current."""

        def state() -> AppState:
            return self._controller.state

        return pystray.Menu(
            pystray.MenuItem(lambda _item: state().status_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda _item: state().interval_label, None, enabled=False),
            pystray.MenuItem("Change Interval...", self._on_interval),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda _item: state().toggle_label,
                self._on_toggle,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda _item: state().screen_label, None, enabled=False),
            pystray.MenuItem(f"About {APP_NAME} {__version__}", self._on_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    # -- rendering -------------------------------------------------------

    @staticmethod
    def _tooltip(state: AppState) -> str:
        suffix = f"active, every {state.interval_seconds}s" if state.running else "idle"
        return f"{TRAY_TOOLTIP} ({suffix})"

    def render(self, state: AppState) -> None:
        """Refresh the tooltip and menu labels."""
        try:
            self._icon.title = self._tooltip(state)
            self._icon.update_menu()
        except Exception:
            logger.debug("Tray refresh failed", exc_info=True)

    # -- callbacks -------------------------------------------------------

    def _on_toggle(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._controller.toggle()

    def _on_interval(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._controller.prompt_for_interval()

    def _on_about(self, _icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._controller.show_about()

    def _on_quit(self, icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        self._controller.shutdown()
        icon.stop()

    # -- lifecycle -------------------------------------------------------

    def run(self) -> None:
        """Show the tray icon and block until the user quits."""
        self._icon.run()
