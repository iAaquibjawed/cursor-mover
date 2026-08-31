"""GTK implementation of :class:`~cursor_mover.systemui.SystemUI`.

Preferred over Tkinter on Linux for two reasons:

* the Flatpak runtime ships GTK and PyGObject but **no** Tkinter, so the Tk
  implementation would silently degrade to log lines and the user could never
  change the interval;
* GTK is already present on any desktop running the tray, so distro users do
  not need to install ``python3-tk`` at all.

Threading: every function here must run on the thread that owns the GTK main
loop. pystray's GTK backend dispatches menu callbacks on that thread, and the
controller's dispatcher covers work raised from the timer thread.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from cursor_mover.systemui import TextPrompt

logger = logging.getLogger(__name__)


def gtk_is_available() -> bool:
    """Whether GTK 3 and PyGObject can be imported in this process."""
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk  # noqa: F401
    except (ImportError, ValueError) as exc:
        logger.debug("GTK is unavailable: %s", exc)
        return False
    return True


def _gtk():
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    return Gtk


def _drain_events() -> None:
    """Let GTK finish tearing a dialog down before returning."""
    Gtk = _gtk()
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)


class GtkUI:
    """Dialogs via GTK; notifications via the tray icon or the desktop portal."""

    def __init__(self, notifier: Callable[[str, str], None] | None = None) -> None:
        self._notifier = notifier

    def set_notifier(self, notifier: Callable[[str, str], None] | None) -> None:
        """Attach a notification sink, normally ``pystray.Icon.notify``."""
        self._notifier = notifier

    def notify(self, title: str, subtitle: str, message: str) -> None:
        """Post a notification. Never raises."""
        body = f"{subtitle}\n{message}" if subtitle else message

        if self._notifier is not None:
            try:
                self._notifier(body, title)
                return
            except Exception as exc:  # noqa: BLE001 - backend-specific failures
                logger.debug("Tray notification failed: %s", exc)

        # Gio reaches the notification portal, which works inside a Flatpak
        # sandbox where notify-send does not.
        try:
            from gi.repository import Gio

            app = Gio.Application.get_default() or Gio.Application(
                application_id="io.github.iaaquibjawed.CursorMover"
            )
            note = Gio.Notification.new(title)
            note.set_body(body)
            app.send_notification(None, note)
            return
        except Exception as exc:  # noqa: BLE001 - portal may be absent
            logger.debug("Gio notification failed: %s", exc)

        logger.info("[notification] %s: %s", title, body)

    def alert(self, title: str, message: str) -> None:
        """Show a modal message with a single dismiss button. Never raises."""
        try:
            Gtk = _gtk()
            dialog = Gtk.MessageDialog(
                transient_for=None,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=title,
            )
            dialog.format_secondary_text(message)
            dialog.set_keep_above(True)
            dialog.run()
            dialog.destroy()
            _drain_events()
        except Exception as exc:  # noqa: BLE001 - toolkit failures are opaque
            logger.warning("Could not show alert %r: %s", title, exc)
            logger.info("[alert] %s: %s", title, message)

    def prompt_for_text(self, title: str, message: str, default: str) -> TextPrompt:
        """Ask for one line of text. Never raises."""
        try:
            Gtk = _gtk()
            dialog = Gtk.MessageDialog(
                transient_for=None,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                text=title,
            )
            dialog.format_secondary_text(message)
            dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Set", Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)
            dialog.set_keep_above(True)

            entry = Gtk.Entry()
            entry.set_text(default)
            entry.set_activates_default(True)
            entry.show()
            dialog.get_content_area().pack_end(entry, False, False, 8)

            response = dialog.run()
            text = entry.get_text()
            dialog.destroy()
            _drain_events()
        except Exception as exc:  # noqa: BLE001 - toolkit failures are opaque
            logger.warning("Could not show prompt %r: %s", title, exc)
            return TextPrompt(confirmed=False, text="")

        if response != Gtk.ResponseType.OK:
            return TextPrompt(confirmed=False, text="")
        return TextPrompt(confirmed=True, text=text.strip())
