<p align="center">
  <img src="assets/icon.png" alt="Cursor Mover" width="128" height="128">
</p>

<h1 align="center">Cursor Mover</h1>

<p align="center">
  <a href="https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml"><img src="https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/iAaquibjawed/cursor-mover/releases"><img src="https://img.shields.io/github/v/release/iAaquibjawed/cursor-mover?sort=semver" alt="Release"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform: macOS, Windows, Linux">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
</p>

A tiny tray app that keeps your computer awake by nudging the cursor to a random
position on a timer. No window, no taskbar entry — just an icon in the menu bar
or system tray.

Runs on **macOS, Windows, and Linux**.

> The icon is a working draft. See [assets/LOGO_BRIEF.md](assets/LOGO_BRIEF.md)
> for the full design brief and a ready-to-paste image-generator prompt.

## Features

- Moves the cursor to a random screen position on a fixed interval
- Configurable interval from 10 seconds to 1 hour, remembered between launches
- Native notifications and dialogs on every platform
- Runs as a background agent — no Dock icon, taskbar button, or app switcher entry
- Single self-contained download per platform; no Python needed

### Platform support

| | macOS | Windows | Linux |
| --- | --- | --- | --- |
| Minimum | 11 Big Sur | 10 | X11 / Xorg session |
| Frontend | menu bar (`rumps`) | system tray (`pystray`) | system tray, or a window |
| Dialogs | native, via AppleScript | Tkinter | Tkinter |
| Permission needed | Accessibility | none | none |
| Keyboard shortcuts | yes | — | — |
| Download | `.dmg` | `.zip` | `.tar.gz` |

**Linux requires X11.** Wayland does not permit applications to move the
pointer, so Cursor Mover cannot work there — it detects Wayland and warns at
startup. Check with `echo $XDG_SESSION_TYPE`; if it prints `wayland`, pick an
Xorg session at the login screen.

### How you open the menu

The interface is the same everywhere — an icon you click for a menu. Only the
mouse button differs, because each platform has its own convention:

| Platform | Open the menu | Extra |
| --- | --- | --- |
| macOS | click the `→` in the menu bar | keyboard shortcuts `s`, `i`, `q` |
| Linux | click the tray icon | — |
| Windows | **right**-click the tray icon | left-click toggles start/stop |

Windows reserves left-click on a tray icon for a default action, so it cannot be
made to open the menu; right-click is the standard Windows gesture. macOS and
Linux both open the menu on a plain click.

**macOS always uses the menu bar.** It never opens a window or a dialog on
startup, and the bundle ships no Tk at all.

### If your desktop has no usable tray

Some Linux setups cannot show a tray menu at all — GNOME ships without a tray
unless you add the *AppIndicator and KStatusNotifierItem Support* extension, and
pystray's bare X11 fallback can display an icon but no menu. Rather than start
invisibly, or show an icon that does nothing when clicked, Cursor Mover falls
back to a small window. Force either interface with `--ui tray` or `--ui window`.

## Install

### From a release

Grab your platform's file from the [Releases](https://github.com/iAaquibjawed/cursor-mover/releases)
page. Each download contains a `README.txt` with full instructions.

| Platform | File | Then |
| --- | --- | --- |
| macOS | `CursorMover-macOS.dmg` | Drag **CursorMover.app** to Applications, then grant Accessibility |
| Windows | `CursorMover-Windows.zip` | Extract and run `CursorMover.exe` |
| Linux | `CursorMover-Linux-x86_64.tar.gz` | Extract and run `./install.sh`, or just `./cursor-mover` |

Builds are **not** code-signed or notarized. macOS: right-click the app and
choose **Open**. Windows: click **More info** then **Run anyway** at the
SmartScreen prompt.

### From source

Requires Python 3.10+. On Debian/Ubuntu also `sudo apt install python3-tk`
(Fedora: `python3-tkinter`) for the dialogs.

```bash
git clone https://github.com/iAaquibjawed/cursor-mover.git
cd cursor-mover

python3 -m venv .venv && source .venv/bin/activate
pip install -e .

cursor-mover
```

Platform-specific dependencies are selected automatically: `rumps` on macOS,
`pystray` elsewhere.

## Usage

Click the icon in the menu bar (macOS) or system tray (Windows, Linux):

| Item | macOS shortcut | Description |
| --- | --- | --- |
| Start / Stop Movement | `s` | Toggle cursor movement |
| Change Interval… | `i` | Set the interval in seconds (10–3600) |
| About | — | Version and settings location |
| Quit | `q` | Stop movement and exit |

The menu also shows the current status, interval, and screen resolution. On
Windows and Linux, double-clicking the tray icon toggles movement.

Command line flags:

```bash
cursor-mover --start            # begin moving immediately
cursor-mover --interval 60      # override the saved interval
cursor-mover --ui window        # force a plain window instead of a tray icon
cursor-mover --verbose          # debug logging
```

### Where settings live

| Platform | Path |
| --- | --- |
| macOS | `~/Library/Application Support/CursorMover/settings.json` |
| Windows | `%APPDATA%\CursorMover\settings.json` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/cursor-mover/settings.json` |

## Permissions

Only macOS restricts pointer control. Grant **Accessibility** access:

**System Settings → Privacy & Security → Accessibility** → enable
**CursorMover** (or your terminal app, when running from source), then relaunch.

Windows needs nothing. Linux needs nothing beyond an X11 session.

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
src/cursor_mover/         Application package
  cli.py                  Arg parsing, platform guard, dependency wiring
  controller.py           All application logic - toolkit-free, heavily tested
  mover.py                Pointer movement engine - toolkit-free
  config.py               Settings validation and JSON persistence
  paths.py                Per-platform data directories
  scheduler.py            Timer abstraction (thread-based + test double)
  runloop.py              macOS run-loop timer (imports rumps)
  artwork.py              The icon, drawn procedurally
  icon.py                 Tray icon loading
  constants.py            Shared metadata and limits
  frontend/
    menubar.py            macOS menu bar view (rumps)
    tray.py               Windows/Linux tray view (pystray)
  systemui/
    applescript.py        macOS dialogs and notifications (osascript)
    tk.py                 Windows/Linux dialogs (Tkinter) and notifications
tests/                    pytest suite - no GUI toolkit required
packaging/                PyInstaller specs and per-OS build scripts
assets/                   Icon files, the design brief, and make_icns.sh
docs/                     Architecture, release, and per-platform install docs
.github/                  CI matrix, release automation, issue and PR templates
```

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before a non-trivial change.
The short version: **only `frontend/` may import a GUI toolkit**, all behaviour
lives in `controller.py`, and each platform's differences are isolated behind
the `Scheduler` and `SystemUI` protocols.

## Building and releasing

PyInstaller cannot cross-compile, so each artifact is built on its own OS:

```bash
make dmg                             # macOS  -> .app and .dmg
make linux                           # Linux  -> binary and .tar.gz
.\packaging\build_windows.ps1         # Windows -> .exe and .zip
```

Pushing a `v*` tag builds all three on GitHub Actions and publishes them to a
release. See [docs/RELEASING.md](docs/RELEASING.md) for the checklist and for
code signing and notarization.

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
