"""macOS run-loop scheduler.

Separate from :mod:`cursor_mover.scheduler` because it imports ``rumps``, which
requires AppKit and a GUI session.
"""

from __future__ import annotations

from collections.abc import Callable

import rumps


class RunLoopScheduler:
    """A :class:`~cursor_mover.scheduler.Scheduler` backed by ``rumps.Timer``.

    The timer fires on the Cocoa main run loop, which is what lets the macOS
    frontend update menu items directly from the tick callback.
    """

    def __init__(self) -> None:
        self._timer: rumps.Timer | None = None

    @property
    def is_active(self) -> bool:
        return self._timer is not None and self._timer.is_alive()

    def start(self, interval: float, callback: Callable[[], None]) -> None:
        self.stop()
        # rumps passes the timer to its callback; the Scheduler contract does not.
        self._timer = rumps.Timer(lambda _timer: callback(), interval)
        self._timer.start()

    def stop(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
