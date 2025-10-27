# Cursor Mover - macOS Menu Bar App

A macOS menu bar application that automatically moves your cursor to random positions on the screen at specified intervals. Perfect for keeping your computer active!

## Features

- 📍 Moves cursor to random screen positions automatically
- ⚙️ Configurable interval (minimum 10 seconds)
- 🔔 Native macOS notifications
- 🎨 Clean menu bar interface with status indicators
- 🔐 Requires Accessibility permission

## Installation

### Requirements
- macOS
- Python 3.8+
- Accessibility permission

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cursor-mover.git
cd cursor-mover
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python cursor_mover.py
```

## Usage

1. Start the app - it will appear in your menu bar with a → icon
2. Grant Accessibility permission when prompted
3. Right-click the menu bar icon to:
   - View current status
   - Change interval (default: 11 seconds)
   - Start/Stop cursor movement
   - View screen resolution
   - Quit

### Keyboard Shortcuts

- `s` - Start/Stop movement
- `i` - Change interval
- `q` - Quit

## Building a Standalone App

To create a macOS app bundle:

```bash
./build.sh
```

The app will be created in `dist/CursorMover.app`

To create a DMG installer:

```bash
./create_dmg.sh
```

## Permissions

Cursor Mover needs Accessibility permission to control your cursor:
1. Go to: **System Settings** → **Privacy & Security** → **Accessibility**
2. Enable your terminal application (Terminal, iTerm2, etc.)

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first.
