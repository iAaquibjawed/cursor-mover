# CursorMover Setup Guide

## Quick Start

### 1. Open the App
```bash
open dist/CursorMover.app
```

### 2. Grant Accessibility Permission

When you first run the app, macOS will need to grant accessibility permission. Here's how:

**Option A: Use the In-App Instructions**
- The app will show instructions if permissions aren't granted
- Follow the dialog to open System Settings

**Option B: Manual Setup**
1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security** → **Accessibility**
3. Click the **"+"** button (or lock to unlock first)
4. Add **CursorMover** or **Terminal** to the list
5. Enable the toggle next to it

**Option C: Trigger Permission Dialog**
1. When the app opens, click the **"Start"** button
2. macOS will show a permission dialog
3. Click **"Open System Settings"** or **"Settings"**
4. Enable the toggle in System Settings
5. Click **"Start"** again

### 3. Use the App

1. Set your desired interval (in seconds) - default is 120 seconds
2. Click **"Start"** to begin
3. The cursor will move automatically after the interval
4. Click **"Stop"** to pause

## Troubleshooting

### App won't start
- Make sure you downloaded the .app file (not the folder)
- Right-click and select "Open" if macOS blocks it

### Cursor not moving
- Check that the status shows "Active" after clicking Start
- Verify accessibility permissions are granted
- Make sure the interval is at least 10 seconds

### App not in Accessibility list
- Try clicking "Start" once - this triggers the permission request
- The app appears in the list after it attempts to control the mouse

## Testing from Command Line

To see debug output:
```bash
/Users/sammalik/Desktop/xyz/cursor_mover_app/dist/CursorMover.app/Contents/MacOS/CursorMover
```

## Permissions Details

The app needs accessibility permission to:
- Detect cursor position
- Move the cursor to random positions

This permission is required by macOS for security reasons.

