# Releasing

## 1. Prepare

- [ ] Update the version in `pyproject.toml`, `src/cursor_mover/__init__.py`,
      and `packaging/CursorMover.spec` (all three must match).
- [ ] Move the `CHANGELOG.md` entries under the new version heading.
- [ ] `ruff check .` and `pytest` pass.

## 2. Build

```bash
pip install -e ".[build]"
./packaging/build_app.sh
./packaging/create_dmg.sh
```

Verify the artifact before shipping it:

```bash
open dist/CursorMover.app     # menu bar shows "→", no Dock icon
```

Check that Start prompts for Accessibility on a clean machine, the interval
dialog accepts and rejects input correctly, and the interval survives a relaunch.

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

```bash
git tag -a v1.1.0 -m "v1.1.0"
git push origin master --tags

gh release create v1.1.0 dist/CursorMover-macOS.dmg \
    --title "v1.1.0" --notes-file <(sed -n '/## \[1.1.0\]/,/## \[1.0.0\]/p' CHANGELOG.md)
```

## Known limitation

Cursor Mover is macOS-only because `rumps` wraps AppKit. There are no Windows or
Linux artifacts to publish. A port would reuse `cursor_mover.mover` behind a
different front end.
