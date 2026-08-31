#!/usr/bin/env bash
# Build a single-file Linux binary plus a distributable tarball.
#
# Usage (from anywhere):  ./packaging/build_linux.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
info()  { printf '\033[1;33m→\033[0m %s\n' "$1"; }
fail()  { printf '\033[0;31m✗\033[0m %s\n' "$1" >&2; exit 1; }

[[ "$(uname -s)" == "Linux" ]] || fail "Linux binaries must be built on Linux."

if ! command -v pyinstaller >/dev/null 2>&1; then
    info "PyInstaller not found; installing…"
    python3 -m pip install --upgrade "pyinstaller>=6.6"
fi
green "PyInstaller $(pyinstaller --version)"

info "Cleaning previous build output…"
rm -rf build dist

info "Building cursor-mover…"
pyinstaller --clean --noconfirm packaging/linux.spec

[[ -f dist/cursor-mover ]] || fail "Build finished but dist/cursor-mover is missing."
chmod +x dist/cursor-mover

info "Staging the tarball…"
STAGE="dist/cursor-mover-linux"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp dist/cursor-mover "$STAGE/"
cp packaging/cursor-mover.desktop "$STAGE/"
cp assets/icon.png "$STAGE/cursor-mover.png"
cp docs/install/linux.txt "$STAGE/README.txt"
cp LICENSE "$STAGE/"
cp packaging/install_linux.sh "$STAGE/install.sh"
chmod +x "$STAGE/install.sh"

tar -czf dist/CursorMover-Linux-x86_64.tar.gz -C dist cursor-mover-linux
rm -rf "$STAGE"

green "Built dist/cursor-mover ($(du -h dist/cursor-mover | cut -f1))"
green "Built dist/CursorMover-Linux-x86_64.tar.gz"
echo
info "Try it:     ./dist/cursor-mover --verbose"
info "Install it: extract the tarball and run ./install.sh"
