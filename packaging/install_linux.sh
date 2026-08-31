#!/usr/bin/env bash
# Install Cursor Mover into the current user's home. No root required.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/512x512/apps"

mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR"

install -m 755 "$HERE/cursor-mover" "$BIN_DIR/cursor-mover"
install -m 644 "$HERE/cursor-mover.png" "$ICON_DIR/cursor-mover.png"
install -m 644 "$HERE/cursor-mover.desktop" "$APP_DIR/cursor-mover.desktop"

command -v update-desktop-database >/dev/null 2>&1 && \
    update-desktop-database "$APP_DIR" 2>/dev/null || true

printf '\033[0;32m✓\033[0m Installed to %s/cursor-mover\n' "$BIN_DIR"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) printf '\033[1;33m→\033[0m Add %s to your PATH to run `cursor-mover`.\n' "$BIN_DIR" ;;
esac

printf '\033[1;33m→\033[0m Launch it from your application menu, or run: cursor-mover\n'
