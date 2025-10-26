# Simple Distribution Guide

## 🎯 TL;DR - What Users Get

### macOS Users
```
File: CursorMover-macOS.dmg
What they do:
1. Download .dmg file
2. Open it (mounts like a CD)
3. Drag app to Applications folder
4. Done!
```

### Windows Users
```
File: CursorMover.exe (or CursorMover-Windows.zip)
What they do:
1. Download .exe file
2. Extract from ZIP if needed
3. Double-click to run
4. Done! (No installation needed)
```

---

## 📊 File Types Comparison

| Feature | macOS (.dmg) | Windows (.exe) |
|---------|--------------|---------------|
| **File Type** | Disk Image | Executable |
| **Size** | ~25 MB | ~30 MB |
| **Installation** | Drag to Applications | Run directly |
| **Portable** | No (needs installation) | Yes (runs anywhere) |
| **Uninstall** | Delete from Applications | Delete the file |

---

## 🚀 What YOU Need To Do

### macOS (✅ DONE!)
```
Already created: dist/CursorMover-macOS.dmg
Just upload this file to share!
```

### Windows (Need to create)
```
1. Find a Windows machine or VM
2. Install Python + PyInstaller
3. Run: pyinstaller CursorMover-windows.spec
4. Get: dist/CursorMover.exe
5. Zip it with README: CursorMover-Windows.zip
6. Upload to share
```

---

## 📦 Your Distribution Strategy

### Option 1: Direct File Sharing (Current approach)

**macOS:**
```
✅ dist/CursorMover-macOS.dmg
   → Users download and install
```

**Windows:**
```
⚠️ Need to build: CursorMover.exe
   → Users download and run
```

### Option 2: GitHub Releases (Recommended)

Create releases with both files:
```
Release v1.0.0
├── CursorMover-macOS.dmg      ✅ Ready
└── CursorMover-Windows.zip    ⚠️ Need to build
```

---

## 🔧 Quick Commands

### Check what you have:
```bash
ls -lh dist/
# You should see: CursorMover-macOS.dmg
```

### macOS (DONE):
```bash
open dist/CursorMover-macOS.dmg
# Verify it works
```

### Windows (Need Windows machine):
```powershell
# On Windows:
pyinstaller CursorMover-windows.spec
Compress-Archive dist/CursorMover.exe CursorMover-Windows.zip
```

---

## 📝 What To Tell Users

### For macOS Users:
```
"Download CursorMover-macOS.dmg, open it, and drag CursorMover.app to Applications"
```

### For Windows Users:
```
"Download CursorMover-Windows.zip, extract, and run CursorMover.exe"
```

**That's it! Simple.**

---

## 💡 Key Differences

**DMG (macOS):**
- ❌ NOT an installer
- ✅ Disk image containing the app
- User manually installs by dragging
- More user-friendly presentation

**EXE (Windows):**
- ✅ Runs directly (portable)
- ✅ No installation needed
- User just runs the file
- Simpler for users

**Both accomplish the same goal: Get the app to users!**

