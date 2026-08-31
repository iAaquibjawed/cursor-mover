# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`apt` installation for Linux.** A signed, flat APT repository is published to
  GitHub Pages on each release, so users add it once and then install and update
  with `sudo apt install cursor-mover` / `sudo apt upgrade`. Built by
  `packaging/build_apt_repo.sh`; requires the `GPG_PRIVATE_KEY` secret and Pages
  enabled — see [docs/RELEASING.md](docs/RELEASING.md).
- A proper Debian package (`packaging/build_deb.sh`) with dependency metadata, a
  desktop entry, an icon, machine-readable copyright, a Debian changelog, and
  postinst/postrm hooks that refresh the desktop and icon caches. Also
  installable standalone: `sudo apt install ./cursor-mover_2.0.0-1_amd64.deb`.
- The bare `CursorMover.exe` is now a release asset, so Windows users download
  and double-click one file instead of unzipping.
- Per-platform install instructions for running from source. The previous
  snippet used `source .venv/bin/activate`, which fails on Windows.
- Real vendored OS logos (`assets/platforms/`) with light and dark variants,
  replacing emoji stand-ins in the README.
- `make deb` and `make apt` targets. CI now builds the `.deb` on every run.

### Fixed
- `docs/install/macos.txt` documented a "⚙️ Change Interval" menu item; the gear
  was dropped from the real menu when the frontends were split.
- The README's Windows platform badge used `logo=windows`, which renders no icon
  at all — Simple Icons removed every Microsoft mark for trademark reasons.
- `docs/install/{macos,windows,linux}.txt` were unreachable from GitHub; they
  shipped only inside the release archives and are now linked from the README.

## [2.0.0]

### Added
- **Windows and Linux support.** The app now runs on macOS, Windows, and Linux
  from one codebase, with a `pystray` system tray frontend alongside the macOS
  `rumps` menu bar.
- `controller.py`, holding all application behaviour so it is shared by both
  frontends and testable without a GUI toolkit.
- `Scheduler` protocol with two implementations: the macOS run-loop timer
  (`runloop.py`) and a thread timer for Windows/Linux, plus a `ManualScheduler`
  test double so the suite never sleeps waiting for a tick.
- `SystemUI` protocol with an AppleScript implementation for macOS and a Tkinter
  one for Windows/Linux; notifications fall through the tray icon,
  `notify-send`, then logging.
- `paths.py`, resolving the per-platform data directory (Application Support,
  `%APPDATA%`, `$XDG_CONFIG_HOME`).
- A Tkinter window frontend (`frontend/window.py`) used automatically when the
  desktop cannot show a tray menu. Two cases: no tray backend at all (GNOME
  without the AppIndicator extension), which would leave the app running
  invisibly; and pystray's bare X11 backend, which sets `HAS_MENU = False` and
  would show an icon that does nothing when clicked. Adapted from the approach
  on the `cross-platform` branch, rebuilt on the shared controller.
- Wayland detection with a startup warning, since Wayland forbids applications
  from moving the pointer.
- `--interval`, `--start`, and `--ui {auto,tray,window}` command line flags.
- An optional dispatcher on `Controller`, so work raised on the timer thread is
  marshalled onto a frontend's event loop. `WindowFrontend` supplies Tkinter's
  `after`; without it, a failed move would touch widgets off the main thread.
- Windows `.ico` output, a Linux `.desktop` entry, a per-user Linux installer,
  PyInstaller specs and build scripts for all three platforms, and per-platform
  install documentation under `docs/install/`.
- CI now runs the suite on macOS, Windows, and Ubuntu, and the release workflow
  builds and publishes all three artifacts from one tag.
- 55 new tests (95 total) covering the controller, schedulers, paths, and the
  system UI factory.

### Changed
- The macOS frontend moved from `app.py` to `frontend/menubar.py` and is now a
  thin view: it renders `AppState` and forwards intent to the controller.
- `macos.py` moved to `systemui/applescript.py`.
- The icon geometry moved into the package as `artwork.py`, so the tray frontend
  and the file renderer share one source of truth. `assets/render_icon.py` is a
  shim.
- Dependencies are now platform-conditional: `rumps` only on macOS, `pystray`
  and `python-xlib` only elsewhere.
- The version is declared once, in `src/cursor_mover/__init__.py`; the
  PyInstaller specs read it from there instead of duplicating it.
- Build scripts renamed for clarity: `packaging/build_macos.sh`,
  `packaging/build_linux.sh`, `packaging/build_windows.ps1`, and specs
  `macos.spec`, `windows.spec`, `linux.spec`.

### Known limitations
- **Linux requires X11.** Wayland cannot be supported.
- GNOME needs an AppIndicator extension to show a tray icon; without it the app
  falls back to a window.
- Keyboard shortcuts remain macOS-only; pystray has no accelerator support.

## [1.1.0]

### Added
- Interval is now persisted to `~/Library/Application Support/CursorMover/settings.json`
  and restored on launch.
- `About` menu item showing the version and settings path.
- `cursor-mover` console entry point with `--version` and `--verbose` flags.
- Unit tests for interval validation, settings persistence, the movement engine,
  and AppleScript escaping, plus a GitHub Actions CI workflow.

### Changed
- Restructured into an installable `src/cursor_mover` package: `mover` (pointer
  logic), `config` (settings), `macos` (system dialogs), `app` (menu bar UI),
  `cli` (wiring).
- Movement is driven by a `rumps.Timer` on the main run loop instead of a
  background thread, so menu updates are no longer made off the main thread.
- The app bundle is now a proper menu bar agent: `LSUIElement` is `True` (no
  Dock icon) and the console window is disabled.
- Build scripts moved to `packaging/` and now fail loudly instead of silently
  producing a broken artifact.

### Fixed
- Invalid-interval and invalid-input alerts raised an AppleScript syntax error
  instead of showing a message, because `{{"OK"}}` was written in a plain
  (non-f) string.
- User text is escaped before being interpolated into AppleScript, so quotes no
  longer break — or inject into — the generated script.
- `rumps.alert` and menu-title updates are no longer called from a background
  thread when a cursor move fails.
- The app no longer forces light appearance via `NSRequiresAquaSystemAppearance`.

### Removed
- `build.bat`, `build_all.sh`, and the Windows/Linux branches of `build.sh`.
  They referenced spec files that were never in the repository and produced
  builds that could not work: the app depends on `rumps`, which is macOS-only.

## [1.0.0]

- Initial release: menu bar app, configurable interval, native notifications.
