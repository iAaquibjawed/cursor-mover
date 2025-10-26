#!/bin/bash
# Build script for all platforms (macOS, Windows, Linux)
# Note: Windows builds must be done on Windows or using Wine
# Linux builds must be done on Linux

set -e

echo "============================================"
echo "Building CursorMover for All Platforms"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Build for macOS (current platform)
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_info "Building for macOS..."

    pyinstaller --clean --noconfirm CursorMover.spec

    print_status "macOS build complete: dist/CursorMover.app"

    # Create macOS DMG
    if [ -f "./create_dmg.sh" ]; then
        ./create_dmg.sh
        print_status "macOS DMG created"
    fi

fi

# Build for Linux (current platform if on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_info "Building for Linux..."

    pyinstaller --clean --noconfirm CursorMover-linux.spec

    chmod +x dist/CursorMover
    print_status "Linux build complete: dist/CursorMover"

    # Create Linux tarball
    print_info "Creating Linux distribution..."
    tar -czf dist/CursorMover-Linux.tar.gz -C dist CursorMover README.txt 2>/dev/null || true
    print_status "Linux tarball created: dist/CursorMover-Linux.tar.gz"
fi

# Build for Windows (note: must be done on Windows or use Wine)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -n "$WINE" ]]; then
    print_info "Building for Windows..."

    pyinstaller --clean --noconfirm CursorMover-windows.spec

    print_status "Windows build complete: dist/CursorMover.exe"

    # Create Windows zip
    if command -v zip &> /dev/null; then
        print_info "Creating Windows zip..."
        cd dist && zip -r CursorMover-Windows.zip CursorMover.exe README.txt 2>/dev/null || true
        cd ..
        print_status "Windows zip created: dist/CursorMover-Windows.zip"
    fi
fi

echo ""
print_status "Build complete for current platform!"
echo ""
print_info "Note: To build for all platforms:"
echo "  - macOS builds: Run on macOS"
echo "  - Linux builds: Run on Linux"
echo "  - Windows builds: Run on Windows"
echo ""
print_info "Cross-platform options:"
echo "  - Use Docker for Linux builds"
echo "  - Use GitHub Actions for automated builds"
echo "  - Use Wine for Windows builds (not recommended)"
echo ""

