# Quick Start Guide

## 🚀 For Developers

### 1. Install Dependencies

```bash
# macOS/Linux
pip3 install -r requirements.txt

# Or run the setup script
python3 setup.py
```

### 2. Test the App

```bash
# Run directly
python3 cursor_mover.py

# Or use the run script
./run.sh
```

### 3. Build Executables

```bash
# macOS/Linux
./build.sh

# Windows
build.bat
```

## 👥 For End Users

### Download

Get the pre-built executable for your platform from GitHub releases.

### macOS

1. Download `CursorMover-macOS.zip`
2. Extract the zip file
3. Double-click `CursorMover.app`
4. If blocked: Right-click → Open

### Windows

1. Download `CursorMover-Windows.zip`
2. Extract and run `CursorMover.exe`
3. If blocked: Click "More info" → "Run anyway"

### Linux

1. Download `CursorMover-Linux.tar.gz`
2. Extract: `tar -xzf CursorMover-Linux.tar.gz`
3. Run: `chmod +x CursorMover && ./CursorMover`

## 🔐 First Time Setup (macOS)

macOS requires accessibility permissions:

1. System Settings → Privacy & Security → Accessibility
2. Click "+" and add "CursorMover" or "Terminal"
3. Enable the toggle

Or run the helper script:
```bash
python3 request_permissions.py
```

## 🎯 Using the App

1. Launch the application
2. Set your desired interval (default: 120 seconds)
3. Click "Start" to begin
4. Your cursor will move automatically
5. Click "Stop" to pause
6. Close the app to exit

## ❓ Troubleshooting

**"Could not control mouse"**
- macOS: Grant Accessibility permissions
- Windows: Run as Administrator
- Linux: Install xdotool

**App won't start**
- Check Python version: `python3 --version` (needs 3.8+)
- Install tkinter: `sudo apt-get install python3-tk`
- Check console for errors

**No cursor movement**
- Make sure "Start" is clicked and status shows "Active"
- Check interval is set to at least 10 seconds
- Verify permissions are granted

## 📚 More Info

- [Full README](README.md)
- [Build Instructions](BUILD_INSTRUCTIONS.md)
- [GitHub Release Guide](GITHUB_RELEASE_GUIDE.md)

