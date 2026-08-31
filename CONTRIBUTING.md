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
| `mover.py` | Deciding where the pointer goes and moving it |
| `config.py` | Validating and persisting user settings |
| `macos.py` | Anything that shells out to `osascript` |
| `app.py` | Menu structure, menu state, and the movement timer |
| `cli.py` | Argument parsing and wiring the pieces together |

`app.py` is the only module allowed to import `rumps`.

## Threading

Movement runs on a `rumps.Timer`, which fires on the main run loop. Do not add
background threads that touch menu items or show dialogs — AppKit requires that
work on the main thread.

## Reporting a bug

Please include your macOS version, how you installed the app (DMG or source),
and the output of `cursor-mover --verbose` if you can reproduce from source.
