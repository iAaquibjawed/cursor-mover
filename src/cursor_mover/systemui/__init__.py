"""Platform-native dialogs and notifications.

Two implementations satisfy the :class:`SystemUI` protocol:

* :mod:`~cursor_mover.systemui.applescript` shells out to ``osascript`` on
  macOS, giving genuinely native dialogs and Notification Center banners.
* :mod:`~cursor_mover.systemui.gtk` uses GTK 3 via PyGObject. Preferred on
  Linux, because GTK is already present wherever a tray is and the Flatpak
  runtime ships GTK but no Tkinter.
* :mod:`~cursor_mover.systemui.tk` uses Tkinter from the standard library. Used
  on Windows, and on Linux when GTK is unavailable.

Nothing in this package imports a GUI toolkit at module scope, so importing it
is safe in a headless test run.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from typing import NamedTuple, Protocol

logger = logging.getLogger(__name__)


class TextPrompt(NamedTuple):
    """Outcome of :meth:`SystemUI.prompt_for_text`."""

    confirmed: bool
    text: str


class SystemUI(Protocol):
    """The dialogs and notifications the app needs from the host OS."""

    def notify(self, title: str, subtitle: str, message: str) -> None:
        """Post a transient notification. Must never raise."""
        ...

    def alert(self, title: str, message: str) -> None:
        """Show a modal message with a single dismiss button. Must never raise."""
        ...

    def prompt_for_text(self, title: str, message: str, default: str) -> TextPrompt:
        """Ask for one line of text. Must never raise."""
        ...


def create_system_ui(
    platform: str | None = None,
    notifier: Callable[[str, str], None] | None = None,
) -> SystemUI:
    """Return the :class:`SystemUI` implementation for ``platform``.

    Args:
        platform: A ``sys.platform`` value. Defaults to the running platform.
        notifier: Optional ``(title, message)`` callable used for notifications
            on non-macOS platforms, normally the tray icon's ``notify`` method.
    """
    plat = platform if platform is not None else sys.platform

    if plat == "darwin":
        from cursor_mover.systemui.applescript import AppleScriptUI

        return AppleScriptUI()

    # On Linux, GTK is the better fit: it is already installed wherever a system
    # tray is running, and it is the only option inside the Flatpak runtime,
    # which ships no Tkinter.
    if not plat.startswith("win"):
        from cursor_mover.systemui.gtk import GtkUI, gtk_is_available

        if gtk_is_available():
            return GtkUI(notifier=notifier)
        logger.info("GTK unavailable; falling back to Tkinter dialogs.")

    from cursor_mover.systemui.tk import TkUI

    return TkUI(notifier=notifier)
