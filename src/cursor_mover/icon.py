"""Tray icon image loading."""

from __future__ import annotations

import logging

from PIL import Image

from cursor_mover.artwork import tray_image

logger = logging.getLogger(__name__)

TRAY_ICON_SIZE = 64


def load_tray_image(size: int = TRAY_ICON_SIZE) -> Image.Image:
    """Return the tray icon, falling back to a plain square if drawing fails.

    A tray backend given no image raises, so it is better to show a blank
    marker the user can still click than to fail to start.
    """
    try:
        return tray_image(size)
    except Exception:
        logger.exception("Could not draw the tray icon; using a plain fallback")
        return Image.new("RGBA", (size, size), (99, 102, 241, 255))
