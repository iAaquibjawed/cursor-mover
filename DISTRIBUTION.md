# How to Distribute Cursor Mover

## Current Status

This app is **macOS-only** (uses native macOS menu bar via `rumps`).

## Distribution Options

### Option 1: macOS App Bundle (Recommended)

**Build the app:**
```bash
./build.sh
```

**Create a DMG installer:**
```bash
./create_dmg.sh
```

**Result:** `dist/CursorMover-macOS.dmg`

**Share it:**
- Upload to GitHub Releases
- Share the download link
- Users can double-click to install

### Option 2: GitHub Repository

**Push to GitHub:**
```bash
git add .
git commit -m "Initial release - macOS menu bar cursor mover"
git push origin master
```

**Then create a release:**
1. Go to GitHub → Releases → "Create a new release"
2. Tag version: `v1.0.0`
3. Upload the DMG file
4. Add release notes

### Option 3: Source Code Distribution

Users can install and run from source:
```bash
git clone https://github.com/yourusername/cursor-mover.git
cd cursor-mover
pip install -r requirements.txt
python cursor_mover.py
```

## For Windows/Linux Users

**Current limitation:** The app uses macOS-specific libraries (`rumps`).

**Options for cross-platform:**

### Option A: Create Separate Versions
- Keep macOS version with `rumps`
- Create Windows/Linux version with `tkinter` or `pystray`
- Requires separate code for each platform

### Option B: Use Cross-Platform Library
- Replace `rumps` with `tkinter` (built into Python)
- Simple GUI window for all platforms
- Less "native" but works everywhere

### Option C: Minimal Command-Line Version
- Run without GUI on all platforms
- Use terminal commands to start/stop
- Smallest footprint

## Publishing Steps

1. **Test the app:**
   ```bash
   python cursor_mover.py
   ```

2. **Build the app:**
   ```bash
   ./build.sh
   ```
   This creates: `dist/CursorMover.app`

3. **Create DMG:**
   ```bash
   ./create_dmg.sh
   ```
   This creates: `dist/CursorMover-macOS.dmg`

4. **Publish to GitHub:**
   - Create a new repository on GitHub
   - Push your code
   - Go to Releases → Draft a new release
   - Upload the DMG file
   - Add release notes

5. **Share with users:**
   - Share the GitHub repo link
   - Or share direct DMG download link from releases

## What Users Need

**macOS users:**
- Download and open the DMG
- Drag to Applications folder
- Grant Accessibility permission when prompted

**From source:**
- Python 3.8+
- Install requirements: `pip install -r requirements.txt`
- Run: `python cursor_mover.py`

