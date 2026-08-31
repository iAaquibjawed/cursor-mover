# Releasing

## 1. Prepare

- [ ] Update the version in `src/cursor_mover/__init__.py` and
      `pyproject.toml`. The PyInstaller specs read it from `__init__.py`, so
      there is nothing else to change.
- [ ] Move the `CHANGELOG.md` entries under the new version heading.
- [ ] `ruff check .` and `pytest` pass.

## 2. Build

PyInstaller cannot cross-compile, so each artifact is built on its own OS. In
practice you push the tag and let CI do all three; build locally only to debug.

```bash
pip install -e ".[build]"

./packaging/build_macos.sh && ./packaging/create_dmg.sh   # on macOS
./packaging/build_linux.sh                                # on Linux
.\packaging\build_windows.ps1                             # on Windows
```

Verify each artifact before shipping:

| Platform | Check |
| --- | --- |
| macOS | `open dist/CursorMover.app` — menu bar shows `→`, no Dock icon |
| Windows | run `dist\CursorMover.exe` — tray icon appears, no console window |
| Linux | `./dist/cursor-mover --verbose` on an **X11** session — tray icon appears |

On every platform confirm: the interval dialog accepts a valid number and
rejects garbage, the interval survives a relaunch, and Quit stops movement.
On macOS also confirm Start prompts for Accessibility on a clean machine.

## 3. Sign and notarize (optional but recommended)

Without this, users see a Gatekeeper warning on first launch.

```bash
codesign --deep --force --options runtime \
    --sign "Developer ID Application: YOUR NAME (TEAMID)" \
    dist/CursorMover.app

xcrun notarytool submit dist/CursorMover-macOS.dmg \
    --keychain-profile "AC_PASSWORD" --wait

xcrun stapler staple dist/CursorMover-macOS.dmg
```

## 4. Publish

Pushing the tag is all that is required — `release.yml` verifies the tag matches
`cursor_mover.__version__`, builds all three platforms in parallel, and attaches
the artifacts to a generated release.

```bash
git tag -a v2.0.0 -m "v2.0.0"
git push origin master --tags
```

If a build fails, fix it and re-run the workflow manually from the Actions tab
(it accepts the tag as an input) rather than re-tagging.

## 5. Verify the release

- [ ] All three artifacts are attached: `.dmg`, `.zip`, `.tar.gz`
- [ ] Download one and confirm it launches on a machine that has never run it

## Known limitations to keep in the notes

- Builds are not code-signed or notarized, so macOS and Windows both show a
  warning on first launch.
- Linux requires an X11 / Xorg session; Wayland forbids pointer control.
- The Linux build is x86_64 only.
