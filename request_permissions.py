#!/usr/bin/env python3
"""
Helper script to request accessibility permissions for CursorMover
"""

import sys
import subprocess

def request_accessibility_permission():
    """Request accessibility permission for the app"""
    print("Requesting accessibility permissions...")

    try:
        # Try to move mouse to trigger permission request
        import pyautogui
        pyautogui.moveRel(1, 0)
        pyautogui.moveRel(-1, 0)
        print("✓ Permission granted!")
        return True
    except Exception as e:
        print(f"Permission not granted: {e}")
        print("\nPlease:")
        print("1. Open System Settings > Privacy & Security > Accessibility")
        print("2. Look for 'CursorMover' or 'Python' in the list")
        print("3. Enable the toggle next to it")
        print("4. Restart the app")
        return False

if __name__ == "__main__":
    if sys.platform == "darwin":
        request_accessibility_permission()
    else:
        print("This script is for macOS only")
