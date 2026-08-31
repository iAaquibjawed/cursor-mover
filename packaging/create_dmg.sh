#!/usr/bin/env bash
# Package dist/CursorMover.app into a distributable DMG.
#
# Usage (from anywhere):  ./packaging/create_dmg.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

APP_NAME="CursorMover"
APP_PATH="dist/${APP_NAME}.app"
DMG_PATH="dist/${APP_NAME}-macOS.dmg"
STAGING_DIR="dist/.dmg-staging"

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
info()  { printf '\033[1;33m→\033[0m %s\n' "$1"; }
fail()  { printf '\033[0;31m✗\033[0m %s\n' "$1" >&2; exit 1; }

[[ -d "$APP_PATH" ]] || fail "$APP_PATH not found. Build it first: ./packaging/build_macos.sh"

rm -f "$DMG_PATH"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

info "Staging bundle…"
cp -R "$APP_PATH" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"
cp docs/install/macos.txt "$STAGING_DIR/README.txt"

info "Creating disk image…"
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov -format UDZO \
    "$DMG_PATH" >/dev/null

rm -rf "$STAGING_DIR"

green "Created $DMG_PATH ($(du -h "$DMG_PATH" | cut -f1))"
echo
info "Attach it to a GitHub release, or share the file directly."
