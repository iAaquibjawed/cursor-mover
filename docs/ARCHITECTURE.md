# Architecture

Cursor Mover runs on macOS, Windows, and Linux from one codebase. This document
explains how, so changes land in the right place.

## The one rule

**Only `frontend/` may import a GUI toolkit.**

`rumps` wraps AppKit; `pystray` wraps Win32, GTK, or Xorg. Both need a real GUI
session, so anything importing them cannot be unit tested in CI. Confining them
to two thin view modules is what keeps the rest of the code — including *all*
application behaviour — testable headlessly.

The three platform differences are isolated behind protocols:

| Difference | Protocol | macOS | Windows / Linux |
| --- | --- | --- | --- |
| Tray UI | `Frontend` | `frontend/menubar.py` (rumps) | `frontend/tray.py` (pystray), or `frontend/window.py` (Tk) |
| Dialogs, notifications | `SystemUI` | `systemui/applescript.py` | `systemui/tk.py` |
| Repeating timer | `Scheduler` | `runloop.py` (run loop) | `scheduler.py` (thread) |
| Data directory | — | `paths.py` | `paths.py` |

Adding a platform means adding one implementation of each — not touching
`controller.py`.

## Module map

```
                        ┌──────────┐
                        │  cli.py  │  args, platform guard, wiring
                        └────┬─────┘
                             │ picks one frontend + scheduler + system UI
              ┌──────────────┴──────────────┐
     ┌────────▼─────────┐        ┌──────────▼────────┐
     │ frontend/menubar │        │  frontend/tray    │   ← the only modules
     │   (rumps, macOS) │        │ (pystray, Win/Lin)│     importing a toolkit
     └────────┬─────────┘        └──────────┬────────┘
              └──────────────┬──────────────┘
                    ┌────────▼─────────┐
                    │  controller.py   │  ALL behaviour lives here
                    └──┬────┬────┬─────┘
         ┌─────────────┘    │    └──────────────┐
   ┌─────▼─────┐   ┌────────▼───────┐   ┌───────▼────────┐
   │  mover.py │   │  scheduler.py  │   │   systemui/    │
   └─────┬─────┘   └────────────────┘   └───────┬────────┘
         │ PointerBackend                       │
   ┌─────▼─────┐                    ┌───────────▼───────────┐
   │ pyautogui │                    │ osascript  |  Tkinter │
   └───────────┘                    └───────────────────────┘
```

| Module | Responsibility | GUI toolkit? | Tested? |
| --- | --- | --- | --- |
| `cli.py` | Parse args, guard the platform, build the object graph | no | smoke only |
| `controller.py` | **All** behaviour: state, timers, validation, copy | no | yes |
| `mover.py` | Where the pointer goes, and moving it | no | yes |
| `config.py` | Validating and persisting settings | no | yes |
| `paths.py` | Per-platform data directories | no | yes |
| `scheduler.py` | Thread timer, factory, and test double | no | yes |
| `systemui/*` | Dialogs and notifications | Tkinter (lazy) | yes |
| `artwork.py` | Drawing the icon | Pillow | no |
| `frontend/menubar.py` | Rendering `AppState` as a macOS menu | **rumps** | no |
| `frontend/tray.py` | Rendering `AppState` as a tray icon | **pystray** | no |
| `frontend/window.py` | Rendering `AppState` as a window (no-tray fallback) | **Tkinter** | no |
| `runloop.py` | macOS run-loop timer | **rumps** | no |

The views are genuinely thin: each is roughly 40 lines of "read `AppState`, set
labels" plus callbacks that forward straight to the controller.

## Key decisions

### The timer is abstracted, because the platforms disagree

macOS has a Cocoa run loop and AppKit *requires* UI work on it, so the timer must
fire there: `runloop.RunLoopScheduler` wraps `rumps.Timer`. pystray's backends
expose no reusable timer, so Windows and Linux use
`scheduler.ThreadScheduler`, a daemon thread with an interruptible wait.

`Controller` only sees the `Scheduler` protocol, so tests drive
`ManualScheduler` and fire ticks explicitly — no sleeping in the test suite.

An earlier version polled every 0.5s on a background thread *and* touched menu
titles from it, which AppKit forbids. If you add a thread, it must not touch a
view.

The cost of the run-loop approach on macOS is that a move blocks the loop for
`MOVE_DURATION_SECONDS` (0.25s) while the cursor glides. That is imperceptible.

### A missing tray must not mean an invisible app

pystray selects its backend at import time and silently falls back to a
non-functional dummy when the session has none — GNOME without the AppIndicator
extension is the common case. An icon built on that dummy never appears, leaving
the process running with no way to stop it.

There is a second, subtler case: pystray's bare X11 backend (`_xorg`) sets
`HAS_MENU = False`. It shows an icon, but clicking it can never open a menu, so
the user cannot change the interval or quit. Since the menu *is* the interface,
that is just as unusable as no icon.

`frontend.tray_is_available()` rejects both — the dummy backend and any backend
without `HAS_MENU` — and `create_frontend` falls back to `WindowFrontend`. This
is the one piece of platform detection that is genuinely a *choice* rather than
an implementation, which is why it lives in the factory and is unit tested.

### Click gestures differ, and cannot be normalised

| Backend | Plain click | Menu |
| --- | --- | --- |
| rumps (macOS) | opens the menu | click |
| pystray `_appindicator` | opens the menu (`HAS_DEFAULT_ACTION = False`) | click |
| pystray `_win32` | fires the default menu item | right-click |

Windows hard-codes left-click to the default action in `_on_notify`, and pystray
exposes no way to open the menu programmatically. So the tray frontend marks the
start/stop item `default=True`: on Windows that makes left-click a toggle
shortcut, and on macOS and Linux it is simply ignored. Do not try to "fix" this
by faking a click handler.

### Long-lived Tk roots need a dispatcher; per-call roots do not

`Controller` accepts a `dispatch` callable, used for re-renders and for the
alert raised when a move fails. Both can originate on the `ThreadScheduler`
thread.

* `WindowFrontend` owns a long-lived `Tk` root bound to the main thread, so it
  supplies `root.after` as the dispatcher. Touching a widget from the scheduler
  thread would be a crash.
* `TrayFrontend` uses the default inline dispatcher: `Icon.update_menu()` is
  documented as thread-safe, and `systemui/tk.py` creates *and destroys* a fresh
  `Tk` root inside a single call, so all of its Tcl calls happen on whichever
  thread invoked it.

### Tkinter dialogs rely on pystray's threading guarantee

`Icon.run()` is called from the main thread and pystray dispatches menu
callbacks on that same thread, so a Tkinter dialog opened from a callback is on
the main thread, as Tk requires. `systemui/tk.py` creates and destroys a fresh
`Tk` root per dialog, and degrades to a log line when Tkinter is missing —
common on Linux, where it is a separate package.

### Notifications fall through three channels

The tray icon's own `notify()` is preferred, then `notify-send` on Linux, then a
log line. The frontend injects the first via `TkUI.set_notifier` once the icon
exists, which is why `Controller` exposes `system_ui` publicly.

### The pointer backend is injected

`mover.py` depends on a `PointerBackend` `Protocol` — the three pyautogui
functions it actually uses (`size`, `position`, `moveTo`), including
pyautogui's camelCase spelling. Tests pass a `FakeBackend` that records calls,
so the movement logic is verified without moving a real cursor.

### AppleScript is built by string interpolation, so quoting is mandatory

There is no parameterised API for `osascript`. Every value that reaches a script
goes through `applescript_quote()`, which escapes backslashes before quotes.
`tests/test_macos.py` includes an injection attempt as a regression guard.

Dialog results come back as `button<US>text`, using ASCII Unit Separator
(`\x1f`) rather than a printable delimiter, so user-entered text cannot forge a
field boundary.

### Settings failures never block launch

`SettingsStore.load()` returns defaults for a missing file, unreadable file,
malformed JSON, non-object JSON, or an out-of-range interval. `save()` logs and
swallows `OSError`. A bad settings file degrades the app to defaults; it never
prevents it from starting. Writes go to a temp file and are renamed, so an
interrupted write cannot leave a truncated file.

## Adding a feature

1. Does it decide *where or whether* the cursor moves? → `mover.py`, with tests.
2. Is it a user preference? → `config.py`, with validation and tests.
3. Does it need a dialog or notification? → `systemui/`, both implementations.
4. Is it a state transition, or user-visible copy? → `controller.py`, with tests.
5. Is it purely how a menu looks? → the relevant `frontend/` module, and add the
   same item to *both* so the platforms do not drift.

If you find yourself writing an `if sys.platform` inside `controller.py`, that
logic belongs behind one of the protocols instead.

## Platform constraints worth knowing

- **Wayland cannot work.** It deliberately forbids applications from moving the
  pointer. `cli.is_wayland()` detects it and warns; there is no workaround short
  of a compositor-specific protocol. X11 only on Linux.
- **PyInstaller cannot cross-compile.** Each artifact is built on its own OS,
  which is why CI uses an OS matrix rather than one job.
- **pystray picks its backend at import time** from the running session, so the
  Linux spec names `_appindicator`, `_gtk`, and `_xorg` as hidden imports and
  ships all three.
- **GNOME has no system tray** by default. Rather than requiring the
  AppIndicator extension, the app falls back to a window. Documented in
  `docs/install/linux.txt`.
- **macOS never loads Tk.** `systemui/create_system_ui` returns the AppleScript
  implementation, and `packaging/macos.spec` excludes `tkinter` and `pystray`
  outright, so the bundle ships no Tcl/Tk runtime.

## Adding a platform

1. Implement `Scheduler` if the platform needs a different timer.
2. Implement `SystemUI` for its dialogs and notifications.
3. Implement `Frontend` for its tray or menu.
4. Add a branch to `paths.config_dir`, and to the three factory functions
   (`create_scheduler`, `create_system_ui`, `create_frontend`).
5. Add a PyInstaller spec and a build script under `packaging/`.

`controller.py`, `mover.py`, and `config.py` should not need to change.
