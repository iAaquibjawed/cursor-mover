# Contributing

Thanks for taking the time to help. Cursor Mover is small, so the bar is simply:
keep it small, keep it tested.

## Getting set up

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Before opening a pull request

- `ruff check .` and `ruff format .` are clean.
- `pytest` passes.
- New behaviour in `mover.py`, `config.py`, or `macos.py` has a test. These
  modules have no rumps dependency specifically so they can be tested headlessly.
- `CHANGELOG.md` has an entry under an Unreleased heading.

## Where code belongs

| Module | Responsibility |
| --- | --- |
| `controller.py` | **All** behaviour: state, timers, validation, user-facing copy |
| `mover.py` | Deciding where the pointer goes and moving it |
| `config.py` / `paths.py` | Validating, persisting, and locating settings |
| `systemui/` | Dialogs and notifications, one module per platform |
| `scheduler.py` / `runloop.py` | Repeating timers |
| `frontend/` | Menu structure and rendering, one module per platform |
| `cli.py` | Argument parsing and wiring the pieces together |

**Only `frontend/` may import a GUI toolkit** (`rumps` or `pystray`). If you
write `if sys.platform` inside `controller.py`, that logic belongs behind the
`Scheduler`, `SystemUI`, or `Frontend` protocol instead.

When you add a menu item, add it to **all three** frontends —
`frontend/menubar.py`, `frontend/tray.py`, and `frontend/window.py` — so the
platforms do not drift.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full picture.

## Threading

macOS drives movement from the Cocoa run loop; Windows and Linux use a daemon
thread. Neither may touch a view from a background thread — AppKit and Tk both
require main-thread access. If your frontend owns a long-lived toolkit object,
give the controller a dispatcher (`Controller.set_dispatcher`) as
`WindowFrontend` does. `ManualScheduler` lets you test tick behaviour without
sleeping.

## Testing across platforms

CI runs the suite on macOS, Windows, and Ubuntu. You only need one locally: the
test suite imports no GUI toolkit, so it passes everywhere. If you change
platform-specific code you cannot run, say so in the PR and CI will cover it.

On Linux, install `python3-tk` for the dialogs and remember that **Wayland cannot
work** — pointer control requires X11.

## Reporting a bug

Please include your OS and version, how you installed the app (release download
or from source), and the output of `cursor-mover --verbose`. On Linux also
include `echo $XDG_SESSION_TYPE` and your desktop environment.
