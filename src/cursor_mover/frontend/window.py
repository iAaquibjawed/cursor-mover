"""Plain-window frontend, built on Tkinter.

This is the fallback for desktops with no system tray. GNOME ships without one
unless the user installs the AppIndicator extension, which would otherwise leave
Cursor Mover running with no way to control it.

Like the other frontends it is a thin view: it renders
:class:`~cursor_mover.controller.AppState` and forwards intent to the controller.

Threading note: the ``Tk`` root is long-lived and belongs to the main thread, so
this frontend hands the controller a dispatcher built on ``after``, which
marshals timer-thread work onto the event loop. Never touch a widget from the
scheduler thread.
"""

from __future__ import annotations

import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from cursor_mover import __version__
from cursor_mover.constants import (
    APP_NAME,
    MAX_INTERVAL_SECONDS,
    MIN_INTERVAL_SECONDS,
)
from cursor_mover.controller import AppState, Controller

logger = logging.getLogger(__name__)

WINDOW_WIDTH = 380
WINDOW_HEIGHT = 250

ACTIVE_COLOUR = "#15803d"
IDLE_COLOUR = "#b91c1c"


class WindowFrontend:
    """Renders the controller as a small always-available window."""

    def __init__(self, controller: Controller) -> None:
        self._controller = controller
        self._root = tk.Tk()
        self._root.title(APP_NAME)
        self._root.resizable(False, False)
        self._centre()

        self._status_var = tk.StringVar()
        self._screen_var = tk.StringVar()
        self._interval_var = tk.StringVar(value=str(controller.state.interval_seconds))

        self._build_ui()

        self._root.protocol("WM_DELETE_WINDOW", self._on_quit)
        controller.set_dispatcher(self.dispatch)
        controller.set_on_change(self.render)
        self.render(controller.state)

    # -- construction ----------------------------------------------------

    def _centre(self) -> None:
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self._root.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _build_ui(self) -> None:
        frame = ttk.Frame(self._root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=APP_NAME, font=("TkDefaultFont", 16, "bold")).pack()
        ttk.Label(frame, text=f"version {__version__}", foreground="grey").pack(pady=(0, 12))

        self._status_label = ttk.Label(frame, font=("TkDefaultFont", 12, "bold"))
        self._status_label.pack(pady=(0, 12))
        self._status_label.configure(textvariable=self._status_var)

        interval_row = ttk.Frame(frame)
        interval_row.pack(pady=(0, 4))
        ttk.Label(interval_row, text="Interval (seconds):").pack(side="left", padx=(0, 6))
        entry = ttk.Entry(interval_row, textvariable=self._interval_var, width=6, justify="center")
        entry.pack(side="left")
        entry.bind("<Return>", lambda _event: self._on_apply_interval())
        ttk.Button(interval_row, text="Apply", command=self._on_apply_interval, width=7).pack(
            side="left", padx=(6, 0)
        )
        ttk.Label(
            frame,
            text=f"{MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS} seconds",
            foreground="grey",
        ).pack(pady=(0, 14))

        buttons = ttk.Frame(frame)
        buttons.pack()
        self._toggle_button = ttk.Button(buttons, text="Start", command=self._on_toggle, width=14)
        self._toggle_button.pack(side="left", padx=4)
        ttk.Button(buttons, text="Quit", command=self._on_quit, width=8).pack(side="left", padx=4)

        ttk.Label(frame, textvariable=self._screen_var, foreground="grey").pack(
            side="bottom", pady=(14, 0)
        )

    # -- threading -------------------------------------------------------

    def dispatch(self, work: Callable[[], None]) -> None:
        """Run ``work`` on the Tk event loop, from any thread."""
        try:
            self._root.after(0, work)
        except RuntimeError:
            # The interpreter is gone; the app is shutting down.
            logger.debug("Dropped work after the Tk loop closed", exc_info=True)

    # -- rendering -------------------------------------------------------

    def render(self, state: AppState) -> None:
        """Sync every widget with ``state``. Must run on the main thread."""
        self._status_var.set(state.status_label)
        self._status_label.configure(foreground=ACTIVE_COLOUR if state.running else IDLE_COLOUR)
        self._toggle_button.configure(text="Stop" if state.running else "Start")
        self._screen_var.set(state.screen_label)

        # Only overwrite the entry when it does not already show the live value,
        # so a half-typed number is not clobbered by an unrelated re-render.
        current = str(state.interval_seconds)
        if self._interval_var.get().strip() != current:
            self._interval_var.set(current)

        self._root.title(f"{APP_NAME} - {'Running' if state.running else 'Idle'}")

    # -- callbacks -------------------------------------------------------

    def _on_apply_interval(self) -> None:
        from cursor_mover.config import InvalidIntervalError

        try:
            self._controller.set_interval(self._interval_var.get())
        except InvalidIntervalError as exc:
            self._controller.system_ui.alert("Invalid Interval", str(exc))
            self._interval_var.set(str(self._controller.state.interval_seconds))

    def _on_toggle(self) -> None:
        # Apply whatever is in the entry before starting, so the user does not
        # have to press Apply first.
        if not self._controller.state.running:
            self._on_apply_interval()
        self._controller.toggle()

    def _on_quit(self) -> None:
        self._controller.shutdown()
        self._root.quit()
        self._root.destroy()

    # -- lifecycle -------------------------------------------------------

    def run(self) -> None:
        """Show the window and block until the user quits."""
        self._root.mainloop()
