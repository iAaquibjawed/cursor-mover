#!/bin/bash
# Quick test script for CursorMover

echo "=== CursorMover Test Script ==="
echo ""
echo "This will:"
echo "1. Launch the app"
echo "2. Open System Settings to Accessibility"
echo "3. Show you how to grant permission"
echo ""
read -p "Press Enter to continue..."

# Kill any existing instance
pkill -f CursorMover 2>/dev/null || true
sleep 0.5

# Launch the app
echo "Launching CursorMover.app..."
open /Users/sammalik/Desktop/xyz/cursor_mover_app/dist/CursorMover.app

# Wait a moment for the app to trigger permission request
sleep 2

echo ""
echo "✓ App launched!"
echo ""
echo "NEXT STEPS:"
echo "1. If you see a macOS permission dialog, click 'Open System Settings'"
echo "2. OR manually open: System Settings → Privacy & Security → Accessibility"
echo "3. Look for 'CursorMover' in the list"
echo "4. Enable the toggle"
echo "5. Return to the CursorMover window and click 'Start'"
echo ""
echo "Opening System Settings now..."
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

echo ""
echo "After granting permission, click 'Start' in the CursorMover window"
echo "The cursor should move after the interval (default: 120 seconds)"

