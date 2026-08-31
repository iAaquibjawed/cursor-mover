# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Windows CursorMover.exe.

Run from the repository root:

    pyinstaller --clean --noconfirm packaging/windows.spec
"""

import re
from pathlib import Path

REPO_ROOT = Path(SPECPATH).parent
ICON = REPO_ROOT / "assets" / "icon.ico"
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
        "cursor_mover.frontend.tray",
        "cursor_mover.frontend.window",
        "cursor_mover.systemui.tk",
        "pyautogui",
        # pystray resolves its backend at import time; name it so PyInstaller
        # does not prune the win32 implementation.
        "pystray",
        "pystray._win32",
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
    name="CursorMover",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # A tray app has no terminal; a console window would be visible noise.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON) if ICON.is_file() else None,
    version=None,
)
