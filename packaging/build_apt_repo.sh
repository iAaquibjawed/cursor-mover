#!/usr/bin/env bash
# Assemble a signed, flat APT repository from the .deb files in dist/.
#
# Output goes to dist/apt/, ready to publish as a static site:
#     Packages, Packages.gz, Release, InRelease, cursor-mover.asc
#
# Requires a GPG secret key already imported into the running agent. In CI the
# key comes from the GPG_PRIVATE_KEY secret; see docs/RELEASING.md.
#
# Usage:  ./packaging/build_apt_repo.sh [signing-key-id]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

green() { printf '\033[0;32m✓\033[0m %s\n' "$1"; }
info()  { printf '\033[1;33m→\033[0m %s\n' "$1"; }
fail()  { printf '\033[0;31m✗\033[0m %s\n' "$1" >&2; exit 1; }

OUT="dist/apt"
ORIGIN="cursor-mover"
KEY_ID="${1:-${GPG_KEY_ID:-}}"

command -v dpkg-scanpackages >/dev/null 2>&1 || fail "dpkg-scanpackages not found. Install dpkg-dev."
command -v apt-ftparchive    >/dev/null 2>&1 || fail "apt-ftparchive not found. Install apt-utils."
command -v gpg               >/dev/null 2>&1 || fail "gpg not found."

shopt -s nullglob
DEBS=(dist/*.deb)
shopt -u nullglob
[[ ${#DEBS[@]} -gt 0 ]] || fail "No .deb files in dist/. Run ./packaging/build_deb.sh first."

rm -rf "$OUT"
mkdir -p "$OUT"
cp "${DEBS[@]}" "$OUT/"
info "Included $(printf '%s ' "${DEBS[@]##*/}")"

# A flat repository: metadata sits beside the packages, so clients use
#   deb [signed-by=...] https://<host>/<path> ./
info "Generating Packages index…"
( cd "$OUT" && dpkg-scanpackages --multiversion . /dev/null > Packages )
gzip -9kfn "$OUT/Packages"

info "Generating Release…"
apt-ftparchive \
    -o "APT::FTPArchive::Release::Origin=$ORIGIN" \
    -o "APT::FTPArchive::Release::Label=$ORIGIN" \
    -o "APT::FTPArchive::Release::Suite=stable" \
    -o "APT::FTPArchive::Release::Codename=stable" \
    -o "APT::FTPArchive::Release::Architectures=amd64" \
    -o "APT::FTPArchive::Release::Components=main" \
    -o "APT::FTPArchive::Release::Description=Cursor Mover releases" \
    release "$OUT" > "$OUT/Release"

# apt refuses an unsigned repository unless the user opts out per-source, so
# signing is mandatory, not optional.
if [[ -z "$KEY_ID" ]]; then
    KEY_ID="$(gpg --list-secret-keys --with-colons 2>/dev/null \
        | awk -F: '/^sec:/ {print $5; exit}')"
fi
[[ -n "$KEY_ID" ]] || fail "No GPG secret key found. Pass a key id or set GPG_KEY_ID."
info "Signing with key $KEY_ID"

GPG_OPTS=(--batch --yes --local-user "$KEY_ID" --digest-algo SHA512)
[[ -n "${GPG_PASSPHRASE:-}" ]] && GPG_OPTS+=(--pinentry-mode loopback --passphrase "$GPG_PASSPHRASE")

# InRelease is the inline-signed form modern apt prefers; Release.gpg is the
# detached form, kept for older clients.
gpg "${GPG_OPTS[@]}" --clearsign  -o "$OUT/InRelease"   "$OUT/Release"
gpg "${GPG_OPTS[@]}" --detach-sign --armor -o "$OUT/Release.gpg" "$OUT/Release"

# Publish the public key so users can trust the repo.
gpg --batch --yes --armor --export "$KEY_ID" > "$OUT/cursor-mover.asc"
[[ -s "$OUT/cursor-mover.asc" ]] || fail "Exported public key is empty."

green "APT repository built in $OUT/"
echo
info "Files:"
( cd "$OUT" && ls -1 | sed 's/^/    /' )
echo
info "Clients install with:"
cat <<'CLIENT'
    sudo install -d -m 0755 /etc/apt/keyrings
    curl -fsSL https://iaaquibjawed.github.io/cursor-mover/cursor-mover.asc \
      | sudo tee /etc/apt/keyrings/cursor-mover.asc > /dev/null
    echo "deb [signed-by=/etc/apt/keyrings/cursor-mover.asc] https://iaaquibjawed.github.io/cursor-mover ./" \
      | sudo tee /etc/apt/sources.list.d/cursor-mover.list > /dev/null
    sudo apt update && sudo apt install cursor-mover
CLIENT
