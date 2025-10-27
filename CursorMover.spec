# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

a = Analysis(
    ['cursor_mover.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=[
        'pyautogui',
        'PIL._tkinter_finder',
        'PIL._webp',
        'numpy',
        'numpy.core',
        'numpy.lib.format',
        'numpy.random',
        'rubicon',
        'rubicon.objc',
        'Quartz',
        'AppKit',
        'Foundation',
        'CoreFoundation',
        'objc'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'scipy', 'PIL.Image.cms'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CursorMover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CursorMover',
)

app = BUNDLE(
    coll,
    name='CursorMover.app',
    icon=None,
    bundle_identifier='com.cursormover.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSUIElement': 'False',
        'NSHumanReadableCopyright': 'Copyright 2024',
        'CFBundleName': 'CursorMover',
        'CFBundleDisplayName': 'CursorMover',
        'CFBundleShortVersionString': '1.0.0',
        'NSRequiresAquaSystemAppearance': 'True',
    },
)
