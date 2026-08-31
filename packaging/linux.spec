# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Linux CursorMover binary.

Run from the repository root:

    pyinstaller --clean --noconfirm packaging/linux.spec
"""

from pathlib import Path

REPO_ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(REPO_ROOT / "src" / "cursor_mover" / "__main__.py")],
    pathex=[str(REPO_ROOT / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[
        "cursor_mover",
        "cursor_mover.frontend.tray",
        "cursor_mover.frontend.window",
        "cursor_mover.systemui.tk",
        "pyautogui",
        # pystray picks a backend at import time based on the session. Name all
        # of them so PyInstaller ships whichever the user's desktop needs.
        "pystray",
        "pystray._appindicator",
        "pystray._gtk",
        "pystray._xorg",
        "gi",
        "Xlib",
        "Xlib.display",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "tkinter",
        "tkinter.messagebox",
        "tkinter.simpledialog",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pandas", "scipy", "pytest", "rumps"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="cursor-mover",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
