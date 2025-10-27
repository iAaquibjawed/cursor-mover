# CursorMover - Technology Stack

## 🎨 GUI Framework

**tkinter** (Built-in Python GUI library)
- Used for: Buttons, labels, windows, entry fields
- Included in Python by default
- Cross-platform (macOS, Windows, Linux)
- No additional installation needed

## 📚 Libraries Used

### Core Libraries

| Library | Purpose | Version | Source |
|---------|---------|---------|--------|
| **tkinter** | GUI framework | Built-in | Comes with Python |
| **pyautogui** | Cursor movement | ≥0.9.54 | User-installed |
| **Pillow** | Image support (for pyautogui) | ≥10.0.0 | User-installed |
| **numpy** | Number operations | Included | Auto-installed |

### Python Standard Library

- `threading` - Run cursor movement in background
- `random` - Generate random cursor positions
- `time` - Timing and intervals
- `sys` - System operations

## 🎯 What Each Library Does

### 1. **tkinter** (GUI)
```python
from tkinter import *          # Main GUI widgets
from tkinter import ttk        # Themed widgets
from tkinter import messagebox # Dialog boxes
```

**Used for:**
- Main window (`Tk()`)
- Buttons (Start, Stop)
- Labels (Status, instructions)
- Entry field (interval input)
- Message dialogs

**Why tkinter?**
- ✅ Built into Python (no extra install for dev)
- ✅ Cross-platform
- ✅ Simple and reliable
- ✅ Perfect for desktop apps
- ✅ Bundled into executable

### 2. **pyautogui** (Cursor Control)
```python
import pyautogui
```

**Used for:**
- Getting screen size
- Moving cursor to random positions
- Positioning the cursor

**Why pyautogui?**
- Cross-platform cursor control
- Simple API
- Works on macOS, Windows, Linux
- Handles permissions automatically

### 3. **Other Built-ins**
```python
import threading  # Background tasks
import random     # Random coordinates
import time       # Delays
```

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   tkinter GUI (Visual)         │
│   - Buttons, Labels, Windows    │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│   pyautogui (Functionality)    │
│   - Cursor movement             │
└─────────────────────────────────┘
```

**Simple & Clean:**
- tkinter = User interface
- pyautogui = Cursor control
- threading = Non-blocking operations

## 📦 Bundle Size

**Why the app is ~25-30 MB:**
- Python runtime
- tkinter (GUI framework)
- pyautogui + dependencies
- Pillow (image library)
- numpy (math library)
- All bundled into one executable

## 🔄 Cross-Platform

**Same code works on all platforms:**
- macOS: ✅ Uses tkinter (built-in)
- Windows: ✅ Uses tkinter (built-in)
- Linux: ✅ Uses tkinter (may need python3-tk)

**No platform-specific GUI code needed!**

## 📝 Summary

**GUI = tkinter only**
- Simple, built-in
- No complex frameworks
- Cross-platform
- Easy to bundle

