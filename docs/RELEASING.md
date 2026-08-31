# Releasing

> [!IMPORTANT]
> The APT repository needs a one-time GPG setup before the first release.
> See [One-time setup: APT signing key](#one-time-setup-apt-signing-key) below.

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


---

## One-time setup: APT signing key

`apt` refuses an unsigned repository, so the `apt-repo` job needs a GPG key.
Do this once; every later release reuses it.

### 1. Generate a key

Use a dedicated key for package signing, not your personal one.

```bash
gpg --batch --quick-generate-key \
    "Cursor Mover Packaging <mallickaaquib@gmail.com>" \
    rsa4096 sign never
```

Note the key id:

```bash
gpg --list-secret-keys --keyid-format=long
```

### 2. Back it up somewhere safe

If you lose this key you cannot publish updates that existing users will
accept — they would have to re-add a new key by hand.

```bash
gpg --armor --export-secret-keys <KEY_ID> > cursor-mover-signing-key.asc
```

Store that file in a password manager, then delete it from disk.

### 3. Add it to GitHub

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
| --- | --- |
| `GPG_PRIVATE_KEY` | the full contents of `cursor-mover-signing-key.asc` |
| `GPG_PASSPHRASE` | the key's passphrase, or omit if it has none |

### 4. Enable GitHub Pages

**Settings → Pages → Build and deployment → Source: GitHub Actions**

The repository is then served at
`https://iaaquibjawed.github.io/cursor-mover/`.

### 5. Verify after the first release

On a Debian or Ubuntu machine:

```bash
sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://iaaquibjawed.github.io/cursor-mover/cursor-mover.asc \
  | sudo tee /etc/apt/keyrings/cursor-mover.asc > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/cursor-mover.asc] https://iaaquibjawed.github.io/cursor-mover ./" \
  | sudo tee /etc/apt/sources.list.d/cursor-mover.list > /dev/null

sudo apt update            # must not report a signature warning
apt policy cursor-mover    # should list the new version
sudo apt install cursor-mover
```

### Notes and limits

- The published repository holds **only the most recent** `.deb`. `apt upgrade`
  works because versions increase, but older versions are not installable via
  apt — they remain on the Releases page.
- The repository is **flat** (`... ./`), which is why the client line has no
  distribution or component. That is intentional: it needs no `dists/` tree and
  works across Debian, Ubuntu, and derivatives.
- Rebuilding locally: `make apt` produces `dist/apt/` using whatever secret key
  your gpg agent holds.
