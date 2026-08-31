# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the macOS CursorMover.app bundle.

Run from the repository root:

    pyinstaller --clean --noconfirm packaging/macos.spec
"""

import re
from pathlib import Path

REPO_ROOT = Path(SPECPATH).parent
ICON = REPO_ROOT / "assets" / "icon.icns"
def _package_version() -> str:
    """Read __version__ from the package without importing it."""
    init = REPO_ROOT / "src" / "cursor_mover" / "__init__.py"
    match = re.search(r'__version__ = "([^"]+)"', init.read_text(encoding="utf-8"))
    if match is None:
        raise SystemExit("Could not find __version__ in src/cursor_mover/__init__.py")
    return match.group(1)


VERSION = _package_version()

a = Analysis(
    [str(REPO_ROOT / "src" / "cursor_mover" / "__main__.py")],
    pathex=[str(REPO_ROOT / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[
        "cursor_mover",
        "cursor_mover.frontend.menubar",
        "cursor_mover.runloop",
        "cursor_mover.systemui.applescript",
        "pyautogui",
        "rumps",
        "objc",
        "AppKit",
        "Foundation",
        "CoreFoundation",
        "Quartz",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # The macOS build uses AppleScript dialogs, so Tk and pystray are dead weight.
    excludes=["matplotlib", "pandas", "scipy", "tkinter", "pytest", "pystray"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CursorMover",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # A menu bar agent has no terminal; a console window would be visible noise.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="CursorMover",
)

app = BUNDLE(
    coll,
    name="CursorMover.app",
    icon=str(ICON) if ICON.is_file() else None,
    bundle_identifier="com.cursormover.app",
    info_plist={
        "CFBundleName": "CursorMover",
        "CFBundleDisplayName": "Cursor Mover",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "NSHumanReadableCopyright": "Copyright © 2026 Md Aaquib Jawed. MIT Licensed.",
        "NSHighResolutionCapable": True,
        # Menu bar agent: no Dock icon, no app switcher entry.
        "LSUIElement": True,
        # Follow the user's light/dark appearance rather than forcing Aqua.
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "11.0",
        "NSAppleEventsUsageDescription":
            "Cursor Mover uses AppleScript to show dialogs and notifications.",
    },
)
