# Build Instructions for Random Cursor Mover

## 🛠️ Building Executables for All Platforms

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)
- All dependencies from `requirements.txt`

### Install Dependencies First

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## 🍎 Building for macOS

### On macOS:

```bash
chmod +x build.sh
./build.sh
```

This will create: `dist/CursorMover.app`

### Manually:

```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onedir \
            --add-data "README.md:." \
            --clean \
            cursor_mover.py
```

**Result:** A macOS application bundle that can be double-clicked.

## 🪟 Building for Windows

### On Windows:

Double-click `build.bat` or run:

```cmd
pyinstaller --name="CursorMover" ^
            --windowed ^
            --onefile ^
            --add-data "README.md;." ^
            --clean ^
            cursor_mover.py
```

**Result:** `dist/CursorMover.exe`

### Cross-platform (from macOS/Linux using Wine):

```bash
# Install Wine first
brew install wine-stable  # macOS
# or
sudo apt-get install wine  # Linux

# Build Windows executable
wine pyinstaller --name="CursorMover" --windowed --onefile cursor_mover.py
```

## 🐧 Building for Linux

### On Linux:

```bash
chmod +x build.sh
./build.sh
```

Or manually:

```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --clean \
            cursor_mover.py

chmod +x dist/CursorMover
```

**Result:** `dist/CursorMover` (executable)

## 📦 Cross-Platform Build Setup

### Using Docker (Recommended for cross-compilation):

Create a Dockerfile for each platform, or use GitHub Actions for automated builds.

### Using GitHub Actions:

Create `.github/workflows/build.yml`:

```yaml
name: Build All Platforms

on: [push, workflow_dispatch]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: pip install -r requirements.txt pyinstaller

    - name: Build
      run: |
        if [ "$RUNNER_OS" == "macOS" ]; then
          pyinstaller --name="CursorMover" --windowed --onedir cursor_mover.py
        elif [ "$RUNNER_OS" == "Linux" ]; then
          pyinstaller --name="CursorMover" --windowed --onefile cursor_mover.py
        else
          pyinstaller --name="CursorMover" --windowed --onefile cursor_mover.py
        fi

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: CursorMover-${{ runner.os }}
        path: dist/
```

## 🎯 Quick Development Build

For testing during development:

```bash
# Just run the Python script directly
python3 cursor_mover.py

# Or use the run script
./run.sh
```

## 📝 Build Optimization Tips

### Smaller Executable Size:

```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --strip \
            --noupx \
            cursor_mover.py
```

### Include/Exclude Modules:

```bash
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --exclude-module matplotlib \
            --exclude-module numpy \
            cursor_mover.py
```

### Custom Icons:

```bash
# macOS (.icns)
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --icon=icon.icns \
            cursor_mover.py

# Windows (.ico)
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --icon=icon.ico \
            cursor_mover.py
```

## 🔍 Troubleshooting Builds

### "ModuleNotFoundError"

Add hidden imports:
```bash
pyinstaller --hidden-import=MODULE_NAME cursor_mover.py
```

### "Large executable size"

Use `--onedir` instead of `--onefile`:
```bash
pyinstaller --name="CursorMover" --windowed --onedir cursor_mover.py
```

### macOS app won't run

Sign the app (for distribution):
```bash
codesign --force --deep --sign - dist/CursorMover.app
```

### Windows SmartScreen issues

Code signing certificate required for Windows. For personal use, users click "More info" → "Run anyway".

## ✅ Testing Builds

### macOS:

```bash
# Test the app bundle
open dist/CursorMover.app

# Or from terminal
dist/CursorMover.app/Contents/MacOS/CursorMover
```

### Windows:

```cmd
# Run from command line
dist\CursorMover.exe

# Or just double-click in Explorer
```

### Linux:

```bash
# Run the executable
./dist/CursorMover

# Or make it executable first
chmod +x dist/CursorMover
./dist/CursorMover
```

## 📦 Distributing Builds

### For macOS:

1. Build the app bundle
2. Zip it: `zip -r CursorMover-macOS.zip dist/CursorMover.app`
3. Optionally create DMG: `hdiutil create -volname CursorMover -srcfolder dist/CursorMover.app -ov -format UDZO CursorMover.dmg`

### For Windows:

1. Build the .exe
2. Zip it: `zip CursorMover-Windows.zip dist/CursorMover.exe`
3. Or use Inno Setup to create installer

### For Linux:

1. Build the executable
2. Tar it: `tar -czf CursorMover-Linux.tar.gz dist/CursorMover`
3. Or create .deb package

## 🚀 Automated Builds with GitHub Actions

See `.github/workflows/build.yml` example above for automated builds on every push.

## 📚 Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Cross-Platform Python Packaging](https://realpython.com/python-application-layouts/)

