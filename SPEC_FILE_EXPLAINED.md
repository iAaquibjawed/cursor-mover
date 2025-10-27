# PyInstaller .spec File Explained in Detail

## 📋 What is a .spec File?

The `.spec` file is PyInstaller's configuration file that controls how your Python app is packaged into an executable. Think of it as a blueprint for building your app.

---

## 🏗️ The Complete Spec File Structure

Your `CursorMover.spec` file has 4 main sections:

```
1. a = Analysis()      - Analyze dependencies
2. pyz = PYZ()         - Create compressed Python bytecode
3. exe = EXE()         - Create the executable
4. app = BUNDLE()      - Package as macOS .app (macOS only)
```

---

## 📖 Section-by-Section Breakdown

### **PART 1: Configuration at Top**

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
block_cipher = None
```

**What it does:**
- Sets file encoding (UTF-8)
- Imports needed modules
- `block_cipher = None` means no encryption (for speed)

---

### **PART 2: Analysis - `a = Analysis()`**

This is the **most important section**. It analyzes your code and finds all dependencies.

```python
a = Analysis(
    ['cursor_mover.py'],  # ← Your main Python file
    pathex=[],            # ← Additional search paths (empty)
    binaries=[],          # ← External binary files (none)
    datas=[('README.md', '.')],  # ← Non-Python files to include

    # HIDDEN IMPORTS: PyInstaller sometimes misses imports
    hiddenimports=[
        'pyautogui',      # ← Explicitly include pyautogui
        'numpy',          # ← And numpy
        'Quartz',         # ← macOS framework for graphics
        'AppKit',         # ← macOS UI framework
        # ... more hidden imports
    ],

    hookspath=[],         # ← Custom PyInstaller hooks
    hooksconfig={},       # ← Hook configuration
    runtime_hooks=[],     # ← Code to run before main app
    excludes=[...],       # ← Libraries to EXCLUDE (save space)

    # Encryption and packaging options
    cipher=block_cipher,
    noarchive=False,
)
```

**Key Parameters Explained:**

#### `['cursor_mover.py']`
- Your main Python file
- PyInstaller starts here and traces all imports

#### `pathex=[]`
- Additional Python paths to search
- Empty = use default

#### `binaries=[]`
- External binary libraries (.dylib, .so, .dll)
- Usually auto-detected

#### `datas=[('README.md', '.')]`
- Non-Python files to include
- Format: `(source, destination)`
- Example: Copy README.md to the same location in the bundle

#### `hiddenimports=[...]`
- **Critical!** Lists modules PyInstaller might miss
- Why needed? Import detection sometimes fails
- These are explicitly included

**For your app:**
```python
'pyautogui'      # Cursor control library
'numpy'          # Math operations
'Quartz'         # macOS drawing API
'AppKit'         # macOS UI components
'Foundation'     # macOS core framework
'PIL._tkinter_finder'  # Pillow (image library)
```

#### `excludes=['matplotlib', 'pandas', 'scipy']`
- Libraries to **skip** to reduce size
- Your app doesn't need these
- Saves 10-20 MB

---

### **PART 3: Python ZIP - `pyz = PYZ()`**

```python
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
```

**What it does:**
- Compresses Python bytecode into a `.pyz` file
- Makes the app smaller
- Includes all `.pyc` files

**Why?**
- Python files are compiled to bytecode
- This compresses them
- Reduces file size

---

### **PART 4: Executable - `exe = EXE()`**

Creates the actual executable file.

```python
exe = EXE(
    pyz,                    # ← Compiled Python code
    a.scripts,              # ← Your scripts
    [],                     # ← Bootloader scripts
    exclude_binaries=True,   # ← Keep binaries separate (for macOS .app)
    name='CursorMover',     # ← Name of executable
    debug=False,            # ← No debug symbols (smaller)
    bootloader_ignore_signals=False,  # ← Handle Ctrl+C
    strip=False,            # ← Don't strip symbols
    upx=False,              # ← Don't compress with UPX (can be unstable)
    console=True,           # ← Show console window (for debugging)
    disable_windowed_traceback=False,  # ← Show errors in window
    argv_emulation=False,    # ← macOS file association
    codesign_identity=None,  # ← Code signing identity (None = unsigned)
    entitlements_file=None,  # ← macOS entitlements (None = default)
)
```

**Key Parameters:**

#### `exclude_binaries=True`
- Keep DLLs/dylibs separate from executable
- Required for macOS .app bundles

#### `console=True`
- Show console window
- Set to `False` for windowed apps
- Currently `True` for debugging

#### `codesign_identity=None`
- For signing the app (requires Apple Developer account)
- None = unsigned (users see security warning)

#### `name='CursorMover'`
- Name of the executable
- Will be: `CursorMover` (Mac/Linux) or `CursorMover.exe` (Windows)

---

### **PART 5: Collect - `coll = COLLECT()`**

```python
coll = COLLECT(
    exe,          # ← The executable
    a.binaries,   # ← Binary libraries
    a.zipfiles,   # ← ZIP files
    a.datas,       # ← Data files (README.md, etc.)
    strip=False,   # ← Don't strip debug symbols
    upx=False,     # ← Don't compress
    upx_exclude=[],
    name='CursorMover',
)
```

**What it does:**
- Collects everything into a folder
- Creates `dist/CursorMover/` directory
- Contains executable + all dependencies

---

### **PART 6: Bundle (macOS only) - `app = BUNDLE()`**

**Only for macOS!** Creates a `.app` bundle.

```python
app = BUNDLE(
    coll,   # ← The collected files
    name='CursorMover.app',  # ← App bundle name
    icon=None, # ← App icon file (.icns)
    bundle_identifier='com.cursormover.app',  # ← Unique ID

    # macOS Info.plist entries
    info_plist={
        'NSHighResolutionCapable': 'True',  # ← Retina display support
        'LSUIElement': 'False',              # ← Don't hide from Dock
        'NSHumanReadableCopyright': 'Copyright 2024',
        'CFBundleName': 'CursorMover',      # ← App name
        'CFBundleDisplayName': 'CursorMover', # ← Display name
        'CFBundleShortVersionString': '1.0.0', # ← Version
        'NSRequiresAquaSystemAppearance': 'True',  # ← Light mode
    },
)
```

**What it does:**
- Creates proper macOS `.app` structure
- Sets metadata (version, name, copyright)
- Makes it behave like a native Mac app

**Bundle Structure:**
```
CursorMover.app/
├── Contents/
│   ├── Info.plist          (metadata)
│   ├── MacOS/
│   │   └── CursorMover     (executable)
│   ├── Resources/          (icons, etc.)
│   └── Frameworks/         (linked libraries)
```

---

## 🎯 How PyInstaller Uses This File

### When you run:
```bash
pyinstaller CursorMover.spec
```

### PyInstaller does:
1. **Analysis** - Reads spec, analyzes code
2. **Bundle** - Includes Python + libraries
3. **Collect** - Gathers everything
4. **Bundle** (macOS) - Creates .app
5. **Output** - `dist/CursorMover.app`

---

## 🔧 Common Customizations

### 1. Add an Icon
```python
icon='path/to/icon.icns'  # macOS
icon='path/to/icon.ico'  # Windows
```

### 2. Remove Console Window
```python
console=False  # Hide console
```

### 3. Code Sign (macOS)
```python
codesign_identity='Developer ID Application: Your Name (TEAM_ID)'
```

### 4. Include More Files
```python
datas=[
    ('config.json', '.'),
    ('assets/', 'assets/'),
    ('README.md', '.'),
]
```

### 5. Exclude Libraries (Smaller Size)
```python
excludes=['matplotlib', 'pandas', 'scipy', 'jupyter']
```

---

## 📊 File Size Impact

**Your current app: ~25 MB**

**Why so big?**
```
Python runtime:     10 MB
pyautogui:           2 MB
Pillow:              3 MB
numpy:               8 MB
tkinter:            1 MB
Other:              1 MB
─────────────────────────
Total:             25 MB
```

**Can you make it smaller?**
- Compress with UPX: `upx=True` (can break some apps)
- Exclude more: More items in `excludes`
- Use Python standalone (smaller Python version)

---

## 💡 Platform-Specific Specs

### macOS (`CursorMover.spec`)
- Has `app = BUNDLE()` section
- Creates `.app` bundle
- Uses macOS frameworks (Quartz, AppKit)

### Windows (`CursorMover-windows.spec`)
- No `app = BUNDLE()` section
- Creates `.exe` file
- Uses Windows-specific imports

### Linux (`CursorMover-linux.spec`)
- No `app = BUNDLE()` section
- Creates executable
- Uses Linux-specific imports (Xlib, etc.)

---

## 🎓 Key Takeaways

1. **Analysis** section is most critical - controls what gets included
2. **hiddenimports** are crucial for libraries like pyautogui
3. **excludes** can save significant space
4. **console** setting controls whether window shows
5. Each platform needs different spec file

---

## ✅ Summary

The spec file is your blueprint for building executables:

```
Analysis → Find all dependencies
   ↓
PYZ     → Compress Python bytecode
   ↓
EXE     → Create executable
   ↓
COLLECT → Gather all files
   ↓
BUNDLE  → Package as .app (macOS)
   ↓
Your executable is ready!
```

**You can modify any section to customize the build!**

