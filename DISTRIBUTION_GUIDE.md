# Distribution Guide for CursorMover

This guide explains how to prepare and distribute the CursorMover app to users.

## 📦 Building for Distribution

### Step 1: Build the App

```bash
./build.sh
```

This creates:
- `dist/CursorMover.app` - The macOS application bundle

### Step 2: Create a DMG

```bash
./create_dmg.sh
```

This creates:
- `dist/CursorMover-macOS.dmg` - A distribution-ready disk image

The DMG includes:
- CursorMover.app
- Applications folder shortcut (for easy installation)
- README with instructions

### Step 3: Test the DMG

Before sharing:
1. Mount the DMG
2. Copy CursorMover.app to Applications
3. Run it and verify it works
4. Test the full workflow including permissions

## 🚀 Distribution Methods

### Option 1: GitHub Releases (Recommended)

1. **Commit and push your code**
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git push origin main
   ```

2. **Create a release on GitHub**
   - Go to your repository on GitHub
   - Click "Releases" → "Draft a new release"
   - Tag: `v1.0.0`
   - Title: `CursorMover v1.0.0`
   - Description: Use the template below

3. **Upload the DMG**
   - Upload `CursorMover-macOS.dmg` to the release
   - Add release notes

4. **Publish the release**

### Option 2: Direct Download Link

Host the DMG file on:
- Your website
- Cloud storage (Google Drive, Dropbox, etc.)
- File sharing service

Share the download link with users.

### Option 3: Homebrew Cask (Advanced)

Create a Homebrew cask for easy installation:

1. Fork [homebrew-cask](https://github.com/Homebrew/homebrew-cask)
2. Create `Casks/cursormover.rb`
3. Submit a PR

## 📝 Release Notes Template

```markdown
# CursorMover v1.0.0

## What's New
- Initial release
- Move cursor at configurable intervals
- Clean GUI interface
- Works on macOS 10.14+

## Installation

1. Download CursorMover-macOS.dmg
2. Open the DMG
3. Drag CursorMover.app to Applications
4. Launch and grant accessibility permission

## Usage

1. Open CursorMover
2. Set your desired interval (default: 120 seconds)
3. Click "Start" to begin
4. Click "Stop" to pause

## Permissions

The app requires accessibility permission to move your cursor.
When you first run it and click "Start", macOS will prompt you to grant permission.

To manually grant permission:
1. System Settings → Privacy & Security → Accessibility
2. Enable CursorMover in the list

## Requirements

- macOS 10.14 or later
- Accessibility permission

## Download

- [CursorMover-macOS.dmg](path-to-dmg)
```

## 🔒 Code Signing (Optional but Recommended)

For users to trust your app:

1. **Get an Apple Developer account** ($99/year)
   - https://developer.apple.com

2. **Sign the app**
   ```bash
   codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" dist/CursorMover.app
   ```

3. **Notarize the app**
   ```bash
   xcrun notarytool submit dist/CursorMover.app --keychain-profile "notary" --wait
   ```

4. **Create DMG with signed app**
   ```bash
   ./create_dmg.sh
   ```

## 📊 File Sizes

Expected sizes:
- CursorMover.app: ~50-80 MB
- CursorMover-macOS.dmg: ~40-60 MB (compressed)

## 🧪 Testing Before Release

Test the DMG on:
- [ ] A clean macOS installation
- [ ] macOS 10.14
- [ ] macOS 12 (Monterey)
- [ ] macOS 13 (Ventura)
- [ ] macOS 14 (Sonoma)
- [ ] macOS 15 (Sequoia)

## 📋 Pre-Release Checklist

- [ ] Build app successfully with `./build.sh`
- [ ] Create DMG with `./create_dmg.sh`
- [ ] Test installation from DMG
- [ ] Test on fresh macOS system
- [ ] Verify permissions work
- [ ] Write release notes
- [ ] Update version numbers
- [ ] Create GitHub release
- [ ] Test download and installation

## 🐛 Common Issues

### "App is damaged" Error
- Not signed: Use `sudo xattr -cr` to remove quarantine
- Explain to users: Right-click → Open (first time)

### "App from unidentified developer"
- This is normal for unsigned apps
- Users need to: Right-click → Open (first time)
- Or: Get a Developer ID for signing

### Permission Issues
- Make sure the app clearly explains permission requirements
- Provide troubleshooting guide

## 📈 Tracking

After release:
- Monitor GitHub issues
- Track download counts
- Collect user feedback
- Prepare for updates

## 🌟 Future Improvements

Consider adding:
- Auto-updater
- Statistics/reporting
- Custom cursor movement patterns
- Scheduled start/stop times
- Multiple interval profiles

