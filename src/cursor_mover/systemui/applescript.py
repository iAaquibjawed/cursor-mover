"""macOS implementation of :class:`~cursor_mover.systemui.SystemUI`.

Everything here shells out to ``osascript``. User-supplied text is escaped with
:func:`applescript_quote` so a stray quote or backslash cannot break — or
inject into — the generated script.
"""

from __future__ import annotations

import logging
import subprocess

from cursor_mover.systemui import TextPrompt

logger = logging.getLogger(__name__)

#: Dialogs wait on a human, so they get a generous timeout.
DIALOG_TIMEOUT_SECONDS = 120
#: Notifications are fire-and-forget.
NOTIFICATION_TIMEOUT_SECONDS = 10


def applescript_quote(text: str) -> str:
    """Return ``text`` as a safely quoted AppleScript string literal."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _run_osascript(script: str, timeout: int) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.info("osascript timed out after %ss", timeout)
    except OSError as exc:
        logger.warning("Could not run osascript: %s", exc)
    return None


def notify(title: str, subtitle: str, message: str) -> None:
    """Post a Notification Center banner. Never raises."""
    script = (
        f"display notification {applescript_quote(message)} "
        f"with title {applescript_quote(title)} "
        f"subtitle {applescript_quote(subtitle)}"
    )
    if _run_osascript(script, NOTIFICATION_TIMEOUT_SECONDS) is None:
        logger.info("[notification] %s: %s - %s", title, subtitle, message)


def alert(title: str, message: str) -> None:
    """Show a modal message with a single OK button. Never raises."""
    script = (
        f"display dialog {applescript_quote(message)} "
        f"with title {applescript_quote(title)} "
        'buttons {"OK"} default button 1'
    )
    _run_osascript(script, DIALOG_TIMEOUT_SECONDS)


#: Separates the button name from the entered text in the AppleScript result.
_FIELD_SEPARATOR = "\x1f"


def prompt_for_text(
    title: str,
    message: str,
    default: str,
    confirm_label: str = "Set",
) -> TextPrompt:
    """Ask the user for a line of text.

    Returns a :class:`TextPrompt` whose ``confirmed`` flag is ``False`` if the
    user cancelled, dismissed the dialog, or the prompt could not be shown.
    """
    script = f"""
    set userResponse to display dialog {applescript_quote(message)} \
        default answer {applescript_quote(default)} \
        with title {applescript_quote(title)} \
        buttons {{"Cancel", {applescript_quote(confirm_label)}}} default button 2
    return (button returned of userResponse) & {applescript_quote(_FIELD_SEPARATOR)} \
        & (text returned of userResponse)
    """
    result = _run_osascript(script, DIALOG_TIMEOUT_SECONDS)

    # A non-zero exit code means the user pressed Cancel or closed the dialog.
    if result is None or result.returncode != 0:
        return TextPrompt(confirmed=False, text="")

    button, _, text = result.stdout.strip().partition(_FIELD_SEPARATOR)
    return TextPrompt(confirmed=button.strip() == confirm_label, text=text.strip())


class AppleScriptUI:
    """Dialogs and notifications via ``osascript``.

    A thin object wrapper over this module's functions, so it satisfies the
    :class:`~cursor_mover.systemui.SystemUI` protocol.
    """

    def notify(self, title: str, subtitle: str, message: str) -> None:
        notify(title, subtitle, message)

    def alert(self, title: str, message: str) -> None:
        alert(title, message)

    def prompt_for_text(self, title: str, message: str, default: str) -> TextPrompt:
        return prompt_for_text(title, message, default)
