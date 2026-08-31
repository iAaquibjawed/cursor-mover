"""Command line entry point, platform checks, and dependency wiring."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from cursor_mover import __version__
from cursor_mover.constants import APP_NAME, MIN_INTERVAL_SECONDS

logger = logging.getLogger(__name__)

SUPPORTED_PLATFORM_PREFIXES = ("darwin", "win", "linux", "freebsd", "openbsd", "netbsd")

WAYLAND_WARNING = (
    "This session appears to be running Wayland, which does not let "
    "applications move the pointer. Cursor Mover will start, but movement will "
    "fail. Log in to an X11 / Xorg session instead."
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cursor-mover",
        description=(
            f"{APP_NAME}: a cross-platform tray app that nudges the cursor to a "
            "random position on a timer, so your computer never registers as idle."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    parser.add_argument(
        "--interval",
        type=int,
        metavar="SECONDS",
        help=f"override the saved interval (minimum {MIN_INTERVAL_SECONDS})",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="begin moving the cursor immediately, without using the menu",
    )
    parser.add_argument(
        "--ui",
        choices=("auto", "tray", "window"),
        default="auto",
        help=(
            "which interface to show. 'auto' (default) uses the tray or menu "
            "bar and falls back to a window when no tray is available; "
            "'window' forces a plain window, useful on GNOME without the "
            "AppIndicator extension"
        ),
    )
    return parser.parse_args(argv)


def is_supported_platform(platform: str) -> bool:
    """Whether Cursor Mover has a frontend for ``platform``."""
    return platform.startswith(SUPPORTED_PLATFORM_PREFIXES)


def is_wayland(env: dict[str, str] | None = None) -> bool:
    """Detect a Wayland session, where pointer control is not permitted."""
    environ = env if env is not None else dict(os.environ)
    if environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
        return True
    return bool(environ.get("WAYLAND_DISPLAY"))


def main(argv: list[str] | None = None) -> int:
    """Launch the tray app. Returns a process exit code."""
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    if not is_supported_platform(sys.platform):
        print(
            f"{APP_NAME} does not support the platform {sys.platform!r}. "
            "Supported: macOS, Windows, Linux, BSD.",
            file=sys.stderr,
        )
        return 1

    if sys.platform.startswith("linux") and is_wayland():
        logger.warning(WAYLAND_WARNING)

    # Imported here so --help and --version work without a GUI stack installed.
    import pyautogui

    from cursor_mover.controller import Controller
    from cursor_mover.frontend import create_frontend
    from cursor_mover.mover import CursorMover
    from cursor_mover.scheduler import create_scheduler
    from cursor_mover.systemui import create_system_ui

    # The cursor is intentionally driven into screen corners, which would
    # otherwise trip pyautogui's fail-safe abort.
    pyautogui.FAILSAFE = False

    controller = Controller(
        mover=CursorMover(backend=pyautogui),
        scheduler=create_scheduler(),
        system_ui=create_system_ui(),
    )

    if args.interval is not None:
        from cursor_mover.config import InvalidIntervalError

        try:
            controller.set_interval(args.interval, announce=False)
        except InvalidIntervalError as exc:
            print(f"--interval: {exc}", file=sys.stderr)
            return 2

    try:
        frontend = create_frontend(controller, choice=args.ui)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.start:
        controller.start(announce=False)

    frontend.run()
    return 0
