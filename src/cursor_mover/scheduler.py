"""Repeating-timer abstraction.

The two frontends need fundamentally different timers:

* macOS/rumps has a Cocoa run loop, and UI work *must* happen on it, so the
  timer has to fire there (:class:`RunLoopScheduler`, provided by the frontend).
* pystray's tray backends have no reusable run loop, so a background thread is
  the only option (:class:`ThreadScheduler`).

:class:`Scheduler` is the contract both satisfy, which lets
:class:`cursor_mover.controller.Controller` stay timer-agnostic and testable
with :class:`ManualScheduler`.
"""

from __future__ import annotations

import sys
import threading
from collections.abc import Callable
from typing import Protocol


class Scheduler(Protocol):
    """A cancellable repeating timer."""

    @property
    def is_active(self) -> bool:
        """Whether the timer is currently scheduled."""
        ...

    def start(self, interval: float, callback: Callable[[], None]) -> None:
        """Begin calling ``callback`` every ``interval`` seconds."""
        ...

    def stop(self) -> None:
        """Cancel the timer. Safe to call when already stopped."""
        ...


class ThreadScheduler:
    """Fires ``callback`` on a daemon thread every ``interval`` seconds.

    Used on Windows and Linux. The wait is interruptible, so :meth:`stop`
    returns promptly instead of blocking for the rest of the interval.
    """

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._wake = threading.Event()
        self._lock = threading.Lock()

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self, interval: float, callback: Callable[[], None]) -> None:
        self.stop()
        with self._lock:
            self._wake.clear()
            self._thread = threading.Thread(
                target=self._loop,
                args=(interval, callback),
                name="cursor-mover-timer",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            thread = self._thread
            self._thread = None
        self._wake.set()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def _loop(self, interval: float, callback: Callable[[], None]) -> None:
        this_thread = threading.current_thread()
        # Event.wait returns True when set, i.e. when we have been stopped.
        while not self._wake.wait(interval):
            with self._lock:
                if self._thread is not this_thread:
                    return
            callback()


class ManualScheduler:
    """Test double: records the interval and fires only when told to."""

    def __init__(self) -> None:
        self.interval: float | None = None
        self._callback: Callable[[], None] | None = None
        self.start_count = 0
        self.stop_count = 0

    @property
    def is_active(self) -> bool:
        return self._callback is not None

    def start(self, interval: float, callback: Callable[[], None]) -> None:
        self.interval = interval
        self._callback = callback
        self.start_count += 1

    def stop(self) -> None:
        if self._callback is not None:
            self.stop_count += 1
        self._callback = None
        self.interval = None

    def fire(self, times: int = 1) -> None:
        """Invoke the scheduled callback, as the real timer would."""
        for _ in range(times):
            if self._callback is None:
                raise RuntimeError("Scheduler is not running; nothing to fire.")
            self._callback()


def create_scheduler(platform: str | None = None) -> Scheduler:
    """Return the scheduler appropriate for ``platform``."""
    plat = platform if platform is not None else sys.platform

    if plat == "darwin":
        from cursor_mover.runloop import RunLoopScheduler

        return RunLoopScheduler()

    return ThreadScheduler()
