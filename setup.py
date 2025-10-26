#!/usr/bin/env python3
"""
Setup script for Random Cursor Mover
Makes the script executable and installs dependencies
"""

import os
import sys
import subprocess

def make_executable():
    """Make the Python script executable"""
    script_path = "cursor_mover.py"
    if sys.platform != "win32":
        os.chmod(script_path, 0o755)
        print(f"✓ Made {script_path} executable")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    try:
        import tkinter
        print("✓ tkinter found")
    except ImportError:
        print("✗ tkinter not found (try: sudo apt-get install python3-tk)")
        return False

    try:
        import pyautogui
        print("✓ pyautogui found")
    except ImportError:
        print("✗ pyautogui not found")
        return False

    try:
        from PIL import Image
        print("✓ Pillow found")
    except ImportError:
        print("✗ Pillow not found")
        return False

    return True

def main():
    print("=" * 40)
    print("Random Cursor Mover Setup")
    print("=" * 40)
    print()

    # Make script executable
    make_executable()

    # Check dependencies
    if not check_dependencies():
        print()
        response = input("Install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            print("Please install dependencies manually:")
            print("  pip install -r requirements.txt")
            sys.exit(1)

    print()
    print("✓ Setup complete!")
    print()
    print("To run the app:")
    print("  python3 cursor_mover.py")
    print()
    print("Or if using PyInstaller:")
    print("  ./build.sh")
    print()

if __name__ == "__main__":
    main()

