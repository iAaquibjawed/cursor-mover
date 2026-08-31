#!/usr/bin/env bash
# Build dist/CursorMover.app with PyInstaller.
#
# Usage (from anywhere):  ./packaging/build_app.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
info()  { printf '\033[1;33m→\033[0m %s\n' "$1"; }
fail()  { printf '\033[0;31m✗\033[0m %s\n' "$1" >&2; exit 1; }

[[ "$(uname -s)" == "Darwin" ]] || fail "Cursor Mover can only be built on macOS."

if ! command -v pyinstaller >/dev/null 2>&1; then
    info "PyInstaller not found; installing…"
    python3 -m pip install --upgrade "pyinstaller>=6.6"
fi
green "PyInstaller $(pyinstaller --version)"

info "Cleaning previous build output…"
rm -rf build dist

info "Building CursorMover.app…"
pyinstaller --clean --noconfirm packaging/CursorMover.spec

[[ -d dist/CursorMover.app ]] || fail "Build finished but dist/CursorMover.app is missing."

# Ad-hoc signature. Replace with a Developer ID identity before distributing:
#   codesign --deep --force --options runtime --sign "Developer ID Application: …"
info "Applying an ad-hoc code signature…"
codesign --force --deep --sign - dist/CursorMover.app

green "Built dist/CursorMover.app ($(du -sh dist/CursorMover.app | cut -f1))"
echo
info "Try it:      open dist/CursorMover.app"
info "Package it:  ./packaging/create_dmg.sh"
