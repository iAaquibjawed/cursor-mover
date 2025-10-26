#!/usr/bin/env python3
"""
Helper script to request macOS accessibility permissions
Run this if the app can't control the cursor
"""

import sys
import subprocess
import os

def request_accessibility_permission():
    """Attempt to guide user to grant accessibility permissions"""

    if sys.platform != "darwin":
        print("This script is for macOS only")
        return

    print("=" * 50)
    print("macOS Accessibility Permissions")
    print("=" * 50)
    print()
    print("The app needs accessibility permissions to control your cursor.")
    print()
    print("Follow these steps:")
    print()
    print("1. Open System Settings")
    print("2. Go to Privacy & Security")
    print("3. Click on Accessibility")
    print("4. Click the '+' button")
    print("5. Navigate to Terminal (or Python if you have it)")
    print("6. Enable the toggle")
    print()
    print("Or run:")
    print("  sudo open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'")
    print()

    response = input("Open System Settings now? (y/n): ")
    if response.lower() == 'y':
        try:
            subprocess.run(["open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
            print("System Settings should open now")
        except Exception as e:
            print(f"Could not open System Settings: {e}")

    print()
    print("After granting permissions, you may need to restart the app.")

if __name__ == "__main__":
    request_accessibility_permission()

