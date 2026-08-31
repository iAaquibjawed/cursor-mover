"""Windows and Linux implementation of :class:`~cursor_mover.systemui.SystemUI`.

Dialogs use Tkinter, which ships with CPython on Windows and macOS but is a
separate package on most Linux distributions (``python3-tk`` on Debian and
Ubuntu, ``python3-tkinter`` on Fedora). Every entry point degrades to a log
line if Tkinter is unavailable, so a missing package never crashes the app.

Notifications prefer, in order:

1. a ``notifier`` callable supplied by the frontend (the tray icon's ``notify``),
2. ``notify-send`` on Linux,
3. a log line.

Threading: Tkinter must be driven from a single thread. pystray dispatches menu
callbacks on the same thread that called ``Icon.run()``, which the frontend
guarantees is the main thread, so dialogs opened from a menu callback are safe.
A fresh ``Tk`` root is created and destroyed per dialog to avoid leaking state
between them.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import contextmanager

from cursor_mover.systemui import TextPrompt

logger = logging.getLogger(__name__)

NOTIFY_SEND_TIMEOUT_SECONDS = 10


@contextmanager
def _hidden_root():
    """Yield a withdrawn Tk root, or ``None`` if Tkinter is unusable."""
    try:
        import tkinter as tk
    except ImportError:
        logger.warning(
            "Tkinter is not available; install python3-tk (Debian/Ubuntu) or "
            "python3-tkinter (Fedora) to enable dialogs."
        )
        yield None
        return

    root = None
    try:
        root = tk.Tk()
    except Exception as exc:  # noqa: BLE001 - no display, broken install, ...
        logger.warning("Could not create a Tk window: %s", exc)
        yield None
        return

    try:
        root.withdraw()
        # Keep dialogs above the app that currently has focus.
        root.attributes("-topmost", True)
        yield root
    finally:
        try:
            root.destroy()
        except Exception:
            logger.debug("Tk root teardown failed", exc_info=True)


class TkUI:
    """Dialogs via Tkinter; notifications via the tray icon or ``notify-send``."""

    def __init__(self, notifier: Callable[[str, str], None] | None = None) -> None:
        self._notifier = notifier

    def set_notifier(self, notifier: Callable[[str, str], None] | None) -> None:
        """Attach a notification sink, normally ``pystray.Icon.notify``."""
        self._notifier = notifier

    def notify(self, title: str, subtitle: str, message: str) -> None:
        """Post a notification, falling back through the available channels."""
        # Tray notifications have no subtitle field, so fold it into the body.
        body = f"{subtitle}\n{message}" if subtitle else message

        if self._notifier is not None:
            try:
                self._notifier(body, title)
                return
            except Exception as exc:  # noqa: BLE001 - backend-specific failures
                logger.debug("Tray notification failed: %s", exc)

        if sys.platform.startswith("linux") and shutil.which("notify-send"):
            try:
                subprocess.run(
                    ["notify-send", "--app-name", title, title, body],
                    check=False,
                    capture_output=True,
                    timeout=NOTIFY_SEND_TIMEOUT_SECONDS,
                )
                return
            except (OSError, subprocess.SubprocessError) as exc:
                logger.debug("notify-send failed: %s", exc)

        logger.info("[notification] %s: %s", title, body)

    def alert(self, title: str, message: str) -> None:
        """Show a modal information dialog."""
        with _hidden_root() as root:
            if root is None:
                logger.info("[alert] %s: %s", title, message)
                return
            from tkinter import messagebox

            try:
                messagebox.showinfo(title, message, parent=root)
            except Exception as exc:  # noqa: BLE001 - toolkit failures are opaque
                logger.warning("Could not show alert %r: %s", title, exc)

    def prompt_for_text(self, title: str, message: str, default: str) -> TextPrompt:
        """Ask for one line of text via a modal entry dialog."""
        with _hidden_root() as root:
            if root is None:
                return TextPrompt(confirmed=False, text="")
            from tkinter import simpledialog

            try:
                result = simpledialog.askstring(title, message, initialvalue=default, parent=root)
            except Exception as exc:  # noqa: BLE001 - toolkit failures are opaque
                logger.warning("Could not show prompt %r: %s", title, exc)
                return TextPrompt(confirmed=False, text="")

        # askstring returns None when the user cancels or closes the dialog.
        if result is None:
            return TextPrompt(confirmed=False, text="")
        return TextPrompt(confirmed=True, text=result.strip())
