<div align="center">

<img src="assets/icon.png" alt="" width="132" height="132">

# Cursor Mover

**Keep your computer awake by nudging the cursor — nothing else.**

A tiny tray app that moves your pointer to a random position every few seconds,
so your machine never registers as idle. No window. No taskbar button. Just an
icon you click for a menu.

[![CI](https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml/badge.svg)](https://github.com/iAaquibjawed/cursor-mover/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/iAaquibjawed/cursor-mover?sort=semver&color=blue)](https://github.com/iAaquibjawed/cursor-mover/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/iAaquibjawed/cursor-mover/total?color=success)](https://github.com/iAaquibjawed/cursor-mover/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![macOS](https://img.shields.io/badge/macOS-11%2B-000000?logo=apple&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2B-0078D6?logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-X11-FCC624?logo=linux&logoColor=black)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)

[**Download**](#-download) · [Usage](#-usage) · [How it works](#-how-it-works) · [FAQ](#-faq) · [Contributing](CONTRIBUTING.md)

</div>

---

## 📦 Download

Grab your platform's file from the [**latest release**](https://github.com/iAaquibjawed/cursor-mover/releases/latest).
Each download includes a `README.txt` with full instructions.

| Platform | File | Then |
| :--- | :--- | :--- |
| 🍎 **macOS** 11+ | `CursorMover-macOS.dmg` | Drag **CursorMover.app** to Applications → grant Accessibility |
| 🪟 **Windows** 10+ | `CursorMover-Windows.zip` | Extract → run `CursorMover.exe` |
| 🐧 **Linux** (X11, x86_64) | `CursorMover-Linux-x86_64.tar.gz` | Extract → `./install.sh`, or just `./cursor-mover` |

> [!NOTE]
> Builds are **not** code-signed or notarized, so the OS will warn you once.
> **macOS:** right-click the app → **Open**. **Windows:** **More info** → **Run anyway**.

<sub>Prefer to run from source? See [Install from source](#install-from-source).</sub>

---

## ✨ Features

|  |  |
| :--- | :--- |
| 🎯 **Random, not robotic** | Each move picks a fresh random point on screen |
| ⏱️ **Your interval** | Anywhere from 10 seconds to 1 hour, remembered between launches |
| 👻 **Genuinely invisible** | No Dock icon, no taskbar button, no app-switcher entry |
| 🔔 **Native notifications** | Notification Center, Windows toasts, `notify-send` |
| 📦 **One file, no Python** | Self-contained build per platform |
| 🧩 **One codebase** | All three platforms share the same tested core |

---

## 🖱️ What it looks like

An icon in the menu bar or system tray. Click it:

```
┌─────────────────────────────────┐
│  Status: 🟢 Active              │
├─────────────────────────────────┤
│  Interval: 30s                  │
│  Change Interval…           ⌘I  │
├─────────────────────────────────┤
│  ⏸ Stop Movement            ⌘S  │
├─────────────────────────────────┤
│  Screen: 1512×982               │
│  About Cursor Mover 2.0.0       │
├─────────────────────────────────┤
│  Quit                       ⌘Q  │
└─────────────────────────────────┘
```

<!-- TODO: replace the block above with a real screenshot.
     macOS: open the menu, then press Cmd+Shift+4 and drag over it.
     Save as docs/screenshot.png and swap in:
     <img src="docs/screenshot.png" alt="The Cursor Mover menu" width="320"> -->

### Opening the menu

Same interface everywhere; only the mouse button differs, because each platform
has its own convention.

| Platform | Open the menu | Bonus |
| :--- | :--- | :--- |
| 🍎 macOS | **click** the `→` in the menu bar | keyboard shortcuts `s` · `i` · `q` |
| 🐧 Linux | **click** the tray icon | — |
| 🪟 Windows | **right**-click the tray icon | left-click toggles start/stop |

<sub>Windows reserves left-click on a tray icon for a default action and offers no
way to open a menu programmatically, so right-click is the standard gesture there.</sub>

---

## 🚀 Usage

Click the icon, press **Start**. That's it.

```bash
cursor-mover                    # launch normally
cursor-mover --start            # launch and begin moving immediately
cursor-mover --interval 60      # override the saved interval
cursor-mover --ui window        # force a plain window instead of a tray icon
cursor-mover --verbose          # debug logging
```

<details>
<summary><b>Where your settings live</b></summary>

<br>

Your interval persists across launches in the platform's conventional location:

| Platform | Path |
| :--- | :--- |
| macOS | `~/Library/Application Support/CursorMover/settings.json` |
| Windows | `%APPDATA%\CursorMover\settings.json` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/cursor-mover/settings.json` |

A missing, unreadable, or corrupt file falls back to defaults rather than
preventing the app from starting.

</details>

<details>
<summary><b>Starting it automatically at login</b></summary>

<br>

**macOS** — System Settings → General → Login Items → **+** → CursorMover.app

**Windows** — press `Win`+`R`, enter `shell:startup`, and put a shortcut to
`CursorMover.exe` in the folder that opens. Add `--start` to the shortcut's
Target to have it running on boot.

**Linux**

```bash
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/cursor-mover.desktop ~/.config/autostart/
```

Append `--start` to the `Exec=` line to have it running on boot.

</details>

---

## 🔐 Permissions

Only macOS restricts pointer control:

**System Settings → Privacy & Security → Accessibility** → enable **CursorMover**
(or your terminal, if running from source), then relaunch the app.

Windows and Linux need nothing.

---

## 🐧 Linux: read this first

> [!IMPORTANT]
> **Cursor Mover requires an X11 / Xorg session.** Wayland deliberately forbids
> applications from moving the pointer, and there is no workaround. Check with:
>
> ```bash
> echo $XDG_SESSION_TYPE     # want: x11
> ```
>
> If it prints `wayland`, log out and choose an Xorg session at the login screen.
> The app detects Wayland and warns at startup rather than failing silently.

<details>
<summary><b>No tray icon? Your desktop may not have one</b></summary>

<br>

GNOME ships without a system tray unless you install the
**AppIndicator and KStatusNotifierItem Support** extension. KDE, XFCE, Cinnamon,
MATE, and Budgie all have one built in.

Where no tray menu is possible, Cursor Mover opens a **small window** instead —
so you are never left with a process you cannot quit, or an icon that does
nothing when clicked. Choose explicitly with `--ui tray` or `--ui window`.

Dialogs need Tkinter, which is a separate package on most distributions:

```bash
sudo apt install python3-tk        # Debian, Ubuntu
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

<sub>Only needed when running from source — the bundled binary includes it.</sub>

</details>

---

## 🧠 How it works

All behaviour lives in a **toolkit-free core**; each platform is a thin view over
it. Adding a platform means implementing three small protocols, not touching the
logic.

| Concern | 🍎 macOS | 🪟 Windows | 🐧 Linux |
| :--- | :--- | :--- | :--- |
| **View** | menu bar (`rumps`) | tray (`pystray`) | tray (`pystray`) |
| **Dialogs** | AppleScript | Tkinter | Tkinter |
| **Timer** | Cocoa run loop | thread | thread |
| **Settings** | Application Support | `%APPDATA%` | `$XDG_CONFIG_HOME` |

```
frontend/  ─┐
            ├─→  controller.py  ─→  mover.py · config.py · scheduler.py · systemui/
            │    (all behaviour)     (no GUI toolkit, 100% unit tested)
  the only ─┘
  toolkit
  importers
```

📖 **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** covers the design decisions,
the threading rules, and the platform constraints in full.

---

## 🛠️ Development

### Install from source

Requires Python 3.10+.

```bash
git clone https://github.com/iAaquibjawed/cursor-mover.git
cd cursor-mover

python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,build]"

cursor-mover
```

Platform dependencies resolve automatically — `rumps` on macOS, `pystray`
elsewhere.

### Common tasks

```bash
make check      # lint, format check, and tests — everything CI runs
make test       # tests with coverage
make format     # apply formatting and safe lint fixes
make run        # launch from source with verbose logging
make icons      # regenerate every icon format
make help       # list every target
```

<details>
<summary><b>Project layout</b></summary>

<br>

```
src/cursor_mover/
├── cli.py               Arg parsing, platform guard, dependency wiring
├── controller.py        All application logic — toolkit-free, heavily tested
├── mover.py             Pointer movement engine — toolkit-free
├── config.py            Settings validation and JSON persistence
├── paths.py             Per-platform data directories
├── scheduler.py         Timer abstraction (thread-based + test double)
├── runloop.py           macOS run-loop timer
├── artwork.py           The icon, drawn procedurally
├── icon.py              Tray icon loading
├── constants.py         Shared metadata and limits
├── frontend/
│   ├── menubar.py       macOS menu bar view (rumps)
│   ├── tray.py          Windows/Linux tray view (pystray)
│   └── window.py        Tkinter window — fallback where no tray exists
└── systemui/
    ├── applescript.py   macOS dialogs and notifications (osascript)
    └── tk.py            Windows/Linux dialogs and notifications

tests/        pytest suite — imports no GUI toolkit, runs anywhere
packaging/    PyInstaller specs and per-OS build scripts
assets/       Icon files, the design brief, and make_icns.sh
docs/         Architecture, release, and per-platform install docs
```

**The one rule:** only `frontend/` may import a GUI toolkit. That is what keeps
the rest testable in CI on all three operating systems.

</details>

### Building

PyInstaller cannot cross-compile, so each artifact is built on its own OS:

```bash
make dmg                        # macOS   → .app and .dmg
make linux                      # Linux   → binary and .tar.gz
.\packaging\build_windows.ps1   # Windows → .exe and .zip
```

Pushing a `v*` tag builds all three on GitHub Actions and publishes them.
See [docs/RELEASING.md](docs/RELEASING.md).

---

## ❓ FAQ

<details>
<summary><b>Does this work on Wayland?</b></summary>

<br>

No, and it cannot. Wayland's security model prevents any application from moving
the pointer. Use an X11 / Xorg session.

</details>

<details>
<summary><b>Will it interfere while I'm working?</b></summary>

<br>

It will — it moves your real cursor. That is the entire mechanism. Stop it from
the menu when you need the pointer to stay put.

</details>

<details>
<summary><b>Why does the cursor jump instead of drifting?</b></summary>

<br>

Each move glides to a random point over 0.25 seconds. Random positions are
harder for idle detection to dismiss than a jiggle in place.

</details>

<details>
<summary><b>Why is the minimum interval 10 seconds?</b></summary>

<br>

Below that, the pointer becomes genuinely unusable. Idle timeouts are measured
in minutes, so a short interval buys nothing.

</details>

<details>
<summary><b>The app is unsigned — is that safe?</b></summary>

<br>

Signing requires a paid Apple Developer account and a Windows code-signing
certificate. The source is here in full and CI builds every release from it, so
you can read what you are running or
[build it yourself](#building) in one command.

</details>

<details>
<summary><b>Can I use this to look active in a chat app?</b></summary>

<br>

Mechanically, yes — that is what preventing idle does. Whether it is acceptable
is between you and whoever set that policy.

</details>

---

## 🤝 Contributing

Issues and pull requests are welcome. Start with
**[CONTRIBUTING.md](CONTRIBUTING.md)**, and read
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) if you are touching more than one
module.

| | |
| :--- | :--- |
| 🐛 [Report a bug](https://github.com/iAaquibjawed/cursor-mover/issues/new?template=bug_report.yml) | Something broken? |
| 💡 [Request a feature](https://github.com/iAaquibjawed/cursor-mover/issues/new?template=feature_request.yml) | Ideas welcome |
| 🔒 [Security policy](SECURITY.md) | Report vulnerabilities privately, **not** in an issue |
| 📜 [Changelog](CHANGELOG.md) | What changed, and when |
| 🤗 [Code of Conduct](CODE_OF_CONDUCT.md) | Be decent to people |

<details>
<summary><b>Design notes</b></summary>

<br>

The icon is drawn in code by
[`artwork.py`](src/cursor_mover/artwork.py) — it is the single source of truth
for the artwork and also supplies the tray icon at runtime.

[`assets/LOGO_BRIEF.md`](assets/LOGO_BRIEF.md) has the full design brief, exact
colour values, and a ready-to-paste image-generator prompt if you want to
improve it. The current icon is a working draft.

</details>

---

## 📄 License

[MIT](LICENSE) © Md Aaquib Jawed

<div align="center">
<sub>If Cursor Mover is useful to you, a ⭐ helps other people find it.</sub>
</div>
