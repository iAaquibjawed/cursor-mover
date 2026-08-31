<p align="center">
  <img src="assets/icon.png" alt="Cursor Mover" width="128" height="128">
</p>

<h1 align="center">Cursor Mover</h1>

<p align="center">
  <a href="https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml"><img src="https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/iAaquibjawed/cursor-mover/releases"><img src="https://img.shields.io/github/v/release/iAaquibjawed/cursor-mover?sort=semver" alt="Release"></a>
  <img src="https://img.shields.io/badge/platform-macOS%2011%2B-lightgrey" alt="Platform: macOS 11+">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
</p>

A tiny macOS menu bar app that keeps your Mac awake by nudging the cursor to a
random position on a timer. No Dock icon, no window — just a `→` in the menu bar.

> The icon is a working draft. See [assets/LOGO_BRIEF.md](assets/LOGO_BRIEF.md)
> for the full design brief and a ready-to-paste image-generator prompt.

## Features

- Moves the cursor to a random screen position on a fixed interval
- Configurable interval from 10 seconds to 1 hour, remembered between launches
- Native macOS notifications and dialogs
- Keyboard shortcuts for start/stop, interval, and quit
- Runs as a background agent — no Dock icon, no app switcher entry

## Install

### From a release

1. Download `CursorMover-macOS.dmg` from the [Releases](https://github.com/iAaquibjawed/cursor-mover/releases) page.
2. Drag **CursorMover.app** into Applications and launch it.
3. Grant Accessibility permission (see [Permissions](#permissions)).

Builds are ad-hoc signed, not notarized. On first launch, right-click the app
and choose **Open**, then confirm.

### From source

Requires macOS 11+ and Python 3.10+.

```bash
git clone https://github.com/iAaquibjawed/cursor-mover.git
cd cursor-mover

python3 -m venv .venv && source .venv/bin/activate
pip install -e .

cursor-mover
```

## Usage

Click the `→` in the menu bar:

| Item | Shortcut | Description |
| --- | --- | --- |
| ▶ / ⏸ Start / Stop Movement | `s` | Toggle cursor movement |
| ⚙️ Change Interval… | `i` | Set the interval in seconds (10–3600) |
| Quit | `q` | Stop movement and exit |

The menu also shows the current status, interval, and screen resolution.
Settings are stored in `~/Library/Application Support/CursorMover/settings.json`.

## Permissions

Cursor Mover needs **Accessibility** access to move the pointer:

**System Settings → Privacy & Security → Accessibility** → enable
**CursorMover** (or your terminal app, when running from source), then relaunch.

## Development

```bash
make install    # editable install with dev and build extras
make run        # launch from source with verbose logging
make check      # lint, format check, and tests - everything CI runs
make app        # build dist/CursorMover.app
make dmg        # build dist/CursorMover-macOS.dmg
make icon       # regenerate assets/icon.png and assets/icon.icns
```

`make help` lists every target. If you prefer not to use make, each target is a
one-line command you can read straight out of the `Makefile`.

### Project layout

```
src/cursor_mover/       Application package
  cli.py                Argument parsing, platform guard, dependency wiring
  app.py                rumps menu bar UI and state (the only rumps importer)
  mover.py              Pointer movement engine - no UI, unit tested
  config.py             Settings validation and JSON persistence
  macos.py              osascript wrappers for dialogs and notifications
  constants.py          Shared metadata and limits
tests/                  pytest suite
packaging/              PyInstaller spec and the build/DMG scripts
assets/                 Icon artwork, the renderer, and the design brief
docs/                   Architecture, release, and end-user documentation
.github/                CI, release automation, issue and PR templates
```

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before a non-trivial change.
The short version: `mover`, `config`, and `macos` must stay free of `rumps` so
they remain testable without a GUI session, and movement runs on the main run
loop rather than a background thread.

## Building and releasing

```bash
make dmg    # -> dist/CursorMover.app and dist/CursorMover-macOS.dmg
```

Pushing a `v*` tag builds and publishes a release automatically; see
[docs/RELEASING.md](docs/RELEASING.md) for the checklist and for code signing
and notarization.

## Platform support

macOS only. The menu bar UI is built on [`rumps`](https://github.com/jaredks/rumps),
which wraps AppKit and has no Windows or Linux equivalent. Porting would mean a
separate front end (for example `pystray`) over the same `mover` module.

## Contributing

Issues and pull requests are welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md), and please read
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) if you are touching more than one
module.

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md) — report vulnerabilities privately, not in an issue
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
