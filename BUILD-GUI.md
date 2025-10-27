# Building Cross-Platform Cursor Mover

This repo contains two versions:

## 1. macOS Version (Native Menu Bar)

**File:** `cursor_mover.py`
**Dependencies:** `requirements.txt` (includes rumps)

**Features:**
- Native macOS menu bar icon
- Keyboard shortcuts
- Native notifications

**Build:**
```bash
./build.sh
```

## 2. Windows/Linux Version (GUI)

**File:** `cursor_mover_gui.py`
**Dependencies:** `requirements-gui.txt` (no rumps)

**Features:**
- Simple GUI window
- Start/Stop buttons
- Configurable interval
- Works on Windows and Linux

**Install dependencies:**
```bash
pip install -r requirements-gui.txt
```

**Run:**
```bash
python cursor_mover_gui.py
```

**Build for Windows:**
```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            cursor_mover_gui.py
```

**Build for Linux:**
```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            cursor_mover_gui.py
```

## Distribution Strategy

### Option 1: Separate Repositories
- Create `cursor-mover-macos` for macOS version
- Create `cursor-mover-gui` for Windows/Linux version

### Option 2: Single Repository (Recommended)
- Main branch has both versions
- GitHub releases has:
  - `CursorMover-macOS.dmg` (macOS)
  - `CursorMover-Windows.exe` (Windows)
  - `CursorMover-Linux` (Linux)

## Files in This Repo

**macOS version:**
- `cursor_mover.py` - Native menu bar app
- `requirements.txt` - Dependencies (includes rumps)
- `CursorMover.spec` - PyInstaller spec for macOS
- `build.sh` - macOS build script
- `create_dmg.sh` - DMG creator

**Cross-platform version:**
- `cursor_mover_gui.py` - Simple GUI app
- `requirements-gui.txt` - Dependencies (tkinter built-in)

## Building All Platforms

**macOS:**
```bash
./build.sh
./create_dmg.sh
```

**Windows:**
```bash
pyinstaller --name="CursorMover-Windows" --windowed --onefile cursor_mover_gui.py
```

**Linux:**
```bash
pyinstaller --name="CursorMover-Linux" --windowed --onefile cursor_mover_gui.py
```

