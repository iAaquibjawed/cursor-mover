# Random Cursor Mover - Desktop App

A cross-platform desktop application that automatically moves your cursor to random positions on the screen at specified intervals. Perfect for keeping your computer active!

## 🌟 Features

- ✅ Moves cursor to random screen positions
- ✅ Configurable interval (10 seconds to 1 hour)
- ✅ Simple, intuitive GUI
- ✅ Cross-platform (macOS, Windows, Linux)
- ✅ No installation required (standalone executable)
- ✅ System tray compatible (optional)
- ✅ Lightweight and fast

## 📦 Distribution

### For Users (Ready to Run)

Download the executable for your platform:

- **macOS**: `CursorMover.app` - Double-click to run
- **Windows**: `CursorMover.exe` - Double-click to run
- **Linux**: `CursorMover` - Make executable with `chmod +x CursorMover`

**No Python installation needed!** Everything is bundled.

### For Developers (Build from Source)

1. **Install Python 3.8+** and pip
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python cursor_mover.py
   ```

## 🛠️ Building Executables (PyInstaller)

### macOS

```bash
# Install PyInstaller
pip install pyinstaller

# Build macOS app
pyinstaller --name="CursorMover" \
            --windowed \
            --onedir \
            --icon=icon.icns \
            cursor_mover.py

# Result will be in dist/CursorMover.app
```

### Windows

```bash
# Build Windows executable
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --icon=icon.ico \
            cursor_mover.py

# Result will be in dist/CursorMover.exe
```

### Linux

```bash
# Build Linux executable
pyinstaller --name="CursorMover" \
            --windowed \
            --onefile \
            --icon=icon.png \
            cursor_mover.py

# Result will be in dist/CursorMover
chmod +x dist/CursorMover
```

## 🚀 Quick Start

### Running the Built Executable

**macOS:**
1. Download `CursorMover.app`
2. Double-click to open
3. If macOS blocks it: Right-click → Open (first time only)

**Windows:**
1. Download `CursorMover.exe`
2. Double-click to run
3. If Windows SmartScreen blocks: Click "More info" → "Run anyway"

**Linux:**
```bash
chmod +x CursorMover
./CursorMover
```

### Using the App

1. **Launch the application**
2. **Set interval** (default: 120 seconds)
3. **Click "Start"** to begin cursor movement
4. **Click "Stop"** to pause
5. **Close the app** to exit

## 🔐 Permissions Required

### macOS

**Accessibility Permission is Required:**

1. System Settings → Privacy & Security → Accessibility
2. Click "+" to add CursorMover
3. Enable the toggle for CursorMover

Alternatively:
- Use the included `request_permissions.py` script

### Windows

No additional permissions needed (as Administrator).

### Linux

May require:
```bash
sudo apt-get install xdotool  # For some distributions
```

## 📋 Requirements

### For End Users

- ✅ **macOS**: macOS 10.14 or later
- ✅ **Windows**: Windows 10 or later
- ✅ **Linux**: Most modern distributions
- ✅ No Python installation needed!

### For Developers

- Python 3.8+
- pyautogui
- Pillow
- tkinter (usually pre-installed with Python)
- PyInstaller (for building executables)

## 🎨 Screenshots

The app features:
- Clean, modern interface
- Real-time status indicator
- Easy Start/Stop controls
- Customizable intervals
- Screen size display

## 🔧 Troubleshooting

### "Could not control mouse"

**macOS:**
- Grant Accessibility permissions in System Settings
- Restart the app after granting permissions

**Windows:**
- Run as Administrator
- Check antivirus isn't blocking

**Linux:**
- Install xdotool: `sudo apt-get install xdotool`

### "App won't start"

**macOS:**
- Right-click app → Open (bypasses Gatekeeper)
- Check Console.app for errors

**Windows:**
- Check Windows Defender
- Try running as Administrator

**Linux:**
- Check Python is installed: `python3 --version`
- Install tkinter: `sudo apt-get install python3-tk`

### "No cursor movement"

- Check interval is set (minimum 10 seconds)
- Make sure "Start" button is clicked
- Check status shows "Active"
- Verify accessibility permissions (macOS)

## 📁 Project Structure

```
cursor_mover_app/
├── cursor_mover.py      # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── build.sh            # Build script
├── setup.py            # Optional setup script
└── icon files          # App icons
```

## 🚀 Building for All Platforms

Run the build script:

```bash
# Build for current platform
./build.sh

# Or build specifically:
./build.sh macos
./build.sh windows
./build.sh linux
```

## 📊 Distribution Checklist

- [ ] Build executables for all platforms
- [ ] Test on each platform
- [ ] Check permissions work
- [ ] Create release notes
- [ ] Upload to GitHub releases
- [ ] Provide installation instructions
- [ ] Create demo video (optional)

## 🎯 Use Cases

- Prevent computer from sleeping
- Keep remote sessions active
- Simulate user activity
- Test screen recording software
- Prevent timeouts in various applications

## ⚖️ License

MIT License - Free to use and modify

## 🤝 Contributing

Contributions welcome! Fork and create a pull request.

## 📝 Changelog

### Version 1.0.0 (Initial Release)
- Basic cursor movement
- GUI interface
- Configurable intervals
- Cross-platform support
- Standalone executables

## 💡 Tips

- Set interval to 120 seconds (2 minutes) for most use cases
- Lower intervals (30-60 seconds) for more frequent activity
- Keep app running in background for continuous movement
- Check "Active" status to confirm it's running

## 🆘 Support

For issues or questions:
- GitHub Issues
- Check troubleshooting section
- Review logs in console

---

**Enjoy keeping your computer active!** 🖥️✨

