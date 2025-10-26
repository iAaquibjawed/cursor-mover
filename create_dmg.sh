#!/bin/bash
# Create a DMG for distribution

set -e

echo "=== Creating DMG for CursorMover ==="
echo ""

APP_NAME="CursorMover"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}-macOS.dmg"
DMG_PATH="dist/${DMG_NAME}"

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: ${APP_PATH} not found!"
    echo "Please build the app first: ./build.sh"
    exit 1
fi

# Clean up old DMG
if [ -f "$DMG_PATH" ]; then
    echo "Removing old DMG..."
    rm "$DMG_PATH"
fi

# Create temporary DMG directory
TEMP_DIR="dist/dmg_build"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy app to temp directory
cp -R "$APP_PATH" "$TEMP_DIR/"

# Create Applications symlink
ln -s /Applications "$TEMP_DIR/Applications"

# Add README
cat > "$TEMP_DIR/README.txt" << 'EOF'
CursorMover - Random Cursor Movement Tool
==========================================

INSTALLATION:
1. Drag CursorMover.app to Applications folder
2. Double-click to launch
3. Grant accessibility permission when prompted
4. Click "Start" to begin

PERMISSIONS:
The app needs accessibility permission to move your cursor.
When you first run it and click "Start", macOS will ask for permission.

USAGE:
1. Launch CursorMover
2. Set your desired interval (default: 120 seconds)
3. Click "Start"
4. The cursor will move automatically after each interval
5. Click "Stop" to pause

TROUBLESHOOTING:
- If the cursor doesn't move: Check System Settings → Privacy & Security → Accessibility
- Make sure CursorMover is enabled in Accessibility
- Restart the app after granting permissions

For more information, visit: https://github.com/yourusername/cursor-mover
EOF

# Create the DMG
echo "Creating DMG..."
hdiutil create -volname "$APP_NAME" -srcfolder "$TEMP_DIR" -ov -format UDZO "$DMG_PATH"

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "✓ DMG created successfully: $DMG_PATH"
echo ""
echo "To distribute:"
echo "1. Upload $DMG_PATH to GitHub releases"
echo "2. Or share it via your preferred method"
echo ""
du -h "$DMG_PATH"

