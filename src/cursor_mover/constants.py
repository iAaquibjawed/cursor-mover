"""Shared constants and metadata for Cursor Mover."""

from __future__ import annotations

from typing import Final

APP_NAME: Final = "Cursor Mover"
BUNDLE_NAME: Final = "CursorMover"
#: Lower-case identifier for XDG paths and executable names.
SLUG: Final = "cursor-mover"
BUNDLE_IDENTIFIER: Final = "com.cursormover.app"

#: Shown in the macOS menu bar. Kept to a single glyph so the bar stays tidy.
MENU_BAR_TITLE: Final = "→"

#: Tooltip shown when hovering the Windows/Linux tray icon.
TRAY_TOOLTIP: Final = APP_NAME

#: Movement interval bounds, in seconds.
MIN_INTERVAL_SECONDS: Final = 10
MAX_INTERVAL_SECONDS: Final = 3600
DEFAULT_INTERVAL_SECONDS: Final = 11

#: How long a single cursor glide takes.
MOVE_DURATION_SECONDS: Final = 0.25

#: Fallback used when the screen size cannot be queried.
FALLBACK_SCREEN_SIZE: Final = (1920, 1080)
