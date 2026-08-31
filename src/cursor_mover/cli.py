"""Command line entry point and dependency wiring."""

from __future__ import annotations

import argparse
import logging
import sys

from cursor_mover import __version__
from cursor_mover.constants import APP_NAME


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cursor-mover",
        description=f"{APP_NAME}: a macOS menu bar app that nudges the cursor "
        "to a random position on a timer.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Launch the menu bar app. Returns a process exit code."""
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    if sys.platform != "darwin":
        print(
            f"{APP_NAME} is macOS-only: it uses the native menu bar via rumps.",
            file=sys.stderr,
        )
        return 1

    # Imported here so that --help and --version work without a GUI stack.
    import pyautogui
    import rumps  # noqa: F401 - imported for the side effect of failing early

    from cursor_mover.app import CursorMoverApp
    from cursor_mover.mover import CursorMover

    # The cursor is intentionally driven into screen corners, which would
    # otherwise trip pyautogui's fail-safe abort.
    pyautogui.FAILSAFE = False

    CursorMoverApp(mover=CursorMover(backend=pyautogui)).run()
    return 0
