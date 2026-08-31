"""Platform frontends.

Each frontend is a thin view over :class:`cursor_mover.controller.Controller`:
it renders :class:`~cursor_mover.controller.AppState` and forwards user intent.
All behaviour lives in the controller.

* :mod:`~cursor_mover.frontend.menubar` — macOS, via ``rumps`` (AppKit).
* :mod:`~cursor_mover.frontend.tray` — Windows and Linux, via ``pystray``.
* :mod:`~cursor_mover.frontend.window` — a plain Tkinter window, used when the
  desktop has no system tray (notably GNOME without the AppIndicator
  extension), or on request via ``--window``.

The GUI toolkits are imported inside the factory, not at module scope, so none
of them is required to import this package.
"""

from __future__ import annotations

import logging
import sys
from typing import Literal, Protocol

from cursor_mover.controller import Controller

logger = logging.getLogger(__name__)

FrontendChoice = Literal["auto", "tray", "window"]


class Frontend(Protocol):
    """A platform tray, menu bar, or window view."""

    def run(self) -> None:
        """Show the UI and block until the user quits."""
        ...


def tray_is_available() -> bool:
    """Whether this session has a tray that can show a clickable menu.

    pystray picks its backend at import time, and two of the outcomes are
    unusable for Cursor Mover:

    * ``_dummy`` — no tray at all. An icon built on it never appears, leaving
      the app running with no way to control it.
    * ``_xorg`` — a bare X11 icon with ``HAS_MENU = False``. The icon appears
      but clicking it can never open a menu, so there is no way to change the
      interval or quit.

    Both fall back to :mod:`~cursor_mover.frontend.window`.
    """
    try:
        import pystray
    except ImportError:
        logger.debug("pystray is not installed")
        return False

    icon_cls = pystray.Icon
    backend = getattr(icon_cls, "__module__", "")

    if backend.endswith("_dummy"):
        logger.info("No system tray backend is available for this session.")
        return False

    # The menu *is* the interface, so a backend without one is no use.
    if not getattr(icon_cls, "HAS_MENU", False):
        logger.info(
            "The %s tray backend cannot show a menu; using a window instead.",
            backend.rsplit("_", 1)[-1] or backend,
        )
        return False

    return True


def create_frontend(
    controller: Controller,
    platform: str | None = None,
    choice: FrontendChoice = "auto",
) -> Frontend:
    """Return the frontend for ``platform``.

    Args:
        controller: The controller the view will render.
        platform: A ``sys.platform`` value. Defaults to the running platform.
        choice: ``"auto"`` picks a tray when one is available and falls back to
            a window; ``"tray"`` and ``"window"`` force the choice.

    Raises:
        RuntimeError: if the platform has no frontend.
    """
    plat = platform if platform is not None else sys.platform

    # macOS always has a menu bar, and rumps is the native fit.
    if plat == "darwin" and choice != "window":
        from cursor_mover.frontend.menubar import MenuBarFrontend

        return MenuBarFrontend(controller)

    if choice == "window" or (choice == "auto" and not tray_is_available()):
        from cursor_mover.frontend.window import WindowFrontend

        if choice == "auto":
            logger.info("Falling back to a window; no system tray was found.")
        return WindowFrontend(controller)

    if plat.startswith(("win", "linux", "freebsd", "openbsd", "netbsd")) or (
        plat == "darwin" and choice == "tray"
    ):
        from cursor_mover.frontend.tray import TrayFrontend

        return TrayFrontend(controller)

    raise RuntimeError(f"No Cursor Mover frontend for platform {plat!r}.")
