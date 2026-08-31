#!/usr/bin/env bash
# Convert a 1024x1024 PNG into the icon.icns the app bundle uses.
#
# Usage:  ./assets/make_icns.sh [path/to/icon-1024.png]
set -euo pipefail

ASSETS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${1:-$ASSETS_DIR/icon.png}"
ICONSET="$ASSETS_DIR/icon.iconset"

[[ -f "$SOURCE" ]] || {
    echo "✗ $SOURCE not found." >&2
    echo "  Export a 1024x1024 PNG from assets/icon.svg first, or pass a path." >&2
    exit 1
}

rm -rf "$ICONSET"
mkdir -p "$ICONSET"

# macOS expects these exact names inside a .iconset directory.
for size in 16 32 128 256 512; do
    sips -z "$size" "$size" "$SOURCE" \
        --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    sips -z $((size * 2)) $((size * 2)) "$SOURCE" \
        --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done

iconutil --convert icns "$ICONSET" --output "$ASSETS_DIR/icon.icns"
rm -rf "$ICONSET"

echo "✓ Wrote $ASSETS_DIR/icon.icns"
echo "  Rebuild to pick it up: ./packaging/build_app.sh"
