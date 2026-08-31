"""The cursor movement engine.

This module deliberately knows nothing about menus, notifications, or rumps so
that it can be unit tested without a running GUI. The only I/O it performs is
through the injected ``backend``.
"""

from __future__ import annotations

import logging
import random
from typing import Protocol

from cursor_mover.constants import (
    FALLBACK_SCREEN_SIZE,
    MOVE_DURATION_SECONDS,
)

logger = logging.getLogger(__name__)

Point = tuple[int, int]


class PointerBackend(Protocol):
    """The slice of pyautogui that Cursor Mover actually depends on."""

    def size(self) -> Point: ...

    def position(self) -> Point: ...

    def moveTo(self, x: int, y: int, duration: float = 0.0) -> None: ...


class AccessibilityPermissionError(RuntimeError):
    """Raised when macOS has not granted Accessibility access."""


def random_point(width: int, height: int, rng: random.Random | None = None) -> Point:
    """Return a uniformly random point inside a ``width`` x ``height`` screen.

    Both bounds are inclusive of 0 and exclusive of the width/height, so the
    result is always addressable.
    """
    if width < 1 or height < 1:
        raise ValueError(f"Screen size must be positive, got {width}x{height}.")
    chooser = rng or random
    return chooser.randint(0, width - 1), chooser.randint(0, height - 1)


class CursorMover:
    """Moves the pointer to a random screen position on demand.

    The caller decides *when* to move (the app uses a run-loop timer); this
    class only decides *where* and performs the move.
    """

    def __init__(
        self,
        backend: PointerBackend,
        rng: random.Random | None = None,
    ) -> None:
        self._backend = backend
        self._rng = rng
        self.screen_size = self._detect_screen_size()

    def _detect_screen_size(self) -> Point:
        try:
            width, height = self._backend.size()
            if width > 0 and height > 0:
                return int(width), int(height)
            logger.warning("Backend reported a non-positive screen size.")
        except Exception as exc:  # noqa: BLE001 - backend failures are opaque
            logger.warning("Could not determine screen size: %s", exc)
        return FALLBACK_SCREEN_SIZE

    def refresh_screen_size(self) -> Point:
        """Re-query the screen size, e.g. after a display change."""
        self.screen_size = self._detect_screen_size()
        return self.screen_size

    def ensure_permission(self) -> None:
        """Verify the pointer can be read.

        Raises:
            AccessibilityPermissionError: if macOS Accessibility access is missing.
        """
        try:
            self._backend.position()
        except Exception as exc:
            raise AccessibilityPermissionError(str(exc)) from exc

    def move_once(self) -> Point:
        """Move the cursor to a fresh random position and return it."""
        target = random_point(*self.screen_size, rng=self._rng)
        self._backend.moveTo(target[0], target[1], duration=MOVE_DURATION_SECONDS)
        logger.debug("Moved cursor to %s", target)
        return target
