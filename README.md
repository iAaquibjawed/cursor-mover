# Cursor Mover - Cross-Platform Desktop App

A desktop application that automatically moves your cursor to random positions on the screen at specified intervals. Perfect for keeping your computer active!

## 📦 Versions

This repository contains two versions:

### 1. macOS Version (Native Menu Bar)

**File:** `cursor_mover.py`

**Features:**
- 📍 Moves cursor to random screen positions automatically
- ⚙️ Configurable interval (minimum 10 seconds)
- 🔔 Native macOS notifications
- 🎨 Native menu bar interface with → icon
- ⌨️ Keyboard shortcuts (s, i, q)
- 🟢 Status indicators (Active/Inactive)

**Installation:**
```bash
pip install -r requirements.txt
python cursor_mover.py
```

**Build:**
```bash
./build.sh
./create_dmg.sh
```

### 2. Windows/Linux Version (GUI)

**File:** `cursor_mover_gui.py`

**Features:**
- 📍 Moves cursor to random screen positions automatically
- ⚙️ Configurable interval (minimum 10 seconds)
- 🖱️ Simple GUI window with Start/Stop buttons
- 💻 Works on Windows and Linux

**Installation:**
```bash
pip install -r requirements-gui.txt
python cursor_mover_gui.py
```

## Requirements

- Python 3.8+
- Accessibility/Input permission

## Usage

### macOS Version

1. Run: `python cursor_mover.py`
2. Look for → icon in menu bar
3. Right-click to access menu:
   - View status (🟢 Active / 🔴 Inactive)
   - Change interval
   - Start/Stop movement
   - View screen resolution
   - Quit

**Keyboard Shortcuts:**
- `s` - Start/Stop
- `i` - Change interval
- `q` - Quit

### Windows/Linux Version

1. Run: `python cursor_mover_gui.py`
2. A window will open
3. Enter interval (minimum 10 seconds)
4. Click "Start Movement"
5. Click "Stop" to stop or "Quit" to exit

## Building Executables

### macOS App Bundle

```bash
./build.sh
./create_dmg.sh
```

Result: `dist/CursorMover-macOS.dmg`

### Windows Executable

```bash
pyinstaller --name="CursorMover-Windows" --windowed --onefile cursor_mover_gui.py
```

Result: `dist/CursorMover-Windows.exe`

### Linux Executable

```bash
pyinstaller --name="CursorMover-Linux" --windowed --onefile cursor_mover_gui.py
chmod +x dist/CursorMover-Linux
```

Result: `dist/CursorMover-Linux`

## Permissions

### macOS
Go to: **System Settings** → **Privacy & Security** → **Accessibility**
Enable: Terminal, iTerm2, or your terminal application

### Windows
May require admin access for cursor control

### Linux
May require input permission configuration

## Distribution

Upload builds to GitHub Releases:
- `CursorMover-macOS.dmg` for macOS
- `CursorMover-Windows.exe` for Windows
- `CursorMover-Linux` for Linux

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first.
