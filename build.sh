#!/bin/bash
# Build script for Random Cursor Mover Desktop App
# Builds executables for macOS, Windows, and Linux

set -e

echo "============================================"
echo "Building Random Cursor Mover"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    print_error "PyInstaller is not installed"
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

print_status "PyInstaller found"

# Create build directories
mkdir -p dist
mkdir -p build

# Detect OS
OS="$(uname -s)"
case "$OS" in
  Darwin*)
    PLATFORM="macos"
    ;;
  Linux*)
    PLATFORM="linux"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    PLATFORM="windows"
    ;;
  *)
    print_error "Unknown operating system"
    exit 1
    ;;
esac

print_info "Detected platform: $PLATFORM"

# Function to build for macOS
build_macos() {
    print_info "Building for macOS..."

    pyinstaller --name="CursorMover" \
                --windowed \
                --onedir \
                --add-data "README.md:." \
                --clean \
                --noconfirm \
                cursor_mover.py

    print_status "macOS build complete: dist/CursorMover.app"
}

# Function to build for Linux
build_linux() {
    print_info "Building for Linux..."

    pyinstaller --name="CursorMover" \
                --windowed \
                --onefile \
                --add-data "README.md:." \
                --clean \
                --noconfirm \
                cursor_mover.py

    chmod +x dist/CursorMover
    print_status "Linux build complete: dist/CursorMover"
}

# Function to build for Windows (requires Windows or Wine)
build_windows() {
    print_info "Building for Windows..."

    pyinstaller --name="CursorMover" \
                --windowed \
                --onefile \
                --add-data "README.md;." \
                --clean \
                --noconfirm \
                cursor_mover.py

    print_status "Windows build complete: dist/CursorMover.exe"
}

# Build for current platform
case "$PLATFORM" in
  macos)
    build_macos
    ;;
  linux)
    build_linux
    ;;
  windows)
    print_error "Windows builds should be done on Windows"
    print_info "Creating Linux executable instead..."
    build_linux
    ;;
esac

echo ""
print_status "Build complete!"
echo ""
print_info "Executable location: dist/"
echo ""
print_info "To test the app:"
case "$PLATFORM" in
  macos)
    echo "  open dist/CursorMover.app"
    ;;
  linux)
    echo "  ./dist/CursorMover"
    ;;
esac
echo ""

