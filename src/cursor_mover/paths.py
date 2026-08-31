"""Platform-appropriate locations for application data.

Each desktop platform has its own convention, and using the wrong one leaves
files where the OS will not clean them up:

    macOS    ~/Library/Application Support/CursorMover
    Windows  %APPDATA%\\CursorMover
    Linux    $XDG_CONFIG_HOME/cursor-mover  (default ~/.config/cursor-mover)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from cursor_mover.constants import BUNDLE_NAME, SLUG


def config_dir(platform: str | None = None, env: dict[str, str] | None = None) -> Path:
    """Return the directory Cursor Mover stores its settings in.

    Args:
        platform: A ``sys.platform`` value. Defaults to the running platform.
        env: Environment mapping to read. Defaults to ``os.environ``.
    """
    plat = platform if platform is not None else sys.platform
    environ = env if env is not None else dict(os.environ)
    home = Path.home()

    if plat == "darwin":
        return home / "Library" / "Application Support" / BUNDLE_NAME

    if plat.startswith("win"):
        # APPDATA is set on every supported Windows version, but fall back
        # rather than crash if the process was started with a scrubbed env.
        appdata = environ.get("APPDATA")
        base = Path(appdata) if appdata else home / "AppData" / "Roaming"
        return base / BUNDLE_NAME

    # Linux, BSD, and anything else XDG-shaped.
    xdg = environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else home / ".config"
    return base / SLUG
