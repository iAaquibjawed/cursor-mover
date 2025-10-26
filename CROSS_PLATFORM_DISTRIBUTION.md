# Cross-Platform Distribution Guide

This guide explains how to build and distribute CursorMover for macOS, Windows, and Linux.

## 📦 Current Setup

You now have:
- ✅ macOS spec file: `CursorMover.spec`
- ✅ Linux spec file: `CursorMover-linux.spec`
- ✅ Windows spec file: `CursorMover-windows.spec`
- ✅ Multi-platform build script: `build_all.sh`

## 🖥️ Building for Different Platforms

### macOS (Current Platform)

You already built this! Your output is:
```
dist/CursorMover-macOS.dmg (25 MB)
```

To rebuild:
```bash
./build.sh          # Build app
./create_dmg.sh      # Create DMG
```

### Linux Build

**Option A: Build on a Linux Machine**
```bash
# On a Linux system
./build_all.sh
# Output: dist/CursorMover and dist/CursorMover-Linux.tar.gz
```

**Option B: Use Docker (Recommended for non-Linux systems)**
```bash
# Build Linux version using Docker
docker run --rm -v "$PWD":/src -w /src python:3.13 bash -c "
  pip install pyinstaller pyautogui pillow numpy tkinter &&
  pyinstaller --clean --noconfirm CursorMover-linux.spec
"
```

**Option C: Use GitHub Actions (See below)**

### Windows Build

**Option A: Build on Windows**
```powershell
# On Windows
pip install pyinstaller pyautogui pillow numpy
pyinstaller --clean --noconfirm CursorMover-windows.spec
```

**Option B: Use GitHub Actions (See below)**

## 🚀 Automated Builds with GitHub Actions

Create `.github/workflows/build.yml`:

```yaml
name: Build CursorMover

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install pyinstaller pyautogui pillow numpy

      - name: Install system dependencies (Linux)
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y python3-tk xdotool

      - name: Build macOS
        if: runner.os == 'macOS'
        run: |
          pyinstaller --clean --noconfirm CursorMover.spec
          ./create_dmg.sh

      - name: Build Linux
        if: runner.os == 'Linux'
        run: |
          pyinstaller --clean --noconfirm CursorMover-linux.spec
          tar -czf CursorMover-Linux.tar.gz -C dist CursorMover README.txt

      - name: Build Windows
        if: runner.os == 'Windows'
        run: |
          pyinstaller --clean --noconfirm CursorMover-windows.spec

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: CursorMover-${{ matrix.os }}
          path: dist/*
```

## 📋 Platform Requirements

### macOS
- Python 3.8+
- pyautogui, Pillow, numpy, tkinter
- PyInstaller
- Accessibility permission required

**Distribution:**
- File: CursorMover-macOS.dmg
- Size: ~25 MB
- Users: Drag to Applications, launch, grant permission

### Linux
- Python 3.8+
- pyautogui, Pillow, numpy, tkinter
- xdotool (for some distributions)
- PyInstaller
- X11 permissions

**Install dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk xdotool

# Fedora
sudo dnf install python3-tk xdotool

# Arch Linux
sudo pacman -S tk xdotool
```

**Distribution:**
- File: CursorMover-Linux.tar.gz
- Size: ~15-20 MB
- Users: Extract and run `./CursorMover`

### Windows
- Python 3.8+
- pyautogui, Pillow, numpy, tkinter
- PyInstaller
- Administrator privileges (for installation)

**Distribution:**
- File: CursorMover-Windows.zip or CursorMover.exe
- Size: ~20-30 MB
- Users: Extract and run CursorMover.exe (may need to allow in Windows Defender)

## 🎯 Recommended Distribution Setup

### 1. GitHub Releases (Best for All Platforms)

**For each release:**

```bash
# On macOS
./build.sh && ./create_dmg.sh
# Upload: CursorMover-macOS.dmg

# On Linux (or via Docker/GitHub Actions)
pyinstaller CursorMover-linux.spec
tar -czf CursorMover-Linux.tar.gz dist/CursorMover
# Upload: CursorMover-Linux.tar.gz

# On Windows
pyinstaller CursorMover-windows.spec
# Upload: CursorMover.exe or CursorMover-Windows.zip
```

### 2. Release Notes Template

```markdown
# CursorMover v1.0.0

Cross-platform cursor movement tool

## Downloads

- **macOS**: [CursorMover-macOS.dmg](link-to-dmg) (25 MB)
- **Linux**: [CursorMover-Linux.tar.gz](link-to-tar) (20 MB)
- **Windows**: [CursorMover.exe](link-to-exe) (30 MB)

## Installation

### macOS
1. Download CursorMover-macOS.dmg
2. Open and drag to Applications
3. Launch and grant accessibility permission

### Linux
1. Download CursorMover-Linux.tar.gz
2. Extract: `tar -xzf CursorMover-Linux.tar.gz`
3. Run: `./CursorMover`
4. Install xdotool if needed: `sudo apt-get install xdotool`

### Windows
1. Download CursorMover.exe
2. Extract (if zipped)
3. Run CursorMover.exe
4. Allow if Windows Defender blocks it
```

## 🔧 Current Files for Each Platform

| Platform | Spec File | Output File | Status |
|----------|-----------|-------------|---------|
| macOS | CursorMover.spec | CursorMover-macOS.dmg | ✅ Ready |
| Linux | CursorMover-linux.spec | CursorMover-Linux.tar.gz | ⚠️ Need to build |
| Windows | CursorMover-windows.spec | CursorMover.exe | ⚠️ Need to build |

## 🚀 Quick Commands

```bash
# Build for current platform
./build.sh

# Create DMG (macOS only)
./create_dmg.sh

# Build all platforms (requires Docker/GitHub Actions)
./build_all.sh
```

## 📝 Next Steps

1. **For macOS**: You already have the DMG ready to share ✅

2. **For Linux**:
   - Set up a Linux environment (VM, Docker, or remote server)
   - Run: `pyinstaller CursorMover-linux.spec`
   - Create tarball: `tar -czf CursorMover-Linux.tar.gz dist/CursorMover`

3. **For Windows**:
   - Set up a Windows environment (VM or real machine)
   - Run: `pyinstaller CursorMover-windows.spec`
   - Zip the result: `zip CursorMover-Windows.zip dist/CursorMover.exe`

4. **For Automatic Builds**:
   - Set up GitHub Actions (see workflow above)
   - Push tags to trigger builds
   - Artifacts are uploaded automatically

## 💡 Tips

- Use GitHub Actions for automated cross-platform builds
- Docker can build Linux version on macOS
- Windows build must be done on Windows
- Test each platform before releasing
- Consider code signing for macOS (optional but recommended)

