# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the CursorMover.app bundle.

Run from the repository root:

    pyinstaller --clean --noconfirm packaging/CursorMover.spec
"""

from pathlib import Path

REPO_ROOT = Path(SPECPATH).parent
ICON = REPO_ROOT / "assets" / "icon.icns"
VERSION = "1.1.0"

a = Analysis(
    [str(REPO_ROOT / "src" / "cursor_mover" / "__main__.py")],
    pathex=[str(REPO_ROOT / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[
        "cursor_mover",
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
    excludes=["matplotlib", "pandas", "scipy", "tkinter", "pytest"],
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
