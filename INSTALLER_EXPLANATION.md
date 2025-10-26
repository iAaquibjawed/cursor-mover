# Installer File Types Explained

## 📦 macOS: DMG (Disk Image)

**What is a DMG?**
- DMG = **Disk Image** file (like a virtual USB drive)
- `.dmg` extension
- macOS native format
- Similar to ISO files on other systems

**How it works:**
1. User downloads `CursorMover-macOS.dmg`
2. Double-click to "mount" (open) it
3. A window appears with the app and Applications folder
4. User drags app to Applications
5. Unmount (eject) the DMG
6. The app is now installed!

**Already created:**
```
dist/CursorMover-macOS.dmg (25 MB) ✅ READY
```

**You can share this file directly!**

---

## 🪟 Windows: EXE (Executable)

**What is an EXE?**
- EXE = **Executable** file
- `.exe` extension
- Windows executable that runs the app directly
- No installation needed (portable)

**Two types of Windows distribution:**

### Option 1: Portable EXE (Simplest - What we'll create)
- Single `.exe` file that runs directly
- No installer, no installation
- User just runs the file
- Similar to DMG concept but simpler

### Option 2: Installer Package (Advanced)
- Uses tools like NSIS, Inno Setup, or WiX
- Creates installer with Start Menu entries, shortcuts
- More professional but more complex

**We'll use Option 1 (Portable EXE)**

---

## 📊 Comparison

| Platform | File Type | Extension | Size | Installation |
|----------|-----------|-----------|------|---------------|
| **macOS** | DMG | `.dmg` | 25 MB | Drag to Applications |
| **Windows** | EXE | `.exe` | 30 MB | Just run the file |

---

## 🎯 What Users Do

### macOS Users:
```
1. Download CursorMover-macOS.dmg
2. Double-click to open
3. Drag CursorMover.app to Applications
4. Launch from Applications folder
5. Grant accessibility permission
```

### Windows Users:
```
1. Download CursorMover.exe
2. Extract if it's in a zip file
3. Run CursorMover.exe directly
4. Grant permission if Windows asks
```

**Windows is simpler!** No installation needed.

---

## 🔧 How To Create Each

### macOS DMG (✅ Already done!)
```bash
./build.sh              # Build the app
./create_dmg.sh          # Create DMG
# Output: dist/CursorMover-macOS.dmg
```

### Windows EXE (Need to do this)
```powershell
# On a Windows machine
pip install pyinstaller pyautogui pillow numpy
pyinstaller CursorMover-windows.spec
# Output: dist/CursorMover.exe
```

---

## 📦 Distribution Packaging

### macOS:
- Use DMG (you have this) ✅
- DMG includes: App + Applications shortcut + Instructions

### Windows:
- Use EXE alone (portable)
- OR package in ZIP with README
- No installer needed for simple apps

**For Windows, I recommend:**
1. Create EXE file
2. Put it in a ZIP with README.txt
3. Share the ZIP file
4. Users extract and run EXE

---

## 🚀 Ready-To-Share Files

### What you have NOW:
```
✅ macOS: CursorMover-macOS.dmg (25 MB)
   → Download, open, drag to Applications
```

### What you need to create:
```
⚠️ Windows: CursorMover.exe (30 MB)
   → Download, extract, run
```

---

## 💡 Summary

**macOS:**
- File: `CursorMover-macOS.dmg`
- Behavior: Mounts like a disk, user drags to install
- **You have this ready!**

**Windows:**
- File: `CursorMover.exe` or `CursorMover-Windows.zip`
- Behavior: Run directly, no installation
- Need to build on Windows

**Both are ready-to-share when created!**

