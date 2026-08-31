# Architecture

Cursor Mover is small — under 600 lines of Python — but it is split
deliberately. This document explains why, so changes land in the right place.

## The one rule

**Only `app.py` may import `rumps`.**

`rumps` wraps AppKit, which needs a real GUI session and a running event loop.
Anything that imports it cannot be unit tested in CI. Keeping it confined to a
single module is what makes the other 80% of the code testable headlessly.

## Module map

```
                 ┌──────────┐
                 │  cli.py  │  argument parsing, platform guard, wiring
                 └────┬─────┘
                      │ constructs
                 ┌────▼─────┐
                 │  app.py  │  ← the only module that imports rumps
                 └──┬──┬──┬─┘
        ┌───────────┘  │  └───────────┐
   ┌────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
   │ mover.py │  │ config.py │  │ macos.py  │
   └────┬─────┘  └───────────┘  └─────┬─────┘
        │ PointerBackend               │ subprocess
   ┌────▼──────┐                 ┌─────▼──────┐
   │ pyautogui │                 │ osascript  │
   └───────────┘                 └────────────┘
```

| Module | Responsibility | Imports rumps? | Tested? |
| --- | --- | --- | --- |
| `cli.py` | Parse args, refuse non-macOS, build the object graph | no | smoke only |
| `app.py` | Menu structure, menu state, the movement timer | **yes** | no |
| `mover.py` | Where the pointer goes, and moving it | no | yes |
| `config.py` | Validating and persisting settings | no | yes |
| `macos.py` | Everything that shells out to `osascript` | no | yes |
| `constants.py` | Shared metadata and limits | no | n/a |

## Key decisions

### Movement runs on the run loop, not a thread

Earlier versions used a background thread that woke every 0.5s to check whether
it was time to move. That thread also touched menu titles and showed alerts on
the failure path — AppKit requires that work on the main thread, so it was a
latent crash.

Movement is now a `rumps.Timer`, which fires on the main run loop. This removed
the polling loop, a lock, and the thread entirely, and it means **every method in
`app.py` already runs on the main thread**. Do not reintroduce a thread that
touches UI.

The cost is that a move blocks the run loop for `MOVE_DURATION_SECONDS` (0.25s)
while the cursor glides. That is imperceptible for a menu bar app.

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
3. Does it need a dialog or notification? → `macos.py`, with tests.
4. Is it a menu item or menu state? → `app.py`. Wire it to the modules above
   rather than putting logic in the callback.

## Porting off macOS

`mover.py` and `config.py` are already platform-neutral. A Windows or Linux port
would replace `app.py` (for example with `pystray`) and `macos.py` (with that
platform's notification mechanism), and reuse the rest. There is currently no
such port, and the README says so plainly.
