# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open-source project scaffolding: issue and pull request templates, a tagged
  release workflow, Dependabot, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `docs/ARCHITECTURE.md`, a `Makefile`, `.editorconfig`, `.gitattributes`, and
  an optional pre-commit configuration.
- `assets/render_icon.py`, which renders the icon with a real alpha channel.
  The macOS SVG rasterisers flatten output onto opaque white, which left a white
  square behind the icon.

### Changed
- Consolidated the artwork on `assets/icon.png` as the single canonical logo.

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
