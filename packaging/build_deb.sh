#!/usr/bin/env bash
# Build a Debian package from the PyInstaller binary.
#
# Produces dist/cursor-mover_<version>-1_amd64.deb, installable with:
#     sudo apt install ./cursor-mover_<version>-1_amd64.deb
#
# Usage (from anywhere, on Linux):  ./packaging/build_deb.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
info()  { printf '\033[1;33m→\033[0m %s\n' "$1"; }
fail()  { printf '\033[0;31m✗\033[0m %s\n' "$1" >&2; exit 1; }

[[ "$(uname -s)" == "Linux" ]] || fail "Debian packages must be built on Linux."
command -v dpkg-deb >/dev/null 2>&1 || fail "dpkg-deb not found. Install dpkg-dev."

PKG="cursor-mover"
ARCH="amd64"
# Debian revision. Bump only if a package is rebuilt without an upstream change.
REVISION="1"

VERSION="$(python3 -c "
import re, pathlib
src = pathlib.Path('src/cursor_mover/__init__.py').read_text()
print(re.search(r'__version__ = \"([^\"]+)\"', src).group(1))
")"
[[ -n "$VERSION" ]] || fail "Could not read __version__ from src/cursor_mover/__init__.py"
DEB_VERSION="${VERSION}-${REVISION}"

# Maintainer field. Change this if you would rather not publish that address.
MAINTAINER="Md Aaquib Jawed <mallickaaquib@gmail.com>"
HOMEPAGE="https://github.com/iAaquibjawed/cursor-mover"

if [[ ! -f dist/cursor-mover ]]; then
    info "dist/cursor-mover not found; building it first…"
    ./packaging/build_linux.sh
fi
[[ -f dist/cursor-mover ]] || fail "dist/cursor-mover is still missing."

STAGE="dist/deb/${PKG}_${DEB_VERSION}_${ARCH}"
rm -rf "dist/deb"
mkdir -p \
    "$STAGE/DEBIAN" \
    "$STAGE/usr/bin" \
    "$STAGE/usr/share/applications" \
    "$STAGE/usr/share/icons/hicolor/512x512/apps" \
    "$STAGE/usr/share/doc/$PKG"

info "Staging package tree…"
install -m 0755 dist/cursor-mover                 "$STAGE/usr/bin/cursor-mover"
install -m 0644 packaging/cursor-mover.desktop    "$STAGE/usr/share/applications/cursor-mover.desktop"
install -m 0644 assets/icon.png                   "$STAGE/usr/share/icons/hicolor/512x512/apps/cursor-mover.png"
install -m 0644 docs/install/linux.txt            "$STAGE/usr/share/doc/$PKG/README.txt"

# Debian wants an uncompressed size in KiB.
INSTALLED_SIZE="$(du -ks "$STAGE" | cut -f1)"

cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $DEB_VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: libc6 (>= 2.31)
Recommends: gir1.2-ayatanaappindicator3-0.1, libnotify-bin
Suggests: python3-tk
Installed-Size: $INSTALLED_SIZE
Maintainer: $MAINTAINER
Homepage: $HOMEPAGE
Description: Keep your computer awake by nudging the cursor
 Cursor Mover is a small tray application that moves the mouse pointer to a
 random position on a timer, so the machine never registers as idle. It shows
 an icon in the system tray with a menu to start, stop, and set the interval.
 .
 The binary is self-contained; no Python installation is required.
 .
 Requires an X11 / Xorg session. Wayland does not permit applications to move
 the pointer, so Cursor Mover cannot work under Wayland.
CONTROL

# Machine-readable copyright, per Debian policy.
cat > "$STAGE/usr/share/doc/$PKG/copyright" <<'COPYRIGHT'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: cursor-mover
Source: https://github.com/iAaquibjawed/cursor-mover

Files: *
Copyright: 2026 Md Aaquib Jawed
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
COPYRIGHT

# Debian changelog. Policy requires it gzipped at maximum compression.
cat > "$STAGE/usr/share/doc/$PKG/changelog.Debian" <<CHANGELOG
$PKG ($DEB_VERSION) stable; urgency=low

  * Release $VERSION. See $HOMEPAGE/blob/master/CHANGELOG.md

 -- $MAINTAINER  $(date -R)
CHANGELOG
gzip -9n "$STAGE/usr/share/doc/$PKG/changelog.Debian"

# Refresh the desktop database and icon cache after install/removal.
cat > "$STAGE/DEBIAN/postinst" <<'POSTINST'
#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    fi
fi
exit 0
POSTINST

cat > "$STAGE/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications || true
    fi
fi
exit 0
POSTRM

chmod 0755 "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"

info "Building the package…"
DEB="dist/${PKG}_${DEB_VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group --build "$STAGE" "$DEB"

green "Built $DEB ($(du -h "$DEB" | cut -f1))"
echo
info "Contents:"
dpkg-deb --contents "$DEB" | awk '{print "    " $6, $7, $8}'
echo
info "Verify:  dpkg-deb --info $DEB"
info "Install: sudo apt install ./$DEB"
if command -v lintian >/dev/null 2>&1; then
    info "Lintian:"
    lintian --no-tag-display-limit "$DEB" 2>&1 | sed 's/^/    /' || true
fi
